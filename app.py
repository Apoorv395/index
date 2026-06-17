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
    # Category Group Header Bar
    st.markdown("""
    <table style="width:100%; border-collapse:collapse; margin-bottom:-2px; text-align:center; font-family:Arial;">
        <tr style="background-color:#0b57d0; color:white; font-weight:bold; font-size:14px;">
            <td style="width:21.4%; border:1px solid #bdc1c6; padding:6px;">Demographics & Metrics</td>
            <td style="width:35.7%; border:1px solid #bdc1c6; padding:6px;">Foundation</td>
            <td style="width:21.4%; border:1px solid #bdc1c6; padding:6px;">IIT JEE</td>
            <td style="width:21.4%; border:1px solid #bdc1c6; padding:6px;">NEET UG</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)
    
    class_headers = ["City", "Centre", "Metric", "Class 6", "Class 7", "Class 8", "Class 9", "Class 10", "Class 11", "Class 12", "Class 13", "Class 11 ", "Class 12 ", "Class 13 "]
    class_rows = []
    for r in raw[3:]:
        if len(r) > 28 and str(r[28]).strip().lower() == owner_name.strip().lower() and (r[13] or r[14]):
            formatted = r[13:16] + [safe_float_convert(cell, to_percent=("%" in str(r[15]))) for cell in r[16:27]]
            class_rows.append(formatted)
    if class_rows:
        render_dataframe(pd.DataFrame(class_rows, columns=class_headers))

def render_subscription():
    st.markdown("<h3 style='font-size:24px;'>3. Subscription Rating</h3>", unsafe_allow_html=True)
    sheet = ss.worksheet("Subscription Rating")
    raw = sheet.get_all_values()
    
    st.markdown("#### 3.1 Goal Comparison :")
    # Category Group Header Bar
    st.markdown("""
    <table style="width:100%; border-collapse:collapse; margin-bottom:-2px; text-align:center; font-family:Arial;">
        <tr style="background-color:#0b57d0; color:white; font-weight:bold; font-size:14px;">
            <td style="width:18.1%; border:1px solid #bdc1c6; padding:6px;">Location Details</td>
            <td style="width:27.3%; border:1px solid #bdc1c6; padding:6px;">Foundation</td>
            <td style="width:27.3%; border:1px solid #bdc1c6; padding:6px;">IIT JEE</td>
            <td style="width:27.3%; border:1px solid #bdc1c6; padding:6px;">NEET UG</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)
    
    goal_headers = ["City", "Centre", "Rating", "Count", "Ref %", "Rating ", "Count ", "Ref % ", "Rating  ", "Count  ", "Ref %  "]
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
        render_dataframe(pd.DataFrame(goal_rows, columns=goal_headers))

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

def render_syllabus():
    st.markdown("<h3 style='font-size:24px;'>5. Syllabus Progress</h3>", unsafe_allow_html=True)
    sheet = ss.worksheet("Syllabus Progress")
    full_data = sheet.get("A90:O167")
    if full_data:
        # Category Group Header Bar
        st.markdown("""
        <table style="width:100%; border-collapse:collapse; margin-bottom:-2px; text-align:center; font-family:Arial;">
            <tr style="background-color:#0b57d0; color:white; font-weight:bold; font-size:14px;">
                <td style="width:14.2%; border:1px solid #bdc1c6; padding:6px;">Details</td>
                <td style="width:28.5%; border:1px solid #bdc1c6; padding:6px;">IIT JEE</td>
                <td style="width:28.5%; border:1px solid #bdc1c6; padding:6px;">NEET UG</td>
                <td style="width:21.4%; border:1px solid #bdc1c6; padding:6px;">Core Metrics</td>
                <td style="width:7.4%; border:1px solid #bdc1c6; padding:6px;">Total</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
        
        headers = full_data[1][:14]
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
            render_dataframe(pd.DataFrame(rows, columns=headers))

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
