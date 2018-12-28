from math import *
from PIL import Image, ImageDraw


def readData(f):
    lines = f.readlines()

    (W, H) = lines[0].split()
    W = int(W)
    H = int(W)

    HISTOGRAM = []

    for l in lines[1:H + 1]:
        s = l.split()
        s = [int(v) / 10.0 for v in s]
        HISTOGRAM += [s]

    return W, H, HISTOGRAM


def mw2d_draw_histogram(filename, threshold=None):
    f = open(filename, "r")
    (W, H, HISTOGRAM) = readData(f)

    TRADITIONAL = False
    try:
        threshold = float(threshold)
    except:
        TRADITIONAL = True

    im = Image.new("RGB", (W, H), "white")
    dr = ImageDraw.Draw(im)

    TOTAL = 0
    MAX = 0
    for y in range(H):
        for x in range(W):
            TOTAL += HISTOGRAM[y][x]
            if HISTOGRAM[y][x] > MAX:
                MAX = HISTOGRAM[y][x]

    print "DRAWING, TOTAL = %d" % TOTAL

    dr.line((0, H / 2, W, H / 2), fill=128)
    dr.line((W / 2, 0, W / 2, H), fill=128)

    if TRADITIONAL:
        print "LOCAL NORMALIZATION"
        for y in range(H):
            for x in range(W):
                if HISTOGRAM[y][x] > 0:
                    inte = 255 - int(255 * (float(HISTOGRAM[y][x]) / MAX))
                    dr.point((x, (H - 1) - y), fill="rgb(255,%d,%d)" % (inte, inte))
    else:
        MAX_VAL = 0.0
        print "GLOBAL NORMALIZATION"
        for y in range(H):
            for x in range(W):
                if HISTOGRAM[y][x] > 0:
                    inte = float(HISTOGRAM[y][x]) / TOTAL
                    val = float(inte) / threshold
                    MAX_VAL = max(val, MAX_VAL)
                    val = (atan(val)) / (pi / 2)
                    val = 255 - int(val * 255)
                    dr.point((x, (H - 1) - y), fill="rgb(%d,%d,%d)" % (val, val, val))
        print "MAX_VAL = ", MAX_VAL

    im.save(filename.replace(".", "_") + ".png")
