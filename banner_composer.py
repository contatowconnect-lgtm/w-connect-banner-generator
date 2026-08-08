import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO

with open("wcds_config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def remove_image_background(image):
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    data = image.getdata()
    new_data = []
    for item in data:
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    image.putdata(new_data)
    return image

def generate_banner(category_name, product_name, price, discount, 
                    benefits=None, logo_path=None, badge_text=None, 
                    output_size=(1080, 1080)):
    
    cat = CONFIG.get("categories", {}).get(category_name, {})
    primary_color = hex_to_rgb(cat.get("primary_color", "#FFFFFF"))
    
    bg_color = hex_to_rgb(CONFIG.get("fixed_colors", {}).get("main_background", "#000000"))
    logo_color = hex_to_rgb(CONFIG.get("fixed_colors", {}).get("logo_color", "#FFFFFF"))
    primary_text = hex_to_rgb(CONFIG.get("fixed_colors", {}).get("primary_text", "#FFFFFF"))
    secondary_text = hex_to_rgb(CONFIG.get("fixed_colors", {}).get("secondary_text", "#CCCCCC"))
    
    width, height = output_size
    banner = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(banner)
    
    positions = CONFIG.get("positions", {})
    title_pos = positions.get("title", {"x": 0.1, "y": 0.1})
    product_pos = positions.get("product", {"x": 0.1, "y": 0.2})
    discount_pos = positions.get("discount", {"x": 0.1, "y": 0.3})
    price_pos = positions.get("price", {"x": 0.1, "y": 0.4})
    benefits_pos = positions.get("benefits", {"x": 0.1, "y": 0.5})
    badge_pos = positions.get("badge", {"x": 0.1, "y": 0.6})
    footer_pos = positions.get("footer", {"x": 0.1, "y": 0.9})
    
    try:
        font_title = ImageFont.truetype("arial.ttf", int(height * 0.08))
        font_product = ImageFont.truetype("arial.ttf", int(height * 0.058))
        font_price = ImageFont.truetype("arialbd.ttf", int(height * 0.068))
        font_discount = ImageFont.truetype("arialbd.ttf", int(height * 0.075))
        font_benefits = ImageFont.truetype("arial.ttf", int(height * 0.032))
        font_badge = ImageFont.truetype("arialbd.ttf", int(height * 0.038))
    except (IOError, OSError):
        font_title = ImageFont.load_default()
        font_product = ImageFont.load_default()
        font_price = ImageFont.load_default()
        font_discount = ImageFont.load_default()
        font_benefits = ImageFont.load_default()
        font_badge = ImageFont.load_default()
    
    draw.text((width * title_pos["x"], height * title_pos["y"]), 
              str(category_name).upper(), fill=primary_color, font=font_title)
    
    draw.text((width * product_pos["x"], height * product_pos["y"]), 
              str(product_name), fill=primary_text, font=font_product)
    
    if discount and discount > 0:
        draw.text((width * discount_pos["x"], height * discount_pos["y"]), 
                  f"-{discount}%", fill=logo_color, font=font_discount)
    
    draw.text((width * price_pos["x"], height * price_pos["y"]), 
              f"R$ {price}", fill=primary_text, font=font_price)
    
    if benefits:
        if isinstance(benefits, list):
            benefits_text = " • ".join(benefits)
        else:
            benefits_text = str(benefits)
        draw.text((width * benefits_pos["x"], height * benefits_pos["y"]), 
                  benefits_text, fill=secondary_text, font=font_benefits)
    
    if badge_text:
        draw.text((width * badge_pos["x"], height * badge_pos["y"]), 
                  str(badge_text), fill=logo_color, font=font_badge)
    
    footer_text = CONFIG.get("assets", {}).get("footer_text", "")
    draw.text((width * footer_pos["x"], height * footer_pos["y"]), 
              footer_text, fill=secondary_text, font=font_benefits)
    
    return banner