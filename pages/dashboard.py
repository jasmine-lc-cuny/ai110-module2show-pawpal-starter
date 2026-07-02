import html as html_escaping
from collections import Counter, defaultdict
from datetime import date, timedelta

import pandas as pd
import streamlit as st

from pawpal_system import format_time_12h, pet_species_icon, task_type_icon
from app_common import PET_TIMELINE_COLORS, get_owners, save_owners

VET_ICONS = {"🏥", "💊"}
PATIENTS_PER_PAGE = 8
WINDOW_START_MIN, WINDOW_END_MIN = 6 * 60, 22 * 60
WINDOW_SPAN_MIN = WINDOW_END_MIN - WINDOW_START_MIN


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


def render_edit_profile(pet, pet_index: int) -> None:
    """Render the weight/diet/chronic-conditions edit form, tucked in an expander."""
    with st.expander("✏️ Edit profile (weight, diet, chronic conditions)"):
        with st.form(f"edit_profile_form_{pet_index}"):
            weight_input = st.text_input(
                "Weight", value=pet.weight or "", key=f"weight_input_{pet_index}"
            )
            diet_good_input = st.text_area(
                "Diet should contain (one per line)",
                value="\n".join(pet.diet_good),
                key=f"diet_good_input_{pet_index}",
            )
            diet_bad_input = st.text_area(
                "Diet should not contain (one per line)",
                value="\n".join(pet.diet_bad),
                key=f"diet_bad_input_{pet_index}",
            )
            chronic_input = st.text_area(
                "Chronic conditions (one per line, e.g. 'Glaucoma: joint pain')",
                value="\n".join(pet.chronic_conditions),
                key=f"chronic_input_{pet_index}",
            )
            submitted_profile = st.form_submit_button("Save profile")

        if submitted_profile:
            pet.weight = weight_input.strip() or None
            pet.diet_good = [line.strip() for line in diet_good_input.splitlines() if line.strip()]
            pet.diet_bad = [line.strip() for line in diet_bad_input.splitlines() if line.strip()]
            pet.chronic_conditions = [
                line.strip() for line in chronic_input.splitlines() if line.strip()
            ]
            st.success("Profile updated.")
            st.rerun()


def render_weekly_timeline(pet_pairs) -> None:
    """Render a Mon-Sun timeline of every patient's tasks for the current week
    as custom HTML/CSS — Streamlit has no built-in Gantt/calendar widget."""
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    week_days = [(monday + timedelta(days=offset), label) for offset, label in enumerate(
        ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    )]
    pet_color = {
        id(pet): PET_TIMELINE_COLORS[index % len(PET_TIMELINE_COLORS)]
        for index, (owner, pet) in enumerate(pet_pairs)
    }

    header_ticks = "".join(
        f'<div style="position:absolute; left:{(hour * 60 - WINDOW_START_MIN) / WINDOW_SPAN_MIN * 100}%; '
        f'font-size:0.7rem; color:#888;">{hour:02d}:00</div>'
        for hour in range(6, 23, 2)
    )

    rows_html = ""
    for day_date, day_label in week_days:
        pills_html = ""
        outside_count = 0
        for owner, pet in pet_pairs:
            for task in pet.tasks:
                if task.due_date != day_date:
                    continue
                hour, minute = map(int, task.time.split(":"))
                start_min = hour * 60 + minute
                end_min = start_min + task.duration_minutes
                clamped_start = max(WINDOW_START_MIN, min(start_min, WINDOW_END_MIN))
                clamped_end = max(WINDOW_START_MIN, min(end_min, WINDOW_END_MIN))
                if clamped_start >= WINDOW_END_MIN or clamped_end <= WINDOW_START_MIN:
                    outside_count += 1
                    continue
                left_pct = (clamped_start - WINDOW_START_MIN) / WINDOW_SPAN_MIN * 100
                width_pct = max((clamped_end - clamped_start) / WINDOW_SPAN_MIN * 100, 2.0)
                opacity = "0.5" if task.completed else "1"
                label = html_escaping.escape(f"{pet.name}: {task.title}")
                tooltip = html_escaping.escape(
                    f"{pet.name} ({owner.name}) — {task.title} at {format_time_12h(task.time)}"
                )
                pills_html += (
                    f'<div class="pp-task-pill" title="{tooltip}" '
                    f'style="left:{left_pct}%; width:{width_pct}%; '
                    f'background:{pet_color[id(pet)]}; opacity:{opacity};">{label}</div>'
                )
        outside_note = (
            f'<span style="font-size:0.7rem; color:#888; margin-left:8px;">+{outside_count} outside window</span>'
            if outside_count
            else ""
        )
        rows_html += (
            '<div style="display:flex; align-items:center; margin-bottom:6px;">'
            f'<div style="width:48px; flex-shrink:0; font-size:0.8rem; color:#aaa;">{day_label}</div>'
            f'<div class="pp-day-row">{pills_html}</div>'
            f"{outside_note}"
            "</div>"
        )

    timeline_html = f"""
    <style>
    .pp-day-row {{ position: relative; height: 40px; flex-grow: 1;
                   background: rgba(255,255,255,0.05); border-radius: 6px; }}
    .pp-task-pill {{ position: absolute; top: 3px; height: 34px; border-radius: 17px;
                      color: white; font-size: 0.72rem; padding: 0 8px; display: flex;
                      align-items: center; overflow: hidden; white-space: nowrap; }}
    </style>
    <div style="display:flex; margin-bottom:6px; margin-left:48px; position:relative; height:16px;">
        {header_ticks}
    </div>
    {rows_html}
    """
    st.markdown(timeline_html, unsafe_allow_html=True)


