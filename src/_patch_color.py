# -*- coding: utf-8 -*-
import io

P1 = r"E:/GBFR_ModMaker/gbfr-font-mod-repo/modmaker/gbfr_mod_maker.py"
P2 = r"E:/GBFR_ModMaker/gbfr-font-mod-repo/modmaker/core.py"

s = io.open(P1, encoding="utf-8").read()

def need(sub, where="?"):
    assert sub in s, "NOT FOUND @ %s:\n%r" % (where, sub[:60])

old_const = '''#   normalAttackColor_ : 普通攻击数字颜色 (浅青, 半透明)
#   spAttackColor_     : SP 攻击数字颜色 (浅黄, 半透明)
# 注: 4 元素数组按 RGBA 理解 (0-1)。UI 内以 0-255 显示/编辑, 写入时换算回 0-1。
COLOR_KEYS = ["normalAttackColor_", "spAttackColor_"]
DEFAULT_COLOR = {  # 0-255 RGBA (由原生模板 0-1 值 ×255 取整)
    "normalAttackColor_": (210, 235, 240, 128),
    "spAttackColor_": (240, 235, 180, 128),
}
COLOR_LABEL_KEYS = {
    "normalAttackColor_": "col_normal",
    "spAttackColor_": "col_sp",
}
COLOR_HINT_KEYS = {
    "normalAttackColor_": "col_normal_hint",
    "spAttackColor_": "col_sp_hint",
}'''
need(old_const, "const")
s = s.replace(old_const, "")

zh_col = '''        "col_section": "数字颜色 (RGBA, 0–255)",
        "col_normal": "普通攻击颜色 normalAttackColor_",
        "col_sp": "SP 攻击颜色 spAttackColor_",
        "col_normal_hint": "点击色块用调色板选色，或直接输入 R/G/B/A（0–255，A=不透明度）。",
        "col_sp_hint": "点击色块用调色板选色，或直接输入 R/G/B/A（0–255，A=不透明度）。",
        "col_preview": "预览(含透明度)",
        "col_rgba": "R/G/B/A (0–255)",
'''
need(zh_col, "zh_col")
s = s.replace(zh_col, "")

en_col = '''        "col_section": "Number Colors (RGBA, 0–255)",
        "col_normal": "Normal Atk color normalAttackColor_",
        "col_sp": "SP Atk color spAttackColor_",
        "col_normal_hint": "Click swatch to pick from palette, or type R/G/B/A (0–255, A=opacity).",
        "col_sp_hint": "Click swatch to pick from palette, or type R/G/B/A (0–255, A=opacity).",
        "col_preview": "Preview (with alpha)",
        "col_rgba": "R/G/B/A (0–255)",
'''
need(en_col, "en_col")
s = s.replace(en_col, "")

s = s.replace('"size_control": "数字大小/闪光颜色控制",', '"size_control": "数字大小控制",')
s = s.replace('"size_control": "Number Size / Flash Color",', '"size_control": "Number Size",')
s = s.replace('"sz_win_title": "数字大小与颜色控制 (hud_param.json)",', '"sz_win_title": "数字大小控制 (hud_param.json)",')
s = s.replace('"sz_win_title": "Number Size & Color (hud_param.json)",', '"sz_win_title": "Number Size (hud_param.json)",')

i = s.index('· 数字颜色(RGBA')
j = s.index('\n', i)
s = s.replace(s[i:j+1], "")
s = s.replace("；颜色为 4 元素 RGBA(0–1) 数组。", "。")
i = s.index('· Colors (RGBA')
j = s.index('\n', i)
s = s.replace(s[i:j+1], "")
s = s.replace("; colors are 4-element RGBA (0–1) arrays.", ".")

s = s.replace("数字大小/颜色控制", "数字大小控制")
s = s.replace("；颜色 normalAttackColor_/spAttackColor_ 支持 RGBA 调色板与 R/G/B/A 输入，可重置为原生基准。", "。")
s = s.replace("Number size & color control", "Number size control")
s = s.replace("; Colors normalAttackColor_/spAttackColor_ support RGBA palette + R/G/B/A input, resettable to native base.", ".")

s = s.replace('"数字大小/闪光颜色控制"', "“数字大小控制”")
s = s.replace("数字大小/闪光颜色控制", "数字大小控制")
s = s.replace(" + RGBA 颜色段", "")
anchor = '数字颜色(RGBA 0–255)：普通攻击 normalAttackColor_ / SP 攻击 spAttackColor_；点击色块用调色板选色，或输入 R/G/B/A（A=不透明度）'
need(anchor, "tut_color_sub")
i = s.index(anchor)
start = i - 6
end = s.index('"', i)
s = s.replace(s[start:end+1], "")

s = s.replace("Number Size / Flash Color", "Number Size")
s = s.replace(" + RGBA color section", "")

init_line = '        self.dmg_colors = {k: tuple(DEFAULT_COLOR[k]) for k in COLOR_KEYS}\n'
need(init_line, "init")
s = s.replace(init_line, "")

a = s.index('    def _color_preview_img(self, rgba, size=(30, 30)):')
b = s.index('    def on_size_control(self):')
s = s[:a] + s[b:]

