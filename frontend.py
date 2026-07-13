import streamlit as st
import time
import requests

st.set_page_config(
    page_title="Port Konteyner Analiz Sistemi",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
  }

  /* ── Açık mavi arka plan ── */
  .stApp {
    background: linear-gradient(160deg, #dbeafe 0%, #e0f2fe 50%, #f0f9ff 100%);
    min-height: 100vh;
  }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e3a5f 0%, #1a4a78 100%);
    border-right: 1px solid rgba(147, 197, 253, 0.25);
  }
  [data-testid="stSidebar"] * { color: #bfdbfe !important; }
  [data-testid="stSidebar"] h3 { color: #e0f2fe !important; font-size: 0.95rem !important; }
  [data-testid="stSidebar"] strong { color: #e0f2fe !important; }
  [data-testid="stSidebar"] code {
    background: rgba(96, 165, 250, 0.15) !important;
    color: #7dd3fc !important;
    border-radius: 5px !important;
    padding: 2px 7px !important;
    font-size: 0.78rem !important;
    border: 1px solid rgba(96,165,250,0.25) !important;
  }
  [data-testid="stSidebar"] hr { border-color: rgba(147,197,253,0.18) !important; }

  /* ── Header: koyu mavi şerit ── */
  .port-header {
    background: linear-gradient(135deg, #1e3a5f 0%, #1a5276 100%);
    border-radius: 14px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(30, 58, 95, 0.18);
  }
  .port-header::after {
    content: '';
    position: absolute;
    bottom: 0; left: 36px; right: 36px; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(125, 211, 252, 0.5), transparent);
  }
  .port-header::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 180px; height: 180px; border-radius: 50%;
    background: radial-gradient(circle, rgba(125,211,252,0.12) 0%, transparent 70%);
    pointer-events: none;
  }
  .port-header h1 {
    color: #f0f9ff;
    font-size: 1.65rem;
    font-weight: 700;
    margin: 0 0 6px 0;
    letter-spacing: -0.2px;
  }
  .port-header p {
    color: #7dd3fc;
    font-size: 0.85rem;
    margin: 0;
  }

  /* ── Kart: beyaz, hafif gölge ── */
  [data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255, 255, 255, 0.88) !important;
    border: 1px solid rgba(147, 197, 253, 0.45) !important;
    border-radius: 14px !important;
    box-shadow: 0 4px 20px rgba(30, 58, 95, 0.08) !important;
  }

  /* ── Kart başlık ── */
  .card-title {
    font-size: 0.78rem;
    font-weight: 700;
    color: #1e40af;
    letter-spacing: 0.7px;
    text-transform: uppercase;
    margin: 0 0 16px 0;
    padding-bottom: 10px;
    border-bottom: 1.5px solid #bfdbfe;
  }

  /* ── Input label ── */
  label,
  .stTextInput label,
  .stSelectbox label,
  .stFileUploader label {
    color: #1e40af !important;
    font-size: 0.73rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
  }

  /* ── Text inputs ── */
  .stTextInput > div > div > input {
    background: #f8faff !important;
    border: 1.5px solid #bfdbfe !important;
    border-radius: 8px !important;
    color: #0f2942 !important;
    font-size: 0.9rem !important;
    padding: 9px 12px !important;
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  .stTextInput > div > div > input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.12) !important;
    outline: none !important;
    background: #ffffff !important;
  }
  .stTextInput > div > div > input::placeholder { color: #93c5fd !important; }

  /* ── Selectbox ── */
  .stSelectbox > div > div {
    background: #f8faff !important;
    border: 1.5px solid #bfdbfe !important;
    border-radius: 8px !important;
  }
  .stSelectbox > div > div > div { color: #0f2942 !important; }
  [data-baseweb="select"] > div { background: #f8faff !important; }
  [data-baseweb="popover"] {
    background: #ffffff !important;
    border: 1.5px solid #bfdbfe !important;
    border-radius: 10px !important;
    box-shadow: 0 8px 24px rgba(30,58,95,0.12) !important;
  }
  [role="option"] { color: #1e3a5f !important; background: transparent !important; }
  [role="option"]:hover { background: #eff6ff !important; }

  /* ── Form submit butonu ── */
  .stFormSubmitButton > button {
    background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 9px !important;
    padding: 11px 28px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.3px !important;
    width: 100%;
    transition: all 0.2s ease;
    box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
  }
  .stFormSubmitButton > button:hover {
    background: linear-gradient(135deg, #1e40af 0%, #1d4ed8 100%) !important;
    box-shadow: 0 6px 20px rgba(37, 99, 235, 0.4) !important;
    transform: translateY(-1px);
  }

  /* ── Analiz butonu ── */
  .stButton > button {
    background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 9px !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.3px !important;
    transition: all 0.2s ease;
    box-shadow: 0 4px 12px rgba(14, 165, 233, 0.28);
  }
  .stButton > button:hover {
    background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
    box-shadow: 0 6px 18px rgba(14, 165, 233, 0.38) !important;
    transform: translateY(-1px);
  }

  /* ── File uploader ── */
  [data-testid="stFileUploader"] {
    background: #f0f9ff !important;
    border: 2px dashed #93c5fd !important;
    border-radius: 10px !important;
  }
  [data-testid="stFileUploader"] * { color: #3b82f6 !important; }
  [data-testid="stFileUploader"] svg { stroke: #60a5fa !important; }
  [data-testid="stFileUploader"] small { color: #93c5fd !important; }

  /* ── Görüntü ── */
  [data-testid="stImage"] img {
    border-radius: 10px;
    border: 1.5px solid #bfdbfe;
    box-shadow: 0 4px 16px rgba(30, 58, 95, 0.1);
  }

  /* ── Analiz sonuç kutusu ── */
  .analiz-sonuc {
    background: linear-gradient(135deg, #eff6ff 0%, #f0f9ff 100%);
    border: 1.5px solid #bfdbfe;
    border-radius: 11px;
    padding: 16px;
    margin-top: 14px;
    position: relative;
    overflow: hidden;
    animation: slide-in 0.35s ease-out;
  }
  .analiz-sonuc::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 3px;
    background: linear-gradient(90deg, #3b82f6, #0ea5e9, #38bdf8);
    border-radius: 11px 11px 0 0;
  }
  .analiz-row {
    display: flex;
    gap: 10px;
  }
  .analiz-item {
    flex: 1;
    background: #ffffff;
    border: 1px solid #dbeafe;
    border-radius: 8px;
    padding: 10px 10px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(30,58,95,0.05);
  }
  .analiz-item .ai-label {
    font-size: 0.63rem;
    color: #60a5fa;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    font-weight: 700;
  }
  .analiz-item .ai-val {
    font-size: 1.05rem;
    font-weight: 700;
    color: #1e3a5f;
    margin-top: 4px;
    line-height: 1.3;
  }

  /* ── Boş durum ── */
  .empty-state {
    text-align: center;
    padding: 36px 20px;
    color: #93c5fd;
    font-size: 0.83rem;
  }
  .empty-state .es-icon {
    font-size: 2.2rem;
    margin-bottom: 10px;
    opacity: 0.6;
  }

  /* ── Alert ── */
  .stSuccess {
    background: #f0fdf4 !important;
    border: 1px solid #86efac !important;
    border-radius: 9px !important;
    color: #166534 !important;
  }
  .stError, .stWarning, .stInfo { border-radius: 9px !important; }
  .stSpinner > div { border-top-color: #3b82f6 !important; }

  /* ── Genel metin ── */
  p, li { color: #475569; }
  hr { border-color: #e2e8f0 !important; margin: 16px 0 !important; }
  .stMarkdown p { color: #64748b; }

  @keyframes slide-in {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
  }
</style>
""", unsafe_allow_html=True)

# ── Session State ────────────────────────────────────────────────────────────
if "analiz_sonucu" not in st.session_state:
    st.session_state.analiz_sonucu = None
if "kayit_sayisi" not in st.session_state:
    st.session_state.kayit_sayisi = 0

CONTAINER_TYPES = ["Kuru Yük", "Soğutmalı", "Açık Üst", "Platform", "Tank", "Özel Amaçlı"]

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="port-header">
  <h1>⚓ Port Konteyner Analiz Sistemi</h1>
  <p>Fotoğraf yükleyin → hasar tespiti yapın → konteyneri kaydedin</p>
</div>
""", unsafe_allow_html=True)

# ── Ana Layout ────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([1, 1.5], gap="large")

# ─── SOL: Hasar Analizi ───────────────────────────────────────────────────────
with col_left:
    with st.container(border=True):
        st.markdown('<p class="card-title">📷 &nbsp;Hasar Görüntü Analizi</p>', unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Fotoğraf yükle",
            type=["jpg", "jpeg", "png"],
            label_visibility="collapsed"
        )

        if uploaded_file:
            st.image(uploaded_file, use_container_width=True)
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

            if st.button("Analizi Başlat", use_container_width=True):
                with st.spinner("Hasar analizi yapılıyor..."):
                    time.sleep(1.8)
                    st.session_state.analiz_sonucu = {
                        "hasar": "Çökme (Dent)",
                        "skor": "94%",
                        "bolge": "Ön panel – sol üst"
                    }
                st.rerun()

            if st.session_state.analiz_sonucu:
                s = st.session_state.analiz_sonucu
                st.markdown(f"""
                <div class="analiz-sonuc">
                  <div class="analiz-row">
                    <div class="analiz-item">
                      <div class="ai-label">Hasar Türü</div>
                      <div class="ai-val" style="font-size:0.84rem">{s['hasar']}</div>
                    </div>
                    <div class="analiz-item">
                      <div class="ai-label">Güven</div>
                      <div class="ai-val">{s['skor']}</div>
                    </div>
                    <div class="analiz-item">
                      <div class="ai-label">Bölge</div>
                      <div class="ai-val" style="font-size:0.76rem;line-height:1.3">{s['bolge']}</div>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
              <div class="es-icon">🖼️</div>
              Konteyner fotoğrafı yükleyerek<br>hasar analizini başlatın
            </div>
            """, unsafe_allow_html=True)

# ─── SAĞ: Kayıt Formu ────────────────────────────────────────────────────────
with col_right:
    with st.container(border=True):
        st.markdown('<p class="card-title">📋 &nbsp;Konteyner Kayıt Formu</p>', unsafe_allow_html=True)

        with st.form("kayit_formu"):
            col_a, col_b = st.columns(2, gap="medium")

            with col_a:
                container_no = st.text_input(
                    "Konteyner No",
                    placeholder="MSCU1234567",
                    help="4 harf + 7 rakam"
                )
                container_type = st.selectbox(
                    "Konteyner Tipi",
                    options=[""] + CONTAINER_TYPES,
                    index=0
                )
                arrive_port = st.text_input(
                    "Geliş Limanı",
                    placeholder="Ambarlı Limanı"
                )

            with col_b:
                company_name = st.text_input(
                    "Şirket İsmi",
                    placeholder="MAERSK"
                )
                destination_port = st.text_input(
                    "Varış Limanı",
                    placeholder="Rotterdam Limanı"
                )

            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            submitted = st.form_submit_button("Kaydet  →", use_container_width=True)

    if submitted:
        hatalar = []
        if not container_no:
            hatalar.append("Konteyner No boş bırakılamaz.")
        if not container_type:
            hatalar.append("Konteyner Tipi seçilmelidir.")
        if not company_name:
            hatalar.append("Şirket İsmi boş bırakılamaz.")
        if not arrive_port:
            hatalar.append("Geliş Limanı boş bırakılamaz.")
        if not destination_port:
            hatalar.append("Varış Limanı boş bırakılamaz.")

        if hatalar:
            for h in hatalar:
                st.error(h)
        else:
            payload = {
                "container_no": container_no,
                "container_type": container_type,
                "company_name": company_name,
                "arrive_port": arrive_port,
                "destination_port": destination_port
            }
            try:
                response = requests.post(
                    "http://localhost:8000/containers/register",
                    json=payload,
                    timeout=5
                )
                if response.status_code == 200:
                    st.session_state.kayit_sayisi += 1
                    st.success(f"✓ Konteyner **{container_no}** başarıyla kayıt edildi.")
                    st.rerun()
                else:
                    detail = response.json().get("detail", response.text)
                    st.error(f"Kayıt hatası: {detail}")
            except requests.exceptions.ConnectionError:
                st.warning("Backend'e bağlanılamadı — sunucunun çalıştığından emin olun.")

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚓ &nbsp;Sistem")
    st.markdown("---")
    st.markdown("**Endpoint**")
    st.code("POST /containers/register", language=None)
    st.markdown("**Host**")
    st.code("localhost:8000", language=None)
    st.markdown("---")
    st.markdown("**Konteyner Tipleri**")
    for t in CONTAINER_TYPES:
        st.markdown(
            f"<span style='color:#7dd3fc;font-size:0.75rem'>▸</span> "
            f"<span style='font-size:0.8rem;color:#bfdbfe'>{t}</span>",
            unsafe_allow_html=True
        )
    st.markdown("---")
    if st.session_state.analiz_sonucu:
        s = st.session_state.analiz_sonucu
        st.markdown("**Son Analiz**")
        st.markdown(f"Tür: `{s['hasar']}`")
        st.markdown(f"Skor: `{s['skor']}`")
        st.markdown("---")
        if st.button("Analizi Temizle", use_container_width=True):
            st.session_state.analiz_sonucu = None
            st.rerun()
    else:
        st.markdown(
            "<span style='color:#7dd3fc;font-size:0.8rem;opacity:0.6'>Henüz analiz yapılmadı.</span>",
            unsafe_allow_html=True
        )
