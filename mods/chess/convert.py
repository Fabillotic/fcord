from PIL import Image
from PIL.ImageDraw import Draw
from svglib.svglib import svg2rlg as svg
from reportlab.graphics.renderPM import drawToFile as render
import os
from fcord import relative as rel

def start():
    print("Converting images...")
    pieces = ["images/chess-bishop.svg", "images/chess-king.svg", "images/chess-knight.svg", "images/chess-pawn.svg", "images/chess-queen.svg", "images/chess-rook.svg"]
    _p = []

    for p in pieces:
        _p.append(rel("mods/chess/" + p))

    pieces = _p

    for p in pieces:
        s = svg(p)
        b = p[:p.rfind(".")]
        f = b + ".png"
        render(s, f, fmt="PNG", bg=0x00ff00)
        i = Image.open(f)
        i = i.convert("RGBA")
        l = i.load()
        d = Draw(i)
        
        h = []
        
        for y in range(i.size[1]):
            for x in range(i.size[0]):
                if l[x, y][1] > 10:
                    l[x, y] = (0, 0, 0, 0)
                else:
                    h.append((x, y))
        
        darken = lambda c, a: tuple([min(max(x - a, 0), 255) for x in c])
        
        cs = [(darken((53, 46, 36, 255), -40), "black"), (darken((231, 201, 137, 255), -40), "white")]
        for x in range(len(cs)):
            c = cs[x]
            border = []
            for n in h:
                l[n[0], n[1]] = c[0]
            ni = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
            ri = i.resize((i.size[0] * 3 // 4, i.size[1] * 3 // 4), Image.NEAREST)
            pp = ((512 - ri.size[0]) // 2, (512 - ri.size[1]) // 2)
            ni.paste(ri, pp, ri)
            o = b + "_" + c[1] + ".png"
            ni.save(o)
            print("Converted file '" + o + "'!")

        os.remove(f)

if __name__ == "__main__":
    print("CONVERTING FROM MAIN!")
    start()
