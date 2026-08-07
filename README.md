# GBFR 伤害字体 Mod Maker

傻瓜式制作《碧蓝幻想 Relink》（Granblue Fantasy: Relink）伤害数字 / 符号字体 mod 的可视化工具。单文件 exe，双击即用，支持中英文界面。

> 当前版本：**v37**（最终版）

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

- **成品 exe（推荐普通用户）**：仓库根目录的 [`gbfr_mod_maker_v37.zip`](gbfr_mod_maker_v37.zip)，解压即得 `gbfr_mod_maker_v37.exe`，双击即用，无需 Python 环境。
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
pip install pyinstaller pillow openpyxl
```

进入 `src/` 目录后用打包命令构建：

```bash
cd src
pyinstaller --noconfirm --onefile ^
  --add-data "resources;resources" ^
  --collect-submodules=PIL --collect-submodules=openpyxl ^
  --name gbfr_mod_maker_v37 gbfr_mod_maker.py
```

> Windows 上 `--add-data` 的分隔符是 `;`（如上）。macOS / Linux 请用 `:`。
> 也可以直接 `pyinstaller gbfr_mod_maker_v37.spec`（同样在 `src/` 目录下运行）。

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
