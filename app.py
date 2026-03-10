import streamlit as st
import joblib
import re
import dns.resolver

st.set_page_config(page_title="Email Secure+", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,600;12..96,700;12..96,800&family=Instrument+Serif:ital@1&family=Geist+Mono:wght@400;500&display=swap');

/* ── Reset Streamlit chrome ─────────────────────────────── */
#MainMenu, header, footer, .stAppDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display:none !important; }

html, body, .stApp, [data-testid="stAppViewContainer"],
[data-testid="stMain"], .main, .block-container {
    background: #f8faf8 !important;
    font-family: 'Bricolage Grotesque', sans-serif !important;
    color: #0a0f0a !important;
}
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="stVerticalBlock"] { gap: 0 !important; }

/* ── Inputs ─────────────────────────────────────────────── */
.stTextInput input {
    background: white !important;
    border: 1.5px solid #e2e8e2 !important;
    border-radius: 14px !important;
    padding: 16px 20px !important;
    font-size: 15px !important;
    font-family: 'Bricolage Grotesque', sans-serif !important;
    color: #0a0f0a !important;
    box-shadow: 0 4px 20px rgba(0,0,0,.05) !important;
    transition: all .2s !important;
}
.stTextInput input:focus {
    border-color: #64f906 !important;
    box-shadow: 0 0 0 3px rgba(100,249,6,.12) !important;
    outline: none !important;
}
.stTextInput input::placeholder { color: #aab8aa !important; }
.stTextInput label { display: none !important; }

.stTextArea textarea {
    background: white !important;
    border: 1.5px solid #e2e8e2 !important;
    border-radius: 14px !important;
    padding: 18px 20px !important;
    font-size: 15px !important;
    font-family: 'Bricolage Grotesque', sans-serif !important;
    color: #0a0f0a !important;
    line-height: 1.7 !important;
    box-shadow: 0 4px 20px rgba(0,0,0,.05) !important;
    transition: all .2s !important;
    resize: vertical !important;
}
.stTextArea textarea:focus {
    border-color: #64f906 !important;
    box-shadow: 0 0 0 3px rgba(100,249,6,.12) !important;
    outline: none !important;
}
.stTextArea textarea::placeholder { color: #aab8aa !important; }
.stTextArea label { display: none !important; }

/* ── Button ─────────────────────────────────────────────── */
.stButton > button {
    background: #64f906 !important;
    color: #0a0f0a !important;
    border: none !important;
    border-radius: 999px !important;
    padding: 14px 36px !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    font-family: 'Bricolage Grotesque', sans-serif !important;
    letter-spacing: -.01em !important;
    width: 100% !important;
    transition: all .2s !important;
    box-shadow: 0 4px 24px rgba(100,249,6,.35) !important;
    cursor: pointer !important;
}
.stButton > button:hover {
    background: #7dff2a !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 32px rgba(100,249,6,.4) !important;
}

/* ── Spinner ─────────────────────────────────────────────── */
.stSpinner > div { border-top-color: #64f906 !important; }
</style>
""", unsafe_allow_html=True)


# ─── HELPERS ─────────────────────────────────────────────────────────────────

def clean_text(text: str) -> str:
    """Identik dengan fungsi clean_text di notebook training."""
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
        except Exception:
            pass
        try:
            for r in dns.resolver.resolve(f"_dmarc.{domain}", "TXT", lifetime=3):
                if "v=dmarc1" in r.to_text().lower():
                    result["has_dmarc"] = True
        except Exception:
            pass
    except Exception as e:
        result["error"] = str(e)
    return result

def dns_multiplier(d: dict) -> float:
    if d["error"]:
        return 1.0
    spf, dmarc = d["has_spf"], d["has_dmarc"]
    if spf and dmarc:   return 0.75
    elif spf or dmarc:  return 0.90
    else:               return 1.15

@st.cache_resource
def load_model():
    return joblib.load("phishing_model.joblib")

model = load_model()


# ─── HERO ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="position:relative;overflow:hidden;padding:30px 48px 60px;text-align:center;">

  <!-- Colorful blobs -->
  <div style="position:absolute;inset:0;pointer-events:none;overflow:hidden;">
    <div style="position:absolute;width:520px;height:520px;border-radius:50%;
      background:rgba(100,249,6,.20);filter:blur(90px);top:-120px;left:-80px;"></div>
    <div style="position:absolute;width:380px;height:380px;border-radius:50%;
      background:rgba(167,139,250,.22);filter:blur(80px);top:-60px;right:0;"></div>
    <div style="position:absolute;width:320px;height:320px;border-radius:50%;
      background:rgba(251,191,36,.18);filter:blur(70px);bottom:0;right:120px;"></div>
    <div style="position:absolute;width:260px;height:260px;border-radius:50%;
      background:rgba(45,212,191,.16);filter:blur(65px);bottom:-40px;left:200px;"></div>
    <div style="position:absolute;width:200px;height:200px;border-radius:50%;
      background:rgba(244,114,182,.14);filter:blur(60px);top:40px;left:40%;"></div>
  </div>

  <!-- Big title -->
  <h1 style="
    position:relative;z-index:2;
    font-size:clamp(64px,10vw,120px);
    font-size:150px;
    font-weight:800;
    letter-spacing:-4px;
    line-height:.88;
    color:#0a0f0a;
    margin-bottom:0;
  ">Email
    <span style="
      font-family:'Instrument Serif',serif;
      font-style:italic;
      color:#64f906;
      -webkit-text-stroke:0px;
    ">Secure+</span>
  </h1>

  <!-- Sub -->
  <p style="
    position:relative;z-index:2;
    margin:5px auto 0;
    max-width:full;
    font-size:16px;
    color:#5a6b5a;
    line-height:1.75;
  ">Detects phishing emails using AI text analysis and real-time DNS verification. Paste any suspicious email below.</p>

</div>
""", unsafe_allow_html=True)


# ─── INPUT FORM ───────────────────────────────────────────────────────────────
st.markdown("""
<div style="
  max-width:full;margin:0 auto;padding:0 24px 8px;
">
  <p style="font-size:12px;font-weight:700;letter-spacing:.08em;
    text-transform:uppercase;color:#8b9a8b;margin-bottom:6px;">
    Sender Email (example@gmai.com, noreply@company.org, etc)
  </p>
</div>
""", unsafe_allow_html=True)

col_pad1, col_form, col_pad2 = st.columns([1, 10, 1])
with col_form:
    sender_input = st.text_input("sender", placeholder="e.g. noreply@bank.com", label_visibility="collapsed")

st.markdown("""
<div style="max-width:620px;margin:0 auto;padding:12px 24px 6px;">
  <p style="font-size:12px;font-weight:700;letter-spacing:.08em;
    text-transform:uppercase;color:#8b9a8b;margin-bottom:6px;">
    Email Body
  </p>
</div>
""", unsafe_allow_html=True)

col_pad3, col_textarea, col_pad4 = st.columns([1, 10, 1])
with col_textarea:
    email_input = st.text_area("body", height=180,
        placeholder="Paste the suspicious email text here...",
        label_visibility="collapsed")

st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

col_pad5, col_btn, col_pad6 = st.columns([1, 10, 1])
with col_btn:
    analyze = st.button("Analyze Now →")


# ─── DIVIDER ─────────────────────────────────────────────────────────────────
st.markdown("""
<div style="max-width:620px;margin:32px auto;height:1px;background:#e2e8e2;"></div>
""", unsafe_allow_html=True)


# ─── RESULT ──────────────────────────────────────────────────────────────────
if analyze:
    if not email_input.strip():
        col_pad7, col_warn, col_pad8 = st.columns([1, 10, 1])
        with col_warn:
            st.markdown("""
            <div style="
              background:#fffbeb;border:1.5px solid #fde68a;
              border-radius:14px;padding:18px 22px;
              font-size:14px;color:#b45309;font-weight:600;
            ">⚠ Please paste an email body before analyzing.</div>
            """, unsafe_allow_html=True)
    else:
        with st.spinner("Analyzing..."):
            cleaned    = clean_text(email_input)
            prob       = model.predict_proba([cleaned])[0]
            raw_score  = float(prob[1])

            dns_result = None
            mult       = 1.0
            if sender_input.strip():
                dns_result = check_domain_dns(sender_input.strip())
                mult       = dns_multiplier(dns_result)

            score = min(max(raw_score * mult, 0.0), 1.0)
            pct   = score * 100

            # ── Verdict config ─────────────────────────────────────────
            if score >= 0.65:
                verdict  = "Phishing Detected"
                emoji    = "🚨"
                accent   = "#ef4444"
                bg       = "#fef2f2"
                border   = "#fecaca"
                txt_col  = "#dc2626"
                bar_col  = "#ef4444"
                desc     = "Strong phishing indicators found. Do not click any links or attachments. Delete this email and report it as spam."
            elif score >= 0.40:
                verdict  = "Suspicious Email"
                emoji    = "⚠️"
                accent   = "#f59e0b"
                bg       = "#fffbeb"
                border   = "#fde68a"
                txt_col  = "#b45309"
                bar_col  = "#f59e0b"
                desc     = "Some phishing-like patterns found. Be cautious — verify through another channel before clicking any links."
            else:
                verdict  = "Looks Safe"
                emoji    = "✅"
                accent   = "#64f906"
                bg       = "#f4fff0"
                border   = "#c3f58a"
                txt_col  = "#2a6600"
                bar_col  = "#64f906"
                desc     = "No significant phishing patterns detected. Still be cautious with unexpected requests for personal data."

            # ── DNS badge HTML ─────────────────────────────────────────
            dns_html = ""
            if dns_result and not dns_result["error"]:
                d = dns_result["domain"]
                spf_badge = (
                    f'<span style="background:#f0fdf4;border:1px solid #bbf7d0;color:#16a34a;'
                    f'padding:5px 12px;border-radius:8px;font-size:11px;font-weight:700;">✓ SPF</span>'
                    if dns_result["has_spf"] else
                    f'<span style="background:#fef2f2;border:1px solid #fecaca;color:#dc2626;'
                    f'padding:5px 12px;border-radius:8px;font-size:11px;font-weight:700;">✕ SPF</span>'
                )
                dmarc_badge = (
                    f'<span style="background:#f0fdf4;border:1px solid #bbf7d0;color:#16a34a;'
                    f'padding:5px 12px;border-radius:8px;font-size:11px;font-weight:700;">✓ DMARC</span>'
                    if dns_result["has_dmarc"] else
                    f'<span style="background:#fef2f2;border:1px solid #fecaca;color:#dc2626;'
                    f'padding:5px 12px;border-radius:8px;font-size:11px;font-weight:700;">✕ DMARC</span>'
                )
                dns_html = f"""
                <div style="margin-top:20px;padding-top:18px;border-top:1px solid {border};">
                  <p style="font-size:11px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;
                    color:#8b9a8b;margin-bottom:10px;">DNS · {d}</p>
                  <div style="display:flex;gap:8px;flex-wrap:wrap;">
                    {spf_badge}{dmarc_badge}
                  </div>
                </div>"""
            elif dns_result and dns_result["error"]:
                dns_html = f"""
                <div style="margin-top:20px;padding-top:18px;border-top:1px solid {border};">
                  <span style="font-size:12px;color:#8b9a8b;">DNS lookup unavailable</span>
                </div>"""

            # ── Render result card ─────────────────────────────────────
            col_p1, col_result, col_p2 = st.columns([1, 10, 1])
            with col_result:
                st.markdown(f"""
                <div style="
                  background:{bg};border:1.5px solid {border};
                  border-radius:20px;padding:32px;
                  box-shadow:0 8px 40px rgba(0,0,0,.06);
                ">
                  <!-- Verdict header -->
                  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;">
                    <div style="display:flex;align-items:center;gap:10px;">
                      <span style="font-size:28px;">{emoji}</span>
                      <span style="font-size:22px;font-weight:800;letter-spacing:-.5px;color:{txt_col};">{verdict}</span>
                    </div>
                    <span style="
                      font-family:'Geist Mono',monospace;
                      font-size:40px;font-weight:500;
                      color:{txt_col};letter-spacing:-2px;line-height:1;
                    ">{pct:.1f}%</span>
                  </div>

                  <!-- Risk bar -->
                  <div style="
                    height:8px;border-radius:999px;
                    background:rgba(0,0,0,.08);margin:18px 0 6px;overflow:hidden;
                  ">
                    <div style="
                      width:{pct}%;height:100%;border-radius:999px;
                      background:{bar_col};
                      box-shadow:0 0 12px {bar_col}88;
                    "></div>
                  </div>
                  <div style="display:flex;justify-content:space-between;
                    font-size:10px;color:{txt_col};opacity:.6;letter-spacing:.06em;margin-bottom:18px;">
                    <span>SAFE</span><span>DANGEROUS</span>
                  </div>

                  <!-- Description -->
                  <p style="font-size:14px;color:#4a5a4a;line-height:1.75;margin:0;">{desc}</p>

                  <!-- DNS -->
                  {dns_html}
                </div>
                """, unsafe_allow_html=True)


# ─── INFO BOX ────────────────────────────────────────────────────────────────
st.markdown("""
<div style="max-width:620px;margin:32px auto 0;padding:0 24px;">
  <div style="
    border-left:3px solid #64f906;
    background:white;
    border-radius:0 14px 14px 0;
    padding:18px 22px;
    box-shadow:0 4px 16px rgba(0,0,0,.04);
  ">
    <p style="font-size:13px;font-weight:700;color:#0a0f0a;margin-bottom:6px;">
      Can't highlight the email text?
    </p>
    <p style="font-size:13px;color:#6b7a6b;line-height:1.75;margin:0;">
      That's already a red flag. <strong style="color:#0a0f0a;">Image-Based Phishing</strong> uses
      screenshot images instead of text to bypass spam filters.
      Don't click anywhere in the image — delete and report as spam.
    </p>
  </div>
</div>
""", unsafe_allow_html=True)


# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
  margin-top:64px;
  padding:28px 48px;
  background:#0a0f0a;
  display:flex;align-items:center;justify-content:space-between;
  flex-wrap:wrap;gap:16px;
">
  <span style="font-weight:800;font-size:15px;color:white;letter-spacing:-.02em;">Email Secure+</span>
  <span style="font-size:11px;color:rgba(255,255,255,.3);letter-spacing:.04em;">
    TF-IDF · LOGISTIC REGRESSION · DNS SPF/DMARC · BUILT BY ZEFANYA VIOLETTA
  </span>
  <a href="https://github.com/violetsareblue97/email-secure" target="_blank"
     style="font-size:12px;color:#64f906;text-decoration:none;font-weight:600;">
    GitHub →
  </a>
</div>
""", unsafe_allow_html=True)