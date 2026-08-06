import streamlit as st
from PIL import Image
from banner_composer import gerar_banner, gerar_legenda, CONFIG

st.set_page_config(
    page_title="W Connect | Banner",
    page_icon="🚀",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    * { -webkit-tap-highlight-color: transparent; }
    .stApp { background-color: #121212; max-width: 480px; margin: 0 auto; }
    h1 { font-size: 1.6rem !important; text-align: center; }
    p, label { color: #fff !important; font-size: 0.95rem !important; }
    .stTextInput > div > div > input, .stTextArea > div > textarea, .stSelectbox > div > div {
        background-color: #1E1E1E !important; color: #fff !important; border: 1px solid #333 !important;
        border-radius: 12px !important; padding: 14px !important; font-size: 16px !important;
    }
    .stButton > button {
        background: linear-gradient(90deg, #00F5D4, #00D4AA); color: #000 !important; font-weight: 900 !important;
        height: 4.5rem !important; border-radius: 16px !important; font-size: 20px !important;
        box-shadow: 0 4px 12px rgba(0,245,212,0.25); border: none;
    }
    .stButton > button:active { transform: scale(0.97); }
    hr { border-color: #2a2a2a; margin: 1.2rem 0; }
    header, footer, #MainMenu { display: none; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🚀 W Connect</h1><p style='text-align:center; color:#999;'>Gerador de Banners v1.4.0</p>", unsafe_allow_html=True)

with st.form("form_banner", border=False):
    categorias = list(CONFIG["categorias"].keys())
    categoria = st.selectbox("📂 Categoria", categorias)
    nome_produto = st.text_input("📦 Nome do Produto", placeholder="ex: FONE BLUETOOTH PRO 5.0")
    preco = st.text_input("💰 Preço (sem R$)", placeholder="ex: 189,90")
    desconto = st.text_input("🔥 Desconto (opcional)", placeholder="ex: 25% OFF")
    beneficios = st.text_area("✨ Benefícios (1 por linha)", placeholder="Envio Grátis\nGarantia 1 Ano", height=100)
    imagem_produto = st.file_uploader("📷 Foto do Produto", type=["png", "jpg", "jpeg"])
    formato = st.radio("📐 Formato", ["Feed 1:1", "Stories 9:16"], horizontal=True)
    gerar = st.form_submit_button("🎨 GERAR BANNER", use_container_width=True, type="primary")

if gerar:
    if not nome_produto.strip() or not preco.strip() or not imagem_produto:
        st.error("❌ Preencha nome, preço e envie a foto!")
    else:
        with st.spinner("🎨 Criando sua arte..."):
            ben_list = [b.strip() for b in beneficios.strip().split("\n") if b.strip()]
            img = Image.open(imagem_produto)
            formato_chave = "feed" if "Feed" in formato else "stories"
            banner = gerar_banner(categoria, nome_produto, preco, desconto, ben_list, img, formato_chave)
            legenda = gerar_legenda(nome_produto, preco, desconto, ben_list, categoria)
        st.success("✅ Pronto! Arte criada!")
        st.divider()
        st.image(banner, use_column_width=True)
        st.markdown("### 📝 Legenda pronta")
        st.text_area("", value=legenda, height=160, label_visibility="collapsed")
        st.download_button("📥 BAIXAR IMAGEM", data=banner, file_name=f"WConnect_{nome_produto.replace(' ','_')}_{formato_chave}.png", mime="image/png", use_container_width=True)=
