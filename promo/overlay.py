import math, subprocess, sys, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = sys.argv[1]
W, H, FPS, DUR = 1920, 1080, 30, 30.0
TITLE = S + "/fonts/BlackHanSans.ttf"
BODY = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

BURG = (139, 27, 62)
BURG_D = (70, 10, 32)
GOLD = (255, 200, 87)
CREAM = (255, 244, 225)
PINK = (255, 92, 160)


def font(path, size):
    return ImageFont.truetype(path, size)


def text_img(txt, path, size, fill, stroke=0, stroke_fill=(0, 0, 0), shadow=True):
    f = font(path, size)
    l, t, r, b = f.getbbox(txt, stroke_width=stroke)
    pad = 30
    w, h = r - l + pad * 2, b - t + pad * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        ImageDraw.Draw(sh).text((pad - l + 4, pad - t + 6), txt, font=f, fill=(0, 0, 0, 170), stroke_width=stroke, stroke_fill=(0, 0, 0, 170))
        im = Image.alpha_composite(im, sh.filter(ImageFilter.GaussianBlur(8)))
    ImageDraw.Draw(im).text((pad - l, pad - t), txt, font=f, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
    return im


def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_back(x):
    x = clamp(x)
    c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def prog(t, start, dur):
    return clamp((t - start) / dur)


def with_alpha(im, a):
    if a >= 0.999:
        return im
    r, g, b, al = im.split()
    al = al.point(lambda v: int(v * a))
    return Image.merge("RGBA", (r, g, b, al))


def paste(canvas, im, cx, cy, alpha=1.0, scale=1.0, anchor="c"):
    if alpha <= 0.003:
        return
    if abs(scale - 1) > 0.002:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BILINEAR)
    im = with_alpha(im, alpha)
    if anchor == "c":
        x, y = int(cx - im.width / 2), int(cy - im.height / 2)
    else:  # left-center
        x, y = int(cx), int(cy - im.height / 2)
    canvas.alpha_composite(im, (x, y)) if 0 <= x and 0 <= y and x + im.width <= W and y + im.height <= H else _safe(canvas, im, x, y)


def _safe(canvas, im, x, y):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(im, (x, y), im)
    canvas.alpha_composite(layer)


# ---------- pre-rendered assets ----------
intro_kicker = text_img("제3회 안산시민을 위한", TITLE, 64, CREAM)
intro_sub = text_img("청소년과 범죄예방위원이 함께하는", TITLE, 72, CREAM)
intro_title = text_img("힐링콘서트", TITLE, 250, GOLD, stroke=6, stroke_fill=BURG_D)

out_title = text_img("힐링콘서트", TITLE, 210, GOLD, stroke=6, stroke_fill=BURG_D)
out_kicker = text_img("제3회 안산시민을 위한 청소년과 범죄예방위원이 함께하는", TITLE, 50, CREAM)
out_date = text_img("2026. 10. 10 (토)  오후 2시", TITLE, 84, (255, 255, 255))
out_place = text_img("썬큰 광장 (고잔 홈플러스 사거리 야외무대)", BODY, 48, CREAM)
out_host = text_img("주최  법무부 청소년 범죄예방위원 상록지구위원회 · 안산시체육회 · 디딤돌밴드", BODY, 34, (235, 220, 225))
out_spon = text_img("후원  수원지방검찰청 안산지청 · 안산시 · 안산교육지원청", BODY, 34, (235, 220, 225))
out_cta = text_img("안산시민 여러분을 초대합니다!", TITLE, 64, (255, 255, 255), stroke=4, stroke_fill=PINK)

bug = text_img("제3회 힐링콘서트", TITLE, 38, (255, 255, 255))

# (start, end, kicker, title)
captions = [
    (3.9, 8.4, "DANCE", "청소년 댄스 공연"),
    (8.7, 10.7, "LIVE", "감동의 라이브 무대"),
    (11.0, 13.5, "TOGETHER", "모두가 함께하는 무대"),
    (13.8, 16.4, "HIGHLIGHT", "열정 가득한 현장"),
    (16.7, 19.4, "HEALING", "시민과 함께하는 힐링 타임"),
]
cap_assets = []
for s, e, k, ttl in captions:
    ki = text_img(k, "/usr/share/fonts/truetype/inter/Inter-Black.ttf" if False else TITLE, 40, (30, 10, 20), shadow=False)
    ti = text_img(ttl, TITLE, 92, (255, 255, 255))
    cap_assets.append((s, e, ki, ti))

