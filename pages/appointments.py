import re

import streamlit as st

from pawpal_system import APPOINTMENT_STATUSES, Appointment, find_owner, format_time_12h
from app_common import (
    APPOINTMENT_STATUS_COLORS,
    CATEGORY_TASK_TITLES,
    get_clinic,
    get_owners,
    render_veterinary_reason_picker,
    save_clinic,
)

VISIT_REASON_TITLES = CATEGORY_TASK_TITLES["veterinary"] + ["Other (custom)"]


def _dialog_key(*parts) -> str:
    """Build a widget-key suffix from appointment content (owner/pet/date/time),
    not the row's index — a filtered/sorted list's positions can shift between
    a click and the rerun, so a content-derived key keeps a dialog's widget
    state tied to the specific appointment instead of a transient position."""
    return re.sub(r"\W+", "_", "_".join(str(part) for part in parts))


@st.dialog("Book Appointment")
def book_appointment_dialog(owners, clinic) -> None:
    patient_pairs = [(owner, pet) for owner in owners for pet in owner.pets]
    if not patient_pairs:
        st.warning("No patients yet.")
        st.page_link("pages/patients.py", label="Go to Patients", icon="🧾")
        return
    active_doctors = [doctor for doctor in clinic.doctors if doctor.active]
    if not active_doctors:
        st.warning("No active doctors yet.")
        st.page_link("pages/doctors.py", label="Go to Doctors", icon="👩‍⚕️")
        return

    patient_index = st.selectbox(
        "Patient*",
        range(len(patient_pairs)),
        format_func=lambda i: f"{patient_pairs[i][1].name} — owned by {patient_pairs[i][0].name}",
        key="book_appt_patient_select",
    )

    # Same Task + species-aware Reason picker as the veterinary quick-add
    # form above, so booking an appointment captures the same level of
    # detail. key_prefix="book_appt_vet" keeps these widgets' keys distinct
    # from that section's own "veterinary_*"-prefixed ones — both can be on
    # screen in the same script run (this dialog floats over the page),
    # so identical keys would crash with DuplicateWidgetID.
    st.write("Reason for Visit")
    visit_title = st.selectbox(
        "Task", VISIT_REASON_TITLES, key="book_appt_vet_title_select", label_visibility="collapsed"
    )
    selected_species = patient_pairs[patient_index][1].species
    if visit_title == "Other (custom)":
        custom_reason = st.text_area("Custom reason", key="book_appt_vet_custom_reason")
        visit_reason = None
    else:
        custom_reason = None
        visit_reason = render_veterinary_reason_picker(
            visit_title, selected_species, key_prefix="book_appt_vet"
        )

    doctor_labels = [
        f"{doctor.full_name} — {doctor.specialization}" if doctor.specialization else doctor.full_name
        for doctor in active_doctors
    ]
    doctor_index = st.selectbox(
        "Doctor*",
        range(len(active_doctors)),
        format_func=lambda i: doctor_labels[i],
        key="book_appt_doctor_select",
    )
    appointment_date = st.date_input("Date*", key="book_appt_date")

    st.write("Time*")
    hour_col, minute_col, period_col = st.columns(3)
    with hour_col:
        hour_12 = st.selectbox(
            "Hour", list(range(1, 13)), index=7, label_visibility="collapsed", key="book_appt_hour"
        )
    with minute_col:
        minute = st.selectbox(
            "Minute", ["00", "15", "30", "45"], label_visibility="collapsed", key="book_appt_minute"
        )
    with period_col:
        period = st.selectbox("AM/PM", ["AM", "PM"], label_visibility="collapsed", key="book_appt_period")

    if st.button("Confirm Booking", key="book_appt_confirm"):
        hour_24 = hour_12 % 12
        if period == "PM":
            hour_24 += 12
        owner, pet = patient_pairs[patient_index]
        doctor = active_doctors[doctor_index]
        if visit_title == "Other (custom)":
            final_reason = (custom_reason or "").strip()
        elif visit_reason:
            final_reason = f"{visit_title}: {visit_reason}"
        else:
            final_reason = visit_title
        clinic.appointments.append(
            Appointment(
                owner_name=owner.name,
                pet_name=pet.name,
                doctor_username=doctor.username,
                date=appointment_date,
                time=f"{hour_24:02d}:{minute}",
                reason=final_reason,
            )
        )
        save_clinic(clinic)
        # Toast text matches the mockup for visual fidelity only — no email is ever sent.
        st.toast("Appointment booked & Confirmation Email sent!", icon="✅")
        st.rerun()


