# Granblue Fantasy Relink — 伤害数字字体 & Buff 图标 文件定位分析（修正版）

> ⚠️ **重要修正**：初版分析认为伤害数字是纯精灵图集，经实际解密验证后纠正如下。
> 游戏目录：`D:\Program Files (x86)\Steam\steamapps\common\Granblue Fantasy Relink\data\`
> 引擎：白金工作室自研引擎（PlatinumGames）

---

## 一、伤害数字显示字体 — 修正结论

### ✅ 最终结论：伤害数字 0-9 是 **SDF 字体渲染的**，不是纯精灵图集

游戏使用 **SDF（Signed Distance Field，有符号距离场）字体系统** 来绘制战斗伤害数字。数字 0-9 的字形存储在预烘焙的距离场纹理中，运行时引擎按需采样 + 着色/缩放。

### 控制伤害数字"字体"的核心文件（绝对路径）

| 作用 | 文件绝对路径 | 说明 |
|---|---|---|
| **⭐ 数字 0-9 字形纹理（主）** | `D:\...\data\font\tt_skip-b_1.wtb` | Skip 字体 SDF 第 1 页，2048×2048，BC7 压缩。**0-9 就在这里面**（已解密可视化确认） |
| **⭐ 数字 0-9 字形纹理（续页）** | `D:\...\data\font\tt_skip-b_2.wtb` | Skip 字体 SDF 第 2 页 |
| **⭐ 数字 0-9 字形纹理（续页）** | `D:\...\data\font\tt_skip-b_3.wtb` | Skip 字体 SDF 第 3 页 |
| **普通伤害数字材质** | `D:\...\data\ui\fonts\fot_skipstd_b_sdf_num_normal01.mat.matb` | 指向 Skip SDF 的材质变体 → 控制 normal 伤害的颜色/描边/发光 |
| **Link 伤害数字材质** | `D:\...\data\ui\fonts\fot_skipstd_b_sdf_num_link01.mat.matb` | Link 伤害（连锁攻击）的材质变体 |
| **Skip 字体基础材质** | `D:\...\data\ui\fonts\fot_skipstd_b_sdf\fot_skipstd_b_sdf_material.mat.matb` | Skip 字体根材质定义 |
| **字体元数据** | `D:\...\data\font\tt_skip-b.msg` | 字体度量/字距等参数 |
| **Overkill! 特效标签图集** | `D:\...\data\ui\atlas\chs\hud_num_battle.wtb` (+`.tex.texb`) | **仅含 "Overkill!" 文字标签**，不含 0-9 数字 |
| **NumberDrawer 配置** | `D:\...\data\ui\data\image\numberdr.image.imageb` / `.list.listb` | 引用 hud_num_battle 图集（用于 Overkill 标签，非数字本体） |
| **累计伤害 "TOTAL" 文字** | 同上 Skip 字体系统 (`fot_skipstd_b_sdf`) | total01 预制体引用 |

### 各语言版本的数字字体材质（同结构）
以下文件控制对应语言下的伤害数字外观（材质级覆盖）：
- 韩文：`ui/fonts/fotk_yoongothic750_sdf_num_normal01.mat.matb` / `num_link01`
- 繁体中文：`ui/fonts/fzhtb_big5_sdf_num_normal01.mat.matb` / `num_link01`
- 简体中文：`ui/fonts/fzht_gb18030_sdf_num_normal01.mat.matb` / `num_link01`
- 英文/其他：`ui/fonts/pfdintextpro_m_sdf_num_normal01.mat.matb` / `num_link01`

### HUD 排版/动画文件（不改字体但改位置/大小/动画手感时用）
- 顶层视图：`ui/layouts/hud/hud01_damage.view.viewb`
- 8 套预制体：`ui/layouts/hud/num_battle/prefabs/num_battle01_{normal,link,guard01,guard02,heal01,heal02,damage,total}01.prfb`
- 动画：`ui/layouts/hud/num_battle/animations/*_digits.anim.animb`（逐位进出动画）、`*_in/loop/out*`（整体弹出/循环/消失）

---

## 二、"怎么渲染进去"——替换伤害数字字体的实操流程

### 方案 A：替换 SDF 字体纹理（推荐，改字形本身）

**原理**：把你的目标字体渲染成 SDF 距离场纹理，替换进 `tt_skip-b_*.wtb`。

**步骤**：
1. **准备目标字体**（.ttf/.otf），确保包含 0-9 数字
2. **生成 SDF 纹理**：
   - 用 MSDF-Gen 或 BMFont 的 SDF 模式，以与原纹理相同的分辨率（2048×2048）和字符集输出
   - 输出格式：单通道距离场 PNG（或直接 BC7 DDS）
   - 关键：字符映射表必须与原字体一致（Unicode 码点），否则数字会错位
3. **编码回 .wtb**：
   - `.wtb` = 4096 字节头 + DDS 数据（BC7/DX10, 512×256 或更大）
   - 头部前 4096 字节是 Platinum 引擎包装（含 GUID/元数据），DDS 从偏移 4096 开始
   - 用 Python 脚本：读原 `.wtb` 前 4096 字节 → 拼接新 DDS → 写回
4. **替换文件**（备份原文件！）：
   - `font/tt_skip-b_1.wtb`、`_2.wtb`、`_3.wtb` 三页全部替换
5. **通过 Reloaded-II mod 加载**（或直接替换后验证文件完整性）

**注意事项**：
- SDF 纹理的 spread/padding 参数必须与原版一致（否则边缘会截断或模糊）
- 如果只改数字不改其他字符，可以只替换 0-9 对应的纹理区域（需要知道 UV 坐标）
- 材质 `.mat.matb` 控制颜色/描边/发光效果，换字体后可能需要微调

### 方案 B：修改材质引用（换已有字体，不改字形）

如果游戏里已经有你喜欢的字体（比如 Rodin Pro），可以直接让伤害数字用它：

1. 编辑 `ui/fonts/fot_skipstd_b_sdf_num_normal01.mat.matb`，将其指向 `fot_newrodinpro_db` 字体的 SDF 纹理
2. 或复制一份 `fot_newrodinpro_db` 的材质，重命名为 num 变体

**限制**：目标字体必须有对应的 SDF 纹理（`data/font/` 下有 `.wtb`），不是所有 UI 字体都有。

### 方案 C：改 Overkill 标签（精灵图集，最容易）

`hud_num_battle.wtb` 是传统精灵图集，替换最简单：

1. 解码：`.wtb` 偏移 4096 起 = 标准 DDS (BC7/DX10)
2. 用任何图片编辑器编辑解码后的 PNG（保持 512×256 尺寸）
3. 编码回 BC7 DDS → 拼接 4096 字节头 → 写回 `.wtb`

---

## 三、人物 Buff 类图标（大小 / 位置 / 具体信息）

### 图标图像
- 主图集：`D:\...\data\ui\atlas\chs\hud_ex_chracter.wtb` (+`.tex.texb`)
- 独立精灵：`D:\...\data\ui\layouts\hud\ex_chracter\noatlastextures\hud_exchr*.wtb`（每个 buff 的底框/图标/特效各一张）
- 共享特效：`...ex_chracter\textures\common\hud_exchr*.wtb`

### 大小与位置数据
- 布局载体：`ui/layouts/hud/hud01_exchr.view.viewb`（顶层）+ **56 个** `ex_chrNN_NN.prfb`
- **位置/尺寸存在 `.prfb` 二进制里 `loc_*` 节点名后的 float32**：
  - `loc_class_01` → 职业/等级图标位（偏移 ~3392，坐标 572/52/-52）
  - `loc_base01` → 底框（~5092, 404）
  - `loc_text01` → 文字位（~6704, 344/-10）
  - `loc_line01` → 分隔线（~3568, 286/52/-286/-52）
  - `loc_gauge` → 进度条/充能槽

### Buff 名称文字（真字体）
- 字体：`ui/fonts/fot_tsukuoldminpro_r_sdf/`（Tsukushi 明朝体 SDF）
- 材质变体：`_class01..04`（不同等级颜色）、`chracter06_lv1..4`
- 文本键：`TXT_HUD_CLASS`，多语言在 `ui/data/language/ld_tsukuoldminpro_r_sdf_class*`

### Buff 具体信息（持续/倍率/效果/绑定）
- `system/table/status.tbl`（主状态表，23528B，含 atkup/defup/poison/freeze/darkburn/dmglimitup 等）
- `chara_status.tbl`、`skill_status.tbl`、`weapon_status*.tbl`、`enemy_status*.tbl`
- 本地化名称：`system/table/text/<语言>/text_status.msg` 及 `_tag.msg`

---

## 四、已解密可查看的素材文件（workspace 中）

| 文件 | 内容 |
|---|---|
| `skip_sdf_09_digits.png` | Skip SDF 字体第 1 页顶部区域（含 0-9 数字字形，3× 放大） |
| `skip_sdf_page1_enhanced.png` | Skip SDF 第 1 页全页（增强对比度） |
| `skip_sdf_page1_edges.png` | Skip SDF 第 1 页全页（边缘检测可视化） |
| `hud_num_battle_atlas_x3.png` | Overkill 标签图集（3× 放大，深灰背景） |
| `common_number_atlas.png` | 通用数字 UI 元素图集 |

## 五、工具链总结

| 操作 | 工具 |
|---|---|
| 解码 .wtb → PNG | Python + imagecodecs（bcn_decode/imread），支持 BC7/DX10 |
| 编码 PNG → .wtb | 反向：PNG→BC7 DDS→拼 4096B 头→写 .wtb |
| 查看/编辑 SDF | 任意图片编辑器（PS/GIMP/Krita）；生成 SDF 用 msdf-atlas-gen |
| 编辑布局 (.prfb/.viewb) | 需白金引擎布局编辑器（社区工具）或定点 hex |
| 加载 mod | Reloaded-II + gbfrelink.utility.manager |
