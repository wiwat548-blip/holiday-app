import calendar
from datetime import date, datetime
import streamlit as st

# ตั้งค่าหน้าเว็บให้รองรับมือถือและคอมพิวเตอร์
st.set_page_config(
    page_title="ระบบลงวันหยุดพนักงาน", page_icon="📅", layout="centered"
)

# --- ปรับแต่ง CSS ให้ตารางบนมือถือแสดงผลสวยงามและกระชับ ---
st.markdown(
    """
    <style>
    /* ลดช่องว่างระหว่างคอลัมน์เพื่อให้มือถือแสดงผล 7 วันได้พอดี */
    [data-testid="column"] {
        padding: 1px !important;
    }
    /* ปรับแต่งปุ่มให้เล็กและกดง่ายบนมือถือ */
    .stButton button {
        font-size: 10px !important;
        padding: 2px 2px !important;
        min-height: 22px !important;
        border-radius: 4px !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# --- 1. จำลองฐานข้อมูลใน Session State ---
if "users" not in st.session_state:
    st.session_state.users = {}

if "leaves" not in st.session_state:
    # เก็บข้อมูลวันหยุด: {date_str (YYYY-MM-DD): [emp_id1, emp_id2, ...]}
    st.session_state.leaves = {}

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# ควบคุมเดือนและปีที่แสดงในปฏิทิน (ค่าเริ่มต้นเป็นเดือนปัจจุบัน)
if "current_year" not in st.session_state:
    st.session_state.current_year = date.today().year
if "current_month" not in st.session_state:
    st.session_state.current_month = date.today().month

# --- ฟังก์ชันช่วยเหลือ ---


def get_user_leave_count(emp_id):
    """นับจำนวนวันที่พนักงานคนนี้ลงหยุดไปแล้ว"""
    count = 0
    for d, emp_list in st.session_state.leaves.items():
        if emp_id in emp_list:
            count += 1
    return count


THAI_MONTHS = [
    "",
    "มกราคม",
    "กุมภาพันธ์",
    "มีนาคม",
    "เมษายน",
    "พฤษภาคม",
    "มิถุนายน",
    "กรกฎาคม",
    "สิงหาคม",
    "กันยายน",
    "ตุลาคม",
    "พฤศจิกายน",
    "ธันวาคม",
]

# --- 2. หน้าจอ Login และ ลงทะเบียน (หน้าแรก) ---
if not st.session_state.logged_in_user:
    st.markdown(
        "<h3 style='text-align: center;'>📌 ระบบลงวันหยุดพนักงาน</h3>",
        unsafe_allow_html=True,
    )
    tab_login, tab_register = st.tabs(
        ["เข้าสู่ระบบ (Login)", "ลงทะเบียนพนักงาน"]
    )

    with tab_login:
        st.subheader("เข้าสู่ระบบ")
        login_emp_id = st.text_input(
            "รหัสพนักงาน", key="login_id", placeholder="เช่น EMP001"
        )

        if st.button("เข้าสู่ระบบ", type="primary", use_container_width=True):
            emp_id = login_emp_id.strip()
            if not emp_id:
                st.warning("กรุณากรอกรหัสพนักงาน")
            elif emp_id in st.session_state.users:
                st.session_state.logged_in_user = emp_id
                st.rerun()
            else:
                st.error("ไม่พบรหัสพนักงานนี้ กรุณาลงทะเบียนก่อน")

    with tab_register:
        st.subheader("ลงทะเบียนพนักงานใหม่")
        reg_emp_id = st.text_input("รหัสพนักงาน", key="reg_id")
        reg_nickname = st.text_input("ชื่อเล่น", key="reg_nick")
        reg_firstname = st.text_input("ชื่อจริง", key="reg_first")

        if st.button("ลงทะเบียน", use_container_width=True):
            emp_id = reg_emp_id.strip()
            nickname = reg_nickname.strip()
            firstname = reg_firstname.strip()

            if not emp_id or not nickname or not firstname:
                st.warning("กรุณากรอกข้อมูลให้ครบทุกช่อง")
            elif emp_id in st.session_state.users:
                st.error("รหัสพนักงานนี้มีอยู่ในระบบแล้ว")
            else:
                st.session_state.users[emp_id] = {
                    "nickname": nickname,
                    "firstname": firstname,
                }
                st.success("ลงทะเบียนสำเร็จ! สลับไปที่แถบเข้าสู่ระบบได้เลย")

# --- 3. ส่วนของระบบหลัง Login (ปฏิทินแบบตารางเต็มเดือน สไตล์มือถือ) ---
else:
    current_user = st.session_state.logged_in_user
    user_info = st.session_state.users[current_user]

    # แถบด้านบน
    col_head1, col_head2 = st.columns([3, 1])
    with col_head1:
        st.write(
            f"👤 **{user_info['nickname']}** (`{current_user}`)"
        )
    with col_head2:
        if st.button("ออกจากระบบ", use_container_width=True):
            st.session_state.logged_in_user = None
            st.rerun()

    # โควต้าวันหยุด
    used_leaves = get_user_leave_count(current_user)
    remaining_leaves = 4 - used_leaves
    st.caption(
        f"ℹ️ โควต้าวันหยุด: ใช้ไป **{used_leaves}/4** วัน (เหลือ **{remaining_leaves}** วัน)"
    )

    # แถบควบคุมเดือน/ปี และปุ่ม "วันนี้"
    c_today, c_prev, c_title, c_next = st.columns([1.2, 0.8, 2.2, 0.8])
    with c_today:
        if st.button("📅 วันนี้", use_container_width=True):
            st.session_state.current_year = date.today().year
            st.session_state.current_month = date.today().month
            st.rerun()
    with c_prev:
        if st.button("◀", use_container_width=True):
            if st.session_state.current_month == 1:
                st.session_state.current_month = 12
                st.session_state.current_year -= 1
            else:
                st.session_state.current_month -= 1
            st.rerun()
    with c_title:
        st.markdown(
            f"<div style='text-align: center; font-weight: bold; font-size: 16px; padding-top: 5px;'>{THAI_MONTHS[st.session_state.current_month]} {st.session_state.current_year + 543}</div>",
            unsafe_allow_html=True,
        )
    with c_next:
        if st.button("▶", use_container_width=True):
            if st.session_state.current_month == 12:
                st.session_state.current_month = 1
                st.session_state.current_year += 1
            else:
                st.session_state.current_month += 1
            st.rerun()

    st.markdown("---")

    # สร้างปฏิทินแบบตาราง 7 วัน (เริ่มต้นวันอาทิตย์เหมือนในภาพตัวอย่าง: firstweekday=6)
    cal = calendar.Calendar(firstweekday=6)
    month_days = cal.monthdayscalendar(
        st.session_state.current_year, st.session_state.current_month
    )

    # หัวตารางวันในสัปดาห์ (อาทิตย์ - เสาร์)
    weekdays_name = [
        "อาทิตย์",
        "จันทร์",
        "อังคาร",
        "พุธ",
        "พฤหัส",
        "ศุกร์",
        "เสาร์",
    ]
    header_cols = st.columns(7)
    for i, day_name in enumerate(weekdays_name):
        header_cols[i].markdown(
            f"<div style='text-align: center; font-size: 11px; font-weight: bold; background-color: #f0f2f6; padding: 4px 0; border-radius: 3px;'>{day_name}</div>",
            unsafe_allow_html=True,
        )

    st.markdown(
        "<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True
    )

    # เช็ควันที่ปัจจุบันสำหรับไฮไลท์ช่อง "วันนี้"
    today_date_str = date.today().strftime("%Y-%m-%d")

    # วนลูปสร้างตารางปฏิทิน
    for week in month_days:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.markdown(
                        "<div style='color: transparent; height: 85px;'>-</div>",
                        unsafe_allow_html=True,
                    )
                else:
                    current_date_obj = date(
                        st.session_state.current_year,
                        st.session_state.current_month,
                        day,
                    )
                    date_str = current_date_obj.strftime("%Y-%m-%d")

                    if date_str not in st.session_state.leaves:
                        st.session_state.leaves[date_str] = []

                    emp_list = st.session_state.leaves[date_str]
                    is_my_leave = current_user in emp_list
                    is_today = date_str == today_date_str

                    # กำหนดสีพื้นหลังช่อง (ถ้าเป็นวันนี้ให้มีกรอบหรือสีไฮไลท์อ่อนๆ)
                    bg_color = (
                        "#fffbe6" if is_today else "#ffffff"
                    )  # เหลืองอ่อนถ้าเป็นวันนี้
                    border_color = "#ffc107" if is_today else "#e0e0e0"

                    with st.container(border=True):
                        # แสดงวันที่และจำนวนคนหยุดแบบย่อ
                        st.markdown(
                            f"<div style='font-size: 12px; font-weight: bold;'>{day} <span style='font-size: 9px; color: gray; float: right;'>{len(emp_list)}/3</span></div>",
                            unsafe_allow_html=True,
                        )

                        # แสดงรายชื่อคนที่ลงหยุดในช่องวันที่
                        if emp_list:
                            names_html = "<div style='min-height: 28px; max-height: 38px; overflow-y: auto;'>"
                            for e in emp_list:
                                if e in st.session_state.users:
                                    n_name = st.session_state.users[e][
                                        "nickname"
                                    ]
                                    names_html += f"<div style='background-color: #e6f0ff; color: #004085; padding: 1px 2px; margin-bottom: 1px; border-radius: 2px; font-size: 9px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{n_name}</div>"
                            names_html += "</div>"
                            st.markdown(names_html, unsafe_allow_html=True)
                        else:
                            st.markdown(
                                "<div style='min-height: 28px; font-size: 9px; color: #ccc;'>-</div>",
                                unsafe_allow_html=True,
                            )

                        # ปุ่มกดลงหยุด / ยกเลิก
                        btn_key = f"btn_{date_str}_{current_user}"
                        if not is_my_leave:
                            if st.button("ลงหยุด", key=btn_key, use_container_width=True):
                                if len(emp_list) >= 3:
                                    st.error("เต็ม 3 คนแล้ว")
                                elif used_leaves >= 4:
                                    st.error("ครบ 4 วันแล้ว")
                                else:
                                    st.session_state.leaves[date_str].append(
                                        current_user
                                    )
                                    st.rerun()
                        else:
                            if st.button("ยกเลิก", key=btn_key, use_container_width=True):
                                st.session_state.leaves[date_str].remove(
                                    current_user
                                )
                                st.rerun()
