from collections import Counter, defaultdict
from datetime import date

import pandas as pd
import streamlit as st

from pawpal_system import format_time_12h, pet_species_icon, task_type_icon
from app_common import get_owners

VET_ICONS = {"🏥", "💊"}
PATIENTS_PER_PAGE = 8


def render_info_card(owner, pet) -> None:
    """Render the mockup's "Info" card: identity basics plus the owner."""
    with st.container(border=True):
        st.markdown("**Info**")
        st.write(f"**Name:** {pet.name}")
        st.write(f"**Owner:** {owner.name}")
        st.write(f"**Breed:** {pet.breed or '—'}")
        st.write(f"**Weight:** {pet.weight or '—'}")
        st.write(f"**Sex:** {pet.sex or '—'}")
        st.write(f"**Age:** {pet.age if pet.age is not None else '—'}")
        st.write(f"**Status:** {pet.status}")


def render_visit_statistics_card(pet) -> None:
    """Render the monthly completed-vet-visit line chart card."""
    with st.container(border=True):
        st.markdown("**📈 Visit statistics**")
        monthly_counts = defaultdict(int)
        for task in pet.tasks:
            if task.completed and task_type_icon(task.title) in VET_ICONS:
                monthly_counts[date(task.due_date.year, task.due_date.month, 1)] += 1
        if monthly_counts:
            sorted_months = sorted(monthly_counts.keys())
            chart_data = pd.DataFrame(
                {"Vet visits": [monthly_counts[month] for month in sorted_months]},
                index=[month.strftime("%b %Y") for month in sorted_months],
            )
            st.line_chart(chart_data)
        else:
            st.info("No completed vet visits yet.")


def render_diet_card(pet) -> None:
    """Render the mockup's "Diet" card: should/should-not bullet lists."""
    with st.container(border=True):
        st.markdown("**Diet**")
        st.markdown("✅ **The diet should contain:**")
        if pet.diet_good:
            for item in pet.diet_good:
                st.markdown(f"- {item}")
        else:
            st.caption("Not set yet.")
        st.markdown("❌ **The diet should not contain:**")
        if pet.diet_bad:
            for item in pet.diet_bad:
                st.markdown(f"- {item}")
        else:
            st.caption("Not set yet.")


def render_chronic_card(pet) -> None:
    """Render the chronic-conditions card, bolding each condition's name."""
    with st.container(border=True):
        st.markdown("**🩺 Chronic diseases**")
        if pet.chronic_conditions:
            for entry in pet.chronic_conditions:
                name, separator, note = entry.partition(":")
                if separator:
                    st.markdown(f"- **{name.strip()}**: {note.strip()}")
                else:
                    st.markdown(f"- {entry.strip()}")
        else:
            st.caption("No chronic conditions on file.")


def render_appointment_reason_card(pet) -> None:
    """Render the appointment-reason card from the most relevant task notes."""
    with st.container(border=True):
        st.markdown("**🐾 Appointment Reason**")
        today = date.today()
        upcoming_with_notes = [t for t in pet.tasks if t.notes and t.due_date >= today]
        past_with_notes = [t for t in pet.tasks if t.notes and t.due_date < today]
        if upcoming_with_notes:
            reason_task = min(upcoming_with_notes, key=lambda t: (t.due_date, t.time))
        elif past_with_notes:
            reason_task = max(past_with_notes, key=lambda t: (t.due_date, t.time))
        else:
            reason_task = None
        if reason_task:
            st.write(reason_task.notes)
        else:
            st.caption("No notes yet.")


owners = get_owners()
pet_pairs = [(owner, pet) for owner in owners for pet in owner.pets]

st.title("📊 Dashboard")
st.caption("A per-patient clinical overview across every owner.")

if not pet_pairs:
    st.info("Add a pet to see their dashboard here.")
    st.page_link("pages/patients.py", label="Go to Patients", icon="🧾")
