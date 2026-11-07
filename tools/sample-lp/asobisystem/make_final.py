# アソビシステム様 採用LP（制作サンプル）の素材づくり Step 3（手順の全体は docs/specs/SAMPLE-LP.md §4）
# Real-ESRGAN で4倍にした素材（work/up4/）を仕上げて PNG を書き出す（ロゴ透過・動画サムネイル合成・リサイズ）
# 実行: make_clean.py と同じ作業フォルダで
#       python3 <リポ>/tools/sample-lp/asobisystem/make_final.py <動画から切り出したフレームPNG>   → work/final/*.png
#       その後 cwebp で sample/asobisystem/img/ へ（SAMPLE-LP.md §4）
import cv2, numpy as np, os, sys

U = 'work/up4'
OUT = 'work/final'
os.makedirs(OUT, exist_ok=True)


def resize_w(img, w):
    h = round(img.shape[0] * w / img.shape[1])
    return cv2.resize(img, (w, h), interpolation=cv2.INTER_AREA)


def out(name, img):
    cv2.imwrite(f'{OUT}/{name}.png', img)
    print(name, img.shape[1], 'x', img.shape[0])


# ---- 写真・イラスト（幅は表示の最大幅の約2倍） ----
SIZES = {
    'hero': [1920, 960],
    'band1': [1920, 960], 'band2': [1920, 960], 'band4': [1920, 960],
    'cta': [1920, 960],
    'story-1': [1600, 800], 'story-2': [840], 'story-3': [840],
    'job-1': [760], 'job-2': [760], 'job-3': [760], 'job-4': [760],
    'flow-banner': [1720, 860],
}
for name, widths in SIZES.items():
    img = cv2.imread(f'{U}/{name}.png')
    for i, w in enumerate(widths):
        out(name if i == 0 else f'{name}-{w}', resize_w(img, w))

# ---- ロゴ: 白地 → 透過（紺とピンクの2色。各画素を「白と文字色の混ざり」とみなして不透明度を出す） ----
logo = cv2.imread(f'{U}/logo.png').astype(np.float32)
hsv = cv2.cvtColor(logo.astype(np.uint8), cv2.COLOR_BGR2HSV)
g = cv2.cvtColor(logo.astype(np.uint8), cv2.COLOR_BGR2GRAY)
is_pink = (hsv[..., 1] > 60) & (logo[..., 2] > logo[..., 0] + 25)
navy = np.median(logo[(g < 70) & ~is_pink], axis=0)
pink = np.median(logo[is_pink & (hsv[..., 1] > 150)], axis=0)
print('navy', navy, 'pink', pink)
T = np.where(is_pink[..., None], pink, navy)
a = np.max((255 - logo) / np.maximum(255 - T, 1), axis=2)
a = np.clip(a, 0, 1)
a[a < .04] = 0
rgba = np.dstack([T, a * 255]).astype(np.uint8)
ys, xs = np.nonzero(a > .05)
rgba = rgba[max(ys.min() - 4, 0):ys.max() + 5, max(xs.min() - 4, 0):xs.max() + 5]
rgba = cv2.resize(rgba, (round(rgba.shape[1] * 600 / rgba.shape[1]), round(rgba.shape[0] * 600 / rgba.shape[1])), interpolation=cv2.INTER_AREA)
out('logo', rgba)

# ---- 動画サムネイル: 本編のフレーム ＋ LP案の手書き文字（白）を背景から抜いて合成 ----
lt = cv2.imread(f'{U}/movie-letter.png')
lg = cv2.cvtColor(lt, cv2.COLOR_BGR2GRAY).astype(np.float32)
ls = cv2.cvtColor(lt, cv2.COLOR_BGR2HSV)[..., 1]
txt = ((lg > 185) & (ls < 70)).astype(np.uint8) * 255
txt[220:, :140] = 0                                  # 左下に写り込んだ人物の顔を除く
txt = cv2.morphologyEx(txt, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
n, lab, st, _ = cv2.connectedComponentsWithStats(txt)
keep = np.zeros_like(txt)
for i in range(1, n):
    cy = st[i, 1] + st[i, 3] / 2
    if st[i, 4] < 60 or (st[i, 4] < 1500 and cy > 380):   # 光の粒は捨てる（句読点は残す）
        continue
    keep[lab == i] = 255
mask = cv2.dilate(keep, np.ones((9, 9), np.uint8))
bg = cv2.inpaint(lt, mask, 9, cv2.INPAINT_TELEA)
bgl = cv2.cvtColor(bg, cv2.COLOR_BGR2GRAY).astype(np.float32)
alpha = np.clip((lg - bgl) / np.maximum(255 - bgl, 1), 0, 1) * (mask > 0)
alpha = cv2.GaussianBlur(alpha, (0, 0), .6)
ys, xs = np.nonzero(alpha > .05)
alpha = alpha[ys.min():ys.max() + 1, xs.min():xs.max() + 1]
cv2.imwrite('work/movie-letter-alpha.png', (alpha * 255).astype(np.uint8))

frame = cv2.imread(sys.argv[1])
poster = cv2.resize(frame, (1280, 720), interpolation=cv2.INTER_AREA)
lw = int(1280 * .27)
la = cv2.resize(alpha, (lw, round(alpha.shape[0] * lw / alpha.shape[1])), interpolation=cv2.INTER_AREA)
x0, y0 = int(1280 * .715), int(720 * .07)
# 読みやすさのため文字の周りだけほんのり暗くする
canvas = np.zeros((720, 1280), np.float32)
canvas[y0:y0 + la.shape[0], x0:x0 + lw] = la
shade = cv2.GaussianBlur(cv2.dilate(canvas, np.ones((15, 15), np.uint8)), (0, 0), 16) * .3
pf = poster.astype(np.float32) * (1 - shade[..., None])
pf = pf * (1 - canvas[..., None]) + 255 * canvas[..., None]
poster = pf.astype(np.uint8)
out('movie-poster', poster)
