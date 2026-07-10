import streamlit as st
from PIL import Image
import time

# Sayfa Ayarları
st.set_page_config(page_title="Konteyner Hasar Tespit Sistemi", layout="centered")

st.title("📦 Konteyner Hasar Tespit Asistanı")
st.write("Analiz etmek istediğiniz konteyner fotoğrafını aşağıya yükleyin.")

# Dosya yükleyici
uploaded_file = st.file_uploader("Bir resim seçin...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Resmi göster
    image = Image.open(uploaded_file)
    st.image(image, caption='Yüklenen Konteyner', use_container_width=True)
    
    if st.button("Hasar Analizi Yap"):
        with st.spinner('Yapay zeka analiz ediyor...'):
            # Buraya kendi modelinizi (örneğin YOLOv8) entegre edeceksiniz
            time.sleep(2) # Simülasyon için gecikme
            
            # Örnek Çıktı
            st.success("Analiz Tamamlandı!")
            st.subheader("Tespit Sonuçları:")
            st.warning("Hasar Türü: Çökme (Dent)")
            st.metric(label="Güven Skoru", value="94%")
            
            st.write("---")
            st.info("Not: Bu bir prototiptir. Gerçek analiz için model ağırlıkları yüklü değildir.")

# Yan çubuk (Sidebar) için ekstra bilgiler
st.sidebar.header("Proje Hakkında")
st.sidebar.info("Bu uygulama, bilgisayarlı görü teknikleri kullanılarak konteynerlerdeki fiziksel hasarları tespit etmek amacıyla geliştirilmiştir.")