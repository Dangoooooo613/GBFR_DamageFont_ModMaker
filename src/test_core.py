#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""core.py headless 自测: 全替换 + 全屏蔽 + TTF 生成, 并回解码校验。"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw
import imagecodecs

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import core

RES = core.get_resource_dir()
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_test_out")
os.makedirs(OUT, exist_ok=True)

nat = core.load_native(RES)
sprites = nat["sprites"]
print("加载: HD %dx%d  FHD %dx%d  精灵 %d" % (nat["AW"], nat["AH"], nat["FW"], nat["FH"], len(sprites)))


def make_test_img(sp, color):
    img = Image.new("RGBA", (sp["w"], sp["h"]), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([2, 2, sp["w"] - 3, sp["h"] - 3], fill=color + (255,))
    return img


# ── 1) 全替换测试 ──
actions, replacements, ratios = {}, {}, {}
for sp in sprites:
    if sp["char"]:
        actions[sp["name"]] = "replace"
        replacements[sp["name"]] = make_test_img(sp, tuple(sp["dominant"]))
        ratios[sp["name"]] = 100.0
    else:
        actions[sp["name"]] = "keep"

zp = core.build_mod(actions, replacements, ratios, OUT, mod_id="test.replace", log=print)
print("替换 zip:", zp, os.path.getsize(zp))

# 回解码校验 HD
wtb_hd = os.path.join(OUT, "test.replace", "GBFR", "data", "ui", "atlas", "hud_num_battle.wtb")
raw = open(wtb_hd, "rb").read()
assert raw[:4] == nat["hd_hdr"][:4] or len(raw) >= 4096
dds = raw[4096:]
open(os.path.join(OUT, "_hd.dds"), "wb").write(dds)
arr = imagecodecs.imread(os.path.join(OUT, "_hd.dds"))
print("HD 回解码 shape:", arr.shape, "期望", (nat["AH"], nat["AW"]))
assert arr.shape[:2] == (nat["AH"], nat["AW"]), "HD 尺寸错误"

# 校验某 replace 精灵区域变了
sp0 = next(s for s in sprites if s["char"])
reg_new = arr[sp0["y"]:sp0["y"] + sp0["h"], sp0["x"]:sp0["x"] + sp0["w"]]
reg_nat = nat["hd_arr"][sp0["y"]:sp0["y"] + sp0["h"], sp0["x"]:sp0["x"] + sp0["w"]]
diff = np.abs(reg_new.astype(int) - reg_nat.astype(int)).sum()
print("替换精灵 %s 与原生差异像素和 = %d" % (sp0["name"], diff))
assert diff > 1000, "替换未生效"

# ── 2) 全屏蔽测试 ──
actions2 = {sp["name"]: ("block" if sp["char"] else "keep") for sp in sprites}
zp2 = core.build_mod(actions2, {}, {}, OUT, mod_id="test.block", log=print)
wtb_hd2 = os.path.join(OUT, "test.block", "GBFR", "data", "ui", "atlas", "hud_num_battle.wtb")
open(os.path.join(OUT, "_blk.dds"), "wb").write(open(wtb_hd2, "rb").read()[4096:])
arr2 = imagecodecs.imread(os.path.join(OUT, "_blk.dds"))
reg_b = arr2[sp0["y"]:sp0["y"] + sp0["h"], sp0["x"]:sp0["x"] + sp0["w"]]
alpha_sum = reg_b[..., 3].sum()
print("屏蔽精灵 %s alpha 和 = %d (应≈0)" % (sp0["name"], alpha_sum))
assert alpha_sum < 100, "屏蔽未生效(应全透明)"

# ── 3) TTF 生成测试 ──
ttf = "C:/Windows/Fonts/arial.ttf"
if os.path.exists(ttf):
    ttf_out = os.path.join(OUT, "ttf_png")
    n = core.generate_from_ttf(ttf, ttf_out, sprites, log=print)
    print("TTF 生成张数:", n)
    assert n == sum(1 for s in sprites if s["char"])
    # 用生成的 PNG 做替换构建
    actions3 = {sp["name"]: ("replace" if sp["char"] else "keep") for sp in sprites}
    reps3 = {}
    for sp in sprites:
        if sp["char"]:
            p = os.path.join(ttf_out, sp["name"] + ".png")
            if os.path.exists(p):
                reps3[sp["name"]] = Image.open(p).convert("RGBA")
    zp3 = core.build_mod(actions3, reps3, {k: 100.0 for k in reps3}, OUT, mod_id="test.ttf", log=print)
    print("TTF 替换 zip:", os.path.getsize(zp3))
else:
    print("跳过 TTF 测试(无 arial.ttf)")

print("\n✅ 所有 core 自测通过")
