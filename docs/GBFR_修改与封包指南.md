# GBFR 伤害数字字体 & Buff 图标 —— 修改与封包指南

> 适用对象：已解包 `Granblue Fantasy Relink\data` 的玩家/Mod 作者
> 本文讲两件事：**改什么**、**用什么工具改 + 怎么重新封包加载**

---

## 0. 先搞清楚格式

GBFR 的纹理不是普通 PNG，而是 `.wtb`：

```
[ 4096 字节  引擎头 ][ DDS 数据 (BC7 / DX10, 通常 2048×2048) ]
```

- **解码（BC7 → 可编辑图）**：纯 Python 用 `imagecodecs` 即可 ✅
- **编码（图 → BC7 DDS）**：`imagecodecs` **做不了 BC7 编码**，必须靠外部工具 `texconv.exe` ❌→✅
- **封包**：把「原 4096 字节头」+「新 DDS」直接拼接写回 `.wtb` 就行

本文配套脚本 `wtb_tool.py` 自动处理 提取 / 解码 / 编码 / 封包 四步。

---

## 1. 工具清单

| 用途 | 工具 | 获取 | 说明 |
|------|------|------|------|
| 提取 / 封包 / 解码 | Python + `imagecodecs`,`Pillow`,`numpy` | 已配好（本工作区 venv） | 跑 `wtb_tool.py` |
| **BC7 编码（必须）** | **texconv.exe** (DirectXTex) | https://github.com/microsoft/DirectXTex/releases （找 `texconv.exe` 下载） | 唯一可靠的 BC7 编码器，把 PNG 压成 BC7 DDS |
| 像素编辑 | Photoshop / GIMP | 任意 | 或直接用 Pillow 脚本批量贴字 |
| 真·SDF 字体生成 | msdf-atlas-gen (Chlumsky) | https://github.com/Chlumsky/msdf-atlas-gen | 想做可无损缩放的 SDF 时才需要；普通改字形用 PS 贴图即可 |
| 加载进游戏 | Reloaded-II + gbfrelink.utility.manager | https://github.com/Nenkai/GBFR-Modding / Reloaded-II | 做文件重定向，**不用手改 data.i** |

> ⚠️ 关于 `imagecodecs`：它只能**解** BC7，不能**压** BC7。所以「封包」这步绕不开 `texconv.exe`。把 `texconv.exe` 所在目录加进系统 PATH，或调用时传 `--texconv "完整路径"`。

---

## 2. 修改伤害数字字体（0-9，在 `tt_skip-b_5.wtb`）

### 2.1 文件定位
- 字体纹理第 5 页：`data/font/tt_skip-b_5.wtb`（page index 4）
- 字形坐标元数据：`data/font/tt_skip-b.msg`（MessagePack，已解析出 0-9 精确矩形）

### 2.2 数字 0-9 在图集里的精确位置（来自 `.msg`，画布 2048×2048）

| 数字 | ID | X | Y | 宽×高 | 偏移 |
|------|----|----|----|-------|------|
| 0 | 48 | 511 | 786 | 39×47 | (-5,-2) |
| 1 | 49 | 1362 | 879 | 28×46 | (-3,-1) |
| 2 | 50 | 1390 | 879 | 36×46 | (-4,-2) |
| 3 | 51 | 1426 | 879 | 37×46 | (-5,-2) |
| 4 | 52 | 1463 | 879 | 39×46 | (-5,-2) |
| 5 | 53 | 550 | 786 | 36×47 | (-4,-2) |
| 6 | 54 | 397 | 691 | 38×48 | (-4,-3) |
| 7 | 55 | 1502 | 879 | 37×46 | (-4,-2) |
| 8 | 56 | 586 | 786 | 39×47 | (-5,-2) |
| 9 | 57 | 625 | 786 | 38×47 | (-5,-2) |

> 替换时：**把新字形画进 (X, Y, 宽, 高) 这个矩形里**即可。只要新字形也用同样的矩形尺寸，`.msg` 坐标不用改，游戏照常定位。

### 2.3 操作步骤

```bash
# 1) 抽出 DDS（跳过前 4096 字节引擎头）
python wtb_tool.py extract "data/font/tt_skip-b_5.wtb" page5.dds

# 2) 解码成可编辑 PNG
python wtb_tool.py decode page5.dds page5.png

# 3) 用 PS/GIMP 打开 page5.png，把 0-9 画进上表对应矩形
#    （或写 Pillow 脚本按坐标批量贴你自己的字体）—— 保存为 page5_new.png
#    注意：保持每个数字矩形尺寸不变，否则要同步改 .msg

# 4) 编码回 BC7 DDS（需要 texconv.exe）
python wtb_tool.py encode page5_new.png page5_new.dds

# 5) 封包：原 4096 头 + 新 DDS → 新 .wtb
python wtb_tool.py repack "data/font/tt_skip-b_5.wtb" page5_new.dds tt_skip-b_5_new.wtb
```

