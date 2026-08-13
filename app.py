import calendar
from datetime import datetime, date
import streamlit as set_default_config

# ตั้งค่าหน้าเว็บ
import streamlit as st

st.set_page_config(
    page_title="ระบบลงวันหยุดพนักงาน", page_icon="📅", layout="wide"
)

# --- 1. จำลองฐานข้อมูลใน Session State ---
if "users" not in st.session_state:
    st.session_state.users = {}

if "leaves" not in st.session_state:
    # เก็บข้อมูลวันหยุด: {date_str (YYYY-MM-DD): [emp_id1, emp_id2, ...]}
    st.session_state.leaves = {}

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# ควบคุมเดือนและปีที่แสดงในปฏิทิน
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
        "<h2 style='text-align: center;'>📌 ระบบลงวันหยุดพนักงาน</h2>",
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
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

# --- 3. ส่วนของระบบหลัง Login (ปฏิทินแบบตารางช่องๆ) ---
else:
    current_user = st.session_state.logged_in_user
    user_info = st.session_state.users[current_user]

    # แถบด้านบน
    col_head1, col_head2 = st.columns([3, 1])
    with col_head1:
        st.title("📅 ตารางปฏิทินวันหยุด")
        st.write(
            f"ผู้ใช้งาน: **{user_info['nickname']} ({user_info['firstname']})** | รหัส: `{current_user}`"
        )
    with col_head2:
        if st.button("ออกจากระบบ", use_container_width=True):
            st.session_state.logged_in_user = None
            st.rerun()

    st.markdown("---")

    # โควต้าวันหยุด
    used_leaves = get_user_leave_count(current_user)
    remaining_leaves = 4 - used_leaves
    st.info(
        f"ℹ️ โควต้าวันหยุดของคุณ: ใช้ไปแล้ว **{used_leaves}/4** วัน (เหลือสิทธิ์ลงได้อีก **{remaining_leaves}** วัน)"
    )

    # ควบคุมเปลี่ยนเดือน/ปี
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("⬅️ เดือนก่อนหน้า", use_container_width=True):
            if st.session_state.current_month == 1:
                st.session_state.current_month = 12
                st.session_state.current_year -= 1
            else:
                st.session_state.current_month -= 1
            st.rerun()
    with c2:
        st.markdown(
            f"<h3 style='text-align: center;'>{THAI_MONTHS[st.session_state.current_month]} {st.session_state.current_year + 543}</h3>",
            unsafe_allow_html=True,
        )
    with c3:
        if st.button("เดือนถัดไป ➡️", use_container_width=True):
            if st.session_state.current_month == 12:
                st.session_state.current_month = 1
                st.session_state.current_year += 1
            else:
                st.session_state.current_month += 1
            st.rerun()

    st.write(
        "💡 **วิธีใช้งาน:** คลิกที่ปุ่มใต้วันที่เพื่อ **ลงวันหยุด** หรือ **ยกเลิกวันหยุด** ของคุณ (จำกัดไม่เกิน 3 คน/วัน)"
    )

    # สร้างปฏิทินแบบตารางสัปดาห์ (จันทร์ - อาทิตย์)
    cal = calendar.Calendar(firstweekday=0)  # เริ่มต้นวันจันทร์
    month_days = cal.monthdayscalendar(
        st.session_state.current_year, st.session_state.current_month
    )

    # หัวตารางวันในสัปดาห์
    weekdays_name = [
        "จันทร์",
        "อังคาร",
        "พุธ",
        "พฤหัสบดี",
        "ศุกร์",
        "เสาร์",
        "อาทิตย์",
    ]
    header_cols = st.columns(7)
    for i, day_name in enumerate(weekdays_name):
        header_cols[i].markdown(
            f"<div style='text-align: center; font-weight: bold; background-color: #f0f2f6; padding: 8px; border-radius: 5px;'>{day_name}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # วนลูปสร้างตารางปฏิทิน
    for week in month_days:
        cols = st.columns(7)
        for i, day in enumerate(week):
            with cols[i]:
                if day == 0:
                    st.markdown(
                        "<div style='color: lightgray; height: 120px;'>-</div>",
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

                    # กล่องแสดงผลในแต่ละวัน
                    with st.container(border=True):
                        st.markdown(
                            f"**{day}** <span style='font-size: 11px; float: right; color: gray;'>({len(emp_list)}/3)</span>",
                            unsafe_allow_html=True,
                        )

                        # แสดงชื่อคนที่หยุดในช่อง (ตามแบบที่ต้องการ)
                        if emp_list:
                            names_html = ""
                            for e in emp_list:
                                if e in st.session_state.users:
                                    n_name = st.session_state.users[e][
                                        "nickname"
                                    ]
                                    names_html += f"<div style='background-color: #e6f0ff; color: #004085; padding: 2px 4px; margin-bottom: 2px; border-radius: 3px; font-size: 12px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>- {n_name}</div>"
                            st.markdown(names_html, unsafe_allow_html=True)
                        else:
                            st.markdown(
                                "<div style='font-size: 11px; color: #ccc;'>ยังไม่มีคนหยุด</div>",
                                unsafe_allow_html=True,
                            )

                        # ปุ่มกดเลือก/ยกเลิกวันหยุด
                        btn_key = f"btn_{date_str}_{current_user}"
                        if not is_my_leave:
                            if st.button("🟢 ลงหยุด", key=btn_key, use_container_width=True):
                                if len(emp_list) >= 3:
                                    st.error("เต็ม 3 คนแล้ว!")
                                elif used_leaves >= 4:
                                    st.error("ใช้สิทธิ์ครบ 4 วันแล้ว!")
                                else:
                                    st.session_state.leaves[date_str].append(
                                        current_user
                                    )
                                    st.rerun()
                        else:
                            if st.button("🔴 ยกเลิก", key=btn_key, use_container_width=True):
                                st.session_state.leaves[date_str].remove(
                                    current_user
                                )
                                st.rerun()
