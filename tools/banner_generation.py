from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from PIL import ImageOps
import random

# ascii art provided by user, no trailing unnecessary spaces, raw string to preserve backslashes
ascii_art = r"""
      ___       ___           ___           ___           ___     
     /\__\     /\  \         /\  \         /\__\         /\  \    
    /:/  /    /::\  \       /::\  \       /::| |        /::\  \   
   /:/  /    /:/\:\  \     /:/\:\  \     /:|:| |       /:/\:\  \  
  /:/  /    /:/  \:\  \   /::\~\:\  \   /:/|:| | __   /::\~\:\  \ 
 /:/__/    /:/__/ \:\__\ /:/\:\ \:\__\ /:/ |:| /\__\ /:/\:\ \:\__\
 \:\  \    \:\  \ /:/  / \/_|::\/:/  / \/__|:|/:/  / \:\~\:\ \/__/
  \:\  \    \:\  /:/  /     |:|::/  /      |:/:/  /   \:\ \:\__\  
   \:\  \    \:\/:/  /      |:|\/__/       |::/  /     \:\ \/__/  
    \:\__\    \::/  /       |:|  |         /:/  /       \:\__\    
     \/__/     \/__/         \|__|         \/__/         \/__/    
""".strip("\n")

# font discovery
FONT_CANDIDATES = [
    "/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Monaco.ttf",
    str(Path.home() / "Library/Fonts/Menlo.ttc"),
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    "/usr/share/fonts/truetype/ubuntu/UbuntuMono-R.ttf",
    "/usr/share/fonts/truetype/freefont/FreeMono.ttf",
    "C:/Windows/Fonts/consola.ttf",
    "C:/Windows/Fonts/Courier New.ttf",
]
FONT_SEARCH_DIRS = [
    Path("/usr/share/fonts"),
    Path("/usr/local/share/fonts"),
    Path.home() / ".fonts",
    Path.home() / ".local/share/fonts",
]
FONT_PATTERNS = ("*Menlo*.ttc", "*Monaco*.ttf", "*Mono*.ttf", "*Mono*.otf")


def resolve_font_path():
    for candidate in FONT_CANDIDATES:
        path = Path(candidate).expanduser()
        if path.exists():
            try:
                ImageFont.truetype(str(path), 20)
                return str(path)
            except OSError:
                continue
    for directory in FONT_SEARCH_DIRS:
        if not directory.exists():
            continue
        for pattern in FONT_PATTERNS:
            for font_file in directory.rglob(pattern):
                try:
                    ImageFont.truetype(str(font_file), 20)
                    return str(font_file)
                except OSError:
                    continue
    return None


RESOLVED_FONT_PATH = resolve_font_path()
if RESOLVED_FONT_PATH is None:
    raise RuntimeError(
        "Unable to locate a monospaced TrueType font. Install one (e.g., DejaVu Sans Mono) "
        "or update FONT_CANDIDATES with an available path."
    )


def load_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(RESOLVED_FONT_PATH, size)


# new dimensions
WIDTH, HEIGHT = 3000, 1000

img = Image.new('RGBA', (WIDTH, HEIGHT), color=(5,5,20,255))
draw = ImageDraw.Draw(img)

# choose maximum font size that fits within 90% width and 80% height
max_width = WIDTH * 0.9
max_height = HEIGHT * 0.8
selected_size = None

# start from high size; maximum maybe 100; we try from 200 down to 10
for size in range(200, 5, -1):
    font = load_font(size)
    bbox = draw.multiline_textbbox((0,0), ascii_art, font=font, spacing=0)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    if w <= max_width and h <= max_height:
        selected_size = size
        break
if selected_size is None:
    selected_size = 20
font = load_font(selected_size)

# compute bounding box for ascii art at selected size
bbox = draw.multiline_textbbox((0,0), ascii_art, font=font, spacing=0)
w = bbox[2] - bbox[0]
h = bbox[3] - bbox[1]
x_text = (WIDTH - w)//2
y_text = (HEIGHT - h)//2

# generate starry background with varied speck sizes
num_stars = int(WIDTH * HEIGHT * 0.00030)  # density based on area, 0.00015 for not too dense
for _ in range(num_stars):
    x = random.randint(0, WIDTH - 1)
    y = random.randint(0, HEIGHT - 1)
    brightness = random.randint(180, 255)
    color = (brightness, brightness, brightness, 255)
    star_radius = random.choice([0, 0, 1, 1, 2])
    plus_probability = 0.06
    wants_plus_star = random.random() < plus_probability
    if wants_plus_star:
        spike_len = random.randint(3, 5)
        spike_width = random.randint(1, 2)
        center_radius = 1
        if (
            x - spike_len < 0
            or x + spike_len >= WIDTH
            or y - spike_len < 0
            or y + spike_len >= HEIGHT
        ):
            wants_plus_star = False
    if wants_plus_star:
        draw.ellipse(
            (x - center_radius, y - center_radius, x + center_radius, y + center_radius),
            fill=color,
        )
        draw.polygon(
            [(x, y - spike_len), (x - spike_width, y - center_radius), (x + spike_width, y - center_radius)],
            fill=color,
        )
        draw.polygon(
            [(x, y + spike_len), (x - spike_width, y + center_radius), (x + spike_width, y + center_radius)],
            fill=color,
        )
        draw.polygon(
            [(x - spike_len, y), (x - center_radius, y - spike_width), (x - center_radius, y + spike_width)],
            fill=color,
        )
        draw.polygon(
            [(x + spike_len, y), (x + center_radius, y - spike_width), (x + center_radius, y + spike_width)],
            fill=color,
        )
    elif star_radius == 0:
        img.putpixel((x, y), color)
    else:
        left = max(0, x - star_radius)
        top = max(0, y - star_radius)
        right = min(WIDTH - 1, x + star_radius)
        bottom = min(HEIGHT - 1, y + star_radius)
        draw.ellipse((left, top, right, bottom), fill=color)

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
