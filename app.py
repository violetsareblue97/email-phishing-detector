import streamlit as st
import joblib
import re

# 1. Konfigurasi Halaman & UI Styling
st.set_page_config(page_title="Email Secure+", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;800&display=swap');
    
    .stApp {
        background-color: #f8f9fa;
        font-family: 'Inter', sans-serif;
        color: #1a1a1a;
    }

    /* Navigasi Minimalis */
    .nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 8%;
        background: white;
        border-bottom: 1px solid #eee;
    }
    .brand { font-weight: 800; font-size: 22px; color: #10b981; }

    /* Judul Utama */
    .headline {
        font-size: 64px;
        font-weight: 800;
        line-height: 1;
        margin-bottom: 25px;
        color: #1a1a1a;
        letter-spacing: -2px;
    }

    /* Kotak Input Teks Pop */
    .stTextArea textarea {
        border-radius: 16px !important;
        border: 1px solid #e5e7eb !important;
        padding: 20px !important;
        background: white !important;
        font-size: 16px !important;
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05) !important;
    }

    /* Tombol Analisis */
    .stButton>button {
        background-color: #10b981 !important;
        color: white !important;
        border: none !important;
        padding: 15px 0px !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        width: 100%;
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #059669 !important;
        transform: translateY(-2px);
    }

    /* Card Ilustrasi */
    .card-right {
        background: #10b981;
        padding: 80px 40px;
        border-radius: 40px;
        text-align: center;
        color: white;
        box-shadow: 30px 30px 0px #d1fae5;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Logika Pemrosesan (SAMA PERSIS DENGAN PERMINTAAN ANDA)
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
st.markdown("""
    <div class="nav-bar">
        <div class="brand">EMAIL SECURE+</div>
        <div style="display: flex; gap: 40px; font-size: 14px; font-weight: 600; color: #4b5563;">
            <span>Features</span><span>Support</span><span>Dashboard</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

# 4. Layout Utama (Hero Section)
col_left, col_right = st.columns([1.2, 1], gap="large")

with col_left:
    st.markdown('<div class="headline">TOTAL<br>INBOX<br>PROTECTED.</div>', unsafe_allow_html=True)
    st.write("Analisis keamanan email Anda secara instan menggunakan model AI yang transparan dan akurat.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Text Area
    email_input = st.text_area("Isi Email:", height=250, label_visibility="collapsed", placeholder="Enter your email content here...")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("ANALISIS SEKARANG"):
        if email_input:
            cleaned_input = clean_text(email_input)
            
            # Ambil probabilitas (Skor keyakinan)
            prob = model.predict_proba([cleaned_input])[0]
            skor_phishing = prob[1] # Probabilitas label 1 (Phishing)
            
            st.markdown("---")
            
            # Logika Threshold (Sesuai kode Anda)
            if skor_phishing > 0.75:
                st.error(f"Status: Positif Phishing ({skor_phishing*100:.2f}%)")
                st.write("Indikasi kuat penipuan. Jangan klik link apa pun!")
            elif skor_phishing > 0.40:
                st.warning(f"Status: Mencurigakan ({skor_phishing*100:.2f}%)")
                st.write("Email ini memiliki pola yang mirip phishing. Tetap waspada.")
            else:
                st.success(f"Status: Aman ({skor_phishing*100:.2f}%)")
                st.write("Email ini terlihat seperti korespondensi normal.")
        else:
            st.warning("Mohon masukkan teks terlebih dahulu.")

with col_right:
    # Ilustrasi Email Minimalis
    st.markdown("""
        <div class="card-right">
            <div style="font-size: 100px; margin-bottom: 20px;">🛡️</div>
            <div style="font-weight: 800; font-size: 24px;">AI PROTECTION</div>
            <div style="opacity: 0.8; font-size: 14px; margin-top: 10px;">Security Model Version 2.4</div>
            <div style="background: rgba(255,255,255,0.2); display: inline-block; padding: 8px 20px; border-radius: 50px; font-size: 12px; margin-top: 30px; font-weight: 700; border: 1px solid white;">
                SYSTEM ACTIVE
            </div>
        </div>
    """, unsafe_allow_html=True)

# 5. Share Functionality di Sidebar
with st.sidebar:
    st.write("### Share Application")
    if st.button("Copy App Link"):
        st.code("https://share.streamlit.io/your-link")
