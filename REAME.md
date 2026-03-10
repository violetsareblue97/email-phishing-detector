# Email Safe+
Aplikasi web untuk mendeteksi email phishing menggunakan Machine Learning dan verifikasi DNS secara real-time.

Live demo: https://emailsecure.streamlit.app

---

## Cara Kerja

**1. Analisis Teks (NLP)**
Model TF-IDF + Logistic Regression menganalisis pola teks pada badan email. Model dilatih dengan 150.000 sampel email (phishing dan legitimate) dari dataset publik Kaggle.

**2. Verifikasi Domain via DNS**
Jika alamat pengirim diisi, sistem melakukan DNS lookup untuk memeriksa keberadaan record SPF dan DMARC pada domain pengirim. Hasil lookup digunakan untuk menyesuaikan skor risiko — domain dengan proteksi penuh mendapat pengurangan skor, domain tanpa SPF/DMARC mendapat kenaikan skor.

**3. Skor Akhir**
Skor final = skor model × multiplier DNS, dikategorikan ke tiga level:
- **≥ 65%** → Terdeteksi Phishing
- **40–64%** → Email Mencurigakan
- **< 40%** → Email Terlihat Aman

---

## Dataset

- Sumber: [Kaggle — Phishing Email Dataset](https://www.kaggle.com/datasets/naserabdullahalam/phishing-email-dataset)
- Ukuran: 150.000 baris (77.449 phishing, 72.551 legitimate)
- Kolom yang dipakai: `text_combined` (teks email), `label` (0/1)

---

## Model

```
Pipeline:
  TfidfVectorizer(max_features=15000, ngram_range=(1,3), stop_words='english')
  LogisticRegression(C=0.1, class_weight='balanced', max_iter=1000)
```

Model disimpan sebagai `phishing_model.joblib`. Preprocessing di `app.py` menggunakan fungsi `clean_text` yang identik dengan yang dipakai saat training.

---

## Cara Menjalankan

```bash
pip install -r requirements.txt
streamlit run app.py
```

Atau buka langsung di: https://emailsecure.streamlit.app

---

## Struktur File

```
├── app.py                        # aplikasi Streamlit
├── email_phishing_training.ipynb # notebook training
├── phishing_model.joblib         # model hasil training
├── requirements.txt
└── README.md
```

---

## Tech Stack

- Python, Streamlit
- Scikit-learn (TF-IDF + Logistic Regression)
- dnspython (DNS lookup SPF/DMARC)
- Joblib (model serialization)