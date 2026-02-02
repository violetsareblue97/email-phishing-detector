import streamlit as st
import joblib

# Memuat otak AI yang kita buat di Colab
model = joblib.load("phishing_model.joblib")

st.set_page_config(page_title="AI Phishing Detector", icon="🛡️")
st.title("🛡️ AI Phishing Email Detector")
st.write("Gunakan AI untuk mendeteksi apakah email ini berbahaya atau aman.")

# Input teks dari user
email_text = st.text_area("Tempel isi email di sini:", height=200)

if st.button("Cek Email"):
    if email_text:
        prediction = model.predict([email_text])[0]
        prob = model.predict_proba([email_text])[0]

        if prediction == 1:
            st.error(f"⚠️ Hati-hati! Ini terdeteksi PHISHING (Akurasi: {prob[1]*100:.2f}%)")
        else:
            st.success(f"✅ Aman. Ini terlihat seperti email normal (Akurasi: {prob[0]*100:.2f}%)")
    else:
        st.warning("Silakan masukkan teks email terlebih dahulu.")
