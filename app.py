import streamlit as st
from banner_composer import generate_banner, remove_image_background, CONFIG
from PIL import Image
import io

st.set_page_config(page_title="W Connect — Gerador de Banners", layout="centered")

st.title("🔌 W Connect Banner Generator v1.4.0")
st.markdown("---")

st.sidebar.header("⚙️ Configurações do Banner")

category_name = st.sidebar.selectbox(
    "Categoria",
    list(CONFIG.get("categories", {}).keys())
)

product_name = st.sidebar.text_input("Nome do Produto")
price = st.sidebar.text_input("Preço (ex: 1.499,90)")
discount = st.sidebar.number_input("Desconto (%)", min_value=0, max_value=100, step=1)
benefits_input = st.sidebar.text_area("Benefícios (separar por vírgula)")
badge_text = st.sidebar.text_input("Texto do Selo")

benefits = [b.strip() for b in benefits_input.split(",")] if benefits_input else None

st.subheader("📋 Pré-visualização")

if st.sidebar.button("🖼️ Gerar Banner", type="primary", use_container_width=True):
    if not product_name or not price:
        st.warning("⚠️ Preencha o nome do produto e o preço!")
    else:
        with st.spinner("Gerando banner..."):
            try:
                banner = generate_banner(
                    category_name=category_name,
                    product_name=product_name,
                    price=price,
                    discount=discount,
                    benefits=benefits,
                    badge_text=badge_text
                )
                st.success("✅ Banner gerado com sucesso!")
                st.image(banner, use_container_width=True)

                buf = io.BytesIO()
                banner.save(buf, format="PNG")
                st.download_button(
                    label="📥 Baixar Banner em PNG",
                    data=buf.getvalue(),
                    file_name=f"banner-{category_name}-{product_name[:20]}.png",
                    mime="image/png"
                )
            except Exception as erro:
                st.error(f"❌ Erro: {str(erro)}")

st.markdown("---")
st.caption("W Connect Design System v1.4.0 — Identidade Visual Oficial")