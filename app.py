"""PawPal+ multi-page Streamlit app entry point.

This file only sets up navigation. Each page's actual content lives in its
own file (in pages/), and every page shares state through app_common.py —
Streamlit keeps st.session_state alive across page switches within a
session, so the same Owner object is used no matter which page is active.
"""

import streamlit as st

from app_common import (
    get_combined_owner,
    get_scheduler,
    render_live_clock,
    render_page_banner,
)

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

SERVICES = [
    ("🛎️", "Service Dashboard", "pages/book_service_dashboard.py"),
    ("🛁", "Grooming", "pages/grooming.py"),
    ("🏠", "Sitting", "pages/sitting.py"),
    ("🎓", "Training", "pages/training.py"),
    ("🐕", "Walking", "pages/walking.py"),
    ("🍖", "Dog Cafes", "pages/special_services.py"),
]


def home_page():
    """Landing page: a service picker plus a quick glance at today's status."""
    owner = get_combined_owner()
    scheduler = get_scheduler()

    st.title("🐾 PawPal+")
    st.caption("Welcome back! What would you like to do today?")
    render_live_clock("Home dashboard")
    render_page_banner("home")

    st.subheader("🛎️ Book a Service")
    cols = st.columns(3)
    for i, (icon, label, path) in enumerate(SERVICES):
        with cols[i % 3]:
            with st.container(border=True):
                st.markdown(
                    f"<div style='text-align:center; font-size:2.5rem;'>{icon}</div>",
                    unsafe_allow_html=True,
                )
                st.page_link(path, label=label, use_container_width=True)

    st.divider()
    st.page_link(
        "pages/dashboard.py",
        label="📊 Dashboard - 🐾 Pet Profile",
        icon="➡️",
        use_container_width=True,
    )
    st.page_link(
        "pages/book_service_dashboard.py",
        label="🛎️ Dashboard - Book a Service",
        icon="➡️",
        use_container_width=True,
    )

    st.divider()
    st.subheader("Quick Glance")
    if owner.pets:
        conflicts = scheduler.detect_conflicts(scheduler.filter_tasks(completed=False))
        col1, col2, col3 = st.columns(3)
        col1.metric("Pets", len(owner.pets))
        col2.metric("Open tasks today", len(scheduler.todays_schedule()))
        col3.metric("Conflicts", len(conflicts))
    else:
        st.info("Add your first pet to get started.")
        st.page_link("pages/patients.py", label="Go to Patients", icon="🧾")


pg = st.navigation(
    {
        "": [st.Page(home_page, title="Home", icon="🏠", url_path="home", default=True)],
        "🐾 PawPal Manage": [
            st.Page("pages/dashboard.py", title="Dashboard - Pet Profile", icon="📊"),
            st.Page("pages/todays_schedule.py", title="Today's Schedule", icon="📅"),
            st.Page("pages/calendar.py", title="Calendar", icon="🗓️"),
            st.Page("pages/task.py", title="Task Hub", icon="📝"),
        ],
        "🛎️ Book a Service": [
            st.Page("pages/book_service_dashboard.py", title="Service Dashboard", icon="🛎️"),
            st.Page("pages/grooming.py", title="Grooming", icon="🛁"),
            st.Page("pages/sitting.py", title="Sitting", icon="🏠"),
            st.Page("pages/training.py", title="Training", icon="🎓"),
            st.Page("pages/walking.py", title="Walking", icon="🐕"),
            st.Page("pages/special_services.py", title="Dog Cafes", icon="🍖"),
            st.Page("pages/staff.py", title="Staff", icon="👥"),
        ],
        "🩺 Veterinarian": [
            st.Page("pages/clinic_dashboard.py", title="Clinic Dashboard", icon="🏥"),
            st.Page("pages/appointments.py", title="Appointments", icon="📋"),
            st.Page("pages/doctors.py", title="Doctors", icon="👩‍⚕️"),
            st.Page("pages/services.py", title="Services", icon="💲"),
            st.Page("pages/patients.py", title="Patients", icon="🧾"),
        ],
    }
)
pg.run()
