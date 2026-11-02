# Huawei HWT Watchface Tools

Python utilities to extract and repack Huawei `.hwt` watchface archives using Windows drag-and-drop.

## Windows standalone app (EXE)

The Windows GUI offers **Extract HWT** and **Repack folder** in one executable. Python/Pillow are bundled into the compiled EXE.

**Download/build:** Open [GitHub Actions](https://github.com/emrahb-ai/Huawei-hwt-Watchface-Extractor-Repack-Tools/actions/workflows/windows-exe.yml), choose **Run workflow**, wait until the run finishes successfully, then download the artifact **Huawei-HWT-Tools-Windows-x64** and unzip it to get `Huawei-HWT-Tools.exe`. Automatic builds also run when GUI/extractor/repacker code changes.

**Usage:** Select an HWT file to Extract; edit PNG files in the resulting same-named folder (resizing is supported in image records; layout positions are not automatically updated); then select that folder for Repack. The original HWT must remain beside the folder. Dragging an HWT file or working folder onto the EXE icon is supported too.

**Validation status:** The extractor has been tried on Windows by the project owner. The repacker and the compiled Windows EXE still require end-to-end tests on Windows and an actual Huawei watch. Do not overwrite your original watchface.

## Features
- Drag an `.hwt` file onto `extract_huawei_watchface.py`: extracts archive contents to a same-named folder and converts compatible `com.huawei.watchface` BGRA/RLE images to PNGs.
- Edit extracted PNG images including their pixel dimensions (layout may need manual adjustment).
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
## Resizing PNG images / Görsel ölçülerini değiştirme

The repacker supports both changed PNG file size (KB) and changed PNG pixel dimensions (width × height). It re-encodes the edited PNG in the watchface BGRA/RLE format and rebuilds the image-record offsets and lengths. **Important:** `layout.protobuf` is preserved, not recalculated. Images that are larger or smaller might be incorrectly placed or clipped on the watch. Device compatibility is not yet confirmed.

Repacker, PNG görsellerinin hem dosya boyutunun hem de piksel genişlik/yüksekliğinin değişmesini kabul eder. Fakat `layout.protobuf` içindeki yerleşim koordinatları otomatik güncellenmez. Saat ekranında konum/kırpılma sorunu oluşabilir.
