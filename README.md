# Huawei HWT Watchface Tools

Python utilities to extract and repack Huawei `.hwt` watchface archives using Windows drag-and-drop.

## Features
- Drag an `.hwt` file onto `extract_huawei_watchface.py`: extracts archive contents to a same-named folder and converts compatible `com.huawei.watchface` BGRA/RLE images to PNGs.
- Edit extracted PNG images without changing their dimensions.
- Drag the extracted folder onto `repack.py`: builds `com.huawei.watchface_repack` and `<original>_repack.hwt`.
- Preserves unknown image records and unmodified image data.
- Supports edits to extracted preview files and `description.xml`.

## Requirements
Python 3.9+ and Pillow:

```powershell
py -m pip install -r requirements.txt
```

## How to use
1. Keep an original backup of your `.hwt`.
2. Drag the `.hwt` file onto `extract_huawei_watchface.py`.
3. Open the new folder (same name as the archive, without `.hwt`) and edit the `watchface_extracted/image_NNN.png` images.
4. Keep image dimensions unchanged, and retain the original `.hwt` alongside the extracted folder.
5. Drag the extracted folder onto `repack.py`.
6. Find `<name>_repack.hwt` beside the original archive.

The extractor avoids overwriting existing folders; the repacker avoids overwriting existing outputs.

## Türkçe
1. `.hwt` dosyasını `extract_huawei_watchface.py` üzerine sürükleyip bırakın.
2. Aynı isimli klasördeki `watchface_extracted` alt klasöründen PNG'leri düzenleyin.
3. Görsellerin piksel ölçülerini değiştirmeyin.
4. Çalışma klasörünü `repack.py` üzerine sürükleyip bırakın.
5. Orijinal dosyanın yanında `_repack.hwt` dosyası oluşturulur.

## Limitations
Supported image format: the Huawei BGRA/RLE records observed in the tested watchface. Other records are preserved rather than decoded. Rebuilding an archive does **not** guarantee installation through Huawei Health or compatibility with all watch models. Huawei trademarks belong to their respective owners. This is an independent community tool.

Do not commit proprietary watchfaces, copyrighted assets, or personal files.