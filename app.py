import streamlit as st
import joblib
import re
import unicodedata

# 1. CSS untuk Desain Sleek & Modern
st.set_page_config(page_title="SecureMail AI", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    .stApp {
        background-color: #ffffff;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Minimalist Header */
    .main-header {
        text-align: center;
        padding: 60px 0 20px 0;
    }
    
    .brand-name {
        font-weight: 800;
        font-size: 14px;
        letter-spacing: 3px;
        color: #10b981;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .main-title {
        font-size: 42px;
        font-weight: 800;
        color: #111827;
        letter-spacing: -1px;
        line-height: 1.2;
    }

    /* Input Area */
    .stTextArea textarea {
        border-radius: 16px !important;
        border: 1px solid #f3f4f6 !important;
        padding: 24px !important;
        background: #f9fafb !important;
        font-size: 16px !important;
        color: #374151 !important;
        transition: all 0.3s ease;
    }

    .stTextArea textarea:focus {
        border-color: #10b981 !important;
        background: #ffffff !important;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05) !important;
    }

    /*  Button */
    .stButton>button {
        background-color: #111827 !important;
        color: white !important;
        padding: 14px 28px !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        border: none !important;
        width: 100% !important;
        margin-top: 20px;
        transition: all 0.2s ease;
    }

    .stButton>button:hover {
        background-color: #10b981 !important;
        transform: translateY(-1px);
    }

    /* Result Cards */
    .result-container {
        margin-top: 40px;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #f3f4f6;
        color: #1a1a1a
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Logika Akurasi Tinggi (Advanced Preprocessing)
def clean_text_accurate(text):
    # Normalisasi karakter unik (Unicode) agar teks aneh bisa dibaca
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = text.lower()
    
    # Menjaga konteks URL dan Email
    text = re.sub(r'http\S+|www\S+|https\S+', 'link_url', text)
    text = re.sub(r'\S+@\S+', 'email_address', text)
    
    # Urgency Tagging untuk deteksi pola tekanan
    urgency_list = ['action required', 'pending', 'selected', 'reward', 'confirm', 'immediately']
    for word in urgency_list:
        text = text.replace(word, f' urgent_{word} ')
        
    text = re.sub(r'[^a-zA-Z\s]', ' ', text)
    text = " ".join(text.split())
    return text

@st.cache_resource
def load_model():
    return joblib.load("phishing_model.joblib")

model = load_model()

# 3. Tampilan UI Sleek
st.markdown("""
    <div class="main-header">
        <div class="brand-name">Secure Analytics</div>
        <div class="main-title">Deteksi Phishing<br>Berbasis AI</div>
    </div>
    """, unsafe_allow_html=True)

# Container Tengah
col1, col2, col3 = st.columns([0.1, 0.8, 0.1])

with col2:
    email_input = st.text_area("", height=220, placeholder="Tempel konten email yang ingin Anda periksa...")
    
    if st.button("Analisis Keamanan"):
        if email_input:
            # Eksekusi Logika Akurat
            cleaned = clean_text_accurate(email_input)
            prob = model.predict_proba([cleaned])[0]
            skor = prob[1]
            
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            
            if skor > 0.65:
                st.error(f"Peringatan: Terdeteksi Phishing ({skor*100:.1f}%)")
                st.markdown("<small>Ditemukan manipulasi teks atau indikasi penipuan yang kuat.</small>", unsafe_allow_html=True)
            elif skor > 0.35:
                st.warning(f"Perhatian: Email Mencurigakan ({skor*100:.1f}%)")
                st.markdown("<small>Pola email ini menyerupai teknik phishing umum. Harap waspada.</small>", unsafe_allow_html=True)
            else:
                st.success(f"Aman: Email Terverifikasi ({skor*100:.1f}%)")
                st.markdown("<small>Tidak ditemukan tanda-tanda ancaman siber yang mencurigakan.</small>", unsafe_allow_html=True)
                
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Silakan masukkan teks email terlebih dahulu.")

st.markdown("<br><br><p style='text-align:center; color:#9ca3af; font-size:12px;'>Powered by AI Security Engine v2.5</p>", unsafe_allow_html=True)
