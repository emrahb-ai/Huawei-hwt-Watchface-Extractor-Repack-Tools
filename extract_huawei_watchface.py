#!/usr/bin/env python3
"""Drag a Huawei HWT onto this script to unpack its archive and BGRA/RLE PNG images."""
import csv
import json
import shutil
import struct
import sys
import zipfile
from pathlib import Path
from PIL import Image

MAGIC = bytes.fromhex("45238888")
RUN = bytes.fromhex("89674523")

def decode_image(blob):
    if len(blob) < 8 or blob[:4] != MAGIC:
        raise ValueError("Unsupported image format")
    width, height = struct.unpack_from("<HH", blob, 4)
    if not (0 < width <= 4096 and 0 < height <= 4096):
        raise ValueError("Invalid dimensions")
    count = width * height
    raw = bytearray(count * 4)
    src = 8
    dst = 0
    while dst < count:
        if src + 4 > len(blob):
            raise ValueError("Truncated image")
        if blob[src:src+4] == RUN:
            if src + 12 > len(blob):
                raise ValueError("Truncated RLE")
            color = blob[src+4:src+8]
            amount = struct.unpack_from("<I", blob, src+8)[0]
            if not (1 <= amount <= count-dst):
                raise ValueError("Invalid RLE count")
            raw[dst*4:(dst+amount)*4] = color * amount
            src += 12
            dst += amount
        else:
            raw[dst*4:dst*4+4] = blob[src:src+4]
            dst += 1
            src += 4
    if src != len(blob):
        raise ValueError("Unexpected trailing data")
    return Image.frombytes("RGBA", (width,height), bytes(raw), "raw", "BGRA")

def extract_images(source, output):
    output.mkdir(parents=True, exist_ok=True)
    data = source.read_bytes()
    if len(data) < 24:
        raise ValueError("Truncated container")
    version, layout_size, table_size, body_size, unknown = struct.unpack_from("<HHIII", data)
    if table_size % 8:
        raise ValueError("Invalid image map")
    body_start = 16 + layout_size + table_size + 8
    if body_start > len(data):
        raise ValueError("Truncated sections")
    (output / "layout.protobuf").write_bytes(data[16:16+layout_size])
    (output / "image_map.bin").write_bytes(data[16+layout_size:body_start-8])
    (output / "separator.bin").write_bytes(data[body_start-8:body_start])
    records = []
    success = 0
    for i in range(table_size // 8):
        off, size = struct.unpack_from("<II", data, 16+layout_size+i*8)
        start = body_start + off - 8
        end = start + size
        row = dict(index=i, offset=off, size=size, status="", width="", height="")
        if size == 0:
            row["status"] = "empty"
        elif start < body_start or end > len(data):
            row["status"] = "invalid range"
        else:
            blob = data[start:end]
            try:
                image = decode_image(blob)
                image.save(output / f"image_{i:03d}.png")
                row.update(status="png",width=image.width,height=image.height)
                success += 1
            except Exception as ex:
                (output / f"image_{i:03d}_unparsed.bin").write_bytes(blob)
                row["status"] = "unparsed: " + str(ex)
        records.append(row)
    with (output / "manifest.csv").open("w",newline="",encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["index","offset","size","status","width","height"])
        writer.writeheader()
        writer.writerows(records)
    metadata = dict(version=version,protobuf_bytes=layout_size,image_map_bytes=table_size,body_length_field=body_size,unknown_header_value=unknown,body_start=body_start,total_bytes=len(data),images_extracted=success,entries=len(records))
    (output / "header.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Extracted {success} PNG images / {len(records)} records")

def extract_hwt(path):
    path = Path(path).resolve()
    if not zipfile.is_zipfile(path):
        raise ValueError("Expected a valid .hwt ZIP archive")
    root = path.with_suffix("")
    if root.exists():
        raise FileExistsError(f"Output folder already exists: {root}")
    root.mkdir()
    try:
        with zipfile.ZipFile(path) as archive:
            for member in archive.infolist():
                destination = (root / member.filename).resolve()
                if not destination.is_relative_to(root.resolve()):
                    raise ValueError(f"Unsafe archive path: {member.filename}")
                if member.is_dir():
                    destination.mkdir(parents=True,exist_ok=True)
                else:
                    destination.parent.mkdir(parents=True,exist_ok=True)
                    with archive.open(member) as src, destination.open("wb") as dst:
                        shutil.copyfileobj(src,dst)
        candidates = list(root.rglob("com.huawei.watchface"))
        if len(candidates) != 1:
            raise ValueError("Expected exactly one com.huawei.watchface")
        extract_images(candidates[0], root / "watchface_extracted")
        (root / ".hwt_source_name.txt").write_text(path.name,encoding="utf-8")
    except Exception:
        shutil.rmtree(root)
        raise
    print("Working folder:", root)

def main():
    if len(sys.argv) < 2:
        print("Drag and drop a .hwt file onto this Python script.")
    for arg in sys.argv[1:]:
        try:
            extract_hwt(arg)
        except Exception as exc:
            print("ERROR:",type(exc).__name__,exc)
    if sys.platform == "win32":
        input("Press Enter to close...")

if __name__ == "__main__":
    main()
