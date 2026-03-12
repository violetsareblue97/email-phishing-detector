import streamlit as st
import joblib
import re
import dns.resolver
import os
from dotenv import load_dotenv
import google.genai as genai

load_dotenv()

st.set_page_config(
    page_title="Email Secure+",
    layout="wide", # Changed to wide to allow more horizontal space
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,700;12..96,800&family=Instrument+Serif:ital@1&family=Geist+Mono:wght@400;500&display=swap');

/* Hide Streamlit chrome */
#MainMenu, header, footer, .stAppDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }

/* Background setup */
html, body { margin: 0; padding: 0; background: #f0f7f0; }

/* Blob hijau — top left */
body::after {
    content: ''; position: fixed;
    width: 650px; height: 650px; border-radius: 50%;
    background: rgba(100,249,6,.22); filter: blur(110px);
    top: -180px; left: -180px; z-index: 0; pointer-events: none;
}
/* Blob ungu — top right */
.blob-purple {
    position: fixed; width: 550px; height: 550px; border-radius: 50%;
    background: rgba(167,139,250,.20); filter: blur(110px);
    top: -100px; right: -140px; z-index: 0; pointer-events: none;
}
/* Blob kuning — bottom center */
.blob-yellow {
    position: fixed; width: 480px; height: 480px; border-radius: 50%;
    background: rgba(251,191,36,.16); filter: blur(100px);
    bottom: -80px; left: 30%; z-index: 0; pointer-events: none;
}
/* Blob teal — bottom right */
.blob-teal {
    position: fixed; width: 400px; height: 400px; border-radius: 50%;
    background: rgba(45,212,191,.14); filter: blur(95px);
    bottom: -60px; right: -80px; z-index: 0; pointer-events: none;
}
/* Blob pink — center left */
.blob-pink {
    position: fixed; width: 320px; height: 320px; border-radius: 50%;
    background: rgba(244,114,182,.12); filter: blur(90px);
    top: 40%; left: -60px; z-index: 0; pointer-events: none;
}

.stApp {
    background: transparent !important;
    font-family: 'Bricolage Grotesque', sans-serif !important;
}

/* Adjusting the main container width and padding */
.block-container {
    padding: 60px 80px !important;
    max-width: 1200px !important;
    position: relative; z-index: 2;
}

[data-testid="stAppViewContainer"],
[data-testid="stMain"], .main {
    background: transparent !important;
}

/* UI Elements Styling */
.stTextInput input, .stTextArea textarea {
    background: rgba(255,255,255,.95) !important;
    border: 1.5px solid #dde8dd !important;
    border-radius: 12px !important;
    font-family: 'Bricolage Grotesque', sans-serif !important;
    box-shadow: 0 2px 10px rgba(0,0,0,.02) !important;
}

.stButton > button {
    background: #64f906 !important;
    color: #0a0f0a !important;
    border-radius: 1000px !important;
    padding: 14px 36px !important;
    font-weight: 700 !important;
    width: 100% !important;
    box-shadow: 0 4px 20px rgba(100,249,6,.3) !important;
}

.field-label {
    font-size: 11px;
    font-weight: 700;
    letter-spacing: .1em;
    text-transform: uppercase;
    color: #7a8c7a;
    margin-bottom: 4px;
    display: block;
}
</style>
<!-- Blob divs — position:fixed so they cover the entire page -->
<div class="blob-purple"></div>
<div class="blob-yellow"></div>
<div class="blob-teal"></div>
<div class="blob-pink"></div>
""", unsafe_allow_html=True)

# ------------------------ HELPER FUNCTIONS ---------------------------

def clean_text(text: str) -> str:
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', 'link_url', text)
    text = re.sub(r'\S+@\S+', 'email_address', text)
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return text

def check_domain_dns(sender: str) -> dict:
    result = {"domain": "", "has_spf": False, "has_dmarc": False, "error": None}
    try:
        if "@" not in sender:
            result["error"] = "invalid"
            return result
        domain = sender.strip().split("@")[-1].lower()
        result["domain"] = domain
        try:
            for r in dns.resolver.resolve(domain, "TXT", lifetime=3):
                if "v=spf1" in r.to_text().lower():
                    result["has_spf"] = True
        except: pass
        try:
            for r in dns.resolver.resolve(f"_dmarc.{domain}", "TXT", lifetime=3):
                if "v=dmarc1" in r.to_text().lower():
                    result["has_dmarc"] = True
        except: pass
    except Exception as e:
        result["error"] = str(e)
    return result

def dns_score_multiplier(d: dict) -> float:
    if d["error"]: return 1.0
    spf, dmarc = d["has_spf"], d["has_dmarc"]
    if spf and dmarc: return 0.75
    elif spf or dmarc: return 0.90
    else: return 1.15

def build_dns_warning(dns_result: dict) -> str:
    if not dns_result or dns_result["error"]: return ""
    spf, dmarc = dns_result["has_spf"], dns_result["has_dmarc"]
    domain = dns_result["domain"]
    if not spf and not dmarc:
        return f"<strong>{domain}</strong> has no SPF or DMARC records. Anyone can forge emails from this domain — treat this email with extra caution."
    if not dmarc:
        return f"<strong>{domain}</strong> has SPF but no DMARC. Without DMARC, spoofed emails from this domain can still reach inboxes."
    if not spf:
        return f"<strong>{domain}</strong> has DMARC but no SPF. This unusual configuration may indicate a misconfigured or spoofed sender."
    return ""

def get_llm_explanation(email_text: str, verdict: str, score_pct: float) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key: return "API Key not found."
    try:
        client = genai.Client(api_key=api_key)
        prompt = f"Explain why this email is '{verdict}' (Risk: {score_pct:.1f}%). Email: {email_text[:500]}"
        response = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
        return response.text.strip()
    except:
        return "Explanation unavailable."

@st.cache_resource
def load_model():
    return joblib.load("phishing_model.joblib")

# ----------------- MAIN LAYOUT -----------------

model = load_model()

# Splitting the screen into two main columns
left_col, right_col = st.columns([1, 1.2], gap="large")

with left_col:
    # Branding and Info
    st.markdown("""
    <div style="margin-top:20px;">
        <p style="font-size:11px; font-weight:700; letter-spacing:.16em; text-transform:uppercase; color:#7a8c7a;">
            AI-Powered Phishing Detector
        </p>
        <h1 style="font-size:72px; font-weight:800; letter-spacing:-3px; line-height:.9; color:#0a0f0a; margin:10px 0;">
            Email<br><span style="font-family:'Instrument Serif',serif; font-style:italic; color:#3d8c00;">Secure+</span>
        </h1>
        <p style="font-size:15px; color:#4a5a4a; line-height:1.7; margin-bottom:40px;">
            Analyzes email text with machine learning and verifies sender domain via DNS lookup.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Warning Box
    st.markdown("""
    <div style="padding:20px; background:rgba(255,251,235,1); border:1.5px solid #fde68a; border-radius:12px;">
        <p style="font-size:13px; font-weight:700; color:#92400e; margin-bottom:5px;">Image-Based Phishing Warning</p>
        <p style="font-size:13px; color:#b45309; line-height:1.6;">
            This tool reads <b>text only</b>. If you can't highlight or copy the content, it is likely an image attack.
        </p>
    </div>
    """, unsafe_allow_html=True)

with right_col:
    # Input Form
    st.markdown('<span class="field-label">Sender Address</span>', unsafe_allow_html=True)
    sender_input = st.text_input("sender", placeholder="e.g. noreply@abc.com", label_visibility="collapsed")
    
    st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
    
    st.markdown('<span class="field-label">Email Body</span>', unsafe_allow_html=True)
    email_input = st.text_area("body", height=250, placeholder="Paste email content here...", label_visibility="collapsed")
    
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    analyze = st.button("Analyze Now")

    # Results Section
    if analyze:
        if not email_input.strip():
            st.error("Please provide email text.")
        else:
            with st.spinner("Analyzing..."):
                cleaned = clean_text(email_input)
                prob = model.predict_proba([cleaned])[0]
                raw_score = float(prob[1])
                
                dns_result = None
                mult = 1.0
                if sender_input.strip():
                    dns_result = check_domain_dns(sender_input.strip())
                    mult = dns_score_multiplier(dns_result)
                
                score = min(max(raw_score * mult, 0.0), 1.0)
                pct = score * 100
                
                # Simple Verdict Logic
                if score >= 0.65:
                    verdict, color, bg = "Phishing Detected", "#dc2626", "rgba(254,242,242,1)"
                    bar_col = "#ef4444"
                    desc = "Strong phishing indicators found. Do not click any links or attachments."
                elif score >= 0.40:
                    verdict, color, bg = "Suspicious Email", "#b45309", "rgba(255,251,235,1)"
                    bar_col = "#f59e0b"
                    desc = "Some phishing-like patterns found. Verify the sender before taking action."
                else:
                    verdict, color, bg = "Looks Safe", "#2a6600", "rgba(240,253,240,1)"
                    bar_col = "#64f906"
                    desc = "No significant phishing patterns detected. Stay cautious with personal data requests."

                # Verdict card
                st.markdown(f"""
                <div style="padding:25px; background:{bg}; border:1px solid {color}33;
                  border-radius:14px; margin-top:20px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                        <span style="font-weight:800; color:{color}; font-size:20px;">{verdict}</span>
                        <span style="font-family:'Geist Mono',monospace; font-size:32px;
                          font-weight:600; color:{color}; letter-spacing:-1px;">{pct:.1f}%</span>
                    </div>
                    <div style="height:5px; border-radius:999px;
                      background:rgba(0,0,0,.08); overflow:hidden; margin-bottom:6px;">
                        <div style="width:{pct}%; height:100%; border-radius:999px;
                          background:{bar_col};"></div>
                    </div>
                    <div style="display:flex; justify-content:space-between;
                      font-size:10px; color:{color}; opacity:.5;
                      letter-spacing:.07em; margin-bottom:14px;">
                        <span>SAFE</span><span>DANGEROUS</span>
                    </div>
                    <p style="font-size:13px; color:#3a4a3a; line-height:1.7; margin:0;">{desc}</p>
                </div>
                """, unsafe_allow_html=True)

                # DNS warning — only shown when SPF or DMARC is missing
                dns_warning = build_dns_warning(dns_result)
                if dns_warning:
                    st.markdown(f"""
                    <div style="margin-top:10px; padding:14px 16px;
                      background:rgba(254,242,242,.95);
                      border-left:4px solid #ef4444;
                      border-radius:0 10px 10px 0;">
                      <p style="font-size:12px; font-weight:700; color:#b91c1c;
                        margin:0 0 4px; letter-spacing:.02em;">
                        DNS Authentication Warning
                      </p>
                      <p style="font-size:13px; color:#dc2626; line-height:1.65; margin:0;">
                        {dns_warning}
                      </p>
                    </div>
                    """, unsafe_allow_html=True)

                # DNS verification badges — always show if sender was provided
                if dns_result and not dns_result["error"]:
                    domain   = dns_result["domain"]
                    spf_ok   = dns_result["has_spf"]
                    dmarc_ok = dns_result["has_dmarc"]

                    # Green for pass, red for fail
                    spf_style   = ("background:#f0fdf4; border:1px solid #bbf7d0; color:#16a34a;"
                                   if spf_ok else
                                   "background:#fef2f2; border:1px solid #fecaca; color:#dc2626;")
                    dmarc_style = ("background:#f0fdf4; border:1px solid #bbf7d0; color:#16a34a;"
                                   if dmarc_ok else
                                   "background:#fef2f2; border:1px solid #fecaca; color:#dc2626;")
                    spf_label   = "SPF  pass"   if spf_ok   else "SPF  fail"
                    dmarc_label = "DMARC  pass" if dmarc_ok else "DMARC  fail"

                    st.markdown(f"""
                    <div style="margin-top:10px; padding:16px 18px;
                      background:rgba(255,255,255,.85);
                      border:1.5px solid #e4ede4; border-radius:12px;">
                      <p style="font-size:11px; font-weight:700; letter-spacing:.1em;
                        text-transform:uppercase; color:#8b9a8b; margin:0 0 10px;">
                        DNS Verification
                        <span style="font-weight:400; text-transform:none;
                          letter-spacing:.04em; color:#b0bcb0; margin-left:6px;">
                          {domain}
                        </span>
                      </p>
                      <div style="display:flex; gap:8px; flex-wrap:wrap;">
                        <span style="{spf_style} padding:5px 14px; border-radius:8px;
                          font-size:12px; font-weight:700;">{spf_label}</span>
                        <span style="{dmarc_style} padding:5px 14px; border-radius:8px;
                          font-size:12px; font-weight:700;">{dmarc_label}</span>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                elif dns_result and dns_result["error"]:
                    st.markdown("""
                    <div style="margin-top:10px; padding:12px 16px;
                      background:rgba(255,255,255,.7);
                      border:1.5px solid #e4ede4; border-radius:10px;
                      font-size:12px; color:#8b9a8b;">
                      DNS lookup unavailable for this sender.
                    </div>
                    """, unsafe_allow_html=True)

                # AI explanation
                llm_explanation = get_llm_explanation(
                    email_text=email_input, verdict=verdict, score_pct=pct
                )
                st.markdown(f"""
                <div style="margin-top:10px; padding:18px 20px;
                  background:rgba(255,255,255,.78);
                  border:1.5px solid #e4ede4; border-radius:12px;">
                  <p style="font-size:11px; font-weight:700; letter-spacing:.1em;
                    text-transform:uppercase; color:#8b9a8b; margin:0 0 8px;">
                    AI Analysis
                  </p>
                  <p style="font-size:13px; color:#3a4a3a; line-height:1.8; margin:0;">
                    {llm_explanation}
                  </p>
                </div>
                """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="margin-top:60px; padding:20px; background:#0a0f0a; border-radius:12px; display:flex; justify-content:space-between; align-items:center;">
    <span style="color:white; font-weight:700;">Email Secure+</span>
    <a href="#" style="color:#64f906; text-decoration:none; font-size:12px;">GitHub</a>
</div>
""", unsafe_allow_html=True)