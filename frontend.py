import streamlit as st
import requests

st.set_page_config(
    page_title="Liman Konteyner Analiz Sistemi",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    border-right: 1px solid rgba(147,197,253,0.25);
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

  /* ── Üst başlık ── */
  .port-header {
    background: linear-gradient(135deg, #1e3a5f 0%, #1a5276 100%);
    border-radius: 14px;
    padding: 28px 36px;
    margin-bottom: 24px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(30,58,95,0.18);
  }
  .port-header::after {
    content: '';
    position: absolute;
    bottom: 0; left: 36px; right: 36px; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(125,211,252,0.5), transparent);
  }
  .port-header h1 { color: #f0f9ff; font-size: 1.65rem; font-weight: 700; margin: 0 0 6px 0; }
  .port-header p  { color: #7dd3fc; font-size: 0.85rem; margin: 0; }

  /* ── Login sayfası merkez wrapper ── */
  .login-page {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-top: 32px;
  }
  .login-logo {
    font-size: 3rem;
    margin-bottom: 6px;
    text-align: center;
  }
  .login-brand {
    font-size: 1.55rem;
    font-weight: 700;
    color: #1e3a5f;
    text-align: center;
    margin-bottom: 2px;
  }
  .login-tagline {
    font-size: 0.82rem;
    color: #64748b;
    text-align: center;
    margin-bottom: 28px;
  }

  /* ── Kart ── */
  [data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255,255,255,0.92) !important;
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

  /* ── Inputs ── */
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

  /* Şifre alanındaki yinelenen ikinci göz ikonunu gizle */
  .stTextInput > div > div > button ~ button { display: none !important; }
  [data-testid="InputInstructions"] { display: none !important; }

  /* Tarayıcı autocomplete dropdown'ını gizle */

  /* Çıkış butonu kırmızı */
  [data-testid="stButton"]:has(button[kind="secondary"]#cikis_btn) button,
  div:has(> button[key="cikis_btn"]) button {
    background: linear-gradient(135deg,#dc2626,#b91c1c) !important;
    box-shadow: 0 4px 12px rgba(220,38,38,0.3) !important;
  }
  /* Onay butonları */
  div:has(> button[key="cikis_evet"]) button {
    background: linear-gradient(135deg,#16a34a,#15803d) !important;
    box-shadow: 0 4px 12px rgba(22,163,74,0.3) !important;
  }
  div:has(> button[key="cikis_hayir"]) button {
    background: linear-gradient(135deg,#6b7280,#4b5563) !important;
    box-shadow: none !important;
  }

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

  /* ── Kullanıcı badge ── */
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

  /* ── DB badge ── */
  .db-badge {
    background: rgba(16,185,129,0.12);
    border: 1px solid rgba(16,185,129,0.3);
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 0.72rem;
    color: #6ee7b7 !important;
    letter-spacing: 0.4px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 6px;
  }

  .stSuccess { background: #f0fdf4 !important; border: 1px solid #86efac !important; border-radius: 9px !important; color: #166534 !important; }
  .stError, .stWarning, .stInfo { border-radius: 9px !important; }
  .stSpinner > div { border-top-color: #3b82f6 !important; }
  p, li { color: #475569; }
  hr { border-color: #e2e8f0 !important; margin: 16px 0 !important; }

  @keyframes slide-in {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
  }
</style>
<script>
  function disableAutocomplete() {
    document.querySelectorAll('input').forEach(function(el) {
      el.setAttribute('autocomplete', 'new-password');
    });
  }
  document.addEventListener('DOMContentLoaded', disableAutocomplete);
  new MutationObserver(disableAutocomplete).observe(document.body, { childList: true, subtree: true });
</script>
""", unsafe_allow_html=True)

_BASE    = "http://localhost:8000"
API_URL  = f"{_BASE}/api/v1"    # versiyonlu endpoint'ler
HEALTH_URL = f"{_BASE}/health"  # versiyonsuz
CONTAINER_TYPES = ["Kuru Yük", "Soğutmalı", "Açık Üst", "Platform", "Tank", "Özel Amaçlı"]

for key, default in [
    ("token", None),
    ("user", None),
    ("analiz_sonucu", None),
    ("kayit_sayisi", 0),
    ("son_kayit_no", None),
    ("cikis_onay", False),
    ("kayit_basarili", None),
    ("list_limit", 10),
    ("list_date_from", None),
    ("list_date_to", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ── Sayfa yenilenince token'ı URL'den geri yükle ──────────────────────────
if st.session_state.token is None:
    saved = st.query_params.get("t")
    if saved:
        try:
            resp = requests.get(
                f"{API_URL}/auth/me",
                headers={"Authorization": f"Bearer {saved}"},
                timeout=3,
            )
            if resp.status_code == 200:
                st.session_state.token = saved
                st.session_state.user  = resp.json()
        except Exception:
            st.query_params.clear()


# ════════════════════════════════════════════════════════════════════════════
# GİRİŞ & KAYIT SAYFASI
# ════════════════════════════════════════════════════════════════════════════
def show_login():
    _, center, _ = st.columns([1, 1.6, 1])
    with center:
        st.markdown("""
        <div class="login-page">
          <div class="login-logo">⚓</div>
          <div class="login-brand">Port Konteyner Sistemi</div>
          <div class="login-tagline">Hasar Tespiti &amp; Kayıt Platformu</div>
        </div>
        """, unsafe_allow_html=True)

        with st.container(border=True):
            tab_giris, tab_kayit = st.tabs(["🔐  Giriş Yap", "📝  Kayıt Ol"])

            # ── GİRİŞ ────────────────────────────────────────────────────
            with tab_giris:
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                with st.form("login_form"):
                    col1, col2 = st.columns(2, gap="small")
                    with col1:
                        login_first = st.text_input("Ad",     placeholder="admin")
                    with col2:
                        login_last  = st.text_input("Soyad",  placeholder="admin")
                    password = st.text_input("Şifre", type="password", placeholder="••••••")
                    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                    submit_login = st.form_submit_button("Giriş Yap", use_container_width=True)

                if submit_login:
                    if not login_first or not login_last or not password:
                        st.error("Ad, soyad ve şifre zorunludur.")
                    else:
                        try:
                            resp = requests.post(
                                f"{API_URL}/auth/login",
                                json={"first_name": login_first, "last_name": login_last, "password": password},
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
                                st.query_params["t"] = data["access_token"]
                                st.rerun()
                            else:
                                st.error(resp.json().get("detail", "Giriş başarısız."))
                        except requests.exceptions.ConnectionError:
                            st.warning("Backend'e bağlanılamadı — sunucuyu başlatın.")

                st.markdown("""
                <div style='text-align:center;margin-top:12px;font-size:0.75rem;color:#94a3b8'>
                  Test hesabı &nbsp;→&nbsp; Ad: <b>admin</b> &nbsp;Soyad: <b>admin</b> &nbsp;Şifre: <b>admin123</b>
                </div>
                """, unsafe_allow_html=True)

            # ── KAYIT ────────────────────────────────────────────────────
            with tab_kayit:
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                with st.form("register_form"):
                    col1, col2 = st.columns(2, gap="small")
                    with col1:
                        reg_first   = st.text_input("Ad",     placeholder="Ali")
                        reg_pass    = st.text_input("Şifre", type="password", placeholder="Min. 6 karakter")
                    with col2:
                        reg_last    = st.text_input("Soyad",  placeholder="Yılmaz")
                        reg_pass2   = st.text_input("Şifre (tekrar)", type="password", placeholder="••••••")
                    reg_company = st.text_input("Şirket", placeholder="Liman A.Ş.")

                    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                    submit_register = st.form_submit_button("Kayıt Ol", use_container_width=True)

                if submit_register:
                    errors = []
                    if not all([reg_first, reg_last, reg_pass, reg_company]):
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
                                    "company":    reg_company,
                                    "password":   reg_pass,
                                },
                                timeout=5,
                            )
                            if resp.status_code == 201:
                                # Kayıt başarılı → otomatik giriş yap
                                login_resp = requests.post(
                                    f"{API_URL}/auth/login",
                                    json={"first_name": reg_first, "last_name": reg_last, "password": reg_pass},
                                    timeout=5,
                                )
                                if login_resp.status_code == 200:
                                    data = login_resp.json()
                                    st.session_state.token = data["access_token"]
                                    st.session_state.user  = {
                                        "full_name": data["full_name"],
                                        "role":      data["role"],
                                        "company":   data["company"],
                                    }
                                    st.query_params["t"] = data["access_token"]
                                    st.rerun()
                                else:
                                    st.success("Kayıt başarılı. Giriş yapabilirsiniz.")
                            elif resp.status_code == 409:
                                st.error(resp.json().get("detail", "Bu isimde bir kullanıcı zaten kayıtlı."))
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

    # ── Header + Çıkış ───────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="port-header">
      <h1>⚓ Port Konteyner Analiz Sistemi</h1>
      <p>Hoş geldiniz, <b>{user['full_name']}</b> &nbsp;·&nbsp;
         {user['role']} &nbsp;·&nbsp; {user['company']}</p>
    </div>
    """, unsafe_allow_html=True)

    # Çıkış satırı: buton → onay butonları aynı yatay çizgide
    if not st.session_state.cikis_onay:
        c1, c2 = st.columns([9, 1])
        with c2:
            if st.button("🚪 Çıkış", use_container_width=True, key="cikis_btn"):
                st.session_state.cikis_onay = True
                st.rerun()
    else:
        cx, c_lbl, c_evet, c_hayir = st.columns([3, 3, 1.4, 1.2])
        cx.empty()
        c_lbl.markdown(
            "<div style='text-align:right;padding-top:8px;font-size:0.82rem;"
            "color:#991b1b;font-weight:600'>⚠️ Çıkış yapmak istediğinize emin misiniz?</div>",
            unsafe_allow_html=True,
        )
        with c_evet:
            if st.button("✓ Evet", use_container_width=True, key="cikis_evet"):
                st.session_state.token         = None
                st.session_state.user          = None
                st.session_state.analiz_sonucu = None
                st.session_state.kayit_sayisi  = 0
                st.session_state.cikis_onay    = False
                st.query_params.clear()
                st.rerun()
        with c_hayir:
            if st.button("✗ İptal", use_container_width=True, key="cikis_hayir"):
                st.session_state.cikis_onay = False
                st.rerun()

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        # Health check
        try:
            h = requests.get(HEALTH_URL, timeout=3).json()
            db_ok    = h.get("database", {}).get("status") == "ok"
            model_ok = h.get("model",    {}).get("status") == "ok"
        except Exception:
            db_ok = model_ok = False

        db_icon    = "🟢" if db_ok    else "🔴"
        model_icon = "🟢" if model_ok else "🔴"
        db_lbl     = "MongoDB bağlı"    if db_ok    else "MongoDB bağlanamadı"
        model_lbl  = "Model yüklü"      if model_ok else "Model yüklenmedi"

        st.markdown(f"""
        <div class="user-badge">
          <div class="ub-name">👤 {user['full_name']}</div>
          <div class="ub-role">{user['role']} &nbsp;·&nbsp; {user['company']}</div>
        </div>
        <div class="db-badge">
          {db_icon} &nbsp;{db_lbl}<br>
          <span style="font-size:0.75rem">{model_icon} &nbsp;{model_lbl}</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Çıkış Yap", use_container_width=True, key="sidebar_cikis"):
            st.session_state.cikis_onay = True
            st.rerun()

        st.markdown("---")
        st.markdown("**Kayıt Sayısı (bu oturum)**")
        st.markdown(
            f"<span style='font-size:1.4rem;font-weight:700;color:#7dd3fc'>"
            f"{st.session_state.kayit_sayisi}</span>",
            unsafe_allow_html=True,
        )
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
            results_list = st.session_state.analiz_sonucu
            st.markdown("**Son Analiz**")
            for i, s in enumerate(results_list):
                st.markdown(f"Resim {i+1}: `{s['hasar']}` — `{s['skor']}`")
            if st.button("Analizi Temizle", use_container_width=True):
                st.session_state.analiz_sonucu = None
                st.rerun()

    # ── Ana Layout ────────────────────────────────────────────────────────────
    col_left, col_right = st.columns([1, 1.5], gap="large")

    # ─── SOL: Görüntü Analizi ────────────────────────────────────────────────
    with col_left:
        with st.container(border=True):
            st.markdown('<p class="card-title">📷 &nbsp;Hasar Görüntü Analizi</p>', unsafe_allow_html=True)

            uploaded_files = st.file_uploader(
                "Fotoğraf yükle (en fazla 3)",
                type=["jpg", "jpeg", "png", "webp"],
                accept_multiple_files=True,
                label_visibility="collapsed",
            )

            # Max 3 kontrolü
            if uploaded_files and len(uploaded_files) > 3:
                st.warning("En fazla 3 resim yükleyebilirsiniz. İlk 3 resim kullanılacak.")
                uploaded_files = uploaded_files[:3]

            if uploaded_files:
                # Dosya seti değiştiyse analizi temizle
                cur_key = "_".join(f"{f.name}_{f.size}" for f in uploaded_files)
                if st.session_state.get("_last_file") != cur_key:
                    st.session_state.analiz_sonucu = None
                    st.session_state["_last_file"] = cur_key

                import base64 as _b64

                # Sonuç varsa annotated görüntüleri, yoksa originalleri göster
                results_list = st.session_state.analiz_sonucu or []
                for idx, uf in enumerate(uploaded_files):
                    if results_list and idx < len(results_list) and results_list[idx].get("annotated_img"):
                        img_bytes = _b64.b64decode(results_list[idx]["annotated_img"])
                        st.image(img_bytes, use_container_width=True)
                    else:
                        st.image(uf, use_container_width=True)

                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

                if st.button("Analizi Başlat", use_container_width=True):
                    with st.spinner("YOLO modeli analiz yapıyor..."):
                        files_payload = [
                            ("files", (uf.name, uf.getvalue(), uf.type))
                            for uf in uploaded_files
                        ]
                        resp = requests.post(
                            f"{API_URL}/containers/analyze",
                            files=files_payload,
                            headers=headers,
                            timeout=60,
                        )
                    if resp.status_code == 200:
                        st.session_state.analiz_sonucu = resp.json().get("results", [])
                        st.rerun()
                    else:
                        try:
                            detail = resp.json().get("detail", resp.text)
                        except Exception:
                            detail = resp.text or f"HTTP {resp.status_code}"
                        if resp.status_code == 413:
                            st.error(f"Dosya çok büyük: {detail}")
                        else:
                            st.error(f"Analiz hatası: {detail}")

                # Sonuç kartları — her resim için
                if st.session_state.analiz_sonucu:
                    for idx, s in enumerate(st.session_state.analiz_sonucu):
                        fname = uploaded_files[idx].name if idx < len(uploaded_files) else f"Resim {idx+1}"
                        renk  = "#ef4444" if s.get("hasar_var") else "#22c55e"
                        st.markdown(f"""
                        <div class="analiz-sonuc" style="margin-bottom:8px">
                          <div style="font-size:.75rem;color:#94a3b8;margin-bottom:4px">
                            📄 {fname}
                          </div>
                          <div class="analiz-row">
                            <div class="analiz-item">
                              <div class="ai-label">Durum</div>
                              <div class="ai-val" style="font-size:.84rem;color:{renk}">
                                {"⚠ Hasar Var" if s.get("hasar_var") else "✓ Temiz"}
                              </div>
                            </div>
                            <div class="analiz-item">
                              <div class="ai-label">Güven</div>
                              <div class="ai-val">{s['skor']}</div>
                            </div>
                            <div class="analiz-item">
                              <div class="ai-label">Tespit</div>
                              <div class="ai-val">{s.get('tespit_sayisi', 0)}</div>
                            </div>
                          </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="empty-state">
                  <div class="es-icon">🖼️</div>
                  Konteyner fotoğrafı yükleyerek<br>hasar analizini başlatın<br>
                  <span style="font-size:.75rem;color:#94a3b8">(en fazla 3 resim)</span>
                </div>
                """, unsafe_allow_html=True)

    # ─── SAĞ: Kayıt Formu ────────────────────────────────────────────────────
    with col_right:
        with st.container(border=True):
            st.markdown('<p class="card-title">📋 &nbsp;Konteyner Kayıt Formu</p>', unsafe_allow_html=True)

            with st.form("kayit_formu"):
                col_a, col_b = st.columns(2, gap="medium")

                with col_a:
                    container_no   = st.text_input("Konteyner No",  placeholder="MSCU1234567", help="4 harf + 7 rakam")
                    container_type = st.selectbox("Konteyner Tipi", options=[""] + CONTAINER_TYPES, index=0)
                    arrive_port    = st.text_input("Geliş Limanı",  placeholder="Ambarlı Limanı")

                with col_b:
                    company_name     = st.text_input("Şirket İsmi",  placeholder="MAERSK")
                    destination_port = st.text_input("Varış Limanı", placeholder="Rotterdam Limanı")

                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                submitted = st.form_submit_button("Veritabanına Kaydet  →", use_container_width=True)

        if submitted:
            hatalar = []
            if not container_no:      hatalar.append("Konteyner No boş bırakılamaz.")
            if not container_type:    hatalar.append("Konteyner Tipi seçilmelidir.")
            if not company_name:      hatalar.append("Şirket İsmi boş bırakılamaz.")
            if not arrive_port:       hatalar.append("Geliş Limanı boş bırakılamaz.")
            if not destination_port:  hatalar.append("Varış Limanı boş bırakılamaz.")

            if hatalar:
                for h in hatalar:
                    st.error(h)
            else:
                payload = {
                    "container_no":     container_no,
                    "container_type":   container_type,
                    "company_name":     company_name,
                    "arrive_port":      arrive_port,
                    "destination_port": destination_port,
                }

                try:
                    resp = requests.post(
                        f"{API_URL}/containers/register",
                        json=payload,
                        headers=headers,
                        timeout=5,
                    )
                    if resp.status_code in (200, 201):
                        st.session_state.kayit_sayisi += 1
                        st.session_state.son_kayit_no = container_no
                        st.session_state.kayit_basarili = container_no
                        st.rerun()
                    elif resp.status_code == 409:
                        st.error(f"Bu konteyner numarası ({container_no}) zaten kayıtlı.")
                    elif resp.status_code == 401:
                        st.error("Oturum süresi doldu. Lütfen tekrar giriş yapın.")
                        st.session_state.token = None
                        st.rerun()
                    else:
                        detail = resp.json().get("detail", resp.text)
                        st.error(f"Kayıt hatası: {detail}")
                except requests.exceptions.ConnectionError:
                    st.warning("Backend'e bağlanılamadı — sunucunun çalıştığından emin olun.")

        if st.session_state.kayit_basarili:
            st.markdown(f"""
            <div style="
                background:#dcfce7; color:#15803d;
                border:1px solid #86efac; border-radius:8px;
                padding:10px 14px; font-size:.88rem; font-weight:600;
                display:flex; align-items:center; gap:8px; margin-top:8px;
            ">
                ✅ &nbsp;<b>{st.session_state.kayit_basarili}</b> başarıyla veritabanına kaydedildi.
            </div>
            """, unsafe_allow_html=True)
            st.session_state.kayit_basarili = None

    # ── Kayıtlı Konteynerlar ─────────────────────────────────────────────────
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<p class="card-title">📦 &nbsp;Kayıtlı Hasarlı Konteynerlar</p>', unsafe_allow_html=True)

    # ── Filtre Satırı ────────────────────────────────────────────────────────
    import datetime as _dt
    fc1, fc2, fc3 = st.columns([2, 2, 3])

    with fc1:
        df_val = st.date_input(
            "Başlangıç Tarihi",
            value=st.session_state.list_date_from,
            key="df_from",
            format="DD.MM.YYYY",
        )
        st.session_state.list_date_from = df_val if df_val else None

    with fc2:
        dt_val = st.date_input(
            "Bitiş Tarihi",
            value=st.session_state.list_date_to,
            key="df_to",
            format="DD.MM.YYYY",
        )
        st.session_state.list_date_to = dt_val if dt_val else None

    with fc3:
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        st.markdown(
            "<span style='font-size:0.75rem;font-weight:600;color:#64748b'>Gösterilecek kayıt sayısı</span>",
            unsafe_allow_html=True,
        )
        lb1, lb2, lb3, lb4 = st.columns([1, 1, 1, 3])
        for col, n in zip([lb1, lb2, lb3], [5, 10, 20]):
            active = st.session_state.list_limit == n
            style  = "background:#1d4ed8;color:#fff;" if active else "background:#e2e8f0;color:#334155;"
            if col.button(str(n), key=f"lim_{n}",
                          help=f"Son {n} kaydı göster",
                          use_container_width=True):
                st.session_state.list_limit = n
                st.rerun()

    # Filtreleri temizle butonu
    if st.session_state.list_date_from or st.session_state.list_date_to:
        if st.button("✕ Filtreyi Temizle", key="clear_filter"):
            st.session_state.list_date_from = None
            st.session_state.list_date_to   = None
            st.rerun()

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── API çağrısı ──────────────────────────────────────────────────────────
    params: dict = {"limit": st.session_state.list_limit}
    if st.session_state.list_date_from:
        params["date_from"] = str(st.session_state.list_date_from)
    if st.session_state.list_date_to:
        params["date_to"] = str(st.session_state.list_date_to)

    try:
        list_resp = requests.get(
            f"{API_URL}/containers/list",
            headers=headers,
            params=params,
            timeout=5,
        )
        if list_resp.status_code == 200:
            data       = list_resp.json()
            containers = data.get("containers", [])
            total      = data.get("total", 0)

            if total == 0:
                st.markdown("""
                <div class="empty-state">
                  <div class="es-icon">📭</div>
                  Filtreyle eşleşen kayıt bulunamadı
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(
                    f"<span style='font-size:0.8rem;color:#64748b'>"
                    f"<b>{total}</b> kayıt gösteriliyor (limit: {st.session_state.list_limit})</span>",
                    unsafe_allow_html=True,
                )
                st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

                # Başlık satırı
                hcols = st.columns([1.1, 2, 1.4, 1.5, 1.8, 1.8, 1.5, 1.2, 0.5])
                for col, label in zip(hcols, ["ID", "Konteyner No", "Tip", "Şirket", "Geliş", "Varış", "Kaydeden", "Tarih", ""]):
                    col.markdown(
                        f"<span style='font-size:0.7rem;font-weight:700;color:#1e40af;"
                        f"text-transform:uppercase;letter-spacing:0.5px'>{label}</span>",
                        unsafe_allow_html=True,
                    )
                st.markdown("<hr style='margin:4px 0 8px 0;border-color:#bfdbfe'>", unsafe_allow_html=True)

                for c in containers:
                    c_no     = c.get("container_no", "")
                    c_id     = c.get("container_id", "—")
                    short_id = c_id[:8] if c_id != "—" else "—"

                    # Tarih: YYYY-MM-DD → GG.AA.YYYY
                    raw_date = c.get("created_at", "")
                    try:
                        tarih = _dt.date.fromisoformat(raw_date[:10]).strftime("%d.%m.%Y")
                    except Exception:
                        tarih = raw_date[:10] if raw_date else "—"

                    row = st.columns([1.1, 2, 1.4, 1.5, 1.8, 1.8, 1.5, 1.2, 0.5])
                    row[0].markdown(
                        f"<span style='font-size:0.72rem;color:#64748b;font-family:monospace'"
                        f" title='{c_id}'>{short_id}…</span>",
                        unsafe_allow_html=True,
                    )
                    row[1].markdown(f"**{c_no}**")
                    row[2].markdown(c.get("container_type", ""))
                    row[3].markdown(c.get("company_name", ""))
                    row[4].markdown(c.get("arrive_port", ""))
                    row[5].markdown(c.get("destination_port", ""))
                    row[6].markdown(c.get("registered_by", ""))
                    row[7].markdown(
                        f"<span style='font-size:0.8rem;color:#475569'>{tarih}</span>",
                        unsafe_allow_html=True,
                    )
                    if row[8].button("🗑", key=f"del_{c_no}", help=f"{c_no} sil"):
                        try:
                            del_resp = requests.delete(
                                f"{API_URL}/containers/{c_no}",
                                headers=headers,
                                timeout=5,
                            )
                            if del_resp.status_code == 200:
                                st.toast(f"🗑 {c_no} silindi", icon="🔴")
                                st.rerun()
                            else:
                                st.error(del_resp.json().get("detail", "Silme hatası."))
                        except requests.exceptions.ConnectionError:
                            st.warning("Backend'e bağlanılamadı.")
    except requests.exceptions.ConnectionError:
        st.warning("Konteyner listesi alınamadı — backend bağlantısı yok.")


# ════════════════════════════════════════════════════════════════════════════
# ROUTER
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.token is None:
    show_login()
else:
    show_app()
