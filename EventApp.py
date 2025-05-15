import streamlit as st
import pandas as pd
import sqlite3
import re
import os
from datetime import datetime

st.markdown(
    """
    <style>
    
    [data-testid="stAppViewContainer"] {
        background-color: #1f242d !important;
        color: black !important;
    }

    /* Force black text for all typical text containers */
    h1, h2, h3, h4, h5, h6, p, label, span, div {
        color: white !important;
    }

    /* Input styling */
    input, textarea {
        color: white !important;
        background-color: #323946 !important;
        border-radius: 6px !important;
        padding: 8px !important;
    }

    /* Change Streamlit button color */
    .stButton > button {
        background-color: #1f242d !important;
        color: white !important;
        border: 2px solid black !important;
        border-radius: 6px;
        font-weight: bold;
    }

    
    .stButton > button:hover {
        background-color: #323946 !important;
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ─────────────────────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect('sumo_registrations.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS registrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    team_name TEXT,
                    leader_name TEXT,
                    email TEXT,
                    phone TEXT,
                    participant_level TEXT,
                    institution TEXT,
                    robot_name TEXT,
                    weight_category TEXT,
                    timestamp TEXT
                )''')
    conn.commit()
    conn.close()

def save_to_csv(data):
    df = pd.DataFrame([data])
    csv_file = 'sumo_registrations.csv'
    if os.path.exists(csv_file) and os.path.getsize(csv_file) > 0:
        try:
            existing_df = pd.read_csv(csv_file)
            df = pd.concat([existing_df, df], ignore_index=True)
        except Exception as e:
            st.warning(f"CSV unreadable. Overwriting. Error: {e}")
    df.to_csv(csv_file, index=False)

def save_to_db(data):
    conn = sqlite3.connect('sumo_registrations.db')
    c = conn.cursor()
    c.execute('''INSERT INTO registrations (
                    team_name, leader_name, email, phone,
                    participant_level, institution, robot_name, weight_category,
                    timestamp)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (data['Team Name'], data['Leader Name'], data['Email'], data['Phone'],
               data['Participant Level'], data['Institution'], data['Robot Name'], data['Weight Category'],
                data['Timestamp']))
    conn.commit()
    conn.close()

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

# ─────────────────────────────────────────────────────────────────────────────
init_db()

if 'submitted' not in st.session_state:
    st.session_state.submitted = False
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}

# ─────────────────────────────────────────────────────────────────────────────
# Tabs for navigation
tab1, tab2, tab3 = st.tabs(["🏠 Home", "📝 Register", "✅ Confirmation"])

# ─────────────────────────────────────────────────────────────────────────────
# Home Tab
with tab1:
    st.title("🤖 Sumo Robot Competition 2025")

    st.markdown("""
    Welcome to the official **Sumo Robot Competition 2025** registration portal!  
    This thrilling event challenges participants to build and compete with their own sumo robots in an intense head-to-head ring battle.

    ---

    ### 🏆 Competition Categories:

     🔹 **1kg Autonomous Robot**
     🔹 **3kg Remote-Controlled Robot**

    All these category must meet required **dimensions and height limits** as per competition rules.

    ---
    
    ### 📋 General Requirements:
    - Each team can have **1–3 members**.
    - One team may only register for **one robot per category**.
    - Robots must pass a **technical inspection** before competing.

    ---

    ### 📅 Event Details:
    - 📍 *Location:* Paradigm Mall Johor Bahru
    - 📆 *Date:* 15/7/2025
    - 🕘 *Time:* 10.00am

    ---

    Click the **Register** tab above to submit your team details and secure your slot.  
    Don't miss your chance to compete in Malaysia’s most exciting robotics arena!

    **Questions?** Contact us at: nrl@email.com
    """)

    with st.expander("📐 Click here to view Robot Category Requirements"):
        st.markdown("""
        ### 🔹 1kg Autonomous Robot
        - Must operate **fully autonomously** (no remote control or manual intervention allowed).
        - **Weight Limit:** ≤ 1.00 kg
        - **Maximum Dimensions:** 20 cm (length) × 20 cm (width)
        - **Maximum Height:** 10 cm
        - Must use onboard sensors for opponent detection and ring boundaries.

        ### 🔹 3kg Remote-Controlled Robot
        - Can be manually controlled using **IR, RF, Bluetooth, or any other remote technology**.
        - **Weight Limit:** ≤ 3.00 kg
        - **Maximum Dimensions:** 30 cm (length) × 30 cm (width)
        - **Maximum Height:** 20 cm
        - No autonomous behavior required; human-controlled operation allowed.
        """)


# ─────────────────────────────────────────────────────────────────────────────
# Register Tab
with tab2:
    with st.form("registration_form"):
        st.title("📝 Team Registration Form")

        st.markdown("### 👥 Team Details")
        col1, col2 = st.columns(2)
        with col1:
            team_name = st.text_input("Team Name")
            leader_name = st.text_input("Team Leader Name")
        with col2:
            email = st.text_input("Email")
            phone = st.text_input("Phone Number", max_chars=12)

        st.markdown("---")

        col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### 🎓 Participant Information")
        participant_level = st.radio("Participant Level", ["School", "College/University", "Professional"], horizontal=True)
        institution = st.text_input("Institution / Organization Name")
        
        st.markdown("---")
        submit = st.form_submit_button("🚀 Submit Registration")

    with col_right:
        st.markdown("### 🤖 Robot Details")
        
        weight_category = st.radio("Robot Weight Category", ["1kg", "3kg"])
        robot_name = st.text_input("Robot Name")
        st.markdown("---")
     
    if submit:
                errors = []

                if not all([team_name, leader_name, email, phone, institution, robot_name]):
                    errors.append("All fields must be filled.")
                if not is_valid_email(email):
                    errors.append("Invalid email format.")
                if not phone.isdigit() or not 7 <= len(phone) <= 12:
                    errors.append("Phone number must be 7 to 12 digits and contain only numbers.")

                if errors:
                    for error in errors:
                        st.error(f"❗ {error}")
                else:
                    form_data = {
                        "Team Name": team_name,
                        "Leader Name": leader_name,
                        "Email": email,
                        "Phone": phone,
                        "Participant Level": participant_level,
                        "Institution": institution,
                        "Robot Name": robot_name,
                        "Weight Category": weight_category,
                        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                    save_to_csv(form_data)
                    save_to_db(form_data)
                    st.session_state.submitted = True
                    st.session_state.form_data = form_data
                    st.success("🎉 Registration successful!")        

# ─────────────────────────────────────────────────────────────────────────────
# Confirmation Tab
with tab3:
    st.title("✅ Confirmation / Status")
    if st.session_state.submitted:
        st.success("😊 Thank you for registering! Here are your team details:")
        
        data = st.session_state.form_data
        df = pd.DataFrame(data.items(), columns=["Field", "Value"])
        st.table(df)

        st.info(
            """
            ✔️ Please review your details carefully.  
            ✔️ If you find any mistakes, you can re-register with the correct information.  
            ✔️ Keep this page or take a screenshot for your reference.  
            ✔️ For any questions, contact us at: nrl@email.com  
            """
        )
    else:
        st.warning("No registration found. Please fill out the registration form first.")
