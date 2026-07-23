# ContainerGuard — Port Konteyner Takip Sistemi

**YZ destekli konteyner hasar tespiti ve liman operasyonları yönetim platformu**

---

## Projenin Amacı

ContainerGuard, liman operatörlerinin konteyner bilgilerini sistematik biçimde kayıt altına almasını ve yapay zeka destekli görüntü analizi ile konteyner hasarlarını **(ezik, pas, delik)** otomatik olarak tespit etmesini sağlayan bir web uygulamasıdır.

Sistem; kullanıcı kimlik doğrulaması, konteyner kayıt/listeleme ve YZ tabanlı hasar + numara analizi olmak üzere temel işlevleri tek bir arayüzde birleştirir.

---

## Kullanılan Teknolojiler

| Katman | Teknoloji |
|--------|-----------|
| **Backend** | Python, FastAPI, Uvicorn |
| **Veritabanı** | MongoDB Atlas (PyMongo) |
| **Kimlik Doğrulama** | JWT (python-jose), bcrypt |
| **Görüntü İşleme** | OpenCV, Pillow, NumPy |
| **YZ / Hasar Modeli** | YOLO — Roboflow Inference API |
| **OCR / Konteyner No** | EasyOCR |
| **Veri Doğrulama** | Pydantic v2 |
| **Frontend** | React 18, Vite |
| **CI/CD** | GitHub Actions |

---

## Özellikler

