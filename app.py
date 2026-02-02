import streamlit as st
import joblib
import re

# 1. Konfigurasi Halaman & CSS Custom
st.set_page_config(page_title="AI Phishing Detector", page_icon="🛡️", layout="wide")

st.markdown("""
    <style>
    /* Mengatur Background Utama dan Font */
    .stApp {
        background-color: #2c4f40;
        color: white;
        font-family: 'Helvetica', sans-serif;
    }

    /* Mengatur Bar Judul di Atas */
    .header-bar {
        background-color: rgba(255, 255, 255, 0.1);
        padding: 20px;
        border-radius: 0px 0px 15px 15px;
        text-align: center;
        margin-bottom: 30px;
        border-bottom: 2px solid #ffffff33;
    }

    /* Mengatur Kotak Input Teks agar lebih "Pop" */
    .stTextArea textarea {
        background-color: #ffffff !important;
        color: #333333 !important;
        border-radius: 15px !important;
        border: 2px solid #f0f2f6 !important;
        font-size: 16px !important;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.3) !important;
    }

    /* Mengatur Tombol Analisis */
    .stButton>button {
        width: 100%;
        background-color: #ffffff !important;
        color: #2c4f40 !important;
        font-weight: bold !important;
        height: 50px !important;
        border-radius: 25px !important;
        border: none !important;
        transition: 0.3s !important;
        font-size: 18px !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .stButton>button:hover {
        background-color: #e0e0e0 !important;
        transform: scale(1.02);
    }
    
    /* Warna teks label input */
    label {
        color: white !important;
        font-weight: bold !important;
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

# 3. Tampilan Header
st.markdown('<div class="header-bar"><h1>🛡️ AI PHISHING EMAIL DETECTOR</h1></div>', unsafe_allow_html=True)

# 4. Konten Utama
col1, col2, col3 = st.columns([1, 2, 1]) # Membuat layout tengah

with col2:
    st.write("Gunakan teknologi AI untuk memverifikasi keamanan pesan Anda.")
    
    email_input = st.text_area("Tempel isi email di bawah ini:", height=250)
    
    st.markdown("<br>", unsafe_allow_html=True) # Spasi
    
    if st.button("Analisis Sekarang"):
        if email_input:
            cleaned_input = clean_text(email_input)
            prob = model.predict_proba([cleaned_input])[0]
            skor_phishing = prob[1]
            
            st.markdown("---")
            if skor_phishing > 0.75:
                st.error(f"⚠️ POSITIF PHISHING ({skor_phishing*100:.1f}%)")
                st.info("Saran: Jangan klik link atau memberikan data pribadi.")
            elif skor_phishing > 0.40:
                st.warning(f"🧐 MENCURIGAKAN ({skor_phishing*100:.1f}%)")
            else:
                st.success(f"✅ AMAN (Skor: {skor_phishing*100:.1f}%)")
        else:
            st.warning("Masukkan teks terlebih dahulu.")
