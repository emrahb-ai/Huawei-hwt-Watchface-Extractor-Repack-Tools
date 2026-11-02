#!/usr/bin/env python3
"""Drag an extracted HWT working folder onto this script to rebuild the image container and HWT."""
import io
import struct
import sys
import zipfile
from pathlib import Path
from PIL import Image

MAGIC = bytes.fromhex("45238888")
RUN = bytes.fromhex("89674523")

def decode(blob):
    if len(blob) < 8 or blob[:4] != MAGIC:
        raise ValueError("Unsupported image header")
    w, h = struct.unpack_from("<HH", blob, 4)
    if not (0 < w <= 4096 and 0 < h <= 4096):
        raise ValueError("Invalid dimensions")
    n = w * h
    pixels = bytearray(n*4)
    src = 8
    dst = 0
    while dst < n:
        if src + 4 > len(blob):
            raise ValueError("Truncated pixel")
        if blob[src:src+4] == RUN:
            if src + 12 > len(blob):
                raise ValueError("Truncated RLE")
            color = blob[src+4:src+8]
            num, = struct.unpack_from("<I", blob, src+8)
            if not (1 <= num <= n-dst):
                raise ValueError("Invalid repeat count")
            pixels[dst*4:(dst+num)*4] = color*num
            dst += num
            src += 12
        else:
            pixels[dst*4:dst*4+4] = blob[src:src+4]
            dst += 1
            src += 4
    if src != len(blob):
        raise ValueError("Trailing image bytes")
    return Image.frombytes("RGBA",(w,h),bytes(pixels),"raw","BGRA")

def encode(img):
    img = img.convert("RGBA")
    w,h = img.size
    if not (0 < w <= 4096 and 0 < h <= 4096):
        raise ValueError("Invalid dimensions")
    raw = img.tobytes("raw","BGRA")
    count = w*h
    result = bytearray(MAGIC + struct.pack("<HH",w,h))
    i = 0
    while i < count:
        color = raw[i*4:i*4+4]
        j = i+1
        while j < count and raw[j*4:j*4+4] == color:
            j += 1
        length = j-i
        if length >= 3 or color == RUN:
            result.extend(RUN + color + struct.pack("<I",length))
        else:
            result.extend(color*length)
        i = j
    result = bytes(result)
    if decode(result).tobytes() != img.tobytes():
        raise ValueError("Encoder verification failed")
    return result

def rebuild(original, png_dir):
    if len(original) < 24:
        raise ValueError("Truncated container")
    version, layout_len, map_len, length_field, unknown = struct.unpack_from("<HHIII", original)
    if map_len % 8:
        raise ValueError("Invalid image table")
    body_start = 16+layout_len+map_len+8
    if body_start > len(original):
        raise ValueError("Invalid sections")
    records = []
    edited = []
    for index in range(map_len//8):
        offset,size = struct.unpack_from("<II",original,16+layout_len+8*index)
        start = body_start+offset-8
        end = start+size
        if start < body_start or end > len(original):
            raise ValueError(f"Invalid block {index}")
        blob = original[start:end]
        png = png_dir / f"image_{index:03d}.png"
        if png.exists():
            original_img = decode(blob)
            with Image.open(png) as image:
                edited_img = image.convert("RGBA")
            # Image dimensions are encoded within each image record. A resized
            # PNG is valid for this container, but the existing layout.protobuf
            # still refers to its original layout/positions and is not rewritten.
            if edited_img.size != original_img.size or edited_img.tobytes() != original_img.tobytes():
                if edited_img.size != original_img.size:
                    print(f"WARNING image_{index:03d}: resized {original_img.size} -> {edited_img.size}; layout.protobuf has not been adjusted.")
                blob = encode(edited_img)
                edited.append(index)
        records.append(blob)
    new_table = bytearray()
    new_body = bytearray()
    for blob in records:
        new_table.extend(struct.pack("<II", len(new_body)+8,len(blob)))
        new_body.extend(blob)
    header = bytearray(original[:16+layout_len])
    struct.pack_into("<I",header,8,len(new_body)+8)
    output = bytes(header) + bytes(new_table) + original[body_start-8:body_start] + bytes(new_body)
    if len(output) < body_start:
        raise ValueError("Bad rebuilt container")
    for index in edited:
        off,size = struct.unpack_from("<II",new_table,index*8)
        reconstructed = decode(output[body_start+off-8:body_start+off-8+size])
        with Image.open(png_dir / f"image_{index:03d}.png") as image:
            if reconstructed.tobytes() != image.convert("RGBA").tobytes():
                raise ValueError(f"Mismatch in image {index}")
    return output,edited

def repack_folder(folder_path):
    folder = Path(folder_path).resolve()
    if not folder.is_dir():
        raise ValueError("Drag the extracted directory, not a file")
    png_dir = folder / "watchface_extracted"
    if not png_dir.is_dir():
        raise FileNotFoundError("Missing watchface_extracted folder")
    source_name_path = folder / ".hwt_source_name.txt"
    source_name = Path(source_name_path.read_text(encoding="utf-8").strip()).name if source_name_path.exists() else folder.name+".hwt"
    source_hwt = folder.parent / source_name
    if not source_hwt.is_file():
        raise FileNotFoundError(f"Original HWT not found: {source_hwt}")
    if not zipfile.is_zipfile(source_hwt):
        raise ValueError("Original file is not an HWT archive")
    out_watchface = folder / "com.huawei.watchface_repack"
    out_hwt = folder.parent / (Path(source_name).stem+"_repack.hwt")
    if out_watchface.exists() or out_hwt.exists():
        raise FileExistsError("Output already exists; move or rename before retrying")
    with zipfile.ZipFile(source_hwt) as archive:
        watchface_names = [name for name in archive.namelist() if Path(name).name == "com.huawei.watchface"]
        if len(watchface_names) != 1:
            raise ValueError("Expected exactly one com.huawei.watchface")
        watchface_name = watchface_names[0]
        original = archive.read(watchface_name)
    rebuilt, changed = rebuild(original,png_dir)
    buffer = io.BytesIO()
    changed_members = []
    with zipfile.ZipFile(source_hwt) as archive, zipfile.ZipFile(buffer,"w") as result:
        result.comment = archive.comment
        for info in archive.infolist():
            if info.is_dir():
                result.writestr(info,b"")
                continue
            if info.filename == watchface_name:
                payload = rebuilt
            else:
                candidate = (folder / info.filename).resolve()
                if not candidate.is_relative_to(folder):
                    raise ValueError("Unsafe archive path")
                original_data = archive.read(info.filename)
                payload = candidate.read_bytes() if candidate.is_file() else original_data
                if payload != original_data:
                    changed_members.append(info.filename)
            result.writestr(info,payload)
    with zipfile.ZipFile(io.BytesIO(buffer.getvalue())) as archive:
        if archive.read(watchface_name) != rebuilt:
            raise ValueError("HWT verification failed")
    out_watchface.write_bytes(rebuilt)
    out_hwt.write_bytes(buffer.getvalue())
    print("New watchface:",out_watchface)
    print("New HWT:",out_hwt)
    print("Edited PNG entries:",changed)
    print("Edited ZIP members:",changed_members)
    print("Unedited container byte-identical:",rebuilt == original)

def main():
    if len(sys.argv) < 2:
        print("Drag the extracted working folder onto repack.py")
    for arg in sys.argv[1:]:
        try:
            repack_folder(arg)
        except Exception as exc:
            print("ERROR:",type(exc).__name__,exc)
    if sys.platform == "win32":
        input("Press Enter to close...")

if __name__ == "__main__":
    main()