# radial burgundy vignette for intro/outro tint
def make_tint():
    g = Image.radial_gradient("L").resize((W, H), Image.BILINEAR)  # 0 center -> 255 edge
    base = Image.new("RGBA", (W, H), BURG + (0,))
    alpha = g.point(lambda v: int(120 + v * 0.45))
    base.putalpha(alpha)
    return base

TINT = make_tint()

# floating particles (notes / bokeh)
random.seed(7)
NOTE_FONT = font(BODY, 60)
particles = []
for i in range(26):
    particles.append(dict(
        x=random.uniform(0, W), y=random.uniform(0, H), sp=random.uniform(30, 90),
        r=random.uniform(6, 26), ph=random.uniform(0, 6.28), col=random.choice([GOLD, PINK, CREAM]),
        note=random.random() < 0.35))
note_imgs = {c: text_img("♪", BODY, 70, c + (230,), shadow=False) for c in [GOLD, PINK, CREAM]}
dot_imgs = {}
for c in [GOLD, PINK, CREAM]:
    d = Image.new("RGBA", (80, 80), (0, 0, 0, 0))
    ImageDraw.Draw(d).ellipse((20, 20, 60, 60), fill=c + (200,))
    dot_imgs[c] = d.filter(ImageFilter.GaussianBlur(6))


def draw_particles(canvas, t, alpha):
    for p in particles:
        y = (p["y"] - p["sp"] * t) % (H + 100) - 50
        x = p["x"] + 30 * math.sin(t * 1.3 + p["ph"])
        a = alpha * (0.5 + 0.5 * math.sin(t * 2 + p["ph"]))
        img = note_imgs[p["col"]] if p["note"] else dot_imgs[p["col"]]
        paste(canvas, img, x, y, a, scale=p["r"] / 16)


def draw_rings(canvas, t, t0, alpha):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(3):
        k = ((t - t0) * 0.6 + i / 3) % 1.0
        r = 200 + k * 900
        a = int(alpha * 110 * (1 - k))
        d.ellipse((W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r), outline=GOLD + (a,), width=4)
    canvas.alpha_composite(layer)


