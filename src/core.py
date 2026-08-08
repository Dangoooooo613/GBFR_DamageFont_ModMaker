#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
GBFR 伤害字体 mod 构建内核 (无 tkinter 依赖, 可 headless 测试)

职责:
  - 加载原生图集(PNG) + 引擎头(bin) + 精灵清单(json)
  - 按每精灵动作 keep / block / replace + 占比 合成 HD 与 FHD 图集
  - texconv 编码 BC7 DDS, 拼回 wtb, 打包 Reloaded-II zip

运行期依赖: numpy, PIL, texconv.exe (resources 内)
"""
import os, sys, json, math, struct, subprocess, shutil, zipfile, io, datetime

import numpy as np
from PIL import Image

HDR_SIZE = 4096


# ── i18n: GUI registers its translator via set_translator(tr) ──
_CORE_I18N_ZH = {
    "core_build_start": "开始构建 mod: 主图集 + 高分辨率图集",
    "core_no_tpl": "  ⚠ 未找到 resources/hud_param.json 模板, 跳过大小控制写入",
    "core_hud_fail": "  ⚠ hud_param.json 写入失败: %s",
    "core_set_replace_no_img": "  ⚠ %s 设为替换但无图片, 按保留处理",
    "core_repl": "  [%s] 替换=%d 屏蔽=%d 保留=%d -> %s",
    "core_pack_done": "  ✅ 打包完成: %s (%s bytes)",
    "core_ttf_gen": "  ✅ TTF 生成 %d 张 PNG -> %s",
    "core_no_texconv": "未找到 texconv.exe (resources 内)",
}
_TR = None
def set_translator(tr_func):
    global _TR
    _TR = tr_func
def _t(key, *args):
    if _TR is not None:
        return _TR(key, *args)
    s = _CORE_I18N_ZH.get(key, key)
    if args:
        try:
            return s % args
        except Exception:
            return s
    return s

def get_resource_dir():
    """资源目录: 打包后为 sys._MEIPASS/resources, 开发期为本文件同级的 resources。"""
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, "resources")
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")


def load_native(res_dir=None):
    """加载原生资源, 返回 dict。

    返回:
      hd_arr, fhd_arr : numpy uint8 RGBA 图集
      hd_hdr, fhd_hdr : bytes 引擎头
      sprites         : list[dict]
      AW, AH, FW, FH   : 主/高分辨率图集尺寸
    """
    res = res_dir or get_resource_dir()
    hd_arr = np.array(Image.open(os.path.join(res, "native_hd_atlas.png")).convert("RGBA"))
    fhd_arr = np.array(Image.open(os.path.join(res, "native_fhd_atlas.png")).convert("RGBA"))
    hd_hdr = open(os.path.join(res, "native_hd_hdr.bin"), "rb").read()
    fhd_hdr = open(os.path.join(res, "native_fhd_hdr.bin"), "rb").read()
    sprites = json.load(open(os.path.join(res, "sprites.json"), encoding="utf-8"))
    AH, AW = hd_arr.shape[:2]
    FH, FW = fhd_arr.shape[:2]
    return {
        "hd_arr": hd_arr, "fhd_arr": fhd_arr,
        "hd_hdr": hd_hdr, "fhd_hdr": fhd_hdr,
        "sprites": sprites, "AW": AW, "AH": AH, "FW": FW, "FH": FH,
    }


def _recenter_content(src_img, alpha_thresh=8):
    """把 src_img(RGBA) 的**不透明内容**重新居中到画布正中(画布尺寸不变)。

    某些来源替换图(旧版 TTF 生成 / 自定义图)内容本身偏离画布中心,
    直接合成会导致预览与游戏内显示偏移。此函数把内容质心对齐到画布中心,
    已居中的图几乎不受影响。仅处理内容, 不改变内容内部形状。"""
    a = np.array(src_img)
    alpha = a[..., 3]
    ys, xs = np.where(alpha > alpha_thresh)
    if len(xs) == 0:
        return src_img
    cw = int(xs.max() - xs.min()) + 1
    ch = int(ys.max() - ys.min()) + 1
    # 内容裁剪块
    content = src_img.crop((int(xs.min()), int(ys.min()),
                            int(xs.max()) + 1, int(ys.max()) + 1))
    new = Image.new("RGBA", src_img.size, (0, 0, 0, 0))
    nx = (src_img.width - cw) // 2
    ny = (src_img.height - ch) // 2
    new.paste(content, (nx, ny))
    return new


def composite_box(arr, x, y, w, h, src_img, ratio, clear_first=False, stretch=False):
    """把 src_img(RGBA) 放到 arr 的 (x,y,w,h) 盒内。
    stretch=True 时无视 ratio, 直接变形拉伸铺满整个盒(等比缩放+裁剪);
    stretch=False 时以 contain 适配并居中, 占比 ratio 控制面积百分比 (面积比, 线性 sqrt)。
    比例无上限: ratio=100 贴合盒一边; ratio>100 放大溢出; ratio<100 缩小。
    clear_first=True 先清目标区域为全透明(replace 模式)。"""
    if src_img is None:
        return False
    # 内容重居中: 无论源图内容多偏, 都先对齐到画布中心
    src_img = _recenter_content(src_img)
    sw, sh = src_img.size
    if sw <= 0 or sh <= 0:
        return False
    H, W = arr.shape[:2]
    x = max(0, min(W - 1, int(x)))
    y = max(0, min(H - 1, int(y)))
    w = max(1, min(int(w), W - x))
    h = max(1, min(int(h), H - y))
    if w <= 0 or h <= 0:
        return False

    if stretch:
        # 铺满模式: 直接拉伸到盒尺寸
        nw, nh = w, h
        rz = src_img.resize((nw, nh), Image.LANCZOS)
    else:
        bw, bh = w, h
        s0 = min(bw / sw, bh / sh)               # contain 适配比例
        scale = s0 * math.sqrt(max(0.0, float(ratio)) / 100.0)   # ratio 无上限
        nw = max(1, int(round(sw * scale)))
        nh = max(1, int(round(sh * scale)))
        rz = src_img.resize((nw, nh), Image.LANCZOS)

    region = arr[y:y + h, x:x + w].astype(np.float64)   # (h,w,4)
    # replace 模式: 先把整个盒清为零(全透明)
    if clear_first:
        region[:] = 0.0
    sarr = np.array(rz, dtype=np.float64)               # (nh,nw,4)
    pa = sarr[..., 3:4] / 255.0
    # 源图在盒内居中放置的偏移(可能为负 => 溢出盒子)
    ox = (w - nw) // 2
    oy = (h - nh) // 2
    # 可见区域(源图与盒相交部分)
    i0 = max(0, -ox); i1 = min(nw, w - ox)
    j0 = max(0, -oy); j1 = min(nh, h - oy)
    vw = i1 - i0; vh = j1 - j0
    if vw <= 0 or vh <= 0:
        arr[y:y + h, x:x + w] = region.astype(np.uint8)
        return True
    src_crop = sarr[j0:j1, i0:i1]            # (vh,vw,4)
    pa_crop = pa[j0:j1, i0:i1]
    dx0 = max(0, ox); dy0 = max(0, oy)
    sub = region[dy0:dy0 + vh, dx0:dx0 + vw]
    out_rgb = src_crop[..., :3] * pa_crop + sub[..., :3] * (1 - pa_crop)
    out_a = src_crop[..., 3:4] * pa_crop + sub[..., 3:4] * (1 - pa_crop)
    region[dy0:dy0 + vh, dx0:dx0 + vw, :3] = np.clip(out_rgb, 0, 255)
    region[dy0:dy0 + vh, dx0:dx0 + vw, 3:4] = np.clip(out_a, 0, 255)
    arr[y:y + h, x:x + w] = region.astype(np.uint8)
    return True


def composite_preview(sprite, src_img, ratio, fhd=False, native=None, stretch=False):
    """生成替换预览: 返回替换后的最终效果(RGBA PIL Image)。

    预览模拟游戏内实际效果(replace = clear_first 模式):
      - 不传 native 或 native=None: 纯透明底 + 替换图(游戏内实际看到的效果)
      - 传 native: 原生图作底 + 替换图叠加(对比参考用途)
    stretch=True 时无视 ratio 直接拉伸铺满整个 UV 盒。
    """
    if fhd:
        x, y, w, h = sprite["_fhd"]
    else:
        x, y, w, h = sprite["x"], sprite["y"], sprite["w"], sprite["h"]
    # 用 numpy 数组作为画布
    canvas = np.zeros((h, w, 4), dtype=np.float64)
    if native is not None:
        ny = max(0, min(native.shape[0] - 1, y))
        nx = max(0, min(native.shape[1] - 1, x))
        nw = min(w, native.shape[1] - nx)
        nh = min(h, native.shape[0] - ny)
        if nw > 0 and nh > 0:
            canvas[:nh, :nw] = native[ny:ny + nh, nx:nx + nw].astype(np.float64)
    if src_img is not None:
        composite_box(canvas, 0, 0, w, h, src_img, ratio, clear_first=True, stretch=stretch)
    return Image.fromarray(np.clip(canvas, 0, 255).astype(np.uint8))


def _encode_bc7(png_path, texconv, tmp_dir, log):
    base = os.path.splitext(os.path.basename(png_path))[0]
    gen = os.path.join(tmp_dir, base + ".DDS")
    if os.path.exists(gen):
        try:
            os.remove(gen)
        except OSError:
            pass
    cmd = [texconv, "-f", "BC7_UNORM", "-m", "1", "-y", "-nologo", "-o", tmp_dir, png_path]
    if log:
        log("[texconv] " + " ".join(cmd))
    r = subprocess.run(cmd, capture_output=True)
    out = (r.stdout or b"").decode("utf-8", "replace")
    err = (r.stderr or b"").decode("utf-8", "replace")
    if r.returncode != 0:
        raise RuntimeError("texconv 失败:\n" + err)
    if not os.path.exists(gen):
        raise RuntimeError("texconv 未生成 " + gen)
    return gen


def _build_resolution(arr, sprites, actions, replacements, ratios,
                      hdr, out_dir, texconv, tmp_dir, label, fhd, dims, log,
                      stretches=None):
    stretches = stretches or {}
    AW, AH = dims["AW"], dims["AH"]
    FW, FH = dims["FW"], dims["FH"]
    work = arr.copy()
    n_rep = n_block = n_keep = 0
    for sp in sprites:
        name = sp["name"]
        act = actions.get(name, "keep")
        if act == "keep":
            n_keep += 1
            continue
        if fhd:
            xf = max(0, min(FW - 1, int(round(sp["x"] * FW / AW))))
            yf = max(0, min(FH - 1, int(round(sp["y"] * FH / AH))))
            wf = min(FW - xf, int(round(sp["w"] * FW / AW)))
            hf = min(FH - yf, int(round(sp["h"] * FH / AH)))
            box = (xf, yf, wf, hf)
            sp["_fhd"] = box
        else:
            box = (sp["x"], sp["y"], sp["w"], sp["h"])
        x, y, w, h = box
        if act == "block":
            H, W = work.shape[:2]
            x = max(0, min(W - 1, x)); y = max(0, min(H - 1, y))
            w = max(1, min(w, W - x)); h = max(1, min(h, H - y))
            work[y:y + h, x:x + w] = 0
            n_block += 1
        else:  # replace
            src = replacements.get(name)
            if src is None:
                if log:
                    log(_t("core_set_replace_no_img", name))
                n_keep += 1
                continue
            ok = composite_box(work, x, y, w, h, src, ratios.get(name, 100.0),
                                 clear_first=True, stretch=stretches.get(name, False))
            if not ok:
                n_keep += 1
            else:
                n_rep += 1
    png_out = os.path.join(tmp_dir, f"{label}_atlas.png")
    Image.fromarray(work).save(png_out)
    dds = _encode_bc7(png_out, texconv, tmp_dir, log)
    # 中间 wtb 写到临时目录(不污染输出目录), 拷贝进 mod 目录后再清理
    wtb = os.path.join(tmp_dir, f"hud_num_battle_{label}.wtb")
    with open(wtb, "wb") as f:
        f.write(hdr)
        f.write(open(dds, "rb").read())
    if log:
        log(_t("core_repl", label, n_rep, n_block, n_keep, os.path.basename(wtb)))
    return wtb


# 伤害数字控制 (hud_param.json 的 damage_ 段)
# 经实机验证的语义:
#   spArtsLinkAttackSize_ : 伤害数字大小(缩放倍数)。必须 >0 的浮点; 1.0 = 原生外观。
#   height_               : 垂直位置(高度)。0 = 字幕区域水平轴线过屏幕中心; 任意浮点。
#   length_               : 水平位置(长度)。0 = 字幕区域垂直轴线过屏幕中心; 任意浮点。
#   space_                : 一串数字自身的拥挤度(间距)。负=更紧, 正=更松; 任意浮点。
# 注: 只有 spArtsLinkAttackSize_ 实际改变数字大小; height_/length_/space_ 控制位置与间距。
# 默认值为原生模板基准(1.0 / 1 / 80 / -12), "全部重置"即恢复这些原生值。
SIZE_KEYS = ["spArtsLinkAttackSize_", "height_", "length_", "viewTime_",
            "space_", "healSpace_", "commonSize_", "criticalSize_",
            "playerSize_", "playerCriticalSize_"]
DEFAULT_SIZE_SCALE = {
    "spArtsLinkAttackSize_": 1.0,
    "height_": 1.0,
    "length_": 80.0,
    "viewTime_": 0.2,
    "space_": -12.0,
    "healSpace_": -32.0,
    "commonSize_": 0.42,
    "criticalSize_": 0.33,
    "playerSize_": 1.0,
    "playerCriticalSize_": 0.8,
}

# 队友伤害颜色 (damage_ 段 normalAttackColor_ / spAttackColor_) 原生基准
#   游戏内为 0-1 浮点 RGBA; 工具内用 0-255 显示/编辑, 写入时 /255
COLOR_KEYS = ["normalAttackColor_", "spAttackColor_"]
DEFAULT_COLOR = {  # 0-255 RGBA
    "normalAttackColor_": (210, 235, 240, 128),
    "spAttackColor_": (240, 235, 180, 128),
}
DEFAULT_COLOR_JSON = {  # 0-1 浮点 (与官方原生 hud_param.json 一致)
    "normalAttackColor_": [c / 255.0 for c in (210, 235, 240, 128)],
    "spAttackColor_": [c / 255.0 for c in (240, 235, 180, 128)],
}



# 浮动范围 (damage_ 段) 原生基准; 4 元素数组, 值越大多个数字分布越散
RANGE_KEYS = ["rangeNear_", "rangeFar_"]
DEFAULT_RANGE = {
    "rangeNear_": [100, 300, 350, 0],
    "rangeFar_":  [100, 200, 250, 0],
}

def build_mod(actions, replacements, ratios, out_dir,
              mod_id="gbfr.damagefont.editor",
              mod_name="GBFR Damage Font Editor Mod",
              log=None, progress=None, stretches=None,
              sizes=None, colors=None, range_alpha=1.0, mod_author="bilibili/Dangoooooo", mod_description=None):
    """构建 mod。

    actions:     {name: 'keep'|'block'|'replace'}
    replacements:{name: PIL.Image(RGBA)}   替换需要
    ratios:      {name: float 0-100}
    stretches:   {name: bool}  铺满模式(无视ratio直接拉伸铺满UV盒)
    sizes:       {name: float} 伤害数字参数(见 SIZE_KEYS)
    colors:      {name: (r,g,b,a) 0-255} 队友伤害颜色(见 COLOR_KEYS); 写入时 /255
    range_alpha:  float 浮动系数(默认1.0=原生); 乘以 rangeNear_/rangeFar_ 各原生值, 越大越散
    mod_author:  ModConfig.ModAuthor
    mod_description: ModConfig.ModDescription(缺省自动生成英文+时间戳)
    out_dir:     输出目录(会在其中写 <mod_id>.zip)
    返回 zip 路径。
    """
    stretches = stretches or {}
    sizes = sizes or dict(DEFAULT_SIZE_SCALE)
    # range_alpha: 1.0=native, multiply each DEFAULT_RANGE element
    res = get_resource_dir()
    texconv = os.path.join(res, "texconv.exe")
    if not os.path.exists(texconv):
        raise RuntimeError(_t("core_no_texconv"))
    native = load_native(res)
    sprites = native["sprites"]
    os.makedirs(out_dir, exist_ok=True)
    tmp = os.path.join(out_dir, "_build_tmp")
    os.makedirs(tmp, exist_ok=True)

    if log:
        log(_t("core_build_start"))

    wtb_hd = _build_resolution(
        native["hd_arr"], sprites, actions, replacements, ratios,
        native["hd_hdr"], out_dir, texconv, tmp, "hd", False,
        {"AW": native["AW"], "AH": native["AH"], "FW": native["FW"], "FH": native["FH"]},
        log, stretches=stretches)
    wtb_fhd = _build_resolution(
        native["fhd_arr"], sprites, actions, replacements, ratios,
        native["fhd_hdr"], out_dir, texconv, tmp, "fhd", True,
        {"AW": native["AW"], "AH": native["AH"], "FW": native["FW"], "FH": native["FH"]},
        log, stretches=stretches)

    # 组装 mod 目录
    mdir = os.path.join(out_dir, mod_id)
    md = os.path.join(mdir, "GBFR", "data", "ui", "atlas")
    mf = os.path.join(mdir, "GBFR", "data", "ui", "fhd", "atlas")
    os.makedirs(md, exist_ok=True)
    os.makedirs(mf, exist_ok=True)
    shutil.copy2(wtb_hd, os.path.join(md, "hud_num_battle.wtb"))
    shutil.copy2(wtb_fhd, os.path.join(mf, "hud_num_battle.wtb"))

    # 写入 hud_param.json (伤害数字控制): 基于原生模板, 仅替换受控字段
    #   spArtsLinkAttackSize_=大小(>0); height_=垂直位置; length_=水平位置; space_=间距
    mt = os.path.join(mdir, "GBFR", "data", "ui", "table")
    os.makedirs(mt, exist_ok=True)
    try:
        tpl = os.path.join(res, "hud_param.json")
        if os.path.exists(tpl):
            hud = json.load(open(tpl, encoding="utf-8"))
            dmg = hud.get("HudParam", {}).get("damage_", {})
            for k in SIZE_KEYS:
                if k in dmg:
                    dmg[k] = float(sizes.get(k, DEFAULT_SIZE_SCALE.get(k, 1.0)))
            if colors:
                for k in COLOR_KEYS:
                    if k in dmg:
                        c = colors.get(k, DEFAULT_COLOR[k])
                        dmg[k] = [c[i] / 255.0 for i in range(4)]
            if range_alpha != 1.0:
                for k in RANGE_KEYS:
                    if k in dmg:
                        dmg[k] = [round(float(v) * range_alpha, 2) for v in DEFAULT_RANGE[k]]
            json.dump(hud, open(os.path.join(mt, "hud_param.json"), "w", encoding="utf-8"),
                      ensure_ascii=False, indent=2)
            if log:
                parts = ", ".join("%s=%.2f" % (k, dmg.get(k, 1.0)) for k in SIZE_KEYS)
                if colors:
                    cstr = []
                    for k in COLOR_KEYS:
                        c = colors.get(k, DEFAULT_COLOR[k])
                        cstr.append("%s=(%.3f,%.3f,%.3f,%.3f)" % (
                            k, c[0] / 255.0, c[1] / 255.0, c[2] / 255.0, c[3] / 255.0))
                    parts += " | " + ", ".join(cstr)
                if range_alpha != 1.0:
                    rstr = []
                    for k in RANGE_KEYS:
                        scaled = [round(v * range_alpha, 2) for v in DEFAULT_RANGE[k]]
                        rstr.append("%s=[%s](alpha=%.2f)" % (k, ", ".join("%.2f" % x for x in scaled), range_alpha))
                    parts += " | " + ", ".join(rstr)
                log("  hud_param.json -> " + parts)

        else:
            if log:
                log(_t("core_no_tpl"))
    except Exception as e:
        if log:
            log(_t("core_hud_fail", e))

    # ModName 追加日期, ModDescription 默认英文+时间戳
    date_str = datetime.datetime.now().strftime("%Y-%m-%d")
    mod_name_full = (mod_name + " " + date_str).strip()
    if mod_description is None:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        mod_description = ("Damage number/symbol font mod generated by the GBFR Damage Font Editor. "
                           "Generated at " + ts)
    mcfg = {
        "ModId": mod_id,
        "ModName": mod_name_full,
        "ModAuthor": mod_author,
        "ModVersion": "1.0.0",
        "ModDescription": mod_description,
        "ModDll": "",
        "ModIcon": "",
        "ModR2RManagedDll32": "",
        "ModR2RManagedDll64": "",
        "ModNativeDll32": "",
        "ModNativeDll64": "",
        "Tags": [],
        "CanUnload": None,
        "HasExports": None,
        "IsLibrary": False,
        "ReleaseMetadataFileName": mod_id + ".ReleaseMetadata.json",
        "PluginData": {},
        "IsUniversalMod": False,
        "ModDependencies": ["gbfrelink.utility.manager", "reloaded.sharedlib.hooks"],
        "OptionalDependencies": [],
        "SupportedAppId": ["granblue_fantasy_relink.exe"],
        "ProjectUrl": "",
    }
    with open(os.path.join(mdir, "ModConfig.json"), "w", encoding="utf-8") as f:
        json.dump(mcfg, f, ensure_ascii=False, indent=2)
    readme = (
        f"# {mod_name}\n\n"
        "本 mod 由 GBFR 伤害字体编辑器生成。\n\n"
        "## 安装\n"
        "1. 安装 Reloaded-II + Granblue Fantasy Relink Mod Manager (Nenkai)。\n"
        "2. 将本 ZIP 拖入 Reloaded-II 窗口, 或解压到 Reloaded-II/Mods/。\n"
        "3. 勾选本 Mod 与 GBFRelinkUtility, 通过 Reloaded-II 启动游戏。\n\n"
        "## 文件\n"
        "GBFR/data/ui/atlas/hud_num_battle.wtb (主)\n"
        "GBFR/data/ui/fhd/atlas/hud_num_battle.wtb (高分辨率)\n"
        "GBFR/data/ui/table/hud_param.json (伤害数字大小缩放倍数, 范围 0–20)\n"
    )
    with open(os.path.join(mdir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme)

    zp = os.path.join(out_dir, mod_id + ".zip")
    if os.path.exists(zp):
        try:
            os.remove(zp)
        except OSError:
            pass
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as zf:
        for rt, ds, fs in os.walk(mdir):
            for fn in fs:
                fp = os.path.join(rt, fn)
                zf.write(fp, os.path.relpath(fp, out_dir))
    # 清理中间产物: 仅保留 zip, 移除解压目录与构建临时目录
    shutil.rmtree(mdir, ignore_errors=True)
    shutil.rmtree(tmp, ignore_errors=True)
    if log:
        log(_t("core_pack_done", zp, "{:,}".format(os.path.getsize(zp))))
    return zp


# ──────────────────────────────────────────────
#  TTF → PNG 批量生成 (给每个可替换精灵上对应主色)
# ──────────────────────────────────────────────
def render_glyph_ttf(ttf_path, sprite, box_w, box_h, fill_scale=0.9,
                     fill=None, bold=False, italic=False):
    """用 ttf 渲染 sprite['char'] 为 RGBA 图, 画在 box_w x box_h 透明画布上。

    fill        : (r,g,b) 文字填充色; 省略则用 sprite['dominant']。
    bold        : 伪加粗(stroke_width 描同色)。
    italic      : 斜体(仿射剪切 x += skew*y)。
    返回 PIL RGBA 或 None。
    """
    from PIL import ImageFont, ImageDraw
    ch = sprite.get("char")
    if not ch:
        return None
    if fill is None:
        fill = tuple(int(c) for c in sprite["dominant"])
    fill = tuple(int(c) for c in fill)
    scale = 3  # 高分辨率渲染后缩小, 文字更平滑
    canvas = Image.new("RGBA", (box_w * scale, box_h * scale), (0, 0, 0, 0))
    draw = ImageDraw.Draw(canvas)
    # 斜体需要给剪切留出水平空间, 收缩一点目标字高
    ital_shrink = 0.14 if italic else 0.0
    target = int(box_h * scale * (fill_scale - ital_shrink))
    font = None
    for fs in range(max(8, target), 8, -2):
        try:
            font = ImageFont.truetype(ttf_path, fs)
        except Exception:
            continue
        try:
            bb = draw.textbbox((0, 0), ch, font=font)
        except Exception:
            bb = None
        if bb is not None:
            th = bb[3] - bb[1]
            if th <= target:
                break
    if font is None:
        font = ImageFont.truetype(ttf_path, max(8, target))
    bb = draw.textbbox((0, 0), ch, font=font)
    tw = bb[2] - bb[0]
    th = bb[3] - bb[1]
    cx = (canvas.width - tw) / 2 - bb[0]
    cy = (canvas.height - th) / 2 - bb[1]
    # 主体(可选伪加粗): 填充色描边同色 => 字更粗
    bw = max(1, int(box_h * scale * 0.02)) if bold else 0
    draw.text((cx, cy), ch, font=font, fill=fill + (255,),
              stroke_width=bw, stroke_fill=fill + (255,))
    # 3) 斜体: 仿射剪切 (PIL AFFINE 为 目标->源 逆映射, 用 -skew 得到右下斜体)
    if italic:
        skew = 0.22
        canvas = canvas.transform(canvas.size, Image.AFFINE, (1, -skew, 0, 0, 1, 0))
    canvas = canvas.resize((box_w, box_h), Image.LANCZOS)
    return canvas


def generate_from_ttf(ttf_path, out_dir, sprites, fill_scale=0.9, log=None,
                      group_colors=None, group_styles=None):
    """为每个可替换精灵生成 {name}.png。返回生成数量。

    group_colors : {group: (r,g,b)} 每组填充色; 缺省则回退到精灵原生 dominant。
    group_styles : {group: dict} 每组样式, 键为:
        bold         : bool  (默认 False)
        italic       : bool  (默认 False)
        opacity      : float (0-255, 默认 255 = 全不透明)
      缺省组的样式用默认值(无加粗/斜体/全不透明)。
    """
    os.makedirs(out_dir, exist_ok=True)
    n = 0
    for sp in sprites:
        if not sp.get("char"):
            continue
        fill = None
        if group_colors:
            gc = group_colors.get(sp["group"])
            if gc:
                fill = gc
        # 按组取样式
        st = {}
        if group_styles:
            st = group_styles.get(sp["group"], {})
        img = render_glyph_ttf(ttf_path, sp, sp["w"], sp["h"], fill_scale,
                               fill=fill,
                               bold=st.get("bold", False),
                               italic=st.get("italic", False))
        if img is None:
            continue
        # 应用不透明度(缩放 alpha 通道)
        opa = st.get("opacity", 255.0)
        if opa < 255.0:
            alpha = max(0.0, min(255.0, opa)) / 255.0
            arr = np.array(img, dtype=np.float64)
            arr[:, :, 3] = np.clip(arr[:, :, 3] * alpha, 0, 255).astype(np.uint8)
            img = Image.fromarray(arr.astype(np.uint8), mode="RGBA")
        img.save(os.path.join(out_dir, sp["name"] + ".png"))
        n += 1
    if log:
        log(_t("core_ttf_gen", n, out_dir))
    return n


if __name__ == "__main__":
    # 简单自测: 全替换成红色方块, 构建一次
    res = get_resource_dir()
    nat = load_native(res)
    print("HD", nat["AW"], nat["AH"], "FHD", nat["FW"], nat["FH"], "sprites", len(nat["sprites"]))
