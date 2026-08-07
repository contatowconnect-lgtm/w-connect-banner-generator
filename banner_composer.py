@@ -0,0 +1,106 @@
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO

with open(“wcds_config.json”, “r”, encoding="utf-8") as f:
    CONFIG = json.load (f)

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip(“#”)
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def remove_image_background(image):
    if image.mode != “RGBA”:
        image = image.convert(“RGBA”)
    data = image.getdata()
    new_data = []
    for item in data:
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    image.putdata(new_data)
    return image

def apply_glow(image, color, intensity):
    w, h = image.size
    glow = Image.new(“RGBA”, (w + intensity*2, h + intensity*2), (0,0,0,0))
    mask = Image.new(“L”, (w + intensity*2, h + intensity*2), 0)
    bbox = (intensity, intensity, w+intensity, h+intensity)
    mask = Image.new(“RGBA”, (w + intensity*2, h + intensity*2), 0)
    for i in range(intensity, 0, -2):
        temp = mask.filter(ImageFilter.GaussianBlur(i))
        layer = Image.new(“RGBA”, glow.size, color + (0,))
        layer.putalpha(temp)
        glow = Image.alpha_composite(glow, layer)
    glow.paste(image, (intensity, intensity), image)
    return glow

def generate_banner(category, product_name, price, discount, benefits, product_image, format="feed"):
    cat = CONFIG[“categories”][category]
    rgb_color = hex_to_rgb(cat[“primary_color”])
    rgb_background = hex_to_rgb(CONFIG[“fixed_colors”][“main_background”])
    dimensions = CONFIG[“formats”][format]
    width, height = dim[“width”], dim[“height”]
    pos = CONFIG[“positions”]
    banner = Image.new(“RGBA”, (width, height), background_rgb)
    draw = ImageDraw.Draw(banner)
    try:
        title_font = ImageFont.truetype(“arialbd.ttf”, int(height * 0.055))
        price_font = ImageFont.truetype(“arialbd.ttf”, int(height * 0.07))
        detail_font = ImageFont.truetype(“arialbd.ttf”, int(height * 0.03))
        footer_font = ImageFont.truetype(“arialbd.ttf”, int(height * 0.022))
    except:
        title_font = price_font = detail_font = footer_font = ImageFont.load_default()
    if product_image:
        product = remove_image_background(product_image.convert(“RGBA”))
        max_size = int(height * 0.32)
        aspect_ratio = min(max_size / product.width, max_size / product.height)
        product_w = int(product.width * aspect_ratio)
        product_h = int(product.height * aspect_ratio)
        product = product.resize((product_w, product_h), Image.Resampling.LANCZOS)
        product = apply_glow(product, rgb_color, cat[“glow_intensity”])
        px = int(pos[“product”][“x”] * width - product.width/2)
        py = int(pos[“product”][“y”] * height - product.height/2)
        banner.paste(product, (px, py), product)
    text_color = hex_to_rgb(CONFIG[“fixed_colors”][“primary_text”])
    bbox = draw.textbbox((0, 0), product_name, font=title_font)
    tx = width/2 - (bbox[2] - bbox[0])/2
    ty = pos[“title”][“y”] * height
    draw.text((tx, ty), product_name, fill=text_color, font=title_font, anchor="mt")
    price_text = f“R$ {price}”
    bbox = draw.textbbox((0, 0), price_text, font=price_font)
    px = width / 2 - (bbox[2] - bbox[0]) / 2
    py = pos[“price”][“y”] * height
    draw.text((px, py), price_text, fill=rgb_color, font=price_font, anchor="mt")
    if discount:
        bbox = draw.textbbox((0, 0), discount, font=detail_font)
        dx = width/2 - (bbox[2] - bbox[0])/2
        dy = pos[“discount”][“y”] * height
        draw.text((dx, dy), discount, fill=rgb_color, font=detail_font, anchor="mt")
    y_ben = pos[“benefits”][“y”] * height
    for ben in benefits:
        if ben.strip():
            bbox = draw.textbbox((0, 0), f“✓ {ben.strip()}”, font=detail_font)
            bx = width/2 - (bbox[2] - bbox[0])/2
            draw.text((bx, y_ben), f“✓ {ben.strip()}”, fill=text_color, font=detail_font, anchor="mt")
            y_ben += (bbox[3]-bbox[1]) * 1.3
    footer_text = CONFIG[“assets”][“footer_text”]
    bbox = draw.textbbox((0, 0), footer_text, font=footer_font)
    rx = width/2 - (bbox[2] - bbox[0])/2
    ry = pos[“footer”][“y”] * height
    draw.text((rx, ry), footer_text, fill=hex_to_rgb(CONFIG[“fixed_colors”][“footer_color”]), font=footer_font, anchor="mt")
    output = BytesIO()
    banner.convert(“RGB”).save(output, format="PNG", quality=95)
    output.seek(0)
    return output

def generate_caption(product_name, price, discount, benefits, category):
    caption = f“🔥 {product_name} 🔥\ n\n🚀 High-quality product!\n”
    for b in benefits:
        if b.strip():
            caption += f“✅ {b.strip()}\n”
    caption += f“\n💰 **For only R$ {price}**\n”
    if discount: caption += f“🔥 {discount}\n”
    caption += “\n👉 Get yours now!\n\n#WConnect #” + category.replace(“ ”, ‘’) + “ #Offer”
    return caption

