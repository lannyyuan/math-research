"""把多张静帧拼成一张联络表，方便一次看完。  python3 -I scripts/contact.py out.png cols w a.png b.png ..."""
import sys
from PIL import Image, ImageDraw
out, cols, w = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
files = sys.argv[4:]
ims = [Image.open(f).convert("RGB") for f in files]
h = int(w * ims[0].height / ims[0].width)
rows = (len(ims) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w, rows * h), (0, 0, 0))
d = ImageDraw.Draw(sheet)
for i, im in enumerate(ims):
    x, y = (i % cols) * w, (i // cols) * h
    sheet.paste(im.resize((w, h), Image.LANCZOS), (x, y))
    d.text((x + 6, y + 4), files[i].split("/")[-1].replace(".png", ""), fill=(255, 255, 0))
sheet.save(out)
