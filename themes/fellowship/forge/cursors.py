#!/usr/bin/env python3
"""Build an XCursor theme from a folder of Windows .ani / .cur cursors.

    python3 cursors.py <src-dir> <out-theme-dir> [--name NAME] [--inherits THEME]

Windows ships cursors as RIFF/ACON containers wrapping ICO-style bitmaps;
Wayland wants XCursor, which is a different binary format entirely. Rather
than take a dependency on win2xcur or xcursorgen, both are implemented here --
each is about fifty lines and the whole thing then rides on Pillow, which the
rest of the forge already needs.

Two details are easy to get wrong and worth naming:

* **The AND mask is the transparency.** Under 32bpp a .cur stores a colour
  bitmap stacked over a 1-bit mask, and a set mask bit means "leave the screen
  alone". Pillow's own CUR reader hands back a fully opaque image, so the mask
  is applied here by hand.
* **XCursor pixels are premultiplied.** The X Render ARGB32 convention, which
  wlroots and Hyprland follow. It only shows at soft edges -- which is exactly
  what rescaling these to other sizes creates.
"""
import os, struct, sys
from PIL import Image

# ------------------------------------------------------------------ decode --

def _riff_chunks(d, off, end):
    while off < end - 8:
        cid = d[off:off + 4]
        sz = struct.unpack('<I', d[off + 4:off + 8])[0]
        if cid == b'LIST':
            yield d[off + 8:off + 12], off + 12, off + 8 + sz
            off += 12
        else:
            yield cid, off + 8, off + 8 + sz
            off += 8 + sz + (sz & 1)


def _first_frame(path):
    """The first icon out of an .ani, or the whole file if it is a .cur."""
    d = open(path, 'rb').read()
    if d[:4] != b'RIFF':
        return d
    for cid, s, e in _riff_chunks(d, 12, len(d)):
        if cid == b'fram':
            for c2, s2, e2 in _riff_chunks(d, s, e):
                if c2 == b'icon':
                    return d[s2:e2]
    raise ValueError('no icon chunk in %s' % path)


