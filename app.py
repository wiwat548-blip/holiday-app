from datetime import datetime, date
import streamlit as st

# ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="ระบบลงวันหยุดพนักงาน", page_icon="📅", layout="centered"
)

# --- 1. จำลองฐานข้อมูลใน Session State ---
if "users" not in st.session_state:
    # เก็บข้อมูลพนักงาน: {emp_id: {"nickname": str, "firstname": str}}
    st.session_state.users = {}

if "leaves" not in st.session_state:
    # เก็บข้อมูลวันหยุด: {date_str (YYYY-MM-DD): [emp_id1, emp_id2, ...]}
    st.session_state.leaves = {}

if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

# --- ฟังก์ชันช่วยเหลือ ---


def get_user_leave_count(emp_id):
    """นับจำนวนวันที่พนักงานคนนี้ลงหยุดไปแล้ว"""
    count = 0
    for d, emp_list in st.session_state.leaves.items():
        if emp_id in emp_list:
            count += 1
    return count


# --- 2. ส่วนของหน้าจอ Login และ ลงทะเบียน (หน้าแรก) ---
if not st.session_state.logged_in_user:
    st.title("📌 ระบบลงวันหยุดพนักงาน")
    tab_login, tab_register = st.tabs(["เข้าสู่ระบบ (Login)", "ลงทะเบียนพนักงาน"])

    # --- Tab: Login ---
    with tab_login:
        st.subheader("เข้าสู่ระบบ")
        login_emp_id = st.text_input(
            "รหัสพนักงาน", key="login_id", placeholder="เช่น EMP001"
        )

        if st.button("เข้าสู่ระบบ", type="primary"):
            emp_id = login_emp_id.strip()
            if not emp_id:
                st.warning("กรุณากรอกรหัสพนักงาน")
            elif emp_id in st.session_state.users:
                st.session_state.logged_in_user = emp_id
                st.success(
                    f"ยินดีต้อนรับคุณ {st.session_state.users[emp_id]['nickname']}"
                )
                st.rerun()
            else:
                st.error("ไม่พบรหัสพนักงานนี้ในระบบ กรุณาลงทะเบียนก่อน")

    # --- Tab: Register ---
    with tab_register:
        st.subheader("ลงทะเบียนพนักงานใหม่ (ไม่ต้องใช้รหัสผ่าน)")
        reg_emp_id = st.text_input("รหัสพนักงาน", key="reg_id")
        reg_nickname = st.text_input("ชื่อเล่น", key="reg_nick")
        reg_firstname = st.text_input("ชื่อจริง", key="reg_first")

        if st.button("ลงทะเบียน"):
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
                st.success(
                    "ลงทะเบียนสำเร็จ! สามารถสลับไปที่แถบ 'เข้าสู่ระบบ' เพื่อใช้งานได้เลย"
                )

# --- 3. ส่วนของระบบหลัง Login (หน้าปฏิทินและลงวันหยุด) ---
else:
    current_user = st.session_state.logged_in_user
    user_info = st.session_state.users[current_user]

    # ส่วนหัวและปุ่มออกจากระบบ
    col_head1, col_head2 = st.columns([3, 1])
    with col_head1:
        st.title("📅 ปฏิทินลงวันหยุด")
        st.write(
            f"ผู้ใช้งาน: **{user_info['nickname']} ({user_info['firstname']})** | รหัส: `{current_user}`"
        )
    with col_head2:
        if st.button("ออกจากระบบ"):
            st.session_state.logged_in_user = None
            st.rerun()

    st.markdown("---")

    # แสดงโควต้าวันหยุดคงเหลือ
    used_leaves = get_user_leave_count(current_user)
    remaining_leaves = 4 - used_leaves
    st.info(
        f"ℹ️ โควต้าของคุณ: ลงหยุดไปแล้ว **{used_leaves}/4** วัน (เหลือสิทธิ์ลงได้อีก **{remaining_leaves}** วัน)"
    )

    st.subheader("เลือกวันที่ต้องการลงหยุด")
    st.write(
        "💡 *คลิกเลือกวันที่ด้านล่างเพื่อลงวันหยุด หรือคลิกซ้ำในวันที่เคยลงแล้วเพื่อยกเลิก*"
    )

    # สร้างตัวเลือกวันที่ (ใช้ Date Input ของ Streamlit เป็นเครื่องมือเลือกวัน)
    selected_date = st.date_input(
        "เลือกวันที่ต้องการจัดการวันหยุด",
        value=date.today(),
        min_value=date.today(),
    )
    date_str = selected_date.strftime("%Y-%m-%d")

    # จัดการข้อมูลวันหยุดของวันที่เลือก
    if date_str not in st.session_state.leaves:
        st.session_state.leaves[date_str] = []

    current_day_leaves = st.session_state.leaves[date_str]
    is_already_off = current_user in current_day_leaves

    col_btn1, col_btn2 = st.columns(2)

    with col_btn1:
        if not is_already_off:
            if st.button(
                f"✅ ยืนยันลงวันหยุดวันที่ {selected_date.strftime('%d/%m/%Y')}",
                type="primary",
            ):
                # ตรวจสอบเงื่อนไข 1: หยุดได้สูงสุดวันละ 3 คน
                if len(current_day_leaves) >= 3:
                    st.error(
                        "❌ วันนี้มีพนักงานลงหยุดครบ 3 คนแล้ว ไม่สามารถลงเพิ่มได้"
                    )
                # ตรวจสอบเงื่อนไข 2: 1 รหัสพนักงานลงได้ 4 วัน
                elif used_leaves >= 4:
                    st.error(
                        "❌ คุณใช้สิทธิ์ครบ 4 วันแล้ว ไม่สามารถลงเพิ่มได้อีก"
                    )
                else:
                    st.session_state.leaves[date_str].append(current_user)
                    st.success(
                        f"🎉 ลงวันหยุดวันที่ {selected_date.strftime('%d/%m/%Y')} สำเร็จ!"
                    )
                    st.rerun()
        else:
            if st.button(
                f"❌ ยกเลิกวันหยุดวันที่ {selected_date.strftime('%d/%m/%Y')}",
                type="secondary",
            ):
                st.session_state.leaves[date_str].remove(current_user)
                st.success(
                    f"🗑️ ยกเลิกวันหยุดวันที่ {selected_date.strftime('%d/%m/%Y')} เรียบร้อยแล้ว"
                )
                st.rerun()

    st.markdown("---")

    # --- แสดงตารางสรุปรายชื่อคนหยุดในแต่ละวัน ---
    st.subheader("👥 สรุปรายชื่อพนักงานที่หยุดในแต่ละวัน")

    if not st.session_state.leaves:
        st.write("ยังไม่มีการลงวันหยุดใดๆ ในระบบ")
    else:
        # เรียงลำดับวันที่จากน้อยไปมาก
        sorted_dates = sorted(st.session_state.leaves.keys())
        for d_str in sorted_dates:
            emp_list = st.session_state.leaves[d_str]
            if emp_list:  # แสดงเฉพาะวันที่มีคนหยุด
                formatted_date = datetime.strptime(d_str, "%Y-%m-%d").strftime(
                    "%d/%m/%Y"
                )
                names = [
                    f"{st.session_state.users[e]['nickname']} ({e})"
                    for e in emp_list
                    if e in st.session_state.users
                ]
                st.write(
                    f"📅 **{formatted_date}** (หยุด {len(emp_list)}/3 คน): {', '.join(names)}"
                )
