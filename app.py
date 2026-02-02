import streamlit as st
import joblib
import re

# 1. Konfigurasi Halaman & CSS Hero Section
st.set_page_config(page_title="Email Secure+", layout="wide")

st.markdown("""
    <style>
    /* Font dan Background Global */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap');
    
    .stApp {
        background-color: #f8f9fa;
        font-family: 'Inter', sans-serif;
        color: #1a1a1a;
    }

    /* Header Navigation */
    .nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 20px 5%;
        background: white;
        border-bottom: 1px solid #eee;
    }
    .brand { font-weight: 700; font-size: 20px; letter-spacing: 1px; }

    /* Hero Section Layout */
    .hero-container {
        display: flex;
        align-items: center;
        padding: 80px 10%;
        gap: 50px;
    }

    .hero-text { flex: 1; }
    .hero-image { flex: 1; text-align: center; }

    .headline {
        font-size: 48px;
        font-weight: 800;
        line-height: 1.1;
        margin-bottom: 20px;
        color: #1a1a1a;
    }

    /* Input Area Styling */
    .stTextArea textarea {
        border-radius: 12px !important;
        border: 1px solid #ddd !important;
        padding: 15px !important;
        background: white !important;
        color: #333 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05) !important;
    }

    /* Button Styling */
    .stButton>button {
        background-color: #10b981 !important;
        color: white !important;
        border: none !important;
        padding: 12px 30px !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        transition: 0.3s;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #059669 !important;
        transform: translateY(-2px);
    }

    /* Ilustrasi Email Simpel */
    .email-illustration {
        background: #10b981;
        width: 300px;
        height: 200px;
        margin: 0 auto;
        border-radius: 20px;
        position: relative;
        box-shadow: 20px 20px 0px #d1fae5;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Logika Pembersihan & Model
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', 'url', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text

@st.cache_resource
def load_model():
    return joblib.load("phishing_model.joblib")

model = load_model()

# 3. Struktur Navigasi
st.markdown("""
    <div class="nav-bar">
        <div class="brand">EMAIL SECURE+</div>
        <div style="display: flex; gap: 30px; font-size: 14px; color: #666;">
            <span>Features</span><span>Support</span><span>Dashboard</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 4. Hero Section
col_text, col_img = st.columns([1.2, 1])

with col_text:
    st.markdown('<div class="headline">TOTAL<br>INBOX<br>PROTECTED</div>', unsafe_allow_html=True)
    st.write("Analisis email Anda secara instan dengan teknologi kecerdasan buatan.")
    
    email_input = st.text_area("Tempel teks email di sini", height=200, label_visibility="collapsed", placeholder="Enter email content...")
    
    if st.button("ANALISIS SEKARANG"):
        if email_input:
            cleaned = clean_text(email_input)
            prob = model.predict_proba([cleaned])[0][1]
            
            st.markdown("---")
            if prob > 0.75:
                st.error(f"Status: Phishing Detected ({prob*100:.1f}%)")
            elif prob > 0.40:
                st.warning(f"Status: Suspicious ({prob*100:.1f}%)")
            else:
                st.success(f"Status: Safe ({prob*100:.1f}%)")
        else:
            st.info("Mohon masukkan teks terlebih dahulu.")

with col_img:
    # Menggunakan komponen visual pengganti foto orang
    st.markdown("""
        <div style="padding-top: 50px;">
            <div style="background: #10b981; padding: 60px; border-radius: 30px; text-align: center; color: white;">
                <div style="font-size: 80px;">✉️</div>
                <div style="font-weight: 800; font-size: 20px; margin-top: 10px;">SECURE ANALYTICS</div>
                <div style="background: white; color: #10b981; display: inline-block; padding: 5px 15px; border-radius: 20px; font-size: 12px; margin-top: 15px; font-weight: bold;">NEW UPDATE</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# 5. Share Button (Minimalis di bawah)
if st.sidebar.button("Share Application"):
    st.sidebar.code("https://share.streamlit.io/your-link")
