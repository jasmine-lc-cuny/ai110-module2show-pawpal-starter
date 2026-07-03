import streamlit as st

from pawpal_system import Staff
from app_common import SERVICE_SECTIONS, get_clinic, save_clinic

clinic = get_clinic()
section_labels = [label for _, label in SERVICE_SECTIONS]
section_icons = dict((label, icon) for icon, label in SERVICE_SECTIONS)

st.title("👥 Service Staff")
st.caption("Manage the team assigned to each bookable service.")

st.subheader("Add New Staff Member")
# Same collapse pattern as the Doctors/Patients pages: a session flag + button
# rather than st.expander, so a successful save can reliably close it.
if "show_add_staff" not in st.session_state:
    st.session_state.show_add_staff = False

if not st.session_state.show_add_staff:
    if st.button("➕ Add a new staff member", key="add_staff_show"):
        st.session_state.show_add_staff = True
        st.rerun()
else:
    if st.button("🔼 View less", key="add_staff_hide"):
        st.session_state.show_add_staff = False
        st.rerun()

    with st.form("add_staff_form", clear_on_submit=True):
        name_cols = st.columns(2)
        with name_cols[0]:
            first_name = st.text_input("First name*")
            username = st.text_input("Username*")
            email = st.text_input("Email address")
        with name_cols[1]:
            last_name = st.text_input("Last name")
            phone = st.text_input("Phone")

        assign_cols = st.columns(2)
        with assign_cols[0]:
            section = st.selectbox(
                "Service section*",
                section_labels,
                format_func=lambda label: f"{section_icons[label]} {label}",
            )
        with assign_cols[1]:
            role = st.text_input("Role / title", placeholder="e.g. Senior Groomer")
        rate = st.number_input("Rate per session ($)", min_value=0.0, step=1.0, value=0.0)
        active = st.checkbox("Active", value=True)

        submitted_staff = st.form_submit_button("Save Staff Member")

    if submitted_staff:
        if not first_name.strip() or not username.strip():
            st.error("First name and username are required.")
        elif clinic.find_staff(username.strip()):
            st.error(f"Username '{username.strip()}' is already in use.")
        else:
            clinic.staff.append(
                Staff(
                    first_name=first_name.strip(),
                    last_name=last_name.strip(),
                    username=username.strip(),
                    section=section,
                    role=role.strip(),
                    phone=phone.strip() or None,
                    email=email.strip() or None,
                    rate=float(rate),
                    active=active,
                )
            )
            save_clinic(clinic)
            st.session_state.show_add_staff = False
            st.success(f"Added {first_name.strip()} {last_name.strip()} to {section}.")
            st.rerun()

st.divider()
st.subheader("Team by Service")

if clinic.staff:
    section_tabs = st.tabs(
        [f"{icon} {label} ({len(clinic.staff_in_section(label))})" for icon, label in SERVICE_SECTIONS]
    )
    for section_tab, (icon, label) in zip(section_tabs, SERVICE_SECTIONS):
        with section_tab:
            members = clinic.staff_in_section(label)
            if members:
                st.table(
                    [
                        {
                            "Name": member.full_name,
                            "Role": member.role or "—",
                            "Phone": member.phone or "—",
                            "Rate": f"${member.rate:.2f}",
                            "Status": "Active" if member.active else "Inactive",
                        }
                        for member in members
                    ]
                )
            else:
                st.info(f"No staff assigned to {label} yet.")

    st.divider()
    delete_staff_index = st.selectbox(
        "Delete a staff member",
        range(len(clinic.staff)),
        format_func=lambda i: f"{clinic.staff[i].full_name} — {clinic.staff[i].section}",
        key="delete_staff_select",
    )
    if st.button("Delete staff member", key="delete_staff_button"):
        removed = clinic.staff.pop(delete_staff_index)
        save_clinic(clinic)
        st.success(f"Deleted {removed.full_name}.")
        st.rerun()
else:
    st.info("No staff yet. Add one above, or run `python -m seed.seed_staff` to seed the team.")

# No render-time save: mutations save inline. A render-time save would let a
# stale browser session silently overwrite the data file just by sitting open.
st.caption("Data is auto-saved to `clinic.json` after every change, so it persists between app runs.")