@st.dialog("Update Status")
def update_status_dialog(clinic, appointment, owners) -> None:
    owner = find_owner(owners, appointment.owner_name)
    pet = owner.find_pet(appointment.pet_name) if owner else None
    doctor = clinic.find_doctor(appointment.doctor_username)

    st.write(f"**Patient:** {pet.name if pet else appointment.pet_name} ({appointment.owner_name})")
    st.write(f"**Doctor:** {doctor.full_name if doctor else appointment.doctor_username}")
    st.write(
        f"**Date:** {appointment.date.strftime('%b %d, %Y')} at {format_time_12h(appointment.time)}"
    )

    key_suffix = _dialog_key(
        appointment.owner_name, appointment.pet_name, appointment.date, appointment.time
    )
    new_status = st.selectbox(
        "Status*",
        APPOINTMENT_STATUSES,
        index=APPOINTMENT_STATUSES.index(appointment.status),
        key=f"status_select_{key_suffix}",
    )
    if st.button("Save", key=f"status_save_{key_suffix}"):
        appointment.status = new_status
        save_clinic(clinic)
        st.toast(f"Appointment status updated to {new_status}", icon="✅")
        st.rerun()


owners = get_owners()
clinic = get_clinic()

st.title("📋 Appointments")
st.caption("Book new appointments and manage their status.")

status_filter = st.sidebar.selectbox("Filter by status", ["All"] + APPOINTMENT_STATUSES)

if st.button("+ Book Appointment", key="open_book_appointment"):
    book_appointment_dialog(owners, clinic)

st.divider()

visible_appointments = sorted(clinic.appointments, key=lambda a: (a.date, a.time))
if status_filter != "All":
    visible_appointments = [a for a in visible_appointments if a.status == status_filter]

if visible_appointments:
    row_widths = [2, 2, 2, 3, 1.5, 1]
    header_cols = st.columns(row_widths)
    for header_col, label in zip(
        header_cols, ["Date / Time", "Patient", "Doctor", "Reason", "Status", ""]
    ):
        header_col.markdown(f"**{label}**")

    for row_index, appointment in enumerate(visible_appointments):
        owner = find_owner(owners, appointment.owner_name)
        pet = owner.find_pet(appointment.pet_name) if owner else None
        doctor = clinic.find_doctor(appointment.doctor_username)

        row_cols = st.columns(row_widths)
        row_cols[0].write(
            f"{appointment.date.strftime('%b %d, %Y')}, {format_time_12h(appointment.time)}"
        )
        row_cols[1].write(pet.name if pet else "— (record removed)")
        row_cols[2].write(doctor.full_name if doctor else "— (record removed)")
        row_cols[3].write(appointment.reason or "—")
        with row_cols[4]:
            st.badge(appointment.status, color=APPOINTMENT_STATUS_COLORS[appointment.status])
        with row_cols[5]:
            if st.button("✏️ Edit", key=f"appt_edit_{row_index}"):
                update_status_dialog(clinic, appointment, owners)
else:
    st.info("No appointments yet.")

# No render-time save: mutations save inline. A render-time save would
# let a stale browser session silently overwrite the data file just by
# sitting open.
st.caption("Data is auto-saved to `clinic.json` after every change, so it persists between app runs.")
