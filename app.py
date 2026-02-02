import streamlit as st
import joblib
import re

# 1. Konfigurasi Halaman & CSS
st.set_page_config(page_title="Email Phishing Detector", layout="wide")

st.markdown("""
    <style>
    /* Background Utama */
    .stApp {
        background-color: #2c4f40;
        color: white;
        font-family: 'Helvetica', sans-serif;
    }

    /* Bar Judul Atas */
    .header-bar {
        display: flex;
        justify-content: center;
        align-items: center;
        background-color: rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 0px 0px 15px 15px;
        margin-bottom: 30px;
        border-bottom: 1px solid #ffffff33;
    }

    .header-title {
        font-size: 24px;
        font-weight: bold;
        letter-spacing: 1px;
    }

    /* Kotak Input Teks */
    .stTextArea textarea {
        background-color: #ffffff !important;
        color: #333333 !important;
        border-radius: 15px !important;
        font-size: 16px !important;
        box-shadow: 0px 8px 20px rgba(0,0,0,0.4) !important;
    }

    /* Gaya Tombol Utama */
    .stButton>button {
        width: 100%;
        background-color: #ffffff !important;
        color: #2c4f40 !important;
        font-weight: bold !important;
        height: 55px !important;
        border-radius: 30px !important;
        border: none !important;
        font-size: 18px !important;
        transition: 0.3s !important;
    }

    .stButton>button:hover {
        background-color: #e0e0e0 !important;
        transform: translateY(-2px);
    }
    
    /* Tombol Share Kecil */
    .share-container {
        text-align: right;
        margin-top: -20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Fungsi Pendukung
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', 'link_url', text)
    text = re.sub(r'\S+@\S+', 'email_address', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text

@st.cache_resource
def load_model():
    return joblib.load("phishing_model.joblib")

model = load_model()

# 3. Bar Judul
st.markdown('<div class="header-bar"><span class="header-title">Email Phishing Detector</span></div>', unsafe_allow_html=True)

# 4. Fitur Share
col_left, col_right = st.columns([5, 1])
with col_right:
    if st.button("🔗 Share"):
        # Logika copy link sederhana menggunakan st.code agar user mudah mengklik
        st.info("Salin link di bawah ini:")
        st.code("https://emailphishingdetector.streamlit.app/") # Ganti dengan link asli web Anda

# 5. Konten Utama
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    email_input = st.text_area("Tempel isi email:", height=250, placeholder="Masukkan teks email yang ingin diperiksa...")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Analisis Sekarang"):
        if email_input:
            cleaned_input = clean_text(email_input)
            prob = model.predict_proba([cleaned_input])[0]
            skor_phishing = prob[1]
            
            st.markdown("---")
            if skor_phishing > 0.75:
                st.error(f"PHISHING ({skor_phishing*100:.1f}%)")
            elif skor_phishing > 0.40:
                st.warning(f"MENCURIGAKAN ({skor_phishing*100:.1f}%)")
            else:
                st.success(f"AMAN (Skor: {skor_phishing*100:.1f}%)")
        else:
            st.warning("Silakan masukkan teks terlebih dahulu.")
