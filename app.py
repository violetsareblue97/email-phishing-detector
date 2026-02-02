import streamlit as st
import joblib
import re

# Konfigurasi Halaman
st.set_page_config(page_title="AI Phishing Detector")

# Fungsi Pembersih (Harus sama dengan saat latihan)
def clean_text(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', 'link_url', text)
    text = re.sub(r'\S+@\S+', 'email_address', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text

# Load Model
@st.cache_resource
def load_model():
    return joblib.load("phishing_model.joblib")

model = load_model()

# Tampilan UI
st.title("AI Phishing Detector")
st.write("Tempel isi email untuk mendeteksi potensi penipuan.")

email_input = st.text_area("Isi Email:", height=200, placeholder="Masukkan teks email di sini...")

if st.button("Analisis Sekarang"):
    if email_input:
        cleaned_input = clean_text(email_input)
        
        # Ambil probabilitas (Skor keyakinan)
        prob = model.predict_proba([cleaned_input])[0]
        skor_phishing = prob[1] # Probabilitas label 1 (Phishing)
        
        st.subheader("Hasil Analisis:")
        
        # Logika Threshold agar tidak terlalu sensitif
        if skor_phishing > 0.75:
            st.error(f"POSITIF PHISHING (Keyakinan: {skor_phishing*100:.2f}%)")
            st.write("Indikasi kuat penipuan. Jangan klik link apa pun dari email ini.")
        elif skor_phishing > 0.40:
            st.warning(f"MENCURIGAKAN (Keyakinan: {skor_phishing*100:.2f}%)")
            st.write("Email ini memiliki pola yang mirip phishing. Tetap waspada.")
        else:
            st.success(f"AMAN (Skor Phishing: {skor_phishing*100:.2f}%)")
            st.write("Email ini terlihat seperti korespondensi normal.")
    else:
        st.warning("Mohon masukkan teks terlebih dahulu.")