start = s.index('    def on_size_control(self):')
end = s.index('    def _on_size_entry(self, k):')
NEW = '''    def on_size_control(self):
        """Number size/pos/spacing control (hud_param.json damage_)."""
        win = tk.Toplevel(self.root)
        win.title(tr("sz_win_title"))
        win.geometry("560x420")
        win.resizable(False, False)
        win.transient(self.root)
        win.grab_set()

        # top description
        desc_frm = ttk.Frame(win)
        desc_frm.pack(fill="x", padx=16, pady=(10, 4))
        ttk.Label(desc_frm, text=tr("sz_desc"),
                  font=("Microsoft YaHei", 9), wraplength=520, justify="left").pack(anchor="w")

        sep = ttk.Separator(win, orient="horizontal")
        sep.pack(fill="x", padx=16, pady=6)

        # size/pos/spacing (grid: label | entry | hint)
        ctrl = ttk.Frame(win)
        ctrl.pack(fill="x", padx=16, pady=4)
        ctrl.grid_columnconfigure(1, weight=1)

        self._size_entries = {}
        for i, k in enumerate(core.SIZE_KEYS):
            lbl = ttk.Label(ctrl, text=tr(SIZE_LABEL_KEYS[k]),
                            font=("Microsoft YaHei", 10, "bold"))
            lbl.grid(row=i, column=0, sticky="e", padx=(0, 10), pady=8)
            ent = ttk.Entry(ctrl, width=10, justify="center",
                            font=("Consolas", 11))
            ent.insert(0, "%.2f" % self.dmg_sizes.get(k, DEFAULT_SIZE_SCALE.get(k, 0.0)))
            ent.grid(row=i, column=1, sticky="w", padx=6, pady=8)
            ent.bind("<Return>", lambda e, kk=k: self._on_size_entry(kk))
            ent.bind("<FocusOut>", lambda e, kk=k: self._on_size_entry(kk))
            self._size_entries[k] = ent
            hint = ttk.Label(ctrl, text=tr(SIZE_HINT_KEYS[k]),
                             font=("Microsoft YaHei", 8), foreground="#888")
            hint.grid(row=i, column=2, sticky="w", padx=(8, 0), pady=8)

        bottom = ttk.Frame(win)
        bottom.pack(fill="x", padx=16, pady=(8, 10))
        ttk.Label(bottom, text=tr("sz_note"),
                  font=("Microsoft YaHei", 8), foreground="#888").pack(side="left", anchor="w")
        btn_area = ttk.Frame(bottom)
        btn_area.pack(side="right")
        ttk.Button(btn_area, text=tr("sz_reset"),
                   command=self._on_size_reset_all).pack(side="left", padx=4)
        ttk.Button(btn_area, text=tr("sz_close"),
                   command=win.destroy).pack(side="left", padx=4)

'''
s = s[:start] + NEW + s[end:]

a = s.index('    def _on_color_pick(self, k):')
b = s.index('    def _on_size_reset_all(self):')
s = s[:a] + s[b:]

reset_block = '''        for k in COLOR_KEYS:
            self.dmg_colors[k] = tuple(DEFAULT_COLOR[k])
            self._refresh_color_widget(k)
'''
need(reset_block, "reset")
s = s.replace(reset_block, "")

s = s.replace("                                 stretches=stretches, sizes=self.dmg_sizes, colors=self.dmg_colors)",
              "                                 stretches=stretches, sizes=self.dmg_sizes)")

io.open(P1, "w", encoding="utf-8").write(s)
print("gbfr_mod_maker.py color removal done")

c = io.open(P2, encoding="utf-8").read()
old_c = '''# 伤害数字颜色 (hud_param.json damage_ 段, 0-1 RGBA 4 元素数组):
#   normalAttackColor_ : 普通攻击数字颜色 (浅青, 半透明)
#   spAttackColor_     : SP 攻击数字颜色 (浅黄, 半透明)
COLOR_KEYS = ["normalAttackColor_", "spAttackColor_"]
DEFAULT_COLOR_JSON = {  # 原生模板基准 (0-1 RGBA)
    "normalAttackColor_": [0.8235295, 0.9215687, 0.9411765, 0.5019608],
    "spAttackColor_": [0.9411765, 0.9215687, 0.7058824, 0.5019608],
}'''
need(old_c, "core_const")
c = c.replace(old_c, "")
c = c.replace("              sizes=None, colors=None, mod_author=", "              sizes=None, mod_author=")
c = c.replace('    colors:      {name: (r,g,b,a)} 伤害数字颜色 RGBA(0-255): normalAttackColor_ / spAttackColor_\n', "")
c = c.replace('    colors = colors or {k: tuple(int(round(x * 255)) for x in DEFAULT_COLOR_JSON[k]) for k in COLOR_KEYS}\n', "")
cw = '''            for k in COLOR_KEYS:
                if k in dmg and k in colors:
                    r, g, b, a = colors[k]
                    dmg[k] = [round(r / 255.0, 6), round(g / 255.0, 6),
                              round(b / 255.0, 6), round(a / 255.0, 6)]
'''
need(cw, "core_cw")
c = c.replace(cw, "")
c = c.replace('                    + " | " + ", ".join("%s=(%s)" % (k, ",".join("%.3f" % x for x in dmg.get(k, [0, 0, 0, 0]))) for k in COLOR_KEYS))',
              '')

io.open(P2, "w", encoding="utf-8").write(c)
print("core.py color removal done")
