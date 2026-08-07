#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
预处理: 把游戏原生 hud_num_battle.wtb (HD + FHD) 转成本工具运行期需要的资源。

输出到 resources/:
  native_hd_atlas.png   主图集 RGBA (4096x2048, 无损)
  native_fhd_atlas.png  高分辨率图集 RGBA (2048x1024, 无损)
  native_hd_hdr.bin     主 wtb 前 4096 字节引擎头
  native_fhd_hdr.bin    高分辨率 wtb 前 4096 字节引擎头
  sprites.json          112 精灵清单(name/group/x/y/w/h/dominant/char)
  texconv.exe           已复制

运行期不再需要 imagecodecs / 游戏原始 wtb, 只需 PIL + numpy + 本资源 + texconv。
"""
import os, json, struct, base64
import numpy as np
from PIL import Image
import imagecodecs

ROOT = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(ROOT, "resources")
os.makedirs(RES, exist_ok=True)

GAME = r"D:/Program Files (x86)/Steam/steamapps/common/Granblue Fantasy Relink"
WTB_HD = os.path.join(GAME, "data/ui/atlas/hud_num_battle.wtb")
WTB_FHD = os.path.join(GAME, "data/ui/fhd/atlas/hud_num_battle.wtb")
V15 = os.path.join(ROOT, "..", "_build_tmp", "v15_table.json")
HDR_SIZE = 4096


def extract_header(wtb_path, out_bin):
    with open(wtb_path, "rb") as f:
        hdr = f.read(HDR_SIZE)
    if len(hdr) < HDR_SIZE:
        raise RuntimeError("文件过小, 不是合法 wtb")
    with open(out_bin, "wb") as f:
        f.write(hdr)
    print(f"[header] {wtb_path} -> {out_bin} ({len(hdr)} bytes)")


def decode_atlas(wtb_path, out_png):
    with open(wtb_path, "rb") as f:
        dds = f.read()[HDR_SIZE:]
    tmp = os.path.join(RES, "_tmp_atlas.dds")
    with open(tmp, "wb") as f:
        f.write(dds)
    arr = imagecodecs.imread(tmp)
    if arr.dtype != np.uint8:
        arr = arr.astype(np.uint8)
    if arr.shape[2] == 3:
        arr = np.dstack([arr, np.full(arr.shape[:2], 255, np.uint8)])
    Image.fromarray(arr).save(out_png)
    os.remove(tmp)
    print(f"[decode] {wtb_path} -> {out_png}  shape={arr.shape}")


def suffix_token(name):
    rest = name[9:]
    if rest.startswith("_"):
        rest = rest[1:]
    if rest.endswith("_add"):
        return rest[:-4]
    for prefix in ["guard01", "guard02", "damage", "effect",
                   "normal", "member", "heal", "link"]:
        if rest.startswith(prefix):
            out = rest[len(prefix):]
            if out.startswith("_"):
                out = out[1:]
            return out
    uidx = rest.rfind("_")
    if uidx > 0:
        return rest[uidx + 1:]
    return rest


def char_from_suffix(tok, group):
    if group == "effect":
        return None
    if tok == "10":
        return "!"
    if tok == "11":
        return "%"
    if tok == "12":
        return "+"
    if tok.isdigit() and len(tok) <= 2:
        return str(int(tok))
    return None


def build_sprites(v15_path, out_json):
    rows = json.load(open(v15_path, encoding="utf-8"))
    out = []
    for r in rows:
        if r.get("img_b64") is None:
            continue
        tok = suffix_token(r["name"])
        ch = char_from_suffix(tok, r["group"])
        out.append({
            "name": r["name"],
            "group": r["group"],
            "x": int(r["x"]), "y": int(r["y"]),
            "w": int(r["w"]), "h": int(r["h"]),
            "dominant": [int(c) for c in r["dominant"]],
            "char": ch,
        })
    out.sort(key=lambda s: s["name"])
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"[sprites] {out_json}: {len(out)} 精灵  "
          f"(可替换={sum(1 for s in out if s['char'])})")
    return out


if __name__ == "__main__":
    extract_header(WTB_HD, os.path.join(RES, "native_hd_hdr.bin"))
    extract_header(WTB_FHD, os.path.join(RES, "native_fhd_hdr.bin"))
    decode_atlas(WTB_HD, os.path.join(RES, "native_hd_atlas.png"))
    decode_atlas(WTB_FHD, os.path.join(RES, "native_fhd_atlas.png"))
    build_sprites(V15, os.path.join(RES, "sprites.json"))
    print("\n预处理完成 ->", RES)