def decode(path):
    """-> (RGBA image, (xhot, yhot))"""
    cur = _first_frame(path)
    _, _, _ = struct.unpack('<HHH', cur[:6])
    w, h, cc, _r, xh, yh, nbytes, off = struct.unpack('<BBBBHHII', cur[6:22])

    if cur[off:off + 8] == b'\x89PNG\r\n\x1a\n':          # Vista-era PNG icons
        import io
        return Image.open(io.BytesIO(cur[off:off + nbytes])).convert('RGBA'), (xh, yh)

    hsize, bw, bh, _planes, bpp, _comp = struct.unpack('<IiiHHI', cur[off:off + 20])
    W, H = bw, abs(bh) // 2          # the DIB stacks the colour bitmap over the mask
    p = off + hsize

    palette = []
    if bpp <= 8:
        for i in range(cc if cc else 1 << bpp):
            b, g, r, _ = cur[p + i * 4:p + i * 4 + 4]
            palette.append((r, g, b))
        p += len(palette) * 4

    stride = lambda bits: ((W * bits + 31) // 32) * 4
    xs, as_ = stride(bpp), stride(1)
    xor = cur[p:p + xs * H]
    mask = cur[p + xs * H:p + xs * H + as_ * H]

    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    px = img.load()
    for y in range(H):
        sy = H - 1 - y                                    # DIB rows run bottom-up
        row = xor[sy * xs:(sy + 1) * xs]
        mrow = mask[sy * as_:(sy + 1) * as_] if mask else b''
        for x in range(W):
            if bpp == 32:
                b, g, r, a = row[x * 4:x * 4 + 4]
                col = (r, g, b, a)
            elif bpp == 24:
                b, g, r = row[x * 3:x * 3 + 3]
                col = (r, g, b, 255)
            elif bpp == 8:
                col = palette[row[x]] + (255,)
            elif bpp == 4:
                v = row[x // 2]
                col = palette[v >> 4 if x % 2 == 0 else v & 0xF] + (255,)
            elif bpp == 1:
                col = palette[(row[x // 8] >> (7 - x % 8)) & 1] + (255,)
            else:
                raise ValueError('unsupported %dbpp in %s' % (bpp, path))
            if mrow and bpp != 32 and (mrow[x // 8] >> (7 - x % 8)) & 1:
                col = (0, 0, 0, 0)
            px[x, y] = col
    return img, (xh, yh)


# ------------------------------------------------------------------ encode --
MAGIC = b'Xcur'
FILE_HEADER_LEN = 16
FILE_VERSION = 0x00010000
CHUNK_IMAGE = 0xFFFD0002
IMAGE_HEADER_LEN = 36
IMAGE_VERSION = 1


def _encode(images):
    """images: [(nominal, w, h, xhot, yhot, delay_ms, RGBA bytes)] -> XCursor file"""
    ntoc = len(images)
    pos = FILE_HEADER_LEN + 12 * ntoc
    toc, chunks = b'', b''
    for nominal, w, h, xh, yh, delay, rgba in images:
        toc += struct.pack('<III', CHUNK_IMAGE, nominal, pos)
        body = struct.pack('<9I', IMAGE_HEADER_LEN, CHUNK_IMAGE, nominal,
                           IMAGE_VERSION, w, h, xh, yh, delay)
        out = bytearray(w * h * 4)
        for i in range(w * h):
            r, g, b, a = rgba[i * 4:i * 4 + 4]
            # premultiply, then store as a little-endian ARGB word => B,G,R,A
            out[i * 4 + 0] = b * a // 255
            out[i * 4 + 1] = g * a // 255
            out[i * 4 + 2] = r * a // 255
            out[i * 4 + 3] = a
        body += bytes(out)
        chunks += body
        pos += len(body)
    return MAGIC + struct.pack('<III', FILE_HEADER_LEN, FILE_VERSION, ntoc) + toc + chunks


def build_cursor(img, hot, sizes):
    """Render one decoded cursor at every nominal size."""
    images = []
    for n in sizes:
        scale = n / max(img.width, img.height)
        w, h = max(1, round(img.width * scale)), max(1, round(img.height * scale))
        # These are 2006 pixel art. Downscaling wants a smooth filter; upscaling
        # looks far better kept crisp than interpolated into mush.
        f = Image.LANCZOS if scale < 1 else Image.NEAREST
        im = img.resize((w, h), f)
        images.append((n, w, h, round(hot[0] * scale), round(hot[1] * scale), 0,
                       im.tobytes()))
    return _encode(images)


# ------------------------------------------------------------------- roles --
# source file (without .ani) -> the X cursor names it should answer to.
# The first name is the file; the rest become symlinks beside it.
#
# The pack has no I-beam, no resize cursors, no crosshair and no move cursor,
# so those are left undefined and come from the inherited theme instead.
ROLES = [
    ("Normal Select", [
        "default", "left_ptr", "arrow", "top_left_arrow", "top_left_corner"]),
    ("Link Select", [
        "pointer", "hand", "hand1", "hand2", "pointing_hand",
        "e29285e634086352946a0e7090d73106", "9d800788f1b08800ae810202380a0822"]),
    ("Busy", [
        "wait", "watch", "0426c94ea35c87780ff01dc239897213"]),
    ("Working in Background", [
        "progress", "left_ptr_watch", "half-busy",
        "00000000000000020006000e7e9ffc3f", "08e8e1c95fe2fc01f976f1e063a24ccd",
        "3ecb610c1bf2410f44200f48c40d3599"]),
    ("Help Select", [
        "help", "question_arrow", "whats_this", "left_ptr_help", "dnd-ask",
        "d9ce0ab605698f320427677b458ad60b", "5c6cd98b3f3ebcb1f9c7f1c204630408"]),
    ("Unavailable", [
        "not-allowed", "crossed_circle", "forbidden", "no-drop", "dnd-none",
        "03b6e0fcb3499374a867c041f52298f0"]),
    ("Handwriting", ["pencil", "draft", "draft_large", "draft_small"]),
    # A gryphon for "move things about" is a liberty, but move/all-scroll is a
    # cursor you actually see in Hyprland, and the alternative is Yaru's.
    ("flight path", ["all-scroll", "fleur", "move", "size_all", "grabbing",
                     "closedhand", "dnd-move"]),
    # The rest have no X role. They ship under their own names so they are
    # there to be wired up, and bind to nothing by default.
    ("loot", ["wow-loot"]),
    ("mail", ["wow-mail"]),
    ("skinning", ["wow-skinning"]),
    ("Male Nightelf", ["wow-male-nightelf"]),
    ("Female Nightelf", ["wow-female-nightelf"]),
    ("Male Ogre", ["wow-male-ogre"]),
]

SIZES = (24, 32, 48, 64)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    opts = dict(zip([a for a in sys.argv[1:] if a.startswith('--')],
                    [sys.argv[i + 1] for i, a in enumerate(sys.argv[1:], 1)
                     if a.startswith('--')]))
    if len(args) < 2:
        sys.exit(__doc__.strip())
    src, out = args[0], args[1]
    name = opts.get('--name', os.path.basename(out.rstrip('/')))
    inherits = opts.get('--inherits', 'Yaru')

    cdir = os.path.join(out, 'cursors')
    os.makedirs(cdir, exist_ok=True)
    for f in os.listdir(cdir):
        os.remove(os.path.join(cdir, f))

    made, missing = 0, []
    for stem, names in ROLES:
        path = os.path.join(src, stem + '.ani')
        if not os.path.exists(path):
            path = os.path.join(src, stem + '.cur')
        if not os.path.exists(path):
            missing.append(stem)
            continue
        img, hot = decode(path)
        primary = names[0]
        with open(os.path.join(cdir, primary), 'wb') as fh:
            fh.write(build_cursor(img, hot, SIZES))
        for alias in names[1:]:
            link = os.path.join(cdir, alias)
            if os.path.lexists(link):
                os.remove(link)
            os.symlink(primary, link)
        made += 1
        print('  %-22s -> %-14s %s at %s' % (stem, primary, img.size,
                                             ','.join(map(str, SIZES))))

    with open(os.path.join(out, 'index.theme'), 'w') as fh:
        fh.write('[Icon Theme]\nName=%s\nInherits=%s\n' % (name, inherits))
    with open(os.path.join(out, 'cursor.theme'), 'w') as fh:
        fh.write('[Icon Theme]\nInherits=%s\n' % name)

    if missing:
        print('  not found in %s: %s' % (src, ', '.join(missing)))
    print('  %d cursors, %d names, inheriting %s' %
          (made, len(os.listdir(cdir)), inherits))


if __name__ == '__main__':
    main()