def render_health_rate_donut(percentage: float) -> None:
    """Render a self-contained fixed-color CSS donut showing a completion percentage.

    Fixed colors rather than theme-derived ones: Streamlit 1.58 doesn't expose
    stable CSS variables to raw markdown HTML, so a theme-blending donut isn't
    realistic without JS — this sidesteps light/dark legibility issues instead.
    """
    if percentage >= 80:
        ring_color = "#12B886"
    elif percentage >= 50:
        ring_color = "#F59F00"
    else:
        ring_color = "#E03131"
    angle = percentage / 100 * 360

    donut_html = f"""
    <div style="background:#1F2937; border-radius:16px; padding:20px; text-align:center;">
      <div style="width:130px; height:130px; border-radius:50%; margin:0 auto;
                  display:flex; align-items:center; justify-content:center;
                  background: conic-gradient({ring_color} 0deg {angle}deg,
                                              rgba(255,255,255,0.15) {angle}deg 360deg);">
        <div style="width:100px; height:100px; border-radius:50%; background:#1F2937;
                    display:flex; flex-direction:column; align-items:center; justify-content:center;">
          <span style="font-size:1.5rem; font-weight:700; color:#FFFFFF;">{percentage:.0f}%</span>
        </div>
      </div>
      <div style="color:#FFFFFF; opacity:0.75; font-size:0.8rem; margin-top:8px;">Health Rate</div>
    </div>
    """
    st.markdown(donut_html, unsafe_allow_html=True)


owners = get_owners()
pet_pairs = [(owner, pet) for owner in owners for pet in owner.pets]

st.title("📊 Dashboard")
st.caption("A per-patient clinical overview across every owner, plus this week's schedule at a glance.")

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

    render_edit_profile(selected_pet, selected_index)

    st.divider()
    st.subheader("Weekly Schedule")
    schedule_col, summary_col = st.columns([3, 1])

    with schedule_col:
        render_weekly_timeline(pet_pairs)

    with summary_col:
        with st.container(border=True):
            st.markdown("**Patients**")
            for species, count in Counter(pet.species for _, pet in pet_pairs).items():
                st.write(f"{pet_species_icon(species)} {species.title()}: {count}")

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

            st.markdown("**Health Rate**")
            total_tasks = len(all_task_triples)
            completed_tasks = sum(1 for _, _, task in all_task_triples if task.completed)
            completion_rate = (
                round(completed_tasks / total_tasks * 100, 1) if total_tasks else 0.0
            )
            render_health_rate_donut(completion_rate)

save_owners(owners)
st.caption("Data is auto-saved to `data.json` after every change, so it persists between app runs.")
