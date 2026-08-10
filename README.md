# GBFR Damage Font Mod Maker

A no-code, visual tool for making damage-number / symbol font mods for *Granblue Fantasy: Relink*. Single-file EXE, double-click to run, with an English / Chinese UI.

> Current version: **v57**

> **v57 changelog**: **Main-table grid redesign.** The 6-column table is now a single grid with solid separator lines between every row and column, drawn on a theme-colored background. The header now lives in the *same* grid container as the data rows, so all columns stay aligned even when you stretch the window (previously the header and body used two separate grids and drifted apart on resize). Columns ⑤ (Replace) and ⑥ (Overlay/Tint) are stretchable.

> **v56 changelog**: Fixed a startup `NameError: name 'inner' is not defined` introduced by the overlay-cell refactor in v55.

> **v55 changelog**: First pass at the line-separated grid layout (solid cell borders; removed the fixed cell widths that caused misalignment when the window was enlarged).

> **v54 changelog**: **Bug fix — tint now applies to the currently displayed replace image, not a stale one.** Root cause: `_apply_tint` tints from `st["repl_base"]`, but two import paths set `st["repl"]` (the preview image) **without updating `st["repl_base"]`** — ① "Replace same sprite code across groups" (the per-code batch replace) and ② Font (TTF/OTF) generation. So if you had, say, generated a font PNG earlier (which set `repl`) and then batch-replaced the same slot with a new PNG (which set `repl` but not `repl_base`), checking Tint would color the *old font PNG* instead of the current preview. Now **every** path that sets the replace image also sets `st["repl_base"]` and calls `_update_tint_enabled` + `_apply_tint`, so Tint always operates on the image currently shown in column ⑤.

> **v53 changelog**: Fixed **excessive row height** — row height was calculated from the **native image's original pixel height** (e.g. 364px for a 226×364 sprite) instead of the **thumbnail display height** (max 92px per NATIVE_MAX). Now uses the same `to_thumb` scale formula to compute display height, with ROW_MIN lowered from 150→130. A 364px-tall sprite now produces a ~130px row instead of ~380px.

> **v53 changelog**: ① Widened column 6 (COL_W 210→260) to give more centering room so data rows align with the header. ② Added a **separate Opacity input field** (0-255) per row in column 6, bi-directionally synced with the A value in the RGBA color box — change either one and the other updates automatically.

> **v51 changelog**: 6th column (Overlay/Tint) overhaul — ① all RGB(A) color pickers merged into **one input box** (type `R,G,B` or `R,G,B,A`); applies to the 6th-column tint, teammate damage color, and TTF per-group color; the swatch is now directly clickable to open the picker (no separate palette tab). ② Tint checkbox is **grayed/disabled while the ⑤ preview is empty**, enables once a replacement image exists, and live-toggles: checked → tints with the RGBA color, unchecked → restores the original (non-destructive). ③ Native Overlay (per-row and header "overlay all") now **resets the ⑤ scale to 100%**. ④ Fixed the 6th column still looking misaligned — root cause was the TABLE body giving only the last column `weight=1` while the HEADER gave columns ④ & ⑤ `weight=1`, so header/data column boundaries diverged and column ⑥ shifted left vs the header. The table now matches the header's column config, so their vertical axes coincide.

> **v48 fix**: Fixed startup crash `TypeError: unsupported operand type(s) for +: 'method' and 'int'` at `_build_row` line 916. Root cause: v47 introduced dynamic row height using `nat_thumb.height + 16`, but `to_thumb()` returns a `PhotoImage` whose `.height` is a **method** (not a property like PIL Image). Fix: use `st["native_pil"].height` (PIL Image, property) instead. Also fixed missing `core.py` module in build directory (`No module named 'core'`).

> **v47 changelog**: Added a 6th column "Native Overlay / Tint" — a per-row "Native Overlay…" button copies that sprite's native image as the replacement (auto-switches to Replace); if the row's "Tint" checkbox is on, it first tints the native image with the RGBA palette color (keeping the native alpha shape) then overlays. The column header has "Overlay all native images to preview…" to batch-overlay every sprite. Recoloring a sprite (e.g. the damage-cap flash) is now one click.

> **v42 changelog**: Added 6 missing effect sprites to `sprites.json` (112→118): the long underline and Y-shaped star flash the previous build had dropped, plus a few others — so the tool no longer misses bottom-left / mid-bottom effects.

