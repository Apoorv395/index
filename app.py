import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# ==========================================
# CONFIGURATION & DATA SOURCE SETTINGS
# ==========================================
SPREADSHEET_NAME = "Centre Trackings"

# Pull keys safely from Streamlit Cloud's internal hidden vault environment
# This guarantees no text-corruption or broken cryptographic JWT signatures
GOOGLE_CREDENTIALS_DICT = st.secrets["gcp_service_account"]

st.set_page_config(layout="wide", page_title="Centre Owner Dashboard")

# High-Visibility Theme Enforcement Block (Locks layout parameters across light/dark system themes)
st.markdown("""
    <style>
    /* Force canvas and body styling rules to plain light grey background */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: Arial, sans-serif !important;
        background-color: #f8f9fa !important;
        color: #1f1f1f !important;
    }
    
    /* Make headers sharp corporate blue */
    .stHeading h1, .stHeading h2, .stHeading h3, .stHeading h4 {
        color: #0b57d0 !important;
        font-family: Arial, sans-serif !important;
        font-weight: bold !important;
    }
    
    /* Fix missing visibility on form input text box label headers */
    label, [data-testid="stWidgetLabel"] p {
        color: #1f1f1f !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }
    
    /* Fix input text container internals to maintain bright visible contrast */
    input[type="text"], input[type="password"] {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    
    /* Force high contrast text visibility on primary blue login button block */
    div.stButton > button {
        background-color: #1a73e8 !important;
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: normal !important;
        border-radius: 4px !important;
        border: none !important;
        padding: 10px 28px !important;
        width: auto !important;
    }
    div.stButton > button:hover {
        background-color: #1557b0 !important;
        color: #ffffff !important;
    }
    
    /* Global spreadsheet-like text data color assignments */
    div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
        color: #000000 !important;
    }
    
    /* Account snapshot profile container banner layout */
    .account-meta {
        font-size: 16px !important;
        line-height: 1.8em !important;
        background-color: #ffffff !important;
        color: #1f1f1f !important;
        padding: 15px 20px !important;
        border-radius: 6px !important;
        border: 1px solid #bdc1c6 !important;
        margin-bottom: 25px !important;
    }
    </style>
""", unsafe_allow_html=True)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_info" not in st.session_state:
    st.session_state.user_info = {}

# ==========================================
# DATABASE HANDSHAKE INITIALIZATION
# ==========================================
@st.cache_resource
def get_sheets_client():
    scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(GOOGLE_CREDENTIALS_DICT, scopes=scopes)
    return gspread.authorize(creds)

try:
    client = get_sheets_client()
    ss = client.open(SPREADSHEET_NAME)
except Exception as e:
    st.error(f"Google API Verification Check Blocked: {e}")
    st.stop()

def check_login(username, password):
    sheet = ss.worksheet("Login Details")
    data = sheet.get_all_values()
    for row in data[1:]:  
        if len(row) >= 5:
            if str(row[0]).strip() == str(username).strip() and str(row[1]).strip() == str(password).strip():
                return {"success": True, "owner": row[4], "city": row[2], "centre": row[3]}
    return {"success": False}

# ==========================================
# PAGE INTERFACE DISPATCHER ROUTINES
# ==========================================
col_title, col_logo = st.columns([8, 2])
with col_logo:
    st.image("https://upload.wikimedia.org/wikipedia/commons/8/85/Unacademy_Logo.png", width=140)

if not st.session_state.logged_in:
    with col_title:
        st.markdown("<h2 style='font-size:28px; margin-top:20px;'>Centre Owner Login</h2>", unsafe_allow_html=True)
        
    with st.form("login_form"):
        username_input = st.text_input("Login ID")
        password_input = st.text_input("Password", type="password")
        submit_btn = st.form_submit_button("Login")
        
        if submit_btn:
            res = check_login(username_input, password_input)
            if res["success"]:
                st.session_state.logged_in = True
                st.session_state.user_info = res
                st.rerun()
            else:
                st.error("Invalid Login Details")
