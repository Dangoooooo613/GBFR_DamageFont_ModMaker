# GBFR Damage Font Mod Maker

A no-code, visual tool for making damage-number / symbol font mods for *Granblue Fantasy: Relink*. Single-file EXE, double-click to run, with an English / Chinese UI.

> Current version: **v40** (final)

> **v40 changelog**: Fixed indicator misalignment for characters with functional indicators (exChr10_/11_/24~28_, endlessIcon_, skillBoard_, etc.). Replaced `hud_param.json` template with the full 52-block native template (previously only 35 blocks, causing 17 blocks to go missing during Reloaded-II's whole-file replacement). Updated all DEFAULT_SIZE_SCALE values to match current native game values (`viewTime_` 1.5→0.2, `commonSize_` 1.0→0.42, `criticalSize_` 1.0→0.33, `playerCriticalSize_` 1.0→0.8). Added numpy dependency.

---

## ✨ Features

- **Generate colored PNGs from TTF**: pick a `.ttf` / `.otf` font, customize color / opacity / bold / italic per group, and one-click generate colored digits that are imported and swapped in automatically.
- **Multiple replacement modes**: manual single-image import, batch import from a folder (filename = element name, auto-matched), or batch-replace an entire group by index (00–12).
- **Damage-number size control**: edit the scale factor in `hud_param.json`, range 0–20, where 1.0 = native size and 0 = hidden.
- **Collapsible grouped table** + live native-ratio preview.
- **Bilingual UI** (English / Chinese), switchable with one click at the top-right.
- **One-click export**: each of columns ①②③ has an "Export…" button — column 1 exports the element-name Excel, column 2 the coordinate-table Excel, column 3 the native-PNG folder; the toolbar "Export all columns…" exports a single Excel with thumbnails (element name / coordinates / size / native image / action / replacement image).
- Click "Generate Mod" to get a zip (output to `./mod_output` by default), then load it with Reloaded-II to apply.

---

## 📥 Download

- **Prebuilt EXE (recommended for most users)**: [`gbfr_mod_maker_v40.zip`](gbfr_mod_maker_v40.zip) at the repo root. Unzip to get `gbfr_mod_maker_v40.exe`, double-click to run — no Python needed.
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
  --name gbfr_mod_maker_v40 gbfr_mod_maker.py
```

> On Windows the `--add-data` separator is `;` (as shown). On macOS / Linux use `:`.
> Or simply run `pyinstaller gbfr_mod_maker_v40.spec` (also from inside `src/`).

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

> 当前版本：**v40**（最终版）

> **v40 更新日志**：修复带功能指示器的角色错位问题（exChr10_/11_/24~28_、endlessIcon_、skillBoard_ 等）。将 `hud_param.json` 模板替换为完整 52 区块原生模板（此前仅 35 区块，导致 Reloaded-II 整文件替换时 17 个区块缺失）。更新所有 DEFAULT_SIZE_SCALE 值以匹配当前原生游戏值（`viewTime_` 1.5→0.2、`commonSize_` 1.0→0.42、`criticalSize_` 1.0→0.33、`playerCriticalSize_` 1.0→0.8）。新增 numpy 依赖。

---

## ✨ 功能特性

- **用 TTF 生成彩色 PNG**：选一个 `.ttf` / `.otf` 字体，按组自定义颜色 / 透明度 / 加粗 / 斜体，一键生成彩色数字并自动导入替换。
- **多种替换方式**：单张手动导入、批量从文件夹导入（文件名 = 元素名自动匹配）、按编号 (00–12) 批量替换全组别。
- **数字大小控制**：修改 `hud_param.json` 缩放倍数，范围 0–20，1.0 = 原生大小，0 = 不显示。
- **可折叠分组表格** + 实时原生比例预览。
- **中英双语界面**，右上角一键切换。
- **一键导出**：列①②③下方各有「导出…」按钮——列1 导出元素名单 Excel、列2 导出坐标表 Excel、列3 导出原生 PNG 文件夹；工具栏「将全列导出…」一键导出含缩略图的整表 Excel（元素名 / 坐标 / 尺寸 / 原生图 / 动作 / 替换图）。
- 点「生成 Mod」得到 zip（默认输出到 `./mod_output`），用 Reloaded-II 加载即可生效。

---

## 📥 下载

- **成品 exe（推荐普通用户）**：仓库根目录的 [`gbfr_mod_maker_v40.zip`](gbfr_mod_maker_v40.zip)，解压即得 `gbfr_mod_maker_v40.exe`，双击即用，无需 Python 环境。
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
  --name gbfr_mod_maker_v40 gbfr_mod_maker.py
```

> Windows 上 `--add-data` 的分隔符是 `;`（如上）。macOS / Linux 请用 `:`。
> 也可以直接 `pyinstaller gbfr_mod_maker_v40.spec`（同样在 `src/` 目录下运行）。

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
