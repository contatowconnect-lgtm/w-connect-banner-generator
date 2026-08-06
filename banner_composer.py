@@ -0,0 +1,106 @@
import json
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO

with open("wcds_config.json", "r", encoding="utf-8") as f:
    CONFIG = json.load(f)

def hex_to_rgb(hex_cor):
    hex_cor = hex_cor.lstrip("#")
    return tuple(int(hex_cor[i:i+2], 16) for i in (0, 2, 4))

def remover_fundo_imagem(imagem):
    if imagem.mode != "RGBA":
        imagem = imagem.convert("RGBA")
    dados = imagem.getdata()
    nova_dados = []
    for item in dados:
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            nova_dados.append((255, 255, 255, 0))
        else:
            nova_dados.append(item)
    imagem.putdata(nova_dados)
    return imagem

def aplicar_glow(imagem, cor, intensidade):
    w, h = imagem.size
    glow = Image.new("RGBA", (w + intensidade*2, h + intensidade*2), (0,0,0,0))
    mascara = Image.new("L", (w + intensidade*2, h + intensidade*2), 0)
    bbox = (intensidade, intensidade, w+intensidade, h+intensidade)
    mascara.paste(255, bbox)
    for i in range(intensidade, 0, -2):
        temp = mascara.filter(ImageFilter.GaussianBlur(i))
        camada = Image.new("RGBA", glow.size, cor + (0,))
        camada.putalpha(temp)
        glow = Image.alpha_composite(glow, camada)
    glow.paste(imagem, (intensidade, intensidade), imagem)
    return glow

def gerar_banner(categoria, nome_produto, preco, desconto, beneficios, imagem_produto, formato="feed"):
    cat = CONFIG["categorias"][categoria]
    cor_rgb = hex_to_rgb(cat["cor_primaria"])
    fundo_rgb = hex_to_rgb(CONFIG["cores_fixas"]["fundo_principal"])
    dim = CONFIG["formatos"][formato]
    largura, altura = dim["largura"], dim["altura"]
    pos = CONFIG["posicoes"]
    banner = Image.new("RGBA", (largura, altura), fundo_rgb)
    draw = ImageDraw.Draw(banner)
    try:
        fonte_titulo = ImageFont.truetype("arialbd.ttf", int(altura*0.055))
        fonte_preco = ImageFont.truetype("arialbd.ttf", int(altura*0.07))
        fonte_detalhe = ImageFont.truetype("arialbd.ttf", int(altura*0.03))
        fonte_rodape = ImageFont.truetype("arialbd.ttf", int(altura*0.022))
    except:
        fonte_titulo = fonte_preco = fonte_detalhe = fonte_rodape = ImageFont.load_default()
    if imagem_produto:
        produto = remover_fundo_imagem(imagem_produto.convert("RGBA"))
        tam_max = int(altura * 0.32)
        proporcao = min(tam_max/produto.width, tam_max/produto.height)
        produto_w = int(produto.width * proporcao)
        produto_h = int(produto.height * proporcao)
        produto = produto.resize((produto_w, produto_h), Image.Resampling.LANCZOS)
        produto = aplicar_glow(produto, cor_rgb, cat["glow_intensity"])
        px = int(pos["produto"]["x"] * largura - produto.width/2)
        py = int(pos["produto"]["y"] * altura - produto.height/2)
        banner.paste(produto, (px, py), produto)
    cor_texto = hex_to_rgb(CONFIG["cores_fixas"]["texto_primario"])
    bbox = draw.textbbox((0,0), nome_produto, font=fonte_titulo)
    tx = largura/2 - (bbox[2]-bbox[0])/2
    ty = pos["titulo"]["y"] * altura
    draw.text((tx, ty), nome_produto, fill=cor_texto, font=fonte_titulo, anchor="mt")
    texto_preco = f"R$ {preco}"
    bbox = draw.textbbox((0,0), texto_preco, font=fonte_preco)
    px = largura/2 - (bbox[2]-bbox[0])/2
    py = pos["preco"]["y"] * altura
    draw.text((px, py), texto_preco, fill=cor_rgb, font=fonte_preco, anchor="mt")
    if desconto:
        bbox = draw.textbbox((0,0), desconto, font=fonte_detalhe)
        dx = largura/2 - (bbox[2]-bbox[0])/2
        dy = pos["desconto"]["y"] * altura
        draw.text((dx, dy), desconto, fill=cor_rgb, font=fonte_detalhe, anchor="mt")
    y_ben = pos["beneficios"]["y"] * altura
    for ben in beneficios:
        if ben.strip():
            bbox = draw.textbbox((0,0), f"✓ {ben.strip()}", font=fonte_detalhe)
            bx = largura/2 - (bbox[2]-bbox[0])/2
            draw.text((bx, y_ben), f"✓ {ben.strip()}", fill=cor_texto, font=fonte_detalhe, anchor="mt")
            y_ben += (bbox[3]-bbox[1]) * 1.3
    texto_rodape = CONFIG["ativos"]["texto_rodape"]
    bbox = draw.textbbox((0,0), texto_rodape, font=fonte_rodape)
    rx = largura/2 - (bbox[2]-bbox[0])/2
    ry = pos["rodape"]["y"] * altura
    draw.text((rx, ry), texto_rodape, fill=hex_to_rgb(CONFIG["cores_fixas"]["cor_rodape"]), font=fonte_rodape, anchor="mt")
    saida = BytesIO()
    banner.convert("RGB").save(saida, format="PNG", quality=95)
    saida.seek(0)
    return saida

def gerar_legenda(nome_produto, preco, desconto, beneficios, categoria):
    legenda = f"🔥 {nome_produto} 🔥\n\n🚀 Produto de alta qualidade!\n"
    for b in beneficios:
        if b.strip():
            legenda += f"✅ {b.strip()}\n"
    legenda += f"\n💰 **Por apenas R$ {preco}**\n"
    if desconto: legenda += f"🔥 {desconto}\n"
    legenda += "\n👉 Garanta o seu agora!\n\n#WConnect #" + categoria.replace(" ", "") + " #Oferta"
    return legenda
