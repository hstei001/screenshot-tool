from PIL import Image, ImageDraw, ImageFont
import random
from math import cos, sin, pi

# Create a new image with a transparent background
size = 256
image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# Fun colors
colors = ['#FF69B4', '#00FF00', '#4169E1', '#FFD700', '#FF4500']

# Draw a crazy camera shape
center = size // 2
# Main camera body (tilted rectangle)
points = [
    (center - 60, center - 40),
    (center + 60, center - 60),
    (center + 80, center + 40),
    (center - 40, center + 60),
]
draw.polygon(points, fill=random.choice(colors))

# Lens (concentric circles with random colors)
for r in range(50, 10, -10):
    draw.ellipse([center - r, center - r, center + r, center + r], 
                 fill=random.choice(colors))

# Add some random decorative elements
for _ in range(10):
    x = random.randint(0, size)
    y = random.randint(0, size)
    r = random.randint(5, 15)
    draw.ellipse([x - r, y - r, x + r, y + r], fill=random.choice(colors))

# Add some stars
for _ in range(5):
    x = random.randint(0, size)
    y = random.randint(0, size)
    points = []
    for i in range(10):
        angle = i * (2 * pi / 10)
        r = 15 if i % 2 == 0 else 7
        points.append((x + r * cos(angle), y + r * sin(angle)))
    draw.polygon(points, fill=random.choice(colors))

# Add version text
try:
    # Try to use Arial font
    font = ImageFont.truetype("arial.ttf", 32)
    small_font = ImageFont.truetype("arial.ttf", 24)
except:
    # Fallback to default font
    font = ImageFont.load_default()
    small_font = ImageFont.load_default()

# Add text with white color and black outline
text_color = 'white'
outline_color = 'black'
outline_width = 2

# Function to draw outlined text
def draw_outlined_text(draw, pos, text, font, text_color, outline_color, outline_width):
    x, y = pos
    # Draw outline
    for adj in range(-outline_width, outline_width+1):
        for opp in range(-outline_width, outline_width+1):
            draw.text((x+adj, y+opp), text, font=font, fill=outline_color, anchor="ms")
    # Draw text
    draw.text((x, y), text, font=font, fill=text_color, anchor="ms")

# Draw text with outline
draw_outlined_text(draw, (size//2, size//2 - 20), "Screenshot", font, text_color, outline_color, outline_width)
draw_outlined_text(draw, (size//2, size//2 + 20), "Tool", font, text_color, outline_color, outline_width)
draw_outlined_text(draw, (size//2, size//2 + 60), "v1.0.1", small_font, text_color, outline_color, outline_width)

# Save as ICO
image.save('whacky_icon.ico', format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