else:
    owner_name = st.session_state.user_info["owner"]
    city_name = st.session_state.user_info["city"]
    
    with col_title:
        st.markdown("<h1 style='font-size:34px; margin-top:10px;'>Centre Performance Dashboard</h1>", unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="account-meta">
        <b>Owner Name :</b> {owner_name}<br>
        <b>City :</b> {city_name}
    </div>
    """, unsafe_allow_html=True)
    
    report_type = st.selectbox("Select Report :", [
        "Choose Report",
        "Overall Dashboard (All Reports)",
        "1. Enrollments",
        "2. Attendance",
        "3. Subscription Rating",
        "4. Educator Quality",
        "5. Syllabus Progress",
        "6. Test"
    ])

    def render_dataframe(df):
        # Clean header index iterator handles duplicate column matrices beautifully
        new_cols = []
        counts = {}
        for col in df.columns:
            col_str = str(col)
            if col_str in counts:
                counts[col_str] += 1
                new_cols.append(f"{col_str} ({counts[col_str]})")
            else:
                counts[col_str] = 0
                new_cols.append(col_str)
        df.columns = new_cols
        st.dataframe(df, use_container_width=True, hide_index=True)

    # ==========================================
    # MODULAR REPORT DATA RENDERING METHODS
    # ==========================================
    
    def render_enrollments():
        st.markdown("<h3 style='font-size:24px;'>1. Enrollments</h3>", unsafe_allow_html=True)
        sheet = ss.worksheet("Enrollments")
        data = sheet.get("BA3:BG100")
        
        if data:
            headers = data[0][:6]
            rows = []
            for r in data[1:]:
                if len(r) >= 7 and str(r[6]).strip().lower() == owner_name.strip().lower():
                    rows.append(r[:6])
            if rows:
                render_dataframe(pd.DataFrame(rows, columns=headers))
            else:
                st.info("No enrollment records found matching this account name.")

    def render_attendance():
        st.markdown("<h3 style='font-size:24px;'>2. Attendance</h3>", unsafe_allow_html=True)
        sheet = ss.worksheet("Attendance")
        raw = sheet.get_all_values()
        
        st.markdown("#### 2.1 MTD Attendance :")
        mtd_headers = raw[2][0:5]
        mtd_rows = [r[0:5] for r in raw[3:] if len(r) > 28 and str(r[28]).strip().lower() == owner_name.strip().lower() and (r[0] or r[1])]
        if mtd_rows:
            render_dataframe(pd.DataFrame(mtd_rows, columns=mtd_headers))

        st.markdown("#### 2.2 Goal Wise Attendance :")
        goal_headers = raw[2][6:12]
        goal_rows = [r[6:12] for r in raw[3:] if len(r) > 28 and str(r[28]).strip().lower() == owner_name.strip().lower() and (r[6] or r[7])]
        if goal_rows:
            render_dataframe(pd.DataFrame(goal_rows, columns=goal_headers))

    def render_subscription():
        st.markdown("<h3 style='font-size:24px;'>3. Subscription Rating</h3>", unsafe_allow_html=True)
        sheet = ss.worksheet("Subscription Rating")
        raw = sheet.get_all_values()
        
        st.markdown("#### 3.1 Goal Comparison :")
        goal_rows = [r[0:11] for r in raw[4:108] if len(r) > 24 and str(r[24]).strip().lower() == owner_name.strip().lower() and (r[0] or r[1])]
        if goal_rows:
            render_dataframe(pd.DataFrame(goal_rows, columns=raw[3][0:11]))

        st.markdown("#### 3.3 Major Detractors :")
        det_rows = [r[27:38] for r in raw[4:] if len(r) > 38 and str(r[38]).strip().lower() == owner_name.strip().lower() and (r[27] or r[28])]
        if det_rows:
            render_dataframe(pd.DataFrame(det_rows, columns=raw[3][27:38]))

    def render_educator():
        st.markdown("<h3 style='font-size:24px;'>4. Educator Quality</h3>", unsafe_allow_html=True)
        sheet = ss.worksheet("Educator Quality")
        data1 = sheet.get("A2:J800")
        
        if data1:
            h1 = data1[0][:9]
            r1 = [row[:9] for row in data1[1:] if len(row) >= 10 and str(row[9]).strip().lower() == owner_name.strip().lower()]
            if r1:
                st.markdown("#### 4.1 Educator Rating % :")
                render_dataframe(pd.DataFrame(r1, columns=h1))

    def render_syllabus():
        st.markdown("<h3 style='font-size:24px;'>5. Syllabus Progress</h3>", unsafe_allow_html=True)
        sheet = ss.worksheet("Syllabus Progress")
        full_data = sheet.get("A90:O167")
        
        if full_data:
            headers = full_data[1][:14]
            rows = []
            for r in full_data[2:]:
                if len(r) >= 15 and str(r[14]).strip().lower() == owner_name.strip().lower():
                    formatted_row = []
                    for idx, cell in enumerate(r[:14]):
                        try:
                            val = float(cell)
                            if 2 <= idx <= 9 or idx == 13:
                                formatted_row.append(f"{val * 100:.2f}%")
                            elif 10 <= idx <= 12:
                                formatted_row.append(f"{val:.0f}")
                            else:
                                formatted_row.append(cell)
                        except ValueError:
                            formatted_row.append(cell)
                    rows.append(formatted_row)
            if rows:
                render_dataframe(pd.DataFrame(rows, columns=headers))

    def render_test():
        st.markdown("<h3 style='font-size:24px;'>6. Test Dashboard</h3>", unsafe_allow_html=True)
        sheet = ss.worksheet("Test")
        raw = sheet.get_all_values()
        
        st.markdown("#### 6.1 Test Summary IIT JEE :")
        iit_summary = [r[2:7] for r in raw[2:90] if len(r) > 0 and str(r[0]).strip().lower() == owner_name.lower() and r[2]]
        if iit_summary:
            render_dataframe(pd.DataFrame(iit_summary, columns=raw[1][2:7]))

    # Navigation Logic Router Execution Hub
    if report_type == "1. Enrollments":
        render_enrollments()
    elif report_type == "2. Attendance":
        render_attendance()
    elif report_type == "3. Subscription Rating":
        render_subscription()
    elif report_type == "4. Educator Quality":
        render_educator()
    elif report_type == "5. Syllabus Progress":
        render_syllabus()
    elif report_type == "6. Test":
        render_test()
    elif report_type == "Overall Dashboard (All Reports)":
        render_enrollments()
        render_attendance()
        render_subscription()
        render_educator()
        render_syllabus()
        render_test()
