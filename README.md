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
| **Veritabanı** | MongoDB (PyMongo) |
| **Kimlik Doğrulama** | JWT (python-jose), bcrypt |
| **Görüntü İşleme** | OpenCV, Pillow, NumPy |
| **YZ / Hasar Modeli** | YOLO — Roboflow Inference API |
| **LLM / Konteyner OCR** | Groq API — `qwen/qwen3.6-27b` (vision) + `llama-3.3-70b-versatile` (judge) |
| **Veri Doğrulama** | Pydantic v2 |
| **Frontend** | React 18, Vite |

---

## Özellikler

- **YZ Destekli Hasar Analizi** — JPG/PNG/WebP formatında 6 adede kadar görüntü yükle; göçük (Dent), pas (Rust) ve delik (Hole) tespiti için YOLO modeli çalıştır
- **Bounding Box Görselleştirme** — Tespit edilen hasarlar kırmızı kutular ve güven skoru etiketiyle görüntü üzerine çizilir
- **LLM ile Konteyner Numarası Tespiti** — Groq vision modeli (`qwen/qwen3.6-27b`) görselden ISO 6346 formatındaki konteyner numarasını okur; `llama-3.3-70b-versatile` modeli formatı doğrular
- **Şirket Tespiti** — BIC kodu tablosu üzerinden konteyner numarasından otomatik şirket adı çıkarımı
- **Konteyner Kaydı** — Uluslararası standartlara uygun numara formatı (ör. `MSCU1234567`) ile konteyner ekleme
- **Konteyner Listesi & Filtreleme** — Numara, yük tipi, şirket ve tarih aralığına göre filtreli listeleme
- **JWT Kimlik Doğrulama** — Güvenli kayıt, giriş ve oturum yönetimi

---

## Klasör Yapısı

```
Container-Damage-Detection/
├── backend/
│   ├── main.py                  # FastAPI uygulama giriş noktası
│   ├── auth/
│   │   ├── router.py            # Kimlik doğrulama endpointleri
│   │   ├── schema.py            # Pydantic şemaları
│   │   └── service.py           # Kullanıcı kayıt / giriş mantığı
│   ├── containers/
│   │   ├── router.py            # Konteyner CRUD endpointleri
│   │   ├── schema.py
│   │   └── service.py
│   ├── yolo_model/
│   │   └── service.py           # Roboflow API entegrasyonu, bbox çizimi
│   ├── llm/
│   │   ├── service.py           # Groq vision + judge çağrıları
│   │   └── bic_table.py         # BIC kodu → şirket adı eşleme tablosu
│   └── core/
│       ├── database.py          # MongoDB bağlantısı ve koleksiyonlar
│       ├── dependencies.py      # FastAPI dependency injection
│       └── security.py          # JWT işlemleri
├── frontend/
│   ├── index.html
│   ├── vite.config.js
│   └── src/                     # React bileşenleri
├── .env                         # Ortam değişkenleri (git'e eklenmez)
└── requirements.txt             # Python bağımlılıkları
```

---

## Kurulum ve Çalıştırma

### Gereksinimler

- Python 3.12+
- Node.js 18+
- MongoDB (yerel kurulum veya [MongoDB Atlas](https://www.mongodb.com/atlas))
- [Roboflow](https://roboflow.com) hesabı (YOLO hasar modeli API anahtarı)
- [Groq](https://console.groq.com) hesabı (LLM konteyner numarası tespiti)

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
MONGODB_URI=mongodb://localhost:27017
DB_NAME=port_konteyner
SECRET_KEY=gizli_anahtar_buraya

# Roboflow — YOLO hasar tespiti
RF_API_KEY=roboflow_api_keyiniz
RF_MODEL_ID=container-damage-ithvn/1
RF_SERVER=https://detect.roboflow.com

# Groq — LLM konteyner numara/şirket tespiti
GROQ_API_KEY=groq_api_keyiniz
```

> `.env` dosyası `.gitignore`'a eklidir, asla repoya yükleme.

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

## LLM Akışı

Görsel analizi sırasında YOLO hasar tespiti ile paralel olarak Groq LLM pipeline'ı çalışır:

1. **Vision** — `qwen/qwen3.6-27b` modeli görselden ISO 6346 formatında konteyner numarasını okur
2. **Judge** — `llama-3.3-70b-versatile` modeli okunan numaranın gerçek bir konteyner kodu olup olmadığını doğrular
3. **BIC Lookup** — Geçerli numara bulunursa ilk 4 harf BIC tablosuyla eşleştirilerek şirket adı döndürülür

---

## API Özeti

| Metot | Endpoint | Açıklama | Auth |
|-------|----------|----------|------|
| POST | `/api/v1/register` | Yeni kullanıcı kaydı | — |
| POST | `/api/v1/login` | Giriş → JWT token | — |
| POST | `/api/v1/logout` | Token'ı geçersiz kıl | ✓ |
| GET | `/api/v1/me` | Oturum açık kullanıcı | ✓ |
| GET | `/api/v1/containers/list` | Konteyner listesi | ✓ |
| POST | `/api/v1/containers/register` | Konteyner ekle | ✓ |
| DELETE | `/api/v1/containers/{no}` | Konteyner sil | ✓ |
| POST | `/api/v1/containers/analyze` | YOLO hasar + LLM numara analizi | ✓ |
| GET | `/health` | Sistem durumu | — |

---

## Lisans

Bu proje MIT Lisansı ile lisanslanmıştır.
