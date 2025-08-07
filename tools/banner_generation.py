from PIL import Image, ImageDraw, ImageFont
from PIL import ImageOps
import random

# ascii art provided by user, no trailing unnecessary spaces, raw string to preserve backslashes
ascii_art = r"""
      ___       ___           ___           ___           ___     
     /\__\     /\  \         /\  \         /\__\         /\  \    
    /:/  /    /::\  \       /::\  \       /::|  |       /::\  \   
   /:/  /    /:/\:\  \     /:/\:\  \     /:|:|  |      /:/\:\  \  
  /:/  /    /:/  \:\  \   /::\~\:\  \   /:/|:|  |__   /::\~\:\  \ 
 /:/__/    /:/__/ \:\__\ /:/\:\ \:\__\ /:/ |:| /\__\ /:/\:\ \:\__\
 \:\  \    \:\  \ /:/  / \/_|::\/:/  / \/__|:|/:/  / \:\~\:\ \/__/
  \:\  \    \:\  /:/  /     |:|::/  /      |:/:/  /   \:\ \:\__\  
   \:\  \    \:\/:/  /      |:|\/__/       |::/  /     \:\ \/__/  
    \:\__\    \::/  /       |:|  |         /:/  /       \:\__\    
     \/__/     \/__/         \|__|         \/__/         \/__/    
""".strip("\n")

# new dimensions
WIDTH, HEIGHT = 3000, 1000

img = Image.new('RGBA', (WIDTH, HEIGHT), color=(5,5,20,255))
draw = ImageDraw.Draw(img)
font_path = "/Library/Fonts/Menlo.ttc"

# choose maximum font size that fits within 90% width and 80% height
max_width = WIDTH * 0.9
max_height = HEIGHT * 0.8
selected_size = None

# start from high size; maximum maybe 100; we try from 200 down to 10
for size in range(200, 5, -1):
    font = ImageFont.truetype(font_path, size)
    bbox = draw.multiline_textbbox((0,0), ascii_art, font=font, spacing=0)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    if w <= max_width and h <= max_height:
        selected_size = size
        break
if selected_size is None:
    selected_size = 20
font = ImageFont.truetype(font_path, selected_size)

# compute bounding box for ascii art at selected size
bbox = draw.multiline_textbbox((0,0), ascii_art, font=font, spacing=0)
w = bbox[2] - bbox[0]
h = bbox[3] - bbox[1]
x_text = (WIDTH - w)//2
y_text = (HEIGHT - h)//2

# generate starry background; more stars for larger canvas
num_stars = int(WIDTH * HEIGHT * 0.00030)  # density based on area, 0.00015 for not too dense
for _ in range(num_stars):
    x = random.randint(0, WIDTH-1)
    y = random.randint(0, HEIGHT-1)
    brightness = random.randint(180,255)
    img.putpixel((x,y),(brightness,brightness,brightness))

# draw ascii art with slight shadow
shadow_offset = selected_size//20 + 2  # dynamic offset relative to font size
shadow_color = (80,80,100)
text_color = (240,240,255)

# draw shadow and text
# customizing line spacing: we used spacing=0 to maintain closeness

# draw shadow
shadow_pos = (x_text + shadow_offset, y_text + shadow_offset)
draw.multiline_text(shadow_pos, ascii_art, font=font, fill=shadow_color, spacing=0)
# draw main text
text_pos = (x_text, y_text)
draw.multiline_text(text_pos, ascii_art, font=font, fill=text_color, spacing=0)

# draw ascii star characters around central art
star_char = "*"
star_font_size = max( int(selected_size * 0.8), 18)  # star char size relative to ascii art size; min 18
star_font = ImageFont.truetype(font_path, star_font_size)

# bounding box for ascii art within canvas
bbox_abs = (x_text + 2, y_text + 3, x_text + w, y_text + h)
x0, y0, x1, y1 = bbox_abs

# define positions around ascii art (eight directions) with dynamic padding
pad = selected_size  # use font size as pad
positions = [
    (x0 - pad - star_font_size, y0 - pad - star_font_size),
    (x1 + pad, y0 - pad - star_font_size),
    (x0 - pad - star_font_size, y1 + pad),
    (x1 + pad, y1 + pad),
    ((x0 + x1)//2 - star_font_size//2, y0 - pad - star_font_size),
    ((x0 + x1)//2 - star_font_size//2, y1 + pad),
    (x0 - pad - star_font_size, (y0 + y1)//2 - star_font_size//2),
    (x1 + pad, (y0 + y1)//2 - star_font_size//2)
]

# clamp positions to within canvas
clamped_positions = []
for px, py in positions:
    px = max(0, min(WIDTH - star_font_size, px))
    py = max(0, min(HEIGHT - star_font_size, py))
    clamped_positions.append((px, py))

star_color = (255,215,0)
for pos in clamped_positions:
    draw.text(pos, star_char, font=star_font, fill=star_color)

# save
output_path = './assets/banner_1000x3000-rounded.png'
# round the corners of the image
radius = 30  # corner radius in pixels
mask = Image.new('L', img.size, 0)
mask_draw = ImageDraw.Draw(mask)
mask_draw.rounded_rectangle([(0, 0), img.size], radius=radius, fill=255)
img = ImageOps.fit(img, img.size, centering=(0.5, 0.5))
img.putalpha(mask)
img.save(output_path)
print('selected font size', selected_size, 'bounding box', w,h)
print(output_path)