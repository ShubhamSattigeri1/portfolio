"""
Hello this is the read me file where there is a description about the latest thought thst arose to my head and started developing this please ypu may also contribute in this project.
in this project i'll be developig an online platform where once you uploaded ypu detains an online qr code would generate 
and once scanned your details would apper on the next persons mobile device,
please help me do this
"""
import pandas as pd
import uuid
import qrcode
import os
from io import BytesIO
import urllib.parse
import streamlit as st
import base64

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(jpg_file):
    bin_str = get_base64(jpg_file)
    page_bg_img = f'''
    <style>
    .stApp {{
    background-image: url("data:image/jpg;base64,{bin_str}");
    background-size: cover;
    }}
    </style>
    '''
    st.markdown(page_bg_img, unsafe_allow_html=True)

# --- Add popup/modal CSS ---
st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{get_base64('75e260a2-fbb7-4413-bc7b-77cbb4ef8261.jpg')}");
        background-size: cover;
    }}
    .qr-modal {{
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0,0,0,0.45);
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
    }}
    .qr-modal-content {{
        background: #14213d !important;
        border-radius: 24px;
        box-shadow: 0 8px 32px rgba(44,62,80,0.18);
        padding: 2.5rem 2rem;
        text-align: center;
        min-width: 320px;
        max-width: 90vw;
        max-height: 90vh;
        color: #fff !important;
    }}
    .qr-modal-content img {{
        margin-bottom: 1.2em;
        border-radius: 16px;
        box-shadow: 0 2px 12px rgba(44,62,80,0.08);
    }}
    .close-btn {{
        background: #3498fd;
        color: #fff;
        border: none;
        border-radius: 16px;
        padding: 0.5em 1.5em;
        font-size: 1em;
        cursor: pointer;
        margin-top: 1em;
        font-weight: 600;
    }}
    /* Form container styling */
    .stForm, .stForm > div {{
        background: #14213d !important;
        border-radius: 24px;
        box-shadow: 0 8px 32px rgba(44,62,80,0.18);
        padding: 2.5rem 2rem;
        color: #fff !important;
    }}
    /* Make form input text white */
    .stForm input, .stForm textarea {{
        color: #fff !important;
        background: #1a1a2e !important;
        border-radius: 12px !important;
    }}
    </style>
""", unsafe_allow_html=True)

set_background('75e260a2-fbb7-4413-bc7b-77cbb4ef8261.jpg')
CSV_FILE = 'main.csv'
TXT_DIR = 'user_txt'

class Portfolio:
    def __init__(self):
        if not os.path.exists(CSV_FILE):
            df = pd.DataFrame(columns=['user_id', 'name', 'surname', 'mobile', 'college', 'city', 'github', 'linkedin'])
            df.to_csv(CSV_FILE, index=False)
        if not os.path.exists(TXT_DIR):
            os.makedirs(TXT_DIR)

    @staticmethod
    def create_whatsapp_link(number, message=""):
        base = f"https://wa.me/{number}"
        if message:
            message_encoded = urllib.parse.quote(message)
            return f"{base}?text={message_encoded}"
        return base

    @staticmethod
    def generate_qr_code(content):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(content)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return buf

    def create_readonly_txt(self, user_id, user_data, whatsapp_link):
        txt_content = (
            f"Name: {user_data['name']}\n"
            f"Surname: {user_data['surname']}\n"
            f"Mobile: {user_data['mobile']}\n"
            f"College: {user_data['college']}\n"
            f"City: {user_data['city']}\n"
            f"GitHub: {user_data['github']}\n"
            f"LinkedIn: {user_data['linkedin']}\n"
            f"WhatsApp Link: {whatsapp_link}\n"
        )
        txt_path = os.path.join(TXT_DIR, f"{user_id}.txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(txt_content)
        return txt_path

    def register_user(self, name, surname, mobile, college, city, github, linkedin):
        if not all([name, surname, mobile, college, city, github, linkedin]):
            raise ValueError("Please fill in all fields.")
        if not (mobile.isdigit() and len(mobile) == 10):
            raise ValueError("Mobile must be 10 digits")

        user_id = str(uuid.uuid4())
        data = {
            'user_id': user_id,
            'name': name,
            'surname': surname,
            'mobile': mobile,
            'college': college,
            'city': city,
            'github': github,
            'linkedin': linkedin
        }

        df = pd.read_csv(CSV_FILE)
        whatsapp_link = self.create_whatsapp_link(
            "91" + mobile,
            f"Hi {name} {surname}, I scanned your QR code!"
        )

        # Create read-only TXT file with all details
        txt_path = self.create_readonly_txt(user_id, data, whatsapp_link)

        # Generate QR code with all details as plain text
        qr_content = (
            f"Name: {name}\n"
            f"Surname: {surname}\n"
            f"Mobile: {mobile}\n"
            f"College: {college}\n"
            f"City: {city}\n"
            f"GitHub: {github}\n"
            f"LinkedIn: {linkedin}\n"
            f"WhatsApp Link: {whatsapp_link}"
        )
        qr_img = self.generate_qr_code(qr_content)

        # Save user data to CSV
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)

        return {
            'qr_img': qr_img,
            'qr_content': qr_content,
            'user_data': data,
            'txt_path': txt_path,
            'whatsapp_link': whatsapp_link,
            'linkedin': linkedin
        }

# --- Streamlit UI ---
st.set_page_config(page_title="Portfolio Registration", layout="centered")
st.title("Portfolio Registration")

portfolio = Portfolio()

# Use session state to control popup
if 'show_qr' not in st.session_state:
    st.session_state['show_qr'] = False
if 'qr_result' not in st.session_state:
    st.session_state['qr_result'] = None

with st.form("register_form"):
    name = st.text_input("First Name")
    surname = st.text_input("Surname")
    mobile = st.text_input("Mobile Number")
    college = st.text_input("College")
    city = st.text_input("City")
    github = st.text_input("GitHub Profile URL")
    linkedin = st.text_input("LinkedIn Profile URL")
    submitted = st.form_submit_button("Register")

    if submitted:
        try:
            result = portfolio.register_user(name, surname, mobile, college, city, github, linkedin)
            st.session_state['show_qr'] = True
            st.session_state['qr_result'] = result
            st.success("Registration successful!")
            st.balloons()
        except Exception as e:
            st.error(str(e))

# --- QR Modal Popup ---
if st.session_state['show_qr'] and st.session_state['qr_result']:
    result = st.session_state['qr_result']
    qr_bytes = result['qr_img'].getvalue()
    qr_base64 = base64.b64encode(qr_bytes).decode()
    st.markdown(
        f"""
        <div class="qr-modal">
            <div class="qr-modal-content">
                <h3>Your QR Pass 🎉</h3>
                <img src="data:image/png;base64,{qr_base64}" width="260"/>
                <div style="margin-bottom:1em;">
                    <b>Scan this QR code to get your details!</b>
                </div>
                <button class="close-btn" onclick="window.location.reload();">Close</button>
                <div style="margin-top:1em; text-align:left;">
                    <b>Entered Details:</b><br>
                    Name: {result['user_data']['name']}<br>
                    Surname: {result['user_data']['surname']}<br>
                    Mobile: {result['user_data']['mobile']}<br>
                    College: {result['user_data']['college']}<br>
                    City: {result['user_data']['city']}<br>
                    GitHub: {result['user_data']['github']}<br>
                    LinkedIn: {result['user_data']['linkedin']}<br>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