else:
    # Pill-style patient switcher (like the mockup's Tortilla/Noodle/Charlie
    # bar), paginated so a large roster shows one row at a time. Duplicate
    # pet names across different owners get the owner's name appended so two
    # pills never look identical.
    name_counts = Counter(pet.name for _, pet in pet_pairs)

    def pill_label(index: int) -> str:
        owner, pet = pet_pairs[index]
        label = f"{pet_species_icon(pet.species)} {pet.name}"
        if name_counts[pet.name] > 1:
            label += f" · {owner.name}"
        return label

    if "dashboard_selected_pet" not in st.session_state:
        st.session_state.dashboard_selected_pet = 0
    if "dashboard_pill_page" not in st.session_state:
        st.session_state.dashboard_pill_page = 0

    total_pages = (len(pet_pairs) + PATIENTS_PER_PAGE - 1) // PATIENTS_PER_PAGE
    pill_page = min(st.session_state.dashboard_pill_page, total_pages - 1)
    page_start = pill_page * PATIENTS_PER_PAGE
    page_options = list(range(page_start, min(page_start + PATIENTS_PER_PAGE, len(pet_pairs))))
    # Each page gets its own widget key: reusing one key while the options
    # list changes underneath it would leave a stale (now-invalid) value in
    # session state and crash the pills widget on rerun.
    page_pills_key = f"dashboard_pet_pills_{pill_page}"

    def _select_pet_from_pills() -> None:
        # on_change only fires on a real click (never on rerender), so this
        # can't clobber a selection made on a different page the way an
        # inline "if value != selection" sync would.
        picked = st.session_state.get(page_pills_key)
        if picked is not None:
            st.session_state.dashboard_selected_pet = picked

    nav_prev, nav_label, nav_next = st.columns([1, 6, 1])
    with nav_prev:
        if st.button("◀", key="pill_page_prev", disabled=pill_page == 0):
            new_page = pill_page - 1
            st.session_state.dashboard_pill_page = new_page
            # Drop the destination page's old widget state so its pills
            # re-render highlighting the current selection (or nothing),
            # instead of a stale pick from an earlier visit.
            st.session_state.pop(f"dashboard_pet_pills_{new_page}", None)
            st.rerun()
    with nav_label:
        default_on_page = (
            st.session_state.dashboard_selected_pet
            if st.session_state.dashboard_selected_pet in page_options
            else None
        )
        st.pills(
            "Patient",
            page_options,
            format_func=pill_label,
            default=default_on_page,
            key=page_pills_key,
            on_change=_select_pet_from_pills,
            label_visibility="collapsed",
        )
        st.caption(f"Patients {page_start + 1}–{page_options[-1] + 1} of {len(pet_pairs)}")
    with nav_next:
        if st.button("▶", key="pill_page_next", disabled=pill_page >= total_pages - 1):
            new_page = pill_page + 1
            st.session_state.dashboard_pill_page = new_page
            st.session_state.pop(f"dashboard_pet_pills_{new_page}", None)
            st.rerun()

    selected_index = min(st.session_state.dashboard_selected_pet, len(pet_pairs) - 1)
    selected_owner, selected_pet = pet_pairs[selected_index]

    top_row = st.columns(3)
    with top_row[0]:
        render_info_card(selected_owner, selected_pet)
    with top_row[1]:
        render_visit_statistics_card(selected_pet)
    with top_row[2]:
        render_diet_card(selected_pet)

    middle_row = st.columns(2)
    with middle_row[0]:
        render_chronic_card(selected_pet)
    with middle_row[1]:
        render_appointment_reason_card(selected_pet)

    st.divider()
    with st.container(border=True):
        today = date.today()
        all_task_triples = [
            (owner, pet, task)
            for owner, pet in pet_pairs
            for task in pet.tasks
        ]
        open_today = [
            triple for triple in all_task_triples
            if triple[2].due_date == today and not triple[2].completed
        ]
        st.markdown("**Today**")
        st.metric("Appointments", len(open_today))

        st.markdown("**Upcoming Appointments**")
        upcoming = sorted(
            (
                triple for triple in all_task_triples
                if triple[2].due_date >= today and not triple[2].completed
            ),
            key=lambda triple: (triple[2].due_date, triple[2].time),
        )[:5]
        if upcoming:
            for upcoming_owner, upcoming_pet, upcoming_task in upcoming:
                st.write(
                    f"{task_type_icon(upcoming_task.title)} {upcoming_pet.name} — "
                    f"{upcoming_task.title} ({format_time_12h(upcoming_task.time)}, "
                    f"{upcoming_task.due_date.isoformat()})"
                )
        else:
            st.caption("No upcoming appointments.")
