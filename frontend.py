import streamlit as st
from PIL import Image
import time

st.set_page_config(page_title="Konteyner Kayıt & Analiz", layout="wide")

st.title("📦 Konteyner Yönetim Paneli")

# Görsel ve Analiz Bölümü
with st.container():
    st.subheader("🖼️ Hasar Analizi")
    uploaded_file = st.file_uploader("Konteyner fotoğrafı yükleyin", type=["jpg", "jpeg", "png"])
    
    # Analiz sonucunu tutacak state
    if "analiz_sonucu" not in st.session_state:
        st.session_state.analiz_sonucu = None

    if uploaded_file:
        st.image(uploaded_file, width=300)
        if st.button("🚀 Analizi Çalıştır"):
            with st.spinner("Analiz ediliyor..."):
                time.sleep(1.5)
                st.session_state.analiz_sonucu = {"hasar": "Çökme (Dent)", "skor": "94%"}
            st.success("Analiz tamamlandı!")

# Kayıt Bölümü - Analizden bağımsız, her zaman görünür
st.write("---")
st.subheader("📝 Konteyner Kayıt Bilgileri")

with st.form("kayit_formu"):
    col1, col2 = st.columns(2)
    
    with col1:
        # Eğer analiz yapıldıysa, sonuçları kutucuğa otomatik ata
        default_hasar = st.session_state.analiz_sonucu["hasar"] if st.session_state.analiz_sonucu else ""
        container_no = st.text_input("Konteyner No", placeholder="Örn: CTN-001")
        hasar_turu = st.text_input("Hasar Türü", value=default_hasar)
    
    with col2:
        sirket = st.text_input("Şirket İsmi")
        liman = st.text_input("Bulunduğu Liman")
    
    if st.form_submit_button("Veritabanına Kaydet"):
        st.success("Kayıt veritabanına başarıyla eklendi!")

# Sidebar bilgisi
st.sidebar.info("Resim analizi yapıldığında 'Hasar Türü' alanı otomatik doldurulacaktır.")