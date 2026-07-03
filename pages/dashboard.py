from collections import Counter, defaultdict
from datetime import date

import pandas as pd
import streamlit as st

from pawpal_system import format_time_12h, pet_species_icon, task_type_icon
from app_common import get_owners

VET_ICONS = {"🏥", "💊"}


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
        if hasattr(pet, 'diet_good') and pet.diet_good:
            for item in pet.diet_good:
                st.markdown(f"- {item}")
        else:
            st.caption("Not set yet.")
        st.markdown("❌ **The diet should not contain:**")
        if hasattr(pet, 'diet_bad') and pet.diet_bad:
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
all_patients = [(owner, pet) for owner in owners for pet in owner.pets]

st.title("📊 Dashboard")
st.caption("Search for a patient to view their complete clinical overview.")

if not all_patients:
    st.info("Add a pet to see their dashboard here.")
    st.page_link("pages/patients.py", label="Go to Patients", icon="🧾")
else:
    PET_CATEGORIES = {
        "🐶 General Companion": ["dog", "cat"],
        "🐹 Exotic Small Pet": ["rabbit", "bunny", "hamster", "gerbil", "mouse", "mice", "rat", "chinchilla", "guinea pig", "ferret", "hedgehog", "sugar glider", "squirrel"],
        "🦜 Exotic Avian": ["budgie", "canary", "finch", "parrot", "cockatiel", "conure", "chicken", "duck", "goose", "pigeon", "owl", "falcon", "snowy owl"],
        "🦎 Reptiles & Amphibians": ["bearded dragon", "leopard gecko", "crested gecko", "chameleon", "iguana", "skink", "turtle", "tortoise", "corn snake", "ball python", "king snake", "frog", "toad", "newt", "salamander"],
        "🐠 Fish & Invertebrates": ["betta", "guppy", "platy", "swordtail", "molly", "tetra", "goldfish", "danio", "minnow", "cichlid", "pleco", "clownfish", "damselfish", "goby", "blenny"]
    }

    # ==========================================
    # 🔍 THE SEARCH & FILTER ENGINE
    # ==========================================
    st.markdown("### 🔍 Find a Patient")
    search_col, filter_col = st.columns([2, 1])
    
    with search_col:
        search_query = st.text_input("Search by pet or owner name...", placeholder="e.g. Snoopy or Michael", label_visibility="collapsed")
    with filter_col:
        selected_group = st.selectbox(
            "Filter by Species Group",
            options=["All Patients"] + list(PET_CATEGORIES.keys()),
            label_visibility="collapsed"
        )

    # --- DYNAMIC SPECIES PILLS ---
    if selected_group == "All Patients":
        allowed_species = None
        selected_species_label = "All"
    else:
        raw_species_list = PET_CATEGORIES[selected_group]
        species_options = ["All"] + [f"{pet_species_icon(s)} {s.capitalize()}" for s in raw_species_list]
        
        # This will render a gorgeous pill selector directly under the search bar
        selected_species_label = st.pills(
            "Filter by specific species",
            options=species_options,
            default="All",
            key="dashboard_species_pills",
            label_visibility="collapsed"
        )

        if not selected_species_label or selected_species_label == "All":
            allowed_species = raw_species_list
        else:
            # Extract pure string (e.g. pulling "dog" from "🐕 Dog")
            target = selected_species_label.split(" ", 1)[-1].lower()
            allowed_species = [target]

    # Apply the filters
    query_lower = search_query.strip().lower()

    filtered_patients = []
    for owner, pet in all_patients:
        matches_search = not query_lower or query_lower in pet.name.lower() or query_lower in owner.name.lower()
        
        if selected_group == "All Patients":
            matches_species = True
        elif "General Companion" in selected_group and (not selected_species_label or selected_species_label == "All"):
            all_known_species = [s for g in PET_CATEGORIES.values() for s in g]
            matches_species = pet.species.lower() in allowed_species or pet.species.lower() not in all_known_species
        else:
            matches_species = pet.species.lower() in allowed_species
            
        if matches_search and matches_species:
            filtered_patients.append((owner, pet))

    st.divider()

    # ==========================================
    # 🩺 DYNAMIC DASHBOARD VIEWER
    # ==========================================
    if not filtered_patients:
        st.warning("No patients match your search criteria.")
    else:
        name_counts = Counter(pet.name for _, pet in filtered_patients)

        def pill_label(index: int) -> str:
            owner, pet = filtered_patients[index]
            label = f"{pet_species_icon(pet.species)} {pet.name}"
            if name_counts[pet.name] > 1:
                label += f" · {owner.name}"
            return label

        # The clean, scalable Drop-down menu
        selected_idx = st.selectbox(
            "Select a matching patient:",
            options=range(len(filtered_patients)),
            format_func=pill_label,
            key="dash_dynamic_select"
        )

        # Safety fallback in case the search changes and resets the index
        if selected_idx is None or selected_idx >= len(filtered_patients):
            selected_idx = 0

        selected_owner, selected_pet = filtered_patients[selected_idx]

        st.markdown(f"### {pet_species_icon(selected_pet.species)} {selected_pet.name}'s Chart")
        
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
                for owner, pet in filtered_patients
                for task in pet.tasks
            ]
            open_today = [
                triple for triple in all_task_triples
                if triple[2].due_date == today and not triple[2].completed
            ]
            st.markdown("**Today's Active Appointments (For Searched Patients)**")
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