import streamlit as st
import time
import requests

st.set_page_config(
    page_title="Port Konteyner Analiz Sistemi",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Ortak CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

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
  [data-testid="stSidebar"] h3 { color: #e0f2fe !important; }
  [data-testid="stSidebar"] strong { color: #e0f2fe !important; }
  [data-testid="stSidebar"] code {
    background: rgba(96,165,250,0.15) !important;
    color: #7dd3fc !important;
    border-radius: 5px !important;
    padding: 2px 7px !important;
    font-size: 0.78rem !important;
    border: 1px solid rgba(96,165,250,0.25) !important;
  }
  [data-testid="stSidebar"] hr { border-color: rgba(147,197,253,0.18) !important; }

  /* ── Header ── */
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
    background: linear-gradient(90deg, transparent, rgba(125,211,252,0.5), transparent);
  }
  .port-header h1 { color: #f0f9ff; font-size: 1.65rem; font-weight: 700; margin: 0 0 6px 0; }
  .port-header p  { color: #7dd3fc; font-size: 0.85rem; margin: 0; }

  /* ── Login Kartı ── */
  .login-wrap {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 48px 16px;
  }
  .login-card {
    background: rgba(255,255,255,0.92);
    border: 1px solid rgba(147,197,253,0.5);
    border-radius: 18px;
    padding: 40px 44px;
    width: 100%;
    max-width: 420px;
    box-shadow: 0 12px 40px rgba(30,58,95,0.12);
  }
  .login-card h2 {
    color: #1e3a5f;
    font-size: 1.3rem;
    font-weight: 700;
    margin: 0 0 4px 0;
    text-align: center;
  }
  .login-card .login-sub {
    color: #64748b;
    font-size: 0.8rem;
    text-align: center;
    margin-bottom: 28px;
  }

  /* ── Kart (container border) ── */
  [data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.88) !important;
    border: 1px solid rgba(147,197,253,0.45) !important;
    border-radius: 14px !important;
    box-shadow: 0 4px 20px rgba(30,58,95,0.08) !important;
  }

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

  /* ── Input ── */
  label,
  .stTextInput label,
  .stSelectbox label {
    color: #1e40af !important;
    font-size: 0.73rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
  }
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
    background: #fff !important;
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
    background: #fff !important;
    border: 1.5px solid #bfdbfe !important;
    border-radius: 10px !important;
    box-shadow: 0 8px 24px rgba(30,58,95,0.12) !important;
  }
  [role="option"] { color: #1e3a5f !important; }
  [role="option"]:hover { background: #eff6ff !important; }

  /* ── Butonlar ── */
  .stFormSubmitButton > button {
    background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 9px !important;
    padding: 11px 28px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    width: 100%;
    transition: all 0.2s ease;
    box-shadow: 0 4px 14px rgba(37,99,235,0.3);
  }
  .stFormSubmitButton > button:hover {
    background: linear-gradient(135deg, #1e40af 0%, #1d4ed8 100%) !important;
    box-shadow: 0 6px 20px rgba(37,99,235,0.4) !important;
  }
  .stButton > button {
    background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 100%) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 9px !important;
    padding: 10px 24px !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    transition: all 0.2s ease;
    box-shadow: 0 4px 12px rgba(14,165,233,0.28);
  }
  .stButton > button:hover {
    background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
    box-shadow: 0 6px 18px rgba(14,165,233,0.38) !important;
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

  [data-testid="stImage"] img {
    border-radius: 10px;
    border: 1.5px solid #bfdbfe;
    box-shadow: 0 4px 16px rgba(30,58,95,0.1);
  }

  /* ── Analiz sonucu ── */
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
  .analiz-row { display: flex; gap: 10px; }
  .analiz-item {
    flex: 1;
    background: #fff;
    border: 1px solid #dbeafe;
    border-radius: 8px;
    padding: 10px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(30,58,95,0.05);
  }
  .analiz-item .ai-label {
    font-size: 0.63rem; color: #60a5fa;
    text-transform: uppercase; letter-spacing: 0.6px; font-weight: 700;
  }
  .analiz-item .ai-val {
    font-size: 1.05rem; font-weight: 700; color: #1e3a5f;
    margin-top: 4px; line-height: 1.3;
  }

  .empty-state {
    text-align: center; padding: 36px 20px;
    color: #93c5fd; font-size: 0.83rem;
  }
  .empty-state .es-icon { font-size: 2.2rem; margin-bottom: 10px; opacity: 0.6; }

  /* ── Kullanıcı badge (sidebar) ── */
  .user-badge {
    background: rgba(96,165,250,0.15);
    border: 1px solid rgba(96,165,250,0.3);
    border-radius: 10px;
    padding: 12px 14px;
    margin-bottom: 14px;
  }
  .user-badge .ub-name { font-size: 0.9rem; font-weight: 700; color: #e0f2fe !important; }
  .user-badge .ub-role {
    font-size: 0.7rem; color: #7dd3fc !important;
    text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px;
  }

  .stSuccess { background: #f0fdf4 !important; border: 1px solid #86efac !important; border-radius: 9px !important; color: #166534 !important; }
  .stError, .stWarning, .stInfo { border-radius: 9px !important; }
  .stSpinner > div { border-top-color: #3b82f6 !important; }
  p, li { color: #475569; }
  hr { border-color: #e2e8f0 !important; margin: 16px 0 !important; }

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] {
    gap: 6px;
    border-bottom: 1.5px solid #bfdbfe !important;
    background: transparent !important;
  }
  .stTabs [data-baseweb="tab"] {
    color: #64748b !important;
    font-weight: 500 !important;
    font-size: 0.83rem !important;
    padding: 6px 16px !important;
    border-radius: 7px 7px 0 0 !important;
    border: none !important;
    background: transparent !important;
  }
  .stTabs [aria-selected="true"] {
    color: #1d4ed8 !important;
    background: #eff6ff !important;
    border-bottom: 2px solid #1d4ed8 !important;
    font-weight: 600 !important;
  }
  .stTabs [data-baseweb="tab-panel"] { padding-top: 12px !important; }

  @keyframes slide-in {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
  }
</style>
""", unsafe_allow_html=True)

API_URL = "http://localhost:8000"
CONTAINER_TYPES = ["Kuru Yük", "Soğutmalı", "Açık Üst", "Platform", "Tank", "Özel Amaçlı"]

# ── Session State ────────────────────────────────────────────────────────────
for key, default in [
    ("token", None),
    ("user", None),
    ("analiz_sonucu", None),
    ("kayit_sayisi", 0),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ════════════════════════════════════════════════════════════════════════════
# GİRİŞ SAYFASI
# ════════════════════════════════════════════════════════════════════════════
def show_login():
    st.markdown("""
    <div class="port-header" style="max-width:480px;margin:40px auto 0 auto;">
      <h1 style="text-align:center">⚓ Port Konteyner</h1>
      <p style="text-align:center">Analiz &amp; Kayıt Sistemi</p>
    </div>
    """, unsafe_allow_html=True)

    _, center, _ = st.columns([1, 1.7, 1])
    with center:
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            tab_giris, tab_kayit = st.tabs(["🔐  Giriş Yap", "📝  Kayıt Ol"])

            # ── GİRİŞ FORMU ─────────────────────────────────────────────
            with tab_giris:
                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                with st.form("login_form"):
                    phone    = st.text_input("Telefon No", placeholder="5554443322")
                    password = st.text_input("Şifre", type="password", placeholder="••••••")
                    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                    submit_login = st.form_submit_button("Giriş Yap", use_container_width=True)

                if submit_login:
                    if not phone or not password:
                        st.error("Telefon ve şifre zorunludur.")
                    else:
                        try:
                            resp = requests.post(
                                f"{API_URL}/auth/login",
                                json={"phone": phone, "password": password},
                                timeout=5,
                            )
                            if resp.status_code == 200:
                                data = resp.json()
                                st.session_state.token = data["access_token"]
                                st.session_state.user  = {
                                    "full_name": data["full_name"],
                                    "role":      data["role"],
                                    "company":   data["company"],
                                }
                                st.rerun()
                            else:
                                st.error(resp.json().get("detail", "Giriş başarısız."))
                        except requests.exceptions.ConnectionError:
                            st.warning("Backend'e bağlanılamadı — sunucuyu başlatın.")

            # ── KAYIT FORMU ──────────────────────────────────────────────
            with tab_kayit:
                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                with st.form("register_form"):
                    col1, col2 = st.columns(2, gap="small")
                    with col1:
                        reg_first = st.text_input("Ad",       placeholder="Ali")
                        reg_phone = st.text_input("Telefon No", placeholder="5321112233")
                        reg_pass  = st.text_input("Şifre", type="password", placeholder="••••••")
                    with col2:
                        reg_last    = st.text_input("Soyad",   placeholder="Yılmaz")
                        reg_company = st.text_input("Şirket",  placeholder="Liman A.Ş.")
                        reg_pass2   = st.text_input("Şifre (tekrar)", type="password", placeholder="••••••")

                    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                    submit_register = st.form_submit_button("Kayıt Ol", use_container_width=True)

                if submit_register:
                    errors = []
                    if not all([reg_first, reg_last, reg_phone, reg_pass, reg_company]):
                        errors.append("Tüm alanlar zorunludur.")
                    elif reg_pass != reg_pass2:
                        errors.append("Şifreler eşleşmiyor.")
                    elif len(reg_pass) < 6:
                        errors.append("Şifre en az 6 karakter olmalıdır.")

                    if errors:
                        for e in errors:
                            st.error(e)
                    else:
                        try:
                            resp = requests.post(
                                f"{API_URL}/auth/register",
                                json={
                                    "first_name": reg_first,
                                    "last_name":  reg_last,
                                    "phone":      reg_phone,
                                    "password":   reg_pass,
                                    "company":    reg_company,
                                },
                                timeout=5,
                            )
                            if resp.status_code == 201:
                                st.success(f"✓ {resp.json()['message']} Şimdi giriş yapabilirsiniz.")
                            elif resp.status_code == 409:
                                st.error(resp.json().get("detail", "Bu telefon numarası zaten kayıtlı."))
                            else:
                                detail = resp.json().get("detail", "Kayıt başarısız.")
                                if isinstance(detail, list):
                                    for d in detail:
                                        st.error(d.get("msg", str(d)))
                                else:
                                    st.error(detail)
                        except requests.exceptions.ConnectionError:
                            st.warning("Backend'e bağlanılamadı — sunucuyu başlatın.")


# ════════════════════════════════════════════════════════════════════════════
# ANA UYGULAMA
# ════════════════════════════════════════════════════════════════════════════
def show_app():
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    user    = st.session_state.user

    # ── Header ──────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="port-header">
      <h1>⚓ Port Konteyner Analiz Sistemi</h1>
      <p>Fotoğraf yükleyin → hasar tespiti yapın → konteyneri kaydedin</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ─────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div class="user-badge">
          <div class="ub-name">👤 {user['full_name']}</div>
          <div class="ub-role">{user['role']} &nbsp;·&nbsp; {user['company']}</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Çıkış Yap", use_container_width=True):
            st.session_state.token = None
            st.session_state.user  = None
            st.session_state.analiz_sonucu = None
            st.session_state.kayit_sayisi  = 0
            st.rerun()

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
                unsafe_allow_html=True,
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

    # ── Ana Layout ───────────────────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1.5], gap="large")

    # ─── SOL: Görüntü Analizi ────────────────────────────────────────────────
    with col_left:
        with st.container(border=True):
            st.markdown('<p class="card-title">📷 &nbsp;Hasar Görüntü Analizi</p>', unsafe_allow_html=True)

            uploaded_file = st.file_uploader(
                "Fotoğraf yükle",
                type=["jpg", "jpeg", "png"],
                label_visibility="collapsed",
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
                            "bolge": "Ön panel – sol üst",
                        }
                    st.rerun()

                if st.session_state.analiz_sonucu:
                    s = st.session_state.analiz_sonucu
                    st.markdown(f"""
                    <div class="analiz-sonuc">
                      <div class="analiz-row">
                        <div class="analiz-item">
                          <div class="ai-label">Hasar Türü</div>
                          <div class="ai-val" style="font-size:.84rem">{s['hasar']}</div>
                        </div>
                        <div class="analiz-item">
                          <div class="ai-label">Güven</div>
                          <div class="ai-val">{s['skor']}</div>
                        </div>
                        <div class="analiz-item">
                          <div class="ai-label">Bölge</div>
                          <div class="ai-val" style="font-size:.76rem;line-height:1.3">{s['bolge']}</div>
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

    # ─── SAĞ: Kayıt Formu ────────────────────────────────────────────────────
    with col_right:
        with st.container(border=True):
            st.markdown('<p class="card-title">📋 &nbsp;Konteyner Kayıt Formu</p>', unsafe_allow_html=True)

            with st.form("kayit_formu"):
                col_a, col_b = st.columns(2, gap="medium")

                with col_a:
                    container_no = st.text_input("Konteyner No", placeholder="MSCU1234567", help="4 harf + 7 rakam")
                    container_type = st.selectbox("Konteyner Tipi", options=[""] + CONTAINER_TYPES, index=0)
                    arrive_port = st.text_input("Geliş Limanı", placeholder="Ambarlı Limanı")

                with col_b:
                    company_name = st.text_input("Şirket İsmi", placeholder="MAERSK")
                    destination_port = st.text_input("Varış Limanı", placeholder="Rotterdam Limanı")

                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                submitted = st.form_submit_button("Kaydet  →", use_container_width=True)

        if submitted:
            hatalar = []
            if not container_no:    hatalar.append("Konteyner No boş bırakılamaz.")
            if not container_type:  hatalar.append("Konteyner Tipi seçilmelidir.")
            if not company_name:    hatalar.append("Şirket İsmi boş bırakılamaz.")
            if not arrive_port:     hatalar.append("Geliş Limanı boş bırakılamaz.")
            if not destination_port: hatalar.append("Varış Limanı boş bırakılamaz.")

            if hatalar:
                for h in hatalar:
                    st.error(h)
            else:
                payload = {
                    "container_no": container_no,
                    "container_type": container_type,
                    "company_name": company_name,
                    "arrive_port": arrive_port,
                    "destination_port": destination_port,
                }
                try:
                    resp = requests.post(
                        f"{API_URL}/containers/register",
                        json=payload,
                        headers=headers,
                        timeout=5,
                    )
                    if resp.status_code == 200:
                        st.session_state.kayit_sayisi += 1
                        st.success(f"✓ Konteyner **{container_no}** başarıyla kayıt edildi.")
                        st.rerun()
                    elif resp.status_code == 401:
                        st.error("Oturum süresi doldu. Lütfen tekrar giriş yapın.")
                        st.session_state.token = None
                        st.rerun()
                    else:
                        detail = resp.json().get("detail", resp.text)
                        st.error(f"Kayıt hatası: {detail}")
                except requests.exceptions.ConnectionError:
                    st.warning("Backend'e bağlanılamadı — sunucunun çalıştığından emin olun.")


# ════════════════════════════════════════════════════════════════════════════
# ROUTER
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.token is None:
    show_login()
else:
    show_app()