def intro(canvas, t):
    out = 1 - prog(t, 3.3, 0.4)
    canvas.alpha_composite(with_alpha(TINT, out))
    draw_rings(canvas, t, 0, out)
    draw_particles(canvas, t, out)
    # gold lines sweeping
    lw = int(ease_out(prog(t, 0.1, 0.6)) * 700)
    if lw > 0:
        line = Image.new("RGBA", (lw, 6), GOLD + (int(255 * out),))
        canvas.alpha_composite(line, (W // 2 - lw // 2, 260))
        canvas.alpha_composite(line, (W // 2 - lw // 2, 820))
    p1 = ease_out(prog(t, 0.15, 0.5))
    paste(canvas, intro_kicker, W / 2, 330 + 40 * (1 - p1), p1 * out)
    p2 = ease_out(prog(t, 0.35, 0.5))
    paste(canvas, intro_sub, W / 2, 420 + 40 * (1 - p2), p2 * out)
    p3 = prog(t, 0.65, 0.55)
    sc = 0.3 + 0.7 * ease_back(p3) if p3 > 0 else 0
    sc *= 1 + 0.02 * math.sin(t * 6) * (p3 >= 1)
    paste(canvas, intro_title, W / 2, 630, clamp(p3 * 3) * out, scale=sc * (1 + 0.15 * (1 - out)))


def caption(canvas, t):
    for s, e, ki, ti in cap_assets:
        if t < s - 0.1 or t > e + 0.1:
            continue
        pin = ease_out(prog(t, s, 0.5))
        pout = ease_out(prog(t, e - 0.4, 0.4))
        x0 = 90
        y = 900
        # accent bar
        bar_w = int(16 * pin)
        bar_h = int(170 * pin * (1 - pout))
        if bar_w > 0 and bar_h > 0:
            canvas.alpha_composite(Image.new("RGBA", (bar_w, bar_h), PINK + (255,)), (x0 - 30, y - 110))
        # kicker pill
        kp = ease_out(prog(t, s + 0.1, 0.4))
        pill_w = int((ki.width - 20) * kp * (1 - pout))
        if pill_w > 4:
            pill = Image.new("RGBA", (pill_w, 58), (0, 0, 0, 0))
            ImageDraw.Draw(pill).rounded_rectangle((0, 0, pill_w - 1, 57), 10, fill=GOLD + (255,))
            canvas.alpha_composite(pill, (x0, y - 110))
            crop = ki.crop((0, 0, min(ki.width, pill_w + 20), ki.height))
            paste(canvas, crop, x0 - 20, y - 81, 1 - pout, anchor="l")
        dx = -120 * (1 - pin) - 80 * pout
        paste(canvas, ti, x0 - 30 + dx, y + 10, pin * (1 - pout), anchor="l")


def bug_draw(canvas, t):
    a = clamp(prog(t, 3.8, 0.5)) * (1 - prog(t, 22.4, 0.4))
    if a <= 0:
        return
    pill = Image.new("RGBA", (bug.width - 20, 70), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle((0, 0, pill.width - 1, 69), 35, fill=BURG + (215,))
    paste(canvas, pill, W - 70 - pill.width / 2, 80, a)
    paste(canvas, bug, W - 70 - pill.width / 2, 80, a)


def outro(canvas, t):
    T0 = 22.7
    pin = ease_out(prog(t, T0, 0.6))
    canvas.alpha_composite(with_alpha(TINT, pin))
    dark = Image.new("RGBA", (W, H), BURG_D + (int(90 * pin),))
    canvas.alpha_composite(dark)
    draw_rings(canvas, t, T0, pin * 0.8)
    draw_particles(canvas, t, pin)
    lt = t - T0
    paste(canvas, out_kicker, W / 2, 175 + 30 * (1 - ease_out(prog(lt, 0.3, 0.5))), ease_out(prog(lt, 0.3, 0.5)))
    p = prog(lt, 0.5, 0.6)
    paste(canvas, out_title, W / 2, 335, clamp(p * 3), scale=(0.4 + 0.6 * ease_back(p)) if p > 0 else 0)
    # divider
    dw = int(ease_out(prog(lt, 1.1, 0.5)) * 900)
    if dw > 0:
        canvas.alpha_composite(Image.new("RGBA", (dw, 5), GOLD + (255,)), (W // 2 - dw // 2, 470))
    for i, (im, y) in enumerate([(out_date, 560), (out_place, 655)]):
        q = ease_out(prog(lt, 1.3 + 0.25 * i, 0.5))
        paste(canvas, im, W / 2 + 80 * (1 - q) * (1 if i % 2 else -1), y, q)
    for i, (im, y) in enumerate([(out_host, 760), (out_spon, 812)]):
        q = ease_out(prog(lt, 2.0 + 0.2 * i, 0.5))
        paste(canvas, im, W / 2, y + 20 * (1 - q), q)
    q = prog(lt, 2.8, 0.5)
    pulse = 1 + 0.04 * math.sin(lt * 5) * (q >= 1)
    paste(canvas, out_cta, W / 2, 935, clamp(q * 2), scale=(0.5 + 0.5 * ease_back(q)) * pulse if q > 0 else 0)
    # final fade to black
    fb = prog(t, 29.2, 0.8)
    if fb > 0:
        canvas.alpha_composite(Image.new("RGBA", (W, H), (0, 0, 0, int(255 * fb))))


CUTS = [3.85, 8.65, 10.95, 13.75, 16.65, 19.65]


def punch(frame, t):
    # quick zoom punch right after each cut for energy
    for c in CUTS:
        k = (t - c) / 0.35
        if 0 <= k < 1:
            sc = 1 + 0.08 * (1 - ease_out(k))
            w, h = int(W / sc), int(H / sc)
            x, y = (W - w) // 2, (H - h) // 2
            return frame.crop((x, y, x + w, y + h)).resize((W, H), Image.BILINEAR)
    return frame


def render(t, frame):
    canvas = punch(frame, t).convert("RGBA")
    if t < 3.8:
        intro(canvas, t)
    else:
        bug_draw(canvas, t)
        caption(canvas, t)
    if t >= 22.7:
        outro(canvas, t)
    return canvas.convert("RGB")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "preview":
        for tt in [float(x) for x in sys.argv[3].split(",")]:
            fr = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(tt), "-i", S + "/base.mp4", "-frames:v", "1", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
            render(tt, Image.frombytes("RGB", (W, H), fr)).save(f"{S}/prev_{tt:05.2f}.jpg", quality=80)
        sys.exit()
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", S + "/base.mp4", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                            "-i", S + "/base.mp4", "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                            "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-c:a", "copy", "-shortest", S + "/final.mp4"], stdin=subprocess.PIPE)
    n = 0
    sz = W * H * 3
    while True:
        buf = dec.stdout.read(sz)
        if len(buf) < sz:
            break
        enc.stdin.write(render(n / FPS, Image.frombytes("RGB", (W, H), buf)).tobytes())
        n += 1
        if n % 150 == 0:
            print("frame", n, flush=True)
    enc.stdin.close()
    enc.wait()
    print("done", n)
