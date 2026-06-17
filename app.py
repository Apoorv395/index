import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# ==========================================
# CONFIGURATION & DATA SOURCE SETTINGS
# ==========================================
SPREADSHEET_NAME = "Centre Trackings"

# Access the dictionary directly out of the native Streamlit secrets container
# This completely bypasses the json.loads parser to avoid JSONDecodeErrors
GOOGLE_CREDENTIALS_DICT = st.secrets["gcp_service_account"]

st.set_page_config(layout="wide", page_title="Centre Owner Dashboard")

# High-Visibility Theme Enforcement Block
st.markdown("""
    <style>
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: Arial, sans-serif !important;
        background-color: #f8f9fa !important;
        color: #1f1f1f !important;
    }
    .stHeading h1, .stHeading h2, .stHeading h3, .stHeading h4 {
        color: #0b57d0 !important;
        font-family: Arial, sans-serif !important;
        font-weight: bold !important;
    }
    label, [data-testid="stWidgetLabel"] p {
        color: #1f1f1f !important;
        font-size: 16px !important;
        font-weight: bold !important;
    }
    input[type="text"], input[type="password"] {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    div.stButton > button {
        background-color: #1a73e8 !important;
        color: #ffffff !important;
        font-size: 16px !important;
        font-weight: normal !important;
        border-radius: 4px !important;
        border: none !important;
        padding: 10px 28px !important;
    }
    div.stButton > button:hover {
        background-color: #1557b0 !important;
    }
    div[data-testid="stDataFrame"] td, div[data-testid="stDataFrame"] th {
        color: #000000 !important;
    }
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
# HELPER DATA RENDERER
# ==========================================
def render_dataframe(df):
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

def safe_float_convert(val, to_percent=False, decimals=2):
    try:
        num = float(val)
        if to_percent:
            return f"{num * 100:.0f}%" if decimals == 0 else f"{num * 100:.{decimals}f}%"
        return f"{num:.0f}" if decimals == 0 else f"{num:.{decimals}f}"
    except (ValueError, TypeError):
        return val

# ==========================================
# MODULAR REPORT RENDERERS
# ==========================================
def render_enrollments():
    st.markdown("<h3 style='font-size:24px;'>1. Enrollments</h3>", unsafe_allow_html=True)
    sheet = ss.worksheet("Enrollments")
    data = sheet.get("BA3:BG100")
    if data:
        headers = data[0][:6]
        rows = [r[:6] for r in data[1:] if len(r) >= 7 and str(r[6]).strip().lower() == owner_name.strip().lower()]
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
    mtd_rows = []
    for r in raw[3:]:
        if len(r) > 28 and str(r[28]).strip().lower() == owner_name.strip().lower() and (r[0] or r[1]):
            formatted = r[0:3] + [safe_float_convert(cell, to_percent=("%" in str(r[2]))) for cell in r[3:5]]
            mtd_rows.append(formatted)
    if mtd_rows:
        render_dataframe(pd.DataFrame(mtd_rows, columns=mtd_headers))

    st.markdown("#### 2.2 Goal Wise Attendance :")
    goal_headers = raw[2][6:12]
    goal_rows = []
    for r in raw[3:]:
        if len(r) > 28 and str(r[28]).strip().lower() == owner_name.strip().lower() and (r[6] or r[7]):
            formatted = r[6:9] + [safe_float_convert(cell, to_percent=("%" in str(r[8]))) for cell in r[9:12]]
            goal_rows.append(formatted)
    if goal_rows:
        render_dataframe(pd.DataFrame(goal_rows, columns=goal_headers))

    st.markdown("#### 2.3 Class Wise Attendance :")
    class_rows = []
    for r in raw[3:]:
        if len(r) > 28 and str(r[28]).strip().lower() == owner_name.strip().lower() and (r[13] or r[14]):
            formatted = r[13:16] + [safe_float_convert(cell, to_percent=("%" in str(r[15]))) for cell in r[16:27]]
            class_rows.append(formatted)
            
    if class_rows:
        # High-Fidelity multi-index array alignments mapping seamlessly across rows
        columns_multi = pd.MultiIndex.from_tuples([
            ("Demographics & Metrics", "City"),
            ("Demographics & Metrics", "Centre"),
            ("Demographics & Metrics", "Metric"),
            ("Foundation", "Class 6"),
            ("Foundation", "Class 7"),
            ("Foundation", "Class 8"),
            ("Foundation", "Class 9"),
            ("Foundation", "Class 10"),
            ("IIT JEE", "Class 11"),
            ("IIT JEE", "Class 12"),
            ("IIT JEE", "Class 13"),
            ("NEET UG", "Class 11"),
            ("NEET UG", "Class 12"),
            ("NEET UG", "Class 13")
        ])
        df_attendance = pd.DataFrame(class_rows, columns=columns_multi)
        st.dataframe(df_attendance, use_container_width=True, hide_index=True)

def render_subscription():
    st.markdown("<h3 style='font-size:24px;'>3. Subscription Rating</h3>", unsafe_allow_html=True)
    sheet = ss.worksheet("Subscription Rating")
    raw = sheet.get_all_values()
    
    st.markdown("#### 3.1 Goal Comparison :")
    goal_rows = []
    for r in raw[4:108]:
        if len(r) > 24 and str(r[24]).strip().lower() == owner_name.strip().lower() and (r[0] or r[1]):
            formatted = []
            for idx, cell in enumerate(r[0:11]):
                if idx in [4, 7, 10]:
                    formatted.append(safe_float_convert(cell, to_percent=True))
                elif idx >= 2:
                    formatted.append(safe_float_convert(cell))
                else:
                    formatted.append(cell)
            goal_rows.append(formatted)
            
    if goal_rows:
        columns_multi = pd.MultiIndex.from_tuples([
            ("Location Details", "City"),
            ("Location Details", "Centre"),
            ("Foundation", "Rating"),
            ("Foundation", "Count"),
            ("Foundation", "Ref %"),
            ("IIT JEE", "Rating"),
            ("IIT JEE", "Count"),
            ("IIT JEE", "Ref %"),
            ("NEET UG", "Rating"),
            ("NEET UG", "Count"),
            ("NEET UG", "Ref %")
        ])
        df_sub = pd.DataFrame(goal_rows, columns=columns_multi)
        st.dataframe(df_sub, use_container_width=True, hide_index=True)

    st.markdown("#### 3.2 MOM Comparison :")
    mom_headers = raw[3][12:17]
    mom_rows = []
    for r in raw[4:108]:
        if len(r) > 24 and str(r[24]).strip().lower() == owner_name.strip().lower() and (r[12] or r[13]):
            formatted = []
            for idx, cell in enumerate(r[12:17]):
                if idx == 4:
                    formatted.append(safe_float_convert(cell, to_percent=True))
                elif idx >= 2:
                    formatted.append(safe_float_convert(cell))
                else:
                    formatted.append(cell)
            mom_rows.append(formatted)
    if mom_rows:
        render_dataframe(pd.DataFrame(mom_rows, columns=mom_headers))

    st.markdown("#### 3.3 Major Detractors :")
    det_headers = raw[3][27:38]
    det_rows = []
    for r in raw[4:]:
        if len(r) > 38 and str(r[38]).strip().lower() == owner_name.strip().lower() and (r[27] or r[28] or r[29]):
            formatted = r[27:29] + [safe_float_convert(cell) for cell in r[29:38]]
            det_rows.append(formatted)
    if det_rows:
        render_dataframe(pd.DataFrame(det_rows, columns=det_headers))

def render_educator():
    st.markdown("<h3 style='font-size:24px;'>4. Educator Quality</h3>", unsafe_allow_html=True)
    sheet = ss.worksheet("Educator Quality")
    
    st.markdown("#### 4.1 Educator Rating % :")
    data1 = sheet.get("A2:J800")
    if data1:
        h1 = data1[0][:9]
        r1 = []
        for row in data1[1:]:
            if len(row) >= 10 and str(row[9]).strip().lower() == owner_name.strip().lower():
                formatted = [safe_float_convert(c, to_percent=(float(c) <= 1 if c.replace('.','',1).isdigit() else False)) for c in row[:9]]
                r1.append(formatted)
        if r1:
            render_dataframe(pd.DataFrame(r1, columns=h1))

    st.markdown("#### 4.2 Educator Rating Batchwise % :")
    data2 = sheet.get("M2:R400")
    if data2:
        h2 = data2[0][:5]
        r2 = []
        for row in data2[1:]:
            if len(row) >= 6 and str(row[5]).strip().lower() == owner_name.strip().lower():
                formatted = [safe_float_convert(c, to_percent=(float(c) <= 1 if c.replace('.','',1).isdigit() else False)) for c in row[:5]]
                r2.append(formatted)
        if r2:
            render_dataframe(pd.DataFrame(r2, columns=h2))

def render_syllabus():
    st.markdown("<h3 style='font-size:24px;'>5. Syllabus Progress</h3>", unsafe_allow_html=True)
    sheet = ss.worksheet("Syllabus Progress")
    full_data = sheet.get("A90:O167")
    if full_data:
        rows = []
        for r in full_data[2:]:
            if len(r) >= 15 and str(r[14]).strip().lower() == owner_name.strip().lower():
                formatted_row = []
                for idx, cell in enumerate(r[:14]):
                    if 2 <= idx <= 9 or idx == 13:
                        formatted_row.append(safe_float_convert(cell, to_percent=True))
                    elif 10 <= idx <= 12:
                        formatted_row.append(safe_float_convert(cell, decimals=0))
                    else:
                        formatted_row.append(cell)
                rows.append(formatted_row)
                
        if rows:
            columns_multi = pd.MultiIndex.from_tuples([
                ("Details", "City"),
                ("Details", "Centre"),
                ("IIT JEE", "Class 11 P1"),
                ("IIT JEE", "Class 11 P2"),
                ("IIT JEE", "Class 12 P1"),
                ("IIT JEE", "Class 12 P2"),
                ("NEET UG", "Class 11 P1"),
                ("NEET UG", "Class 11 P2"),
                ("NEET UG", "Class 12 P1"),
                ("NEET UG", "Class 12 P2"),
                ("Core Metrics", "Total Batches"),
                ("Core Metrics", "Syllabus Live"),
                ("Core Metrics", "Behind Tracker"),
                ("Total", "Overall Progress %")
            ])
            df_syllabus = pd.DataFrame(rows, columns=columns_multi)
            st.dataframe(df_syllabus, use_container_width=True, hide_index=True)

def render_test():
    st.markdown("<h3 style='font-size:24px;'>6. Test Dashboard</h3>", unsafe_allow_html=True)
    sheet = ss.worksheet("Test")
    raw = sheet.get_all_values()
    
    st.markdown("#### 6.1 Test Summary IIT JEE :")
    iit_summary = [r[2:7] for r in raw[2:90] if len(r) > 0 and str(r[0]).strip().lower() == owner_name.lower() and str(r[2]).strip() != ""]
    if iit_summary:
        st.markdown(f'<div style="background-color:#0b57d0; color:white; font-weight:bold; padding:6px; text-align:center; border-radius:4px 4px 0 0; font-size:14px;">{raw[0][2] if raw[0][2] else "Test Summary Overview"}</div>', unsafe_allow_html=True)
        render_dataframe(pd.DataFrame(iit_summary, columns=raw[1][2:7]))

    st.markdown("#### 6.2 Centre Toppers IIT JEE :")
    iit_toppers = [r[9:13] for r in raw[2:90] if len(r) > 9 and str(r[0]).strip().lower() == owner_name.lower() and str(r[9]).strip() != ""]
    if iit_toppers:
        st.markdown(f'<div style="background-color:#0b57d0; color:white; font-weight:bold; padding:6px; text-align:center; border-radius:4px 4px 0 0; font-size:14px;">{raw[0][9] if raw[0][9] else "Centre Toppers Standings"}</div>', unsafe_allow_html=True)
        render_dataframe(pd.DataFrame(iit_toppers, columns=raw[1][9:13]))

    st.markdown("#### 6.3 Test Summary NEET :")
    max_rows = min(len(raw), 80)
    neet_summary = []
    for r in raw[2:max_rows]:
        if len(r) > 17 and str(r[16]).strip().lower() == owner_name.lower() and str(r[17]).strip() != "":
            formatted = []
            for cell in r[17:23]:
                try:
                    num = float(cell)
                    formatted.append(f"{num * 100:.1f}%" if 0 < num <= 1 else cell)
                except ValueError:
                    formatted.append(cell)
            neet_summary.append(formatted)
    if neet_summary:
        st.markdown(f'<div style="background-color:#0b57d0; color:white; font-weight:bold; padding:6px; text-align:center; border-radius:4px 4px 0 0; font-size:14px;">{raw[0][17] if raw[0][17] else "Test Summary NEET Overview"}</div>', unsafe_allow_html=True)
        render_dataframe(pd.DataFrame(neet_summary, columns=raw[1][17:23]))

    st.markdown("#### 6.4 Centre Toppers NEET :")
    neet_toppers = [r[24:28] for r in raw[2:max_rows] if len(r) > 24 and str(r[16]).strip().lower() == owner_name.lower() and str(r[24]).strip() != ""]
    if neet_toppers:
        st.markdown(f'<div style="background-color:#0b57d0; color:white; font-weight:bold; padding:6px; text-align:center; border-radius:4px 4px 0 0; font-size:14px;">{raw[0][24] if raw[0][24] else "Centre Toppers NEET Standings"}</div>', unsafe_allow_html=True)
        render_dataframe(pd.DataFrame(neet_toppers, columns=raw[1][24:28]))

# ==========================================
# PAGE ROUTER DISPATCHER
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
        if st.form_submit_button("Login"):
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
    
    st.markdown(f'<div class="account-meta"><b>Owner Name :</b> {owner_name}<br><b>City :</b> {city_name}</div>', unsafe_allow_html=True)
    
    report_type = st.selectbox("Select Report :", [
        "Choose Report", "Overall Dashboard (All Reports)", "1. Enrollments", "2. Attendance", "3. Subscription Rating", "4. Educator Quality", "5. Syllabus Progress", "6. Test"
    ])

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
