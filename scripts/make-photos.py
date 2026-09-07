# -*- coding: utf-8 -*-
"""從原檔重新產生站上用的照片。改裁切就改這裡的參數，然後重跑：

    python3 scripts/make-photos.py

原檔：蔡律師形象照.png（1024×1536 法袍去背，家屬 2026-09-07 提供）
      ⚠️ 這張**背景是全透明的**（53% 像素 alpha=0）。直接放上網，在不同底色上
      會露出底下的東西、存下來用看圖軟體開會看到灰白格子。所以站上這張一律
      先把去背合成到一個實體底色再輸出。
產出：public/images/tsai-portrait.jpg  4:5 直幅 1040×1300，index／profile 兩處共用
      public/images/og.jpg             1200×630，分享到 LINE／Facebook 的預覽圖
需要 Pillow：pip3 install Pillow
"""
from PIL import Image, ImageDraw, ImageFont
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, '蔡律師形象照.png')
OUT = os.path.join(ROOT, 'public', 'images')

# 人物在原檔的位置（用 alpha>128 量出來的）：水平中心、肩寬、頭頂 y。
SUBJ_CX, SUBJ_W, HEAD_TOP = 565, 708, 86
FILL = 0.86        # 肩寬佔畫面寬的比例；0.72 太遠、1.00 會頂到左右邊
HEAD_Y = 0.09      # 頭頂離上緣的比例
SONGTI = '/System/Library/Fonts/Supplemental/Songti.ttc'   # 索引 7=TC Regular、2=TC Bold
GOLD, CREAM = (201, 168, 112), (247, 244, 237)


def font(size, bold=False):
    return ImageFont.truetype(SONGTI, size, index=2 if bold else 7)


def gradient(size, start, end, horiz=False):
    """畫一條線性漸層後拉滿整張圖。horiz=True 為左右向，否則上下向。"""
    w, h = size
    n = w if horiz else h
    strip = Image.new('RGB', (w, 1) if horiz else (1, h))
    px = strip.load()
    for i in range(n):
        t = i / (n - 1)
        c = tuple(int(start[k] + (end[k] - start[k]) * t) for k in range(3))
        if horiz:
            px[i, 0] = c
        else:
            px[0, i] = c
    return strip.resize(size, Image.BILINEAR)


def radial(size, inner, outer, cx=0.5, cy=0.34, radius=0.95):
    """柔和的棚拍暈影：中心亮、四角略暗，讓人物有立足的底而不是浮在色塊上。"""
    w, h = size
    base, top = Image.new('RGB', size, outer), Image.new('RGB', size, inner)
    m = Image.new('L', (max(1, w // 4), max(1, h // 4)))
    px = m.load()
    mw, mh = m.size
    for y in range(mh):
        for x in range(mw):
            dx, dy = x / mw - cx, (y / mh - cy) * 0.78
            d = ((dx * dx + dy * dy) ** 0.5) / radius
            px[x, y] = int(255 * (max(0.0, 1.0 - d) ** 1.5))
    base.paste(top, (0, 0), m.resize(size, Image.BICUBIC))
    return base


def tracked(draw, xy, text, fnt, fill, track=0):
    """逐字加字距——中文標題不加字距會太擠。"""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=fnt, fill=fill)
        x += draw.textlength(ch, font=fnt) + track


def main():
    os.makedirs(OUT, exist_ok=True)
    src = Image.open(SRC).convert('RGBA')

    # 直幅：合成到暖米色暈影底（與站上 --paper #f7f4ed 同色系，但四角略深，
    # 這樣照片在米色頁面上仍看得出邊界，不會糊成一片）
    w, h = 1040, 1300
    s = (w * FILL) / SUBJ_W
    figure = src.resize((int(src.width * s), int(src.height * s)), Image.LANCZOS)
    canvas = radial((w, h), (245, 241, 232), (223, 216, 203)).convert('RGBA')
    canvas.alpha_composite(figure, (w // 2 - int(SUBJ_CX * s), int(h * HEAD_Y) - int(HEAD_TOP * s)))
    canvas.convert('RGB').save(os.path.join(OUT, 'tsai-portrait.jpg'),
                               quality=86, optimize=True, progressive=True)

    # OG 卡：深綠底，人物直接站在綠底上（去背在這裡剛好派上用場），左側放姓名
    ow, oh, pw = 1200, 630, 600
    s2 = (pw * 0.80) / SUBJ_W
    fig2 = src.resize((int(src.width * s2), int(src.height * s2)), Image.LANCZOS)
    panel = Image.new('RGBA', (pw, oh), (0, 0, 0, 0))
    panel.alpha_composite(fig2, (pw // 2 - int(SUBJ_CX * s2) - 10, int(oh * 0.12) - int(HEAD_TOP * s2)))

    card = gradient((ow, oh), (24, 56, 48), (13, 29, 25)).convert('RGBA')
    card.alpha_composite(panel, (ow - pw, 0))
    d = ImageDraw.Draw(card)
    tracked(d, (88, 150), '臺南 · 中西區府前路', font(24), GOLD, 6)
    d.line([(88, 214), (144, 214)], fill=GOLD, width=2)
    tracked(d, (88, 258), '蔡青芬律師', font(76, True), CREAM, 10)
    tracked(d, (88, 382), '蔡青芬律師事務所', font(30), (200, 206, 201), 5)
    tracked(d, (88, 452), '初次諮詢不收費 · 可電話或視訊', font(24), (168, 180, 172), 4)
    card.convert('RGB').save(os.path.join(OUT, 'og.jpg'), quality=88, optimize=True, progressive=True)
    print('寫出 tsai-portrait.jpg 與 og.jpg 到', OUT)


if __name__ == '__main__':
    main()