### 2.4 关于「真 SDF」
游戏用的是**有向距离场（SDF）**字体，原本能任意缩放不失真。如果你只是用 PS 把普通抗锯齿字形贴进去（非 SDF），在固定显示尺寸下**看着没问题**，但极端缩放会糊。
- 想做到和原版一样可无损缩放：用 `msdf-atlas-gen` 生成新字体的 SDF 图集，再裁出 0-9 贴回对应矩形。
- 只想换个性字体看个爽：PS 直接贴高分辨率抗锯齿字即可，最省事。

---

## 3. 修改 Buff 图标（大小 / 位置 / 图形）

### 3.1 文件定位
- 图标图集：`data/ui/atlas/chs/hud_ex_chracter.wtb`（及 `noatlastextures/hud_exchr*.wtb`）
- 布局/位置/大小：56 个 `data/ui/layouts/hud/ex_chracter/ex_chrNN_NN.prfb`（二进制 prefab）
- Buff 定义（哪种状态对应哪个图标）：`data/system/table/status.tbl`
- 图标下方文字字体：`data/ui/fonts/fot_tsukuoldminpro_r_sdf/`

### 3.2 改「图标图形」
和字体同理——抽出图集 DDS、解码、改像素、编码、封回：

```bash
python wtb_tool.py extract "data/ui/atlas/chs/hud_ex_chracter.wtb" exchr.dds
python wtb_tool.py decode  exchr.dds exchr.png
# 用 PS 改图标像素 -> exchr_new.png
python wtb_tool.py encode  exchr_new.png exchr_new.dds
python wtb_tool.py repack  "data/ui/atlas/chs/hud_ex_chracter.wtb" exchr_new.dds hud_ex_chracter_new.wtb
```

### 3.3 改「大小和位置」
位置/尺寸数据写在 `.prfb` 里（二进制），紧跟在 `loc_*` 节点之后，是 4 字节 float：
- 例：`loc_class_01` 节点在偏移 3392，其后的 3408 处三个 float = `572 / 52 / -52`（X / Y / Z 屏幕坐标）。
- 改大小同理找对应的 scale 字段。`.prfb` 没有现成通用编辑器，需要：
  1. 用十六进制编辑器（010 Editor + 现成 `.bt` 模板，或 HxD）定位 float；
  2. 或写脚本按偏移读写 float32（注意字节序 = little-endian）。
- 改完直接覆盖原 `.prfb` 即可，**不需要**重新封包成别的格式（`.prfb` 本身就是要被引擎直接读的）。

> 注意：`status.tbl` 决定「中毒/攻击提升/冻结…」等状态映射到哪个图标 ID；想改图标含义（而不是图形）才动它。

---

## 4. 封包后怎么让游戏读到（加载方式）

推荐 **Reloaded-II + gbfrelink.utility.manager（Nenkai）**：

1. 装 Reloaded-II，装 GBFR 的 utility manager 模组；
2. 用它做**文件重定向**：把游戏对 `tt_skip-b_5.wtb` / `hud_ex_chracter.wtb` 的读取指向你修改后的文件；
3. 启动游戏即可，**完全不用手改 `data.i` 的字节数**（旧教程那步只是讲原理）。

如果 utility manager 不直接支持 `.wtb` 纹理重定向，退路是：
- 备份原文件 → 把 `xxx_new.wtb` 改名覆盖原 `xxx.wtb`（放在解包后的 `data` 对应目录）。
- 出错就用 Steam「验证游戏文件完整性」还原。

---

## 5. 踩坑提醒

1. **务必先备份** `data.i`、原 `.wtb`、原 `.prfb`，出错一键还原。
2. **BC7 编码只能用 texconv**（或 AMD Compressonator），别指望 Python 自己压。
3. 改字体时**保持数字矩形尺寸不变**，否则得同步改 `tt_skip-b.msg` 里的坐标，容易翻车。
4. 封包时**必须用「原 .wtb 的前 4096 字节头」**，不要自己造头——引擎头里可能带校验/版本信息。
5. SDF 字体若用普通字贴图，缩放会糊；追求完美用 msdf-atlas-gen。

---

## 附：wtb_tool.py 命令速查

| 命令 | 作用 |
|------|------|
| `extract <wtb> <dds>` | 抽 DDS（去头） |
| `decode <dds> <png>` | BC7 DDS → PNG |
| `encode <png> <dds> [--texconv 路径]` | PNG → BC7 DDS |
| `repack <原wtb> <dds> <输出wtb>` | 头+新DDS 拼回 |
| `roundtrip` | 自测字节一致性 |
