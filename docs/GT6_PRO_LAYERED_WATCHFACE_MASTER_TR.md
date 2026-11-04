# Huawei GT 6 Pro — Layered Watchface Master Workflow (TR)
**Revision:** 2026-11-04 · **Reference model:** Champagne / Graphite · **Designer:** `rabilgic` · **Target canvas:** 466 × 466 px

This document preserves the established working agreement for converting the user's OTHER previously designed watchfaces into **true editable, separate PNG layers**. The Champagne design is the reference **workflow**, not a style to impose on other designs.

## Non-negotiable rules
1. **Do not invent a new watchface design** when asked to extract or prepare layers from an existing preview. Preserve shape, scale, texture, lighting, placement and colors of THAT preview.
2. Separate **static background** from dynamic information. The background must keep its panels, metal textures, decorative rings, dividers (unless explicitly removed), and other deliberately static visual elements; it must NOT include fixed time/date/sensor values, moving hands or animated progress.
3. When a visual element has been separated into its own PNG, remove it **only from the source background**, without removing other elements or changing surrounding geometry. Never use a recreated approximation when exact pixel-preserving local editing is possible.
4. Every independent asset: RGBA PNG with transparent pixels outside the asset, a **cropped** version plus optionally a **466 × 466 full-canvas** version anchored at (0,0). Provide X/Y, width/height, pivot/rotation metadata. Verify alpha visually (solid black is not transparency).
5. Each set of alternate dynamic states uses identical dimensions and alignment.
6. Export separate **TR and EN** weekday/month/label assets; keep 19-character maximum English watchface title; designer `rabilgic`.
7. **Always On Display (AOD)** must use very dark, sparse, desaturated champagne/gray assets with low energy use. Theme Studio warning: dial overall brightness must be <50%. AOD passes only after measurement in actual Theme Studio.
8. Old template HWT repacks are **experimental**, NOT genuine Theme Studio source projects and NOT developer-ready exports. Never claim watch-side support, signed install, or Theme Studio validation without actual testing.
9. Do not silently replace the user's requested content with generated image approximations. Show source/after comparison and document deviations.

## Standard output tree (per watchface)
```
<short-watchface-name>/
  00_reference/preview.png
  01_background/image_001.png              # 466×466, no live contents
  02_time/hour_0..9.png; minute_0..9.png; colon.png; second_0..9.png; AM.png; PM.png
  03_hands/hour.png; minute.png; second.png; pivot.json
  04_calendar/weekdays_TR/; weekdays_EN/; days_00..31/; months_TR/; months_EN/
  05_labels/TR/; EN/
  06_data_digits/calories/; temperature/; battery/; steps/; heart_rate/; distance/; step_goal/
  07_progress/calories_00..13/; battery_0..4/; steps_goal_0..4/
  08_weather/icons/
  09_icons_and_separators/
  10_aod/background.png; hour.png; minute.png
  manifest.json                              # coordinates, dimensions, transparency, source provenance
  README.md
```

## Established Champagne reference layers
- Time: white hour/minute digits 0–9, colon; champagne seconds 0–9; AM and PM images.
- Clock hands: hour, minute and second as **three independent assets**. Pivot must align precisely to face center and hands must be tested when rotated.
- Weekdays: seven full names and 3-letter variants in TR and EN.
- Calendar: dates 0–31 (0 included because explicitly requested, but 1–31 used for valid dates); twelve months in TR/EN, full and abbreviated.
- Static labels (independent TR/EN): KALORİ/CALORIES, HAVA/WEATHER, PİL/BATTERY, ADIM/STEPS, NABIZ/PULSE, MESAFE/DISTANCE, HEDEF/TARGET, and independent bottom goal ADIM/STEPS. Also `kcal`.
- Data digits: seven independent 0–9 font/size groups: calorie, temperature, battery %, step count, heart rate, distance, step target. Symbols: `°`, `%`, `km`, `kcal`, decimal point, minus sign.
- Calories: original 13-segment arc, from lowest segment moving upward; 0/13 dark + 1/13 through 13/13 Champagne progressively lit states. Each same-size asset.
- Battery: same external battery icon, four internal segments; five states (0–4 filled, left to right).
- Step target: four diagonal segment bars; five states (0–4 filled, left to right); preserve exact size/shape.
- Weather icons: separate variants; recolor warm orange/yellow sun, question mark, lightning and moon to muted Champagne, preserve cloud/other detail.
- Icons: calendar, flame, calorie arc, sun/cloud, battery, shoe, heart/ECG, location marker, target; separate `kcal` label and dividers.
- AOD: face rim plus minimal desaturated Champagne markers, separate dim hour and minute hands; no colorful dashboard data.

## Source archives and preservation
Source archives generated together during the Champagne session include:
`GT6_Pro_Dijital_Saat_Rakamlari_PNG.zip`,
`GT6_Pro_Gunler_TR_EN_PNG.zip`,
`GT6_Pro_Gun_0_31_Aylar_TR_EN_PNG.zip`,
`GT6_Pro_Sabit_Etiketler_TR_EN.zip`,
`GT6_Pro_7_Alan_Rakamlar_ve_Birimler.zip`,
`GT6_Pro_Simgeler_Ayri_Katmanlar.zip`,
`GT6_Pro_4_Ayirici_Cizgi_PNG.zip`,
`GT6_Pro_Kalori_Cemberi_13_Kademe.zip`,
`GT6_Pro_4_Cubuk_5_Varyasyon.zip`,
`GT6_Pro_Pil_4_Kutu_5_Kademe.zip`,
`GT6_Pro_Hava_Durumu_Sampanya_7_PNG.zip`,
`GT6_Pro_AOD_Sampanya_Paket.zip`,
plus progressive background edits and the 10 original design reference images.

**Important:** File names in this GitHub document are an index, **not proof that binary assets were uploaded here**. The companion local backup ZIP must be retained/uploaded to a GitHub Release or external storage separately.

## For the other nine designs
Receive preview + original source if available. Determine visual fields and dynamic behavior. Reconstruct this entire asset schema in one coherent pass, with consistent canvas and manifest; only adapt actual elements and palette from that design. No 100-turn back-and-forth required for routine separation.

## Quality gate before delivery
- 466×466 output and alpha check
- State counts and left-to-right / bottom-to-top order
- All visible source-preview values removed from `image_001.png`; decorative fixed labels handled per approved layer plan
- Independent layers overlay background with original coordinate alignment
- Compare reconstructed sample preview with source reference for visual consistency
- AOD low-luminance check in Theme Studio
- HWT only after native Theme Studio assembly, simulation, export, validation and device test

## Device/install limitation
Huawei Watch GT 6 Pro on HarmonyOS 6.1.0 may reject third-party custom HWT activation; Gadgetbridge showing transfer complete does not establish installation. Developer publishing/approval is separate from asset preparation.
