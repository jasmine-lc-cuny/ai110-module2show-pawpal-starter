import streamlit as st

from pawpal_system import Doctor
from app_common import get_clinic, save_clinic

clinic = get_clinic()

st.title("👩‍⚕️ Doctors")
st.caption("Manage the clinic's medical staff.")

st.subheader("Add New Doctor")
# Same collapse pattern as the Patients page forms: a session flag +
# button rather than st.expander, so a successful save can reliably
# close it (expander toggle state lives client-side with no key).
if "show_add_doctor" not in st.session_state:
    st.session_state.show_add_doctor = False

if not st.session_state.show_add_doctor:
    if st.button("➕ Add a new doctor", key="add_doctor_show"):
        st.session_state.show_add_doctor = True
        st.rerun()
else:
    if st.button("🔼 View less", key="add_doctor_hide"):
        st.session_state.show_add_doctor = False
        st.rerun()

    with st.form("add_doctor_form", clear_on_submit=True):
        st.markdown("**Login Details**")
        login_cols = st.columns(2)
        with login_cols[0]:
            first_name = st.text_input("First name")
            username = st.text_input("Username*")
            email = st.text_input("Email address")
        with login_cols[1]:
            last_name = st.text_input("Last name")
            password = st.text_input(
                "Password*",
                type="password",
                help="Stored as a plain record field for reference only — PawPal+ has no login system.",
            )
            phone = st.text_input("Phone")

        st.markdown("**Professional Details**")
        prof_cols = st.columns(2)
        with prof_cols[0]:
            department_name = st.text_input("Department*")
            specialization = st.text_input("Specialization*")
        with prof_cols[1]:
            education = st.text_input("Education")
            visit_fee = st.number_input("Visit Fee ($)", min_value=0.0, step=1.0, value=0.0)
        active = st.checkbox("Active", value=True)

        submitted_doctor = st.form_submit_button("Save Doctor")

    if submitted_doctor:
        if not username.strip() or not password or not specialization.strip():
            st.error("Username, password, and specialization are required.")
        elif clinic.find_doctor(username.strip()):
            st.error(f"Username '{username.strip()}' is already in use.")
        else:
            clinic.doctors.append(
                Doctor(
                    first_name=first_name.strip(),
                    last_name=last_name.strip(),
                    username=username.strip(),
                    password=password,
                    email=email.strip() or None,
                    phone=phone.strip() or None,
                    department_name=department_name.strip(),
                    specialization=specialization.strip(),
                    education=education.strip(),
                    visit_fee=float(visit_fee),
                    active=active,
                )
            )
            save_clinic(clinic)
            # Collapse the add-doctor section after a successful save.
            st.session_state.show_add_doctor = False
            st.success(f"Added Dr. {first_name.strip()} {last_name.strip()}.")
            st.rerun()

st.divider()
st.subheader("Medical Staff")
if clinic.doctors:
    st.table(
        [
            {
                "Doctor Name": doctor.full_name,
                "Department": doctor.department_name,
                "Specialization": doctor.specialization,
                "Mobile": doctor.phone or "—",
                "Visit Fee": f"${doctor.visit_fee:.2f}",
                "Status": "Active" if doctor.active else "Inactive",
            }
            for doctor in clinic.doctors
        ]
    )

    delete_doctor_index = st.selectbox(
        "Delete a doctor",
        range(len(clinic.doctors)),
        format_func=lambda i: clinic.doctors[i].full_name,
        key="delete_doctor_select",
    )
    if st.button("Delete doctor", key="delete_doctor_button"):
        removed = clinic.doctors.pop(delete_doctor_index)
        save_clinic(clinic)
        st.success(f"Deleted {removed.full_name}.")
        st.rerun()
else:
    st.info("No doctors yet.")

# No render-time save: mutations save inline. A render-time save would
# let a stale browser session silently overwrite the data file just by
# sitting open.
st.caption("Data is auto-saved to `clinic.json` after every change, so it persists between app runs.")
