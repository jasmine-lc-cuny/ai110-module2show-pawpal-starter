import calendar
import html as html_escaping
from collections import defaultdict
from datetime import date

import streamlit as st

from pawpal_system import format_time_12h, task_type_icon
from app_common import (
    PET_TIMELINE_COLORS,
    get_combined_owner,
    get_scheduler,
    render_live_clock,
    task_rows,
)

MAX_BADGES_PER_DAY = 3


def render_month_grid(owner, target_year: int, target_month: int) -> None:
    """Render a Mon-Sun month grid with a colored badge per task, as custom
    HTML/CSS — Streamlit has no built-in calendar widget."""
    weeks = calendar.Calendar(firstweekday=0).monthdatescalendar(target_year, target_month)
    today = date.today()

    tasks_by_date = defaultdict(list)
    for pet, task in owner.all_tasks():
        tasks_by_date[task.due_date].append((pet, task))

    pet_color = {
        pet.name: PET_TIMELINE_COLORS[index % len(PET_TIMELINE_COLORS)]
        for index, pet in enumerate(owner.pets)
    }

    header_html = "".join(
        f'<div class="pp-cal-header">{abbr}</div>'
        for abbr in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    )

    weeks_html = ""
    for week in weeks:
        week_html = ""
        for day in week:
            day_tasks = tasks_by_date.get(day, [])
            badges_html = ""
            for pet, task in day_tasks[:MAX_BADGES_PER_DAY]:
                tooltip = html_escaping.escape(
                    f"{pet.name}: {task.title} at {format_time_12h(task.time)}"
                )
                badge_label = html_escaping.escape(pet.name)
                badges_html += (
                    f'<div class="pp-cal-badge" style="background:{pet_color[pet.name]};" '
                    f'title="{tooltip}">{task_type_icon(task.title)} {badge_label}</div>'
                )
            overflow = len(day_tasks) - MAX_BADGES_PER_DAY
            if overflow > 0:
                badges_html += f'<div class="pp-cal-more">+{overflow} more</div>'

            cell_classes = "pp-cal-cell"
            if day.month != target_month:
                cell_classes += " pp-cal-outside"
            if day == today:
                cell_classes += " pp-cal-today"

            week_html += (
                f'<div class="{cell_classes}"><div class="pp-cal-daynum">{day.day}</div>'
                f"{badges_html}</div>"
            )
        weeks_html += f'<div class="pp-cal-week">{week_html}</div>'

    calendar_html = f"""
    <style>
    .pp-cal-header {{ flex:1; text-align:center; font-size:0.75rem; color:#888; padding:4px 0; }}
    .pp-cal-week {{ display:flex; gap:4px; margin-bottom:4px; }}
    .pp-cal-cell {{ flex:1; min-height:80px; background:rgba(255,255,255,0.05); border-radius:8px;
                    padding:6px; display:flex; flex-direction:column; gap:2px; box-sizing:border-box; }}
    .pp-cal-outside {{ opacity:0.35; }}
    .pp-cal-today {{ border:2px solid #3B5BDB; }}
    .pp-cal-daynum {{ font-size:0.8rem; color:#ccc; font-weight:600; margin-bottom:2px; }}
    .pp-cal-badge {{ border-radius:6px; color:white; font-size:0.65rem; padding:1px 4px;
                      overflow:hidden; white-space:nowrap; text-overflow:ellipsis; }}
    .pp-cal-more {{ font-size:0.65rem; color:#888; }}
    </style>
    <div style="display:flex; gap:4px; margin-bottom:4px;">{header_html}</div>
    {weeks_html}
    """
    st.markdown(calendar_html, unsafe_allow_html=True)


owner = get_combined_owner()
scheduler = get_scheduler()

st.title("🗓️ Calendar")
st.caption("Browse tasks by month, and drill into any day's full schedule.")
render_live_clock("Calendar")

if not owner.pets:
    st.info("Add a pet to see their calendar here.")
    st.page_link("pages/patients.py", label="Go to Patients", icon="🧾")
else:
    if "calendar_month_offset" not in st.session_state:
        st.session_state.calendar_month_offset = 0

    today = date.today()
    month_index = today.month - 1 + st.session_state.calendar_month_offset
    target_year = today.year + month_index // 12
    target_month = month_index % 12 + 1

    nav_prev, nav_label, nav_today, nav_next = st.columns([1, 3, 1, 1])
    with nav_prev:
        if st.button("◀ Previous", key="calendar_prev"):
            st.session_state.calendar_month_offset -= 1
            st.rerun()
    with nav_label:
        st.markdown(f"### {calendar.month_name[target_month]} {target_year}")
    with nav_today:
        if st.button("Today", key="calendar_today"):
            st.session_state.calendar_month_offset = 0
            st.rerun()
    with nav_next:
        if st.button("Next ▶", key="calendar_next"):
            st.session_state.calendar_month_offset += 1
            st.rerun()

    render_month_grid(owner, target_year, target_month)

    st.divider()
    st.subheader("Day Details")

    month_dates = [
        day
        for week in calendar.Calendar(firstweekday=0).monthdatescalendar(target_year, target_month)
        for day in week
        if day.month == target_month
    ]
    default_date = today if today in month_dates else month_dates[0]
    # Index-based, not the date objects themselves — st.selectbox() options
    # that are plain values like dates don't round-trip cleanly through
    # Streamlit's widget state (breaks AppTest's get_widget_states(), and
    # is the same class of gotcha documented elsewhere for Pet/Task objects).
    selected_date_index = st.selectbox(
        "View a day's tasks",
        range(len(month_dates)),
        index=month_dates.index(default_date),
        format_func=lambda i: month_dates[i].strftime("%A, %B %d"),
        key="calendar_day_select",
    )
    selected_date = month_dates[selected_date_index]

    day_tasks = scheduler.sort_by_time(
        [pair for pair in owner.all_tasks() if pair[1].due_date == selected_date]
    )
    if day_tasks:
        st.table(task_rows(day_tasks))
    else:
        st.info("No tasks scheduled for this day.")

    day_conflicts = scheduler.detect_conflicts(day_tasks)
    for warning in day_conflicts:
        st.warning(warning)

# No render-time save: mutations save inline. A render-time save would
# let a stale browser session silently overwrite the data file just by
# sitting open.
st.caption("Data is auto-saved to `data.json` after every change, so it persists between app runs.")
