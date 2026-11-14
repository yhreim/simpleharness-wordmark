from pathlib import Path
import math
import random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# 所有圆点先落在同一网格上，再统一做倾斜变换。
OUT = Path(__file__).parent
W, H = 1800, 900
STEP, RADIUS = 9, 3.55
BG = (5, 9, 22)
COLORS = [(255, 255, 255), (196, 235, 255), (255, 215, 241)]
rng = random.Random(47)
mask = Image.new('L', (W, H))
font = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 224)
d = ImageDraw.Draw(mask)
text = 'SimpleHarness'
box = d.textbbox((0, 0), text, font=font)
x = (W - (box[2] - box[0])) / 2
# 字形仅用于决定晶格点的亮度，不直接画进成品。
d.text((x, 330 - box[1]), text, font=font, fill=255, stroke_width=3)
halo = mask.filter(ImageFilter.GaussianBlur(36))
wide = mask.filter(ImageFilter.GaussianBlur(83))
points = []
for y in range(150, 711, STEP):
    for x in range(16, W - 16, STEP):
        inside = mask.getpixel((x, y)) > 120
        near = halo.getpixel((x, y)) / 255
        far = wide.getpixel((x, y)) / 255
        if inside:
            # 三种主体色形成缓慢变化的色块，保留少量暗位。
            field = math.sin(x / 125 + y / 93) + .55 * math.cos(x / 73 - y / 116)
            color = COLORS[0 if field > .25 else 1 if field > -1.15 else 2]
            if rng.random() < .015:
                color = (31, 49, 103)
        else:
            if rng.random() > min(.94, far * 3.1):
                continue
            if rng.random() < near * .15:
                color = COLORS[rng.randrange(3)]
            else:
                strength = min(1, near * 1.5 + far * .6)
                color = (int(14 + 13 * strength), int(22 + 29 * strength), int(52 + 86 * strength))
        # 同一个仿射变换保证点阵行列始终笔直、平行。
        px = x + .11 * (y - H / 2)
        py = H / 2 + .93 * (y - H / 2) - .065 * (x - W / 2)
        points.append((px, py, color))

# SVG 保留真正的矢量圆点，PNG 用超采样输出平滑边缘。
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', '<title>SimpleHarness — strict lattice wordmark</title>', f'<rect width="100%" height="100%" fill="rgb{BG}"/>']
image = Image.new('RGB', (W * 2, H * 2), BG)
canvas = ImageDraw.Draw(image)
for x, y, color in points:
    svg.append(f'<ellipse cx="{x:.2f}" cy="{y:.2f}" rx="{RADIUS}" ry="{RADIUS*.93:.2f}" fill="rgb{color}"/>')
    canvas.ellipse(((x-RADIUS)*2, (y-RADIUS*.93)*2, (x+RADIUS)*2, (y+RADIUS*.93)*2), fill=color)
svg.append('</svg>')
(OUT / 'wordmark-code-v4.svg').write_text('\n'.join(svg), encoding='utf-8')
image.resize((W,H), Image.Resampling.LANCZOS).save(OUT / 'wordmark-code-v4.png')
print(f'{len(points)} lattice sites rendered.')



