# アソビシステム様 採用LP（制作サンプル）の素材づくり Step 1（手順の全体は docs/specs/SAMPLE-LP.md §4）
# LP案（941px幅のPNG×5枚）から各素材を切り出し、HTMLで置き換える文字・ボタンを消した 1x 画像を作る。
# 座標はこの客先のLP案専用。次の客先はこのファイルを複製して座標を測り直す（関数はそのまま使える）
# 実行: 作業フォルダ（リポの外）に src/lp1.png〜lp5.png を置き、そこで
#       python3 <リポ>/tools/sample-lp/asobisystem/make_clean.py   → work/clean/*.png
# 必要: OpenCV（contrib の xphoto を含むもの）
import cv2, numpy as np, os

os.makedirs('work/clean', exist_ok=True)
L = {n: cv2.imread(f'src/lp{n}.png') for n in range(1, 6)}


def save(name, img):
    cv2.imwrite(f'work/clean/{name}.png', img)


def pill(m, x0, y0, x1, y1, pad):
    x0 -= pad; y0 -= pad; x1 += pad; y1 += pad
    r = (y1 - y0) // 2
    cv2.rectangle(m, (x0 + r, y0), (x1 - r, y1), 255, -1)
    cv2.circle(m, (x0 + r, y0 + r), r, 255, -1)
    cv2.circle(m, (x1 - r, y0 + r), r, 255, -1)


def strokes(img, box, mode, dil=5):
    """box 内の文字の線だけをマスクにする。mode='light' は明るい文字、'dark' は暗い文字"""
    x0, y0, x1, y1 = box
    m = np.zeros(img.shape[:2], np.uint8)
    sub = img[y0:y1, x0:x1]
    g = cv2.cvtColor(sub, cv2.COLOR_BGR2GRAY).astype(int)
    s = cv2.cvtColor(sub, cv2.COLOR_BGR2HSV)[..., 1]
    if mode == 'light':
        hit = (g > 170) & (s < 90)
    else:
        bg = cv2.medianBlur(g.astype(np.uint8), 31).astype(int)
        hit = g < bg - 22
    m[y0:y1, x0:x1] = hit.astype(np.uint8) * 255
    return cv2.dilate(m, np.ones((dil, dil), np.uint8))


def inpaint(img, mask, roi=None, smooth_chroma=True):
    """FSR_BEST で穴埋め。roi で処理範囲を絞る（速度のため）。穴埋め部の色ムラは色差だけぼかして周囲に馴染ませる"""
    out = img.copy()
    x0, y0, x1, y1 = roi or (0, 0, img.shape[1], img.shape[0])
    sub = img[y0:y1, x0:x1].copy()
    msub = mask[y0:y1, x0:x1]
    valid = (msub == 0).astype(np.uint8) * 255
    res = np.zeros_like(sub)
    cv2.xphoto.inpaint(sub, valid, res, cv2.xphoto.INPAINT_FSR_BEST)
    if smooth_chroma:
        lab = cv2.cvtColor(res, cv2.COLOR_BGR2Lab).astype(np.float32)
        blur = cv2.GaussianBlur(lab, (0, 0), 14)
        w = cv2.GaussianBlur((msub > 0).astype(np.float32), (0, 0), 4)[..., None]
        lab[..., 1:] = lab[..., 1:] * (1 - w) + blur[..., 1:] * w
        # 明るさも少しだけぼかす（周囲のボケ味に合わせる）
        lab[..., :1] = lab[..., :1] * (1 - w * .5) + blur[..., :1] * (w * .5)
        res = cv2.cvtColor(np.clip(lab, 0, 255).astype(np.uint8), cv2.COLOR_Lab2BGR)
    out[y0:y1, x0:x1] = res
    return out


# ---- ヘッダーのロゴ（白地のまま。透過は後工程） ----
save('logo', L[1][20:64, 34:380])

# ---- ヒーロー: 右側の説明文とボタン2つを消す（手書きのキャッチと左下のメモは絵として残す） ----
hero = L[1][81:845].copy()          # hero 座標 = lp1 座標 - 81
m = strokes(hero, (562, 359, 890, 499), 'light')
pill(m, 535, 523, 899, 596, 7)
pill(m, 535, 609, 899, 682, 7)
hero = inpaint(hero, m, roi=(470, 300, hero.shape[1], hero.shape[0]))
save('hero', hero)

# ---- 区切りの帯（手書きの一言は絵として残す） ----
save('band1', L[1][1531:1672])
save('band2', L[2][1541:1672])
b4 = L[4][1531:1672].copy()         # band4 座標 = lp4 座標 - 1531
m = strokes(b4, (640, 40, 925, 95), 'dark', dil=5)
b4 = inpaint(b4, m, roi=(560, 0, b4.shape[1], b4.shape[0]))
save('band4', b4)

# ---- 最後のCTA: 説明文・ボタン2つ・右下の一言を消す（手書きのキャッチと女性は残す） ----
cta = L[5][1323:1622].copy()        # cta 座標 = lp5 座標 - 1323
m = strokes(cta, (80, 140, 322, 240), 'dark', dil=5)
m |= strokes(cta, (655, 182, 860, 232), 'dark', dil=5)
pill(m, 621, 60, 887, 114, 7)
pill(m, 621, 119, 887, 174, 7)
cta = inpaint(cta, m, roi=(40, 30, cta.shape[1], cta.shape[0]))
save('cta', cta)

# ---- 物語のコマ・仕事内容の写真・流れのバナー（枠線と角丸は CSS で付け直すので内側を切り出す） ----
save('story-1', L[3][244:514, 58:885])
save('story-2', L[3][530:727, 59:479])
save('story-3', L[3][530:727, 495:884])
save('job-1', L[3][1004:1140, 68:450])
save('job-2', L[3][1005:1140, 493:875])
save('job-3', L[3][1307:1442, 68:450])
save('job-4', L[3][1307:1442, 493:875])
save('flow-banner', L[4][460:666, 40:902])

# ---- 動画サムネイルの手書き文字（後工程で背景から文字だけを抜く） ----
save('movie-letter', L[2][305:420, 636:886])
print('done')
