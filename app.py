import streamlit as st
import joblib
import re
import unicodedata
import dns.resolver

st.set_page_config(page_title="EmailSecure", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&display=swap');
    
    /* 1. Menghapus Navbar, Settings, dan Footer */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    .stAppDeployButton {display:none;}

    .stApp {
        background-color: #050505;
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #e6edf3;
    }

    /* Minimalist Header Futuristik */
    .main-header {
        text-align: center;
        padding: 40px 0 20px 0;
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
        color: #ffffff;
        letter-spacing: -1px;
        line-height: 1.2;
    }

    /* 2. Custom Style untuk Label di atas Input */
    .input-label {
        font-size: 14px;
        font-weight: 600;
        color: #8b949e;
        margin-bottom: 8px;
        margin-top: 15px;
    }

    /* 3. Menyamakan Desain Text Input dan Text Area */
    .stTextInput input, .stTextArea textarea {
        border-radius: 16px !important;
        border: 1px solid #1f2937 !important;
        padding: 16px 24px !important;
        background: #0d1117 !important;
        font-size: 16px !important;
        color: #ffffff !important;
        transition: all 0.3s ease;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #10b981 !important;
        background: #0d1117 !important;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.1) !important;
        outline: none !important;
    }

    /* Button Glow */
    .stButton>button {
        background-color: #ffffff !important;
        color: black !important;
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
        color: white !important;
        transform: translateY(-1px);
    }

    /* Result Cards */
    .result-container {
        margin-top: 40px;
        padding: 24px;
        border-radius: 16px;
        border: 1px solid #1f2937;
        background: #111111;
    }
    </style>
    """, unsafe_allow_html=True)

def check_domain_safety(sender_input):
    trusted = ['google.com', 'apple.com', 'microsoft.com', 'accounts.google.com']
    try:
        domain = sender_input.split('@')[-1].lower()
        if domain in trusted:
            return True
    except: pass
    return False

def clean_text_accurate(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = text.lower()
    text = re.sub(r'http\S+|www\S+|https\S+', 'link_url', text)
    text = re.sub(r'\S+@\S+', 'email_address', text)
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

#Header
st.markdown("""
    <div class="main-header">
        <div class="brand-name">Email Safe+</div>
        <div class="main-title">Deteksi Email Phishing<br>Berbasis AI</div>
    </div>
    """, unsafe_allow_html=True)

#form isi
st.markdown('<p class="input-label">Alamat Pengirim (contoh: abc@gmail.com)</p>', unsafe_allow_html=True)
sender_input = st.text_input(label="", label_visibility="collapsed", placeholder="Alamat email pengirim...")

st.markdown('<p class="input-label">Isi badan email:</p>', unsafe_allow_html=True)
email_input = st.text_area(label="", label_visibility="collapsed", height=220, placeholder="Tempel isi badan email yang ingin diperiksa disini...")

#button
if st.button("Analisis Keamanan"):
    if email_input:
        cleaned = clean_text_accurate(email_input)
        prob = model.predict_proba([cleaned])[0]
        skor = prob[1]
        
        if sender_input and check_domain_safety(sender_input):
            skor = skor * 0.1 

        st.markdown('<div class="result-container">', unsafe_allow_html=True)
        
        if skor > 0.65:
            st.error(f"Peringatan: Terdeteksi Phishing ({skor*100:.1f}%)")
            st.markdown("<small>Ditemukan manipulasi teks atau indikasi penipuan yang kuat.</small>", unsafe_allow_html=True)
        elif skor > 0.35:
            st.warning(f"Perhatian: Email Mencurigakan ({skor*100:.1f}%)")
            st.markdown("<small>Pola email ini menyerupai phishing. Harap waspada.</small>", unsafe_allow_html=True)
        else:
            st.success(f"Aman: Email Terverifikasi ({skor*100:.1f}%)")
            st.markdown("<small>Tidak ditemukan tanda-tanda ancaman siber yang mencurigakan.</small>", unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Silakan masukkan teks email terlebih dahulu.")

#informasi
st.markdown("""
    <div class="info-container" style="margin-top:40px; padding:20px; border-left:4px solid #10b981; background:#111111;">
        <div class="info-title" style="color:white; font-weight:bold;">⚠️ Tidak bisa menyalin teks email?</div>
        <div class="info-text" style="color:#8b949e; font-size:14px;">
            Jika email Anda sepenuhnya berupa gambar (tidak bisa di-highlight), ini adalah tanda kuat <b>Image-Based Phishing</b>. 
            Scammer menggunakan teknik ini untuk menghindari filter keamanan teks. 
            <b>Jangan klik bagian mana pun dari gambar tersebut!</b> Segera hapus dan lapor sebagai spam.
        </div>
    </div>
""", unsafe_allow_html=True)