> **v40 changelog**: Fixed indicator misalignment for characters with functional indicators (exChr10_/11_/24~28_, endlessIcon_, skillBoard_, etc.). Replaced `hud_param.json` template with the full 52-block native template (previously only 35 blocks, causing 17 blocks to go missing during Reloaded-II's whole-file replacement). Updated all DEFAULT_SIZE_SCALE values to match current native game values (`viewTime_` 1.5→0.2, `commonSize_` 1.0→0.42, `criticalSize_` 1.0→0.33, `playerCriticalSize_` 1.0→0.8). Added numpy dependency.

---

## ✨ Features

- **Generate colored PNGs from TTF**: pick a `.ttf` / `.otf` font, customize color / opacity / bold / italic per group, and one-click generate colored digits that are imported and swapped in automatically.
- **Multiple replacement modes**: manual single-image import, batch import from a folder (filename = element name, auto-matched), or batch-replace an entire group by index (00–12).
- **Damage-number size control**: edit the scale factor in `hud_param.json`, range 0–20, where 1.0 = native size and 0 = hidden.
- **Collapsible grouped table** + live native-ratio preview.
- **Bilingual UI** (English / Chinese), switchable with one click at the top-right.
- **6-column layout**: ① Name · ② Coord · ③ Native (real ratio) · ④ Action (Keep/Block/Replace) · ⑤ Replace image (import + scale + stretch) · ⑥ **Native Overlay / Tint** — one-click "Native Overlay…" copies the sprite's native image as the replacement; with "Tint" checked it recolors the native image via the RGBA palette (keeping the native alpha shape) first. The header button "Overlay all native images to preview…" batches it for every sprite.
- **One-click export**: each of columns ①②③ has an "Export…" button — column 1 exports the element-name Excel, column 2 the coordinate-table Excel, column 3 the native-PNG folder; the toolbar "Export all columns…" exports a single Excel with thumbnails (element name / coordinates / size / native image / action / replacement image).
- Click "Generate Mod" to get a zip (output to `./mod_output` by default), then load it with Reloaded-II to apply.

---

## 📥 Download

- **Prebuilt EXE (recommended for most users)**: [`gbfr_mod_maker_v57.zip`](gbfr_mod_maker_v57.zip) at the repo root. Unzip to get `gbfr_mod_maker_v57.exe`, double-click to run — no Python needed.
- To use "Generate PNG from TTF" out of the box, drop any `.ttf` next to the exe and rename it to `LiXuKeShuFa-1.ttf` (or click "Browse" in the app to pick a font).

> For a nicer download button, check the repo **Releases** page (the same zip is usually attached there).

---

## 🚀 Quick Start

1. (Optional) Click "Generate PNG from TTF" to make colored font PNGs; or import replacement images manually / in batch.
2. (Optional) Click "Damage-number size control" to adjust the scale.
3. Click "Generate Mod" to produce a zip (output to `./mod_output` by default).
4. Load the generated mod with Reloaded-II + `gbfrelink.utility.manager`, then launch the game.

> ⚠️ Note the two different output folders: "Mod output directory" (`./mod_output`, the final archive) vs "Font PNG output directory" (`./font_output`, the colored PNGs from TTF). They are not the same.

---

## 🧩 Prerequisites (to run mods)

- [Reloaded-II](https://github.com/Reloaded-Project/Reloaded-II)
- [gbfrelink.utility.manager](https://github.com/Nenkai23/GBFR-Utils) (Nenkai)

---

## 🛠️ Build from Source

Requires Python 3.10+ and these dependencies:

```bash
pip install pyinstaller pillow openpyxl numpy
```

Build from inside the `src/` directory:

```bash
cd src
pyinstaller --noconfirm --onefile ^
  --add-data "resources;resources" ^
  --collect-submodules=PIL --collect-submodules=openpyxl ^
  --hidden-import numpy --collect-submodules=numpy ^
  --name gbfr_mod_maker_v57 gbfr_mod_maker.py
```

> On Windows the `--add-data` separator is `;` (as shown). On macOS / Linux use `:`.
> Or simply run `pyinstaller gbfr_mod_maker_v57.spec` (also from inside `src/`).

Native assets (atlases / `sprites.json` / `hud_param.json` template / `texconv.exe`) live in `src/resources/`.

---

## 📚 Reference Docs

The `docs/` folder contains analysis notes from the project's development, for those who want to dig deeper:

- `docs/GBFR_伤害数字与Buff图标_分析报告.md` — structure analysis of damage numbers and buff icons in the game's assets.
- `docs/GBFR_修改与封包指南.md` — how to modify and repackage results back into the game.
- `docs/GBFR伤害字体Mod演示文案.txt` — subtitle script for screen-recording / video demos.

---

## 🙏 Credits / Asset Licensing

- Native assets and original ideas: **bilibili @Dangoooooo** (QQ: 1041271418).
- `src/resources/texconv.exe` comes from Microsoft's **DirectXTex** (MIT licensed).
- The game's native atlases / `sprites.json` / `hud_param.json` are extracted from *Granblue Fantasy: Relink* game files; copyright belongs to **Cygames**. This repository shares them only as part of a modding tool; these assets are not separately licensed. Please comply with the game's EULA and applicable law.

---

## 📄 License

The tool's source code is released under the **MIT License** — see [LICENSE](LICENSE).

---

# GBFR 伤害字体 Mod Maker（中文）

傻瓜式制作《碧蓝幻想 Relink》（Granblue Fantasy: Relink）伤害数字 / 符号字体 mod 的可视化工具。单文件 exe，双击即用，支持中英文界面。

> 当前版本：**v57**

> **v57 更新日志**：**主表格网格化重构**。六列主表改为单一网格，行列之间均有实线分隔，背景采用主题色。表头与数据行现在共用同一个 grid 容器，窗口缩放时各列始终保持对齐（此前表头与表体分属两个 grid，放大后会错位）。第⑤列（替换图）与第⑥列（原生覆盖/染色）可拉伸。

> **v56 更新日志**：修复 v55 重构覆盖单元格时引入的启动报错（NameError: name 'inner' is not defined）。

> **v55 更新日志**：主表改为带分隔线的网格布局的初次尝试（单元格实线边框；去掉导致缩放错位的固定单元格宽度）。

> **v54 更新日志**：**Bug 修复——染色现在作用于当前预览图，而非旧图**。根因：`_apply_tint` 染色用的是 `st["repl_base"]`，但有两条导入路径只设了预览图 `st["repl"]` 却**没更新 `st["repl_base"]`**：①「按编号批量替换不同组别的相同元素个体」；②「用字体生成png」。所以若你之前生成过字体 PNG（设了 repl）又用批量替换换了同槽位的新图（设了 repl 但没设 repl_base），点染色会把**旧字体 PNG** 染色而非当前预览图。现已让**所有**设置替换图的路径都同步设 `st["repl_base"]` 并调用 `_update_tint_enabled` + `_apply_tint`，染色始终作用于第5列当前显示的图。

> **v53 更新日志**：修复**行距过大**——行高之前按原生图原始像素高度算（如 226×364 的精灵→行高 380px），现在改为按缩略图显示高度算（NATIVE_MAX 限制最大 92px），ROW_MIN 从 150 降到 130。原来占大半屏的一行现在只占 ~130px。

> **v52 更新日志**：① 加宽第6列（COL_W 210→260）让数据行与列头对齐更准确。② 第6列每行新增独立不透明度输入框（0-255），与 RGBA 颜色框中的 A 值双向同步——改任一方另一方自动更新。

> **v51 更新日志**：第6列（原生覆盖/染色）大改 ——

> **v42 更新日志**：补全 `sprites.json` 漏提的 6 个特效精灵（112→118）：之前版本漏掉的左下角长横线、中下 Y 型星闪等，工具不再漏掉左下/中下特效。

> **v40 更新日志**：修复带功能指示器的角色错位问题（exChr10_/11_/24~28_、endlessIcon_、skillBoard_ 等）。将 `hud_param.json` 模板替换为完整 52 区块原生模板（此前仅 35 区块，导致 Reloaded-II 整文件替换时 17 个区块缺失）。更新所有 DEFAULT_SIZE_SCALE 值以匹配当前原生游戏值（`viewTime_` 1.5→0.2、`commonSize_` 1.0→0.42、`criticalSize_` 1.0→0.33、`playerCriticalSize_` 1.0→0.8）。新增 numpy 依赖。

---

## ✨ 功能特性

- **用 TTF 生成彩色 PNG**：选一个 `.ttf` / `.otf` 字体，按组自定义颜色 / 透明度 / 加粗 / 斜体，一键生成彩色数字并自动导入替换。
- **多种替换方式**：单张手动导入、批量从文件夹导入（文件名 = 元素名自动匹配）、按编号 (00–12) 批量替换全组别。
- **数字大小控制**：修改 `hud_param.json` 缩放倍数，范围 0–20，1.0 = 原生大小，0 = 不显示。
- **可折叠分组表格** + 实时原生比例预览。
- **中英双语界面**，右上角一键切换。
- **六列布局**：① 元素名 · ② 坐标 · ③ 原生图(真实比例) · ④ 动作(保留/屏蔽/替换) · ⑤ 替换图(导入＋占比＋铺满) · ⑥ **原生覆盖/染色**——「原生覆盖…」一键把精灵原生图当作替换图；勾选「染色」后先用 RGBA 调色板给原生图染色（保留透明形状）再覆盖。列头「将原生图片全部覆盖到预览图…」按钮可批量覆盖全部精灵。
- **一键导出**：列①②③下方各有「导出…」按钮——列1 导出元素名单 Excel、列2 导出坐标表 Excel、列3 导出原生 PNG 文件夹；工具栏「将全列导出…」一键导出含缩略图的整表 Excel（元素名 / 坐标 / 尺寸 / 原生图 / 动作 / 替换图）。
- 点「生成 Mod」得到 zip（默认输出到 `./mod_output`），用 Reloaded-II 加载即可生效。

---

## 📥 下载

- **成品 exe（推荐普通用户）**：仓库根目录的 [`gbfr_mod_maker_v57.zip`](gbfr_mod_maker_v57.zip)，解压即得 `gbfr_mod_maker_v57.exe`，双击即用，无需 Python 环境。
- 若想「用 TTF 生成 PNG」开箱即用，把任意 `.ttf` 放到 exe 同目录并命名为 `LiXuKeShuFa-1.ttf`（或在软件里点「浏览」自行选择字体）。

> 想让下载按钮更漂亮，也可以去仓库 **Releases** 页面下载（作者通常会把同一个 zip 挂到 Release 上）。

---

## 🚀 快速使用

1. （可选）点「用 TTF 生成 PNG」生成彩色字体 PNG；或手动 / 批量导入替换图。
2. （可选）点「数字大小控制」调缩放倍数。
3. 点「生成 Mod」得到 zip（默认输出到 `./mod_output`）。
4. 用 Reloaded-II + `gbfrelink.utility.manager` 加载生成的 mod，启动游戏即可生效。

> ⚠️ 注意区分两个目录：「Mod 输出目录」(`./mod_output`，最终压缩包) 与「字体 PNG 输出目录」(`./font_output`，TTF 生成的彩色 PNG)，二者不同。

---

## 🧩 前置依赖（运行 mod 用）

- [Reloaded-II](https://github.com/Reloaded-Project/Reloaded-II)
- [gbfrelink.utility.manager](https://github.com/Nenkai23/GBFR-Utils)（Nenkai）

---

## 🛠️ 从源码构建

需要 Python 3.10+，并安装依赖：

```bash
pip install pyinstaller pillow openpyxl numpy
```

进入 `src/` 目录后用打包命令构建：

```bash
cd src
pyinstaller --noconfirm --onefile ^
  --add-data "resources;resources" ^
  --collect-submodules=PIL --collect-submodules=openpyxl ^
  --hidden-import numpy --collect-submodules=numpy ^
  --name gbfr_mod_maker_v57 gbfr_mod_maker.py
```

> Windows 上 `--add-data` 的分隔符是 `;`（如上）。macOS / Linux 请用 `:`。
> 也可以直接 `pyinstaller gbfr_mod_maker_v57.spec`（同样在 `src/` 目录下运行）。

原生资源（图集 / `sprites.json` / `hud_param.json` 模板 / `texconv.exe`）位于 `src/resources/`。

---

## 📚 参考文档

`docs/` 目录下附带了项目过程中的分析笔记，供想深入研究的同学参考：

- `docs/GBFR_伤害数字与Buff图标_分析报告.md` —— 伤害数字与 Buff 图标在游戏资源里的结构分析。
- `docs/GBFR_修改与封包指南.md` —— 如何修改并把成果封包回游戏。
- `docs/GBFR伤害字体Mod演示文案.txt` —— 录屏 / 视频演示用的字幕文案。

---

## 🙏 致谢 / 资源版权

- 原生资源与思路参考：**bilibili @Dangoooooo**（QQ: 1041271418）。
- `src/resources/texconv.exe` 来自微软 **DirectXTex**（MIT 许可）。
- 游戏原生图集 / `sprites.json` / `hud_param.json` 提取自《碧蓝幻想 Relink》游戏文件，版权归 **Cygames** 所有；本仓库仅作 mod 工具用途分享，相关资源不另行授权，请遵守游戏 EULA 与当地法律。

---

## 📄 许可证

本工具源代码以 **MIT 许可证** 发布，详见 [LICENSE](LICENSE)。
