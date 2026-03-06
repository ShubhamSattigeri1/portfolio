"""
Portfolio QR Code App — no database, no storage.
All details are encoded directly in the QR URL as query parameters.
When scanned, the phone opens the profile page and reads details from the URL.
"""

import qrcode
import urllib.parse
import streamlit as st
import base64
from io import BytesIO

BASE_URL = "http://192.168.29.172:8501/"  # Set to your deployed URL e.g. "https://yourapp.streamlit.app"


def get_app_base_url():
    if BASE_URL:
        return BASE_URL.rstrip("/")
    try:
        host = st.context.headers.get("host", "localhost:8501")
        proto = "https" if "streamlit.app" in host else "http"
        return f"{proto}://{host}"
    except Exception:
        return "http://localhost:8501"


def generate_qr(url: str) -> str:
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def inject_css():
    st.markdown("""
    <style>
    .stApp { background: #0a0e1a; }
    .stTextInput input {
        background: #1a1a2e !important;
        color: #fff !important;
        border-radius: 10px !important;
    }
    label { color: #ccc !important; }
    .stForm, .stForm > div {
        background: #14213d !important;
        border-radius: 24px;
        padding: 2rem;
    }
    .card {
        background: #14213d;
        border-radius: 24px;
        box-shadow: 0 8px 32px rgba(44,62,80,.25);
        padding: 2.5rem 2rem;
        color: #fff;
        max-width: 480px;
        margin: 2rem auto;
    }
    .card h2 { color: #3498fd; }
    .card a  { color: #3498fd; }
    .profile-field { margin: .5rem 0; font-size: 1rem; }
    .profile-field span { color: #aaa; }
    .qr-box {
        background: #14213d;
        border-radius: 24px;
        padding: 2rem;
        text-align: center;
        color: #fff;
        max-width: 400px;
        margin: 1rem auto;
    }
    </style>
    """, unsafe_allow_html=True)


def page_register():
    st.title("📇 Portfolio QR Generator")

    with st.form("register_form"):
        name     = st.text_input("First Name")
        surname  = st.text_input("Surname")
        mobile   = st.text_input("Mobile Number (10 digits)")
        college  = st.text_input("College")
        city     = st.text_input("City")
        github   = st.text_input("GitHub Profile URL")
        linkedin = st.text_input("LinkedIn Profile URL")
        submitted = st.form_submit_button("Generate QR Code")

    if submitted:
        if not all([name, surname, mobile, college, city, github, linkedin]):
            st.error("Please fill in all fields.")
            return
        if not (mobile.isdigit() and len(mobile) == 10):
            st.error("Mobile must be exactly 10 digits.")
            return

        # Build profile URL with all data in query params — no DB needed
        params = urllib.parse.urlencode({
            "name": name, "surname": surname, "mobile": mobile,
            "college": college, "city": city,
            "github": github, "linkedin": linkedin
        })
        profile_url = f"{get_app_base_url()}/?{params}"
        qr_b64 = generate_qr(profile_url)

        st.markdown(f"""
        <div class="qr-box">
            <h3>Your QR Pass 🎉</h3>
            <img src="data:image/png;base64,{qr_b64}" width="240" style="border-radius:12px;"/>
            <p style="color:#aaa; font-size:.85rem; margin-top:.8rem;">
                Scan with any phone camera to view your profile.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.balloons()


def page_profile(p):
    wa_msg  = f"Hi {p['name']} {p['surname']}, I scanned your QR code!"
    wa_link = f"https://wa.me/91{p['mobile']}?text={urllib.parse.quote(wa_msg)}"

    st.markdown(f"""
    <div class="card">
        <h2>👤 {p['name']} {p['surname']}</h2>
        <div class="profile-field"><span>📱 Mobile: </span>{p['mobile']}</div>
        <div class="profile-field"><span>🏫 College: </span>{p['college']}</div>
        <div class="profile-field"><span>🏙️ City: </span>{p['city']}</div>
        <div class="profile-field"><span>💻 GitHub: </span>
            <a href="{p['github']}" target="_blank">{p['github']}</a></div>
        <div class="profile-field"><span>🔗 LinkedIn: </span>
            <a href="{p['linkedin']}" target="_blank">{p['linkedin']}</a></div>
        <div style="margin-top:1.5rem;">
            <a href="{wa_link}" target="_blank"
               style="background:#25d366;color:#fff;padding:.6em 1.4em;
                      border-radius:14px;text-decoration:none;font-weight:600;">
                💬 WhatsApp Me
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)


def main():
    st.set_page_config(page_title="Portfolio QR", layout="centered")
    inject_css()

    p = st.query_params
    if p.get("name"):
        page_profile({
            "name":     p.get("name", ""),
            "surname":  p.get("surname", ""),
            "mobile":   p.get("mobile", ""),
            "college":  p.get("college", ""),
            "city":     p.get("city", ""),
            "github":   p.get("github", ""),
            "linkedin": p.get("linkedin", ""),
        })
    else:
        page_register()


if __name__ == "__main__":
    main()