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
    
    cat = CONFIG["categories"].get(category_name, {})
    primary_color = hex_to_rgb(cat.get("primary_color", "#FFFFFF"))
    style_name = cat.get("visual_style", "")
    glow_intensity = cat.get("glow_intensity", 0)
    
    bg_color = hex_to_rgb(CONFIG["fixed_colors"]["main_background"])
    footer_color = hex_to_rgb(CONFIG["fixed_colors"]["footer_color"])
    logo_color = hex_to_rgb(CONFIG["fixed_colors"]["logo_color"])
    primary_text = hex_to_rgb(CONFIG["fixed_colors"]["primary_text"])
    secondary_text = hex_to_rgb(CONFIG["fixed_colors"]["secondary_text"])
    
    width, height = output_size
    banner = Image.new("RGBA", (width, height), bg_color)
    draw = ImageDraw.Draw(banner)
    
    positions = CONFIG["positions"]
    logo_pos = positions["logo"]
    badge_pos = positions["badge"]
    product_pos = positions["product"]
    title_pos = positions["title"]
    price_pos = positions["price"]
    discount_pos = positions["discount"]
    benefits_pos = positions["benefits"]
    footer_pos = positions["footer"]
    
    try:
        font_title = ImageFont.truetype("arial.ttf", int(height * 0.08))
        font_product = ImageFont.truetype("arial.ttf", int(height * 0.058))
        font_price = ImageFont.truetype("arialbd.ttf", int(height * 0.068))
        font_discount = ImageFont.truetype("arialbd.ttf", int(height * 0.075))
        font_benefits = ImageFont.truetype("arial.ttf", int(height * 0.032))
        font_badge = ImageFont.truetype("arialbd.ttf", int(height * 0.038))
    except:
        font_title = ImageFont.load_default()
        font_product = ImageFont.load_default()
        font_price = ImageFont.load_default()
        font_discount = ImageFont.load_default()
        font_benefits = ImageFont.load_default()
        font_badge = ImageFont.load_default()
    
    draw.text((width * title_pos["x"], height * title_pos["y"]), 
              category_name.upper(), fill=primary_color, font=font_title)
    
    draw.text((width * product_pos["x"], height * product_pos["y"]), 
              product_name, fill=primary_text, font=font_product)
    
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
                  badge_text, fill=logo_color, font=font_badge)
    
    footer_text = CONFIG["assets"]["footer_text"]
    draw.text((width * footer_pos["x"], height * footer_pos["y"]), 
              footer_text, fill=secondary_text, font=font_benefits)
    
    return banner