- **YZ Destekli Hasar Analizi** — JPG/PNG/WebP formatında 6 adede kadar görüntü yükle; göçük (Dent), pas (Rust) ve delik (Hole) tespiti için YOLO modeli çalıştır
- **Bounding Box Görselleştirme** — Tespit edilen hasarlar kırmızı kutular ve güven skoru etiketiyle görüntü üzerine çizilir
- **OCR ile Konteyner Numarası Tespiti** — EasyOCR ile görselden ISO 6346 formatındaki konteyner numarası okunur
- **Şirket Tespiti** — BIC kodu tablosu üzerinden konteyner numarasından otomatik şirket adı çıkarımı
- **Konteyner Kaydı** — Uluslararası standartlara uygun numara formatı (ör. `MSCU1234567`) ve BIC doğrulaması ile konteyner ekleme
- **Konteyner Listesi & Filtreleme** — Numara, yük tipi, şirket, liman ve tarih aralığına göre filtreli listeleme
- **Inline Silme Onayı** — Sil butonuna basıldığında yerinde onay adımı gösterilir (tarayıcı popup'ı yok)
- **JWT Kimlik Doğrulama** — Güvenli kayıt, giriş ve oturum yönetimi; token TTL ile otomatik geçersiz kılma
- **Otomatik Test** — GitHub Actions ile her push'ta 38 test çalışır (21 unit + 17 entegrasyon)

---

## Klasör Yapısı

```
Container-Damage-Detection/
├── .github/
│   └── workflows/
│       └── ci.yml               # GitHub Actions CI/CD
├── backend/
│   ├── main.py                  # FastAPI uygulama giriş noktası, lifespan
│   ├── auth/
│   │   ├── router.py            # Kimlik doğrulama endpointleri
│   │   ├── schema.py            # Pydantic şemaları
│   │   └── service.py           # Kullanıcı kayıt / giriş mantığı
│   ├── containers/
│   │   ├── router.py            # Konteyner CRUD + BIC map endpointleri
│   │   ├── schema.py
│   │   └── service.py
│   ├── ocr/
│   │   └── service.py           # EasyOCR konteyner numarası tespiti
│   ├── yolo_model/
│   │   └── service.py           # Roboflow API entegrasyonu, bbox çizimi
│   ├── core/
│   │   ├── bic_table.py         # BIC kodu → şirket adı eşleme tablosu
│   │   ├── database.py          # MongoDB bağlantısı, koleksiyonlar, init_db()
│   │   ├── dependencies.py      # FastAPI dependency injection
│   │   └── security.py          # JWT işlemleri
│   └── tests/
│       ├── test_bic.py          # BIC tablosu unit testleri
│       ├── test_schema.py       # Pydantic şema unit testleri
│       └── test_integration.py  # Auth + konteyner entegrasyon testleri
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   └── src/
│       ├── api.js               # API istek katmanı
│       ├── App.jsx
│       └── components/          # React bileşenleri
├── .env                         # Ortam değişkenleri (git'e eklenmez)
└── requirements.txt             # Sabitlenmiş Python bağımlılıkları
```

---

## Kurulum ve Çalıştırma

### Gereksinimler

- Python 3.12+
- Node.js 18+
- [MongoDB Atlas](https://www.mongodb.com/atlas) hesabı
- [Roboflow](https://roboflow.com) hesabı (YOLO hasar modeli API anahtarı)

---

### 1. Projeyi İndir

```bash
git clone https://github.com/AE1024/Container-Damage-Detection.git
cd Container-Damage-Detection
```

---

### 2. Ortam Değişkenlerini Ayarla

Proje kök dizininde `.env` dosyası oluştur:

```env
MONGODB_URI=mongodb+srv://<kullanici>:<sifre>@cluster.mongodb.net/
DB_NAME=port_konteyner
SECRET_KEY=gizli_ve_uzun_bir_anahtar

# Roboflow — YOLO hasar tespiti
RF_API_KEY=roboflow_api_keyiniz
RF_MODEL_ID=container-damage-ithvn/1
RF_SERVER=https://detect.roboflow.com
```

> `.env` dosyası `.gitignore`'a eklidir, asla repoya yükleme.  
> `SECRET_KEY` boş bırakılırsa sunucu başlamaz.

---

### 3. Backend — Kurulum ve Başlatma

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

pip install -r requirements.txt

cd backend
uvicorn main:app --reload --port 8000
```

Çalışıyor mu kontrol et:

```
http://localhost:8000/health
```

---

### 4. Frontend — Kurulum ve Başlatma

Yeni bir terminal aç:

```bash
cd frontend
npm install
npm run dev
```

Uygulama şu adreste açılır:

```
http://localhost:5173
```

---

### 5. Testleri Çalıştır

```bash
cd backend

# Unit testler (DB gerekmez, hızlı)
..\.venv\Scripts\pytest tests\test_bic.py tests\test_schema.py -v

# Entegrasyon testleri (MongoDB Atlas bağlantısı gerekli)
..\.venv\Scripts\pytest tests\test_integration.py -v

# Tümü
..\.venv\Scripts\pytest tests\ -v
```

---

## API Özeti

### Kimlik Doğrulama

| Metot | Endpoint | Açıklama | Auth |
|-------|----------|----------|------|
| POST | `/api/v1/auth/register` | Yeni kullanıcı kaydı | — |
| POST | `/api/v1/auth/login` | Giriş → JWT token | — |
| POST | `/api/v1/auth/logout` | Token'ı geçersiz kıl | ✓ |
| GET | `/api/v1/auth/me` | Oturum açık kullanıcı bilgisi | ✓ |
| DELETE | `/api/v1/auth/me` | Hesabı sil | ✓ |
| GET | `/api/v1/auth/check-username/{username}` | Kullanıcı adı müsait mi? | — |

### Konteynerler

| Metot | Endpoint | Açıklama | Auth |
|-------|----------|----------|------|
| GET | `/api/v1/containers/list` | Filtreli konteyner listesi | ✓ |
| POST | `/api/v1/containers/register` | Konteyner ekle (BIC doğrulamalı) | ✓ |
| DELETE | `/api/v1/containers/{no}` | Konteyner sil | ✓ |
| POST | `/api/v1/containers/analyze` | YOLO hasar + EasyOCR analizi | ✓ |
| GET | `/api/v1/containers/bic-map` | BIC kodu → şirket adı tablosu | ✓ |

### Sistem

| Metot | Endpoint | Açıklama |
|-------|----------|----------|
| GET | `/health` | Sistem durumu |

---

## CI/CD

Her `main` branch push'unda GitHub Actions iki iş çalıştırır:

- **Backend** — `pip install`, `pytest` (38 test: 21 unit + 17 entegrasyon)
- **Frontend** — `npm ci`, `npm run build`

Gerekli GitHub Secrets: `MONGODB_URI`, `RF_API_KEY`

---

## Lisans

Bu proje MIT Lisansı ile lisanslanmıştır.
