import streamlit as st

from pawpal_system import Owner, Pet, pet_species_icon
from app_common import NEW_OWNER_CHOICE, get_owners, save_owners

# ==========================================
# 🐾 MASTER SPECIES ARCHITECTURE
# ==========================================
PET_CATEGORIES = {
    "🐶 General Companion": ["dog", "cat"],
    "🐹 Exotic Small Pet": ["rabbit", "bunny", "hamster", "gerbil", "mouse", "mice", "rat", "chinchilla", "guinea pig", "ferret", "hedgehog", "sugar glider", "squirrel"],
    "🦜 Exotic Avian": ["budgie", "canary", "finch", "parrot", "cockatiel", "conure", "chicken", "duck", "goose", "pigeon", "owl", "falcon", "snowy owl"],
    "🦎 Reptiles & Amphibians": ["bearded dragon", "leopard gecko", "crested gecko", "chameleon", "iguana", "skink", "turtle", "tortoise", "corn snake", "ball python", "king snake", "frog", "toad", "newt", "salamander"],
    "🐠 Fish & Invertebrates": ["betta", "guppy", "platy", "swordtail", "molly", "tetra", "goldfish", "danio", "minnow", "cichlid", "pleco", "clownfish", "damselfish", "goby", "blenny"]
}

GROUP_OPTIONS = list(PET_CATEGORIES.keys())
SEX_OPTIONS = ["Female", "Male"]
SPAYED_NEUTERED_OPTIONS = ["Unknown", "Yes", "No"]
STATUS_OPTIONS = ["Alive", "Deceased"]

owners = get_owners()

st.title("🧾 Patients")
st.caption("Register, edit, and search patients (pets and their owners).")
st.page_link("pages/pets_and_schedule.py", label="View the Pet Profile directory", icon="🐾")

# ==========================================
# ➕ NEW PATIENT REGISTRATION FORM
# ==========================================
st.subheader("New Patient Registration")

if "show_register_patient" not in st.session_state:
    st.session_state.show_register_patient = False

if not st.session_state.show_register_patient:
    if st.button("➕ Register a new patient", key="register_patient_show"):
        st.session_state.show_register_patient = True
        st.rerun()
else:
    if st.button("🔼 View less", key="register_patient_hide"):
        st.session_state.show_register_patient = False
        st.rerun()

    owner_choice = st.selectbox(
        "Owner",
        list(range(len(owners))) + [NEW_OWNER_CHOICE],
        format_func=lambda option: owners[option].name if isinstance(option, int) else option,
        key="patient_owner_choice",
    )
    new_owner_name = (
        st.text_input("New owner name", key="patient_new_owner_name")
        if owner_choice == NEW_OWNER_CHOICE
        else None
    )

    # --- CASCADING SPECIES LOGIC (REGISTRATION) ---
    selected_reg_group = st.selectbox(
        "Species Group*", 
        GROUP_OPTIONS, 
        key="reg_species_group_select"
    )
    
    reg_allowed_species = sorted(PET_CATEGORIES[selected_reg_group])
    if "other" not in reg_allowed_species:
        reg_allowed_species.append("other")

    with st.form("register_patient_form", clear_on_submit=True):
        st.markdown("**Basic Info**")
        basic_cols = st.columns(3)
        with basic_cols[0]:
            pet_name = st.text_input("Name*")
        with basic_cols[1]:
            pet_species = st.selectbox(
                "Species*", 
                reg_allowed_species, 
                format_func=lambda s: s.capitalize()
            )
        with basic_cols[2]:
            pet_breed = st.text_input("Breed")
            
        basic_cols_2 = st.columns(2)
        with basic_cols_2[0]:
            pet_age = st.number_input("Age", min_value=0, max_value=40, value=1)
        with basic_cols_2[1]:
            pet_sex = st.selectbox("Sex*", SEX_OPTIONS)

        st.markdown("**Physical Traits**")
        physical_cols = st.columns(3)
        with physical_cols[0]:
            pet_weight = st.text_input("Weight")
        with physical_cols[1]:
            pet_height = st.text_input("Height")
        with physical_cols[2]:
            pet_color_markings = st.text_input("Color/Markings")

        st.markdown("**Health & Safety**")
        health_cols = st.columns(2)
        with health_cols[0]:
            pet_microchip = st.text_input("Microchip #")
            pet_spayed_neutered = st.selectbox("Spayed/Neutered", SPAYED_NEUTERED_OPTIONS)
        with health_cols[1]:
            pet_allergies = st.text_input("Allergies")
            pet_blood_type = st.text_input("Blood group")
        pet_behavioral_notes = st.text_area("Behavioral Notes")
        medical_history = st.text_area("Medical history (one condition per line)")

        st.markdown("**Diet**")
        diet_cols = st.columns(2)
        with diet_cols[0]:
            pet_diet_good = st.text_area("Diet should contain (one per line)", key="reg_pet_diet_good")
        with diet_cols[1]:
            pet_diet_bad = st.text_area("Diet should not contain (one per line)", key="reg_pet_diet_bad")

        st.markdown("**Owner/Contact**")
        contact_cols = st.columns(3)
        existing_owner = owners[owner_choice] if isinstance(owner_choice, int) else None
        with contact_cols[0]:
            owner_phone = st.text_input("Phone", value=(existing_owner.phone or "") if existing_owner else "")
        with contact_cols[1]:
            owner_email = st.text_input("Email", value=(existing_owner.email or "") if existing_owner else "")
        with contact_cols[2]:
            owner_address = st.text_input(
                "Address", value=(existing_owner.address or "") if existing_owner else ""
            )

        submitted_patient = st.form_submit_button("Save Patient")

    if submitted_patient:
        owner_name = new_owner_name.strip() if owner_choice == NEW_OWNER_CHOICE else None
        if owner_choice == NEW_OWNER_CHOICE and not owner_name:
            st.error("Enter a name for the new owner.")
        elif not pet_name.strip():
            st.error("Pet name is required.")
        else:
            if owner_choice == NEW_OWNER_CHOICE:
                target_owner = Owner(owner_name)
                owners.append(target_owner)
            else:
                target_owner = owners[owner_choice]
            target_owner.phone = owner_phone.strip() or None
            target_owner.email = owner_email.strip() or None
            target_owner.address = owner_address.strip() or None
            
            target_owner.add_pet(
                Pet(
                    name=pet_name.strip(),
                    species=pet_species.lower(),
                    age=int(pet_age),
                    sex=pet_sex,
                    breed=pet_breed.strip() or None,
                    weight=pet_weight.strip() or None,
                    height=pet_height.strip() or None,
                    color_markings=pet_color_markings.strip() or None,
                    microchip_number=pet_microchip.strip() or None,
                    spayed_neutered=pet_spayed_neutered if pet_spayed_neutered != "Unknown" else None,
                    allergies=pet_allergies.strip() or None,
                    blood_type=pet_blood_type.strip() or None,
                    behavioral_notes=pet_behavioral_notes.strip() or None,
                    chronic_conditions=[
                        line.strip() for line in medical_history.splitlines() if line.strip()
                    ],
                    diet_good=[
                        line.strip() for line in pet_diet_good.splitlines() if line.strip()
                    ],
                    diet_bad=[
                        line.strip() for line in pet_diet_bad.splitlines() if line.strip()
                    ],
                )
            )
            save_owners(owners)
            st.session_state.show_register_patient = False
            st.success(f"Registered {pet_name.strip()} under {target_owner.name}.")
            st.rerun()

# ==========================================
# ✏️ EDIT PATIENT FORM SECTION
# ==========================================
st.divider()
st.subheader("Edit a Patient")

all_patients = [(owner, pet) for owner in owners for pet in owner.pets]

if not all_patients:
    st.info("No patients yet.")
else:
    if "show_edit_patient" not in st.session_state:
        st.session_state.show_edit_patient = False

    if not st.session_state.show_edit_patient:
        if st.button("✏️ View edit form", key="edit_patient_show"):
            st.session_state.show_edit_patient = True
            st.rerun()
    else:
        if st.button("🔼 View less", key="edit_patient_hide"):
            st.session_state.show_edit_patient = False
            st.rerun()

        edit_index = st.selectbox(
            "Patient to edit",
            range(len(all_patients)),
            format_func=lambda i: f"{pet_species_icon(all_patients[i][1].species)} {all_patients[i][1].name} — owned by {all_patients[i][0].name}",
            key="edit_patient_select",
        )
        edit_owner, edit_pet = all_patients[edit_index]

        # --- CASCADING SPECIES LOGIC (EDIT) ---
        current_pet_species = edit_pet.species.lower() if edit_pet.species else "other"
        default_group_index = 0
        for idx, (group_name, species_list) in enumerate(PET_CATEGORIES.items()):
            if current_pet_species in species_list:
                default_group_index = idx
                break

        selected_edit_group = st.selectbox(
            "Species Group*",
            GROUP_OPTIONS,
            index=default_group_index,
            key=f"edit_species_group_{edit_index}"
        )

        edit_allowed_species = sorted(PET_CATEGORIES[selected_edit_group])
        if "other" not in edit_allowed_species:
            edit_allowed_species.append("other")

        with st.form("edit_patient_form"):
            st.markdown("**Basic Info**")
            edit_basic_cols = st.columns(3)
            with edit_basic_cols[0]:
                edited_name = st.text_input("Name*", value=edit_pet.name, key=f"edit_pet_name_{edit_index}")
            with edit_basic_cols[1]:
                try:
                    species_sub_index = edit_allowed_species.index(current_pet_species)
                except ValueError:
                    species_sub_index = edit_allowed_species.index("other")

                edited_species = st.selectbox(
                    "Species*",
                    edit_allowed_species,
                    index=species_sub_index,
                    format_func=lambda s: s.capitalize(),
                    key=f"edit_pet_species_{edit_index}",
                )
            with edit_basic_cols[2]:
                edited_breed = st.text_input("Breed", value=edit_pet.breed or "", key=f"edit_pet_breed_{edit_index}")
            
            edit_basic_cols_2 = st.columns(2)
            with edit_basic_cols_2[0]:
                edited_age = st.number_input(
                    "Age", min_value=0, max_value=40, value=edit_pet.age or 0, key=f"edit_pet_age_{edit_index}"
                )
            with edit_basic_cols_2[1]:
                edited_sex = st.selectbox(
                    "Sex*",
                    SEX_OPTIONS,
                    index=SEX_OPTIONS.index(edit_pet.sex) if edit_pet.sex in SEX_OPTIONS else 0,
                    key=f"edit_pet_sex_{edit_index}",
                )

            st.markdown("**Physical Traits**")
            edit_physical_cols = st.columns(3)
            with edit_physical_cols[0]:
                edited_weight = st.text_input("Weight", value=edit_pet.weight or "", key=f"edit_pet_weight_{edit_index}")
            with edit_physical_cols[1]:
                edited_height = st.text_input("Height", value=edit_pet.height or "", key=f"edit_pet_height_{edit_index}")
            with edit_physical_cols[2]:
                edited_color_markings = st.text_input("Color/Markings", value=edit_pet.color_markings or "", key=f"edit_pet_color_markings_{edit_index}")

            st.markdown("**Health & Safety**")
            edit_health_cols = st.columns(2)
            with edit_health_cols[0]:
                edited_microchip = st.text_input("Microchip #", value=edit_pet.microchip_number or "", key=f"edit_pet_microchip_{edit_index}")
                edited_spayed_neutered = st.selectbox(
                    "Spayed/Neutered",
                    SPAYED_NEUTERED_OPTIONS,
                    index=SPAYED_NEUTERED_OPTIONS.index(edit_pet.spayed_neutered) if edit_pet.spayed_neutered in SPAYED_NEUTERED_OPTIONS else 0,
                    key=f"edit_pet_spayed_neutered_{edit_index}",
                )
            with edit_health_cols[1]:
                edited_allergies = st.text_input("Allergies", value=edit_pet.allergies or "", key=f"edit_pet_allergies_{edit_index}")
                edited_blood_type = st.text_input("Blood group", value=edit_pet.blood_type or "", key=f"edit_pet_blood_type_{edit_index}")
            
            edited_behavioral_notes = st.text_area("Behavioral Notes", value=edit_pet.behavioral_notes or "", key=f"edit_pet_behavioral_notes_{edit_index}")
            edited_medical_history = st.text_area(
                "Medical history (one condition per line)",
                value="\n".join(edit_pet.chronic_conditions),
                key=f"edit_pet_medical_history_{edit_index}",
            )

            st.markdown("**Diet**")
            edit_diet_cols = st.columns(2)
            with edit_diet_cols[0]:
                edited_diet_good = st.text_area(
                    "Diet should contain (one per line)",
                    value="\n".join(edit_pet.diet_good) if hasattr(edit_pet, 'diet_good') else "",
                    key=f"edit_pet_diet_good_{edit_index}",
                )
            with edit_diet_cols[1]:
                edited_diet_bad = st.text_area(
                    "Diet should not contain (one per line)",
                    value="\n".join(edit_pet.diet_bad) if hasattr(edit_pet, 'diet_bad') else "",
                    key=f"edit_pet_diet_bad_{edit_index}",
                )

            edited_status = st.selectbox(
                "Status",
                STATUS_OPTIONS,
                index=STATUS_OPTIONS.index(edit_pet.status) if edit_pet.status in STATUS_OPTIONS else 0,
                key=f"edit_pet_status_{edit_index}",
            )

            submitted_edit = st.form_submit_button("Save changes")

        if submitted_edit and edited_name.strip():
            edit_pet.name = edited_name.strip()
            edit_pet.species = edited_species.lower()
            edit_pet.breed = edited_breed.strip() or None
            edit_pet.age = int(edited_age)
            edit_pet.sex = edited_sex
            edit_pet.weight = edited_weight.strip() or None
            edit_pet.height = edited_height.strip() or None
            edit_pet.color_markings = edited_color_markings.strip() or None
            edit_pet.microchip_number = edited_microchip.strip() or None
            edit_pet.spayed_neutered = edited_spayed_neutered if edited_spayed_neutered != "Unknown" else None
            edit_pet.allergies = edited_allergies.strip() or None
            edit_pet.blood_type = edited_blood_type.strip() or None
            edit_pet.behavioral_notes = edited_behavioral_notes.strip() or None
            edit_pet.chronic_conditions = [line.strip() for line in edited_medical_history.splitlines() if line.strip()]
            edit_pet.diet_good = [line.strip() for line in edited_diet_good.splitlines() if line.strip()]
            edit_pet.diet_bad = [line.strip() for line in edited_diet_bad.splitlines() if line.strip()]
            edit_pet.status = edited_status
            
            save_owners(owners)
            st.session_state.show_edit_patient = False
            st.success(f"Updated {edit_pet.name}.")
            st.rerun()

    st.markdown("**Delete a Patient**")
    delete_index = st.selectbox(
        "Patient to delete",
        range(len(all_patients)),
        format_func=lambda i: f"{pet_species_icon(all_patients[i][1].species)} {all_patients[i][1].name} — owned by {all_patients[i][0].name}",
        key="delete_patient_select",
    )
    if st.button("Delete patient", key="delete_patient_button"):
        delete_owner, delete_pet = all_patients[delete_index]
        delete_owner.remove_pet(delete_pet)
        save_owners(owners)
        st.success(f"Deleted {delete_pet.name}.")
        st.rerun()

# ==========================================
# 📊 CATEGORIZED PATIENTS DIRECTORY (TABS)
# ==========================================
st.divider()
st.subheader("Patients Directory")

selected_group = st.radio(
    "Filter by Species Group",
    options=list(PET_CATEGORIES.keys()),
    horizontal=True,
    key="patient_directory_group"
)

search_query = st.text_input("Search by pet or owner name")

def render_patient_cards(patient_list):
    if not patient_list:
        st.info("No patients matching this sub-category.")
        return
        
    for owner, pet in patient_list:
        status_flag = "" if pet.status == "Alive" else " 🪦"
        with st.expander(f"{pet_species_icon(pet.species)} {pet.name}{status_flag} — owned by {owner.name}"):
            info_cols = st.columns(4)
            info_cols[0].metric("Species", pet.species.capitalize())
            info_cols[1].metric("Sex", pet.sex or "—")
            info_cols[2].metric("Age", pet.age if pet.age is not None else "—")
            info_cols[3].metric("Status", pet.status)
            
            st.write(f"**Breed:** {pet.breed or '—'}")
            st.write(f"**Weight:** {pet.weight or '—'}  |  **Height:** {pet.height or '—'}")
            st.write(f"**Color/Markings:** {pet.color_markings or '—'}")
            st.write(f"**Microchip #:** {pet.microchip_number or '—'}")
            st.write(f"**Spayed/Neutered:** {pet.spayed_neutered or 'Unknown'}")
            st.write(f"**Allergies:** {pet.allergies or '—'}")
            st.write(f"**Blood group:** {pet.blood_type or '—'}")
            st.write(f"**Behavioral Notes:** {pet.behavioral_notes or '—'}")
            
            if hasattr(pet, 'diet_good') and pet.diet_good:
                st.write("**Allowed Foods:**")
                for item in pet.diet_good:
                    st.markdown(f"- {item}")
            if hasattr(pet, 'diet_bad') and pet.diet_bad:
                st.write("**Prohibited Foods:**")
                for item in pet.diet_bad:
                    st.markdown(f"- :red[{item}]")
                    
            st.write(f"**Owner phone:** {owner.phone or '—'}")
            st.write(f"**Owner email:** {owner.email or '—'}")
            st.write(f"**Owner address:** {owner.address or '—'}")
            if pet.chronic_conditions:
                st.write("**Medical history:**")
                for entry in pet.chronic_conditions:
                    st.markdown(f"- {entry}")
            else:
                st.write("**Medical history:** —")

allowed_species = PET_CATEGORIES[selected_group]
query_lower = search_query.strip().lower()

filtered_group_patients = []
for owner, pet in all_patients:
    matches_search = not query_lower or query_lower in pet.name.lower() or query_lower in owner.name.lower()
    
    if selected_group == "🐶 General Companion":
        all_known_species = [s for g in PET_CATEGORIES.values() for s in g]
        matches_species = pet.species.lower() in allowed_species or pet.species.lower() not in all_known_species
    else:
        matches_species = pet.species.lower() in allowed_species
        
    if matches_search and matches_species:
        filtered_group_patients.append((owner, pet))

if not filtered_group_patients:
    st.info("No patients currently registered under this category.")
else:
    if "General Companion" in selected_group:
        tab_titles = ["🐕 Dogs", "🐈 Cats", "🐾 Others"]
        tabs = st.tabs(tab_titles)
        with tabs[0]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() == "dog"])
        with tabs[1]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() == "cat"])
        with tabs[2]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() not in ["dog", "cat"]])

    elif "Exotic Small Pet" in selected_group:
        tab_titles = ["🐿️ Rodents", "🦔 Special Mammals"]
        tabs = st.tabs(tab_titles)
        rodents = ["rabbit", "bunny", "hamster", "gerbil", "mouse", "mice", "rat", "chinchilla", "guinea pig"]
        with tabs[0]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() in rodents])
        with tabs[1]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() not in rodents])

    elif "Exotic Avian" in selected_group:
        tab_titles = ["🐤 Small Birds", "🦅 Large Birds & Raptors", "🐓 Poultry"]
        tabs = st.tabs(tab_titles)
        small_birds = ["budgie", "canary", "finch", "cockatiel"]
        poultry = ["chicken", "duck", "goose", "pigeon"]
        with tabs[0]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() in small_birds])
        with tabs[1]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() not in small_birds and p.species.lower() not in poultry])
        with tabs[2]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() in poultry])

    elif "Reptiles & Amphibians" in selected_group:
        tab_titles = ["🦎 Lizards & Snakes", "🐢 Chelonians", "🐸 Amphibians"]
        tabs = st.tabs(tab_titles)
        snakes_lizards = ["bearded dragon", "leopard gecko", "crested gecko", "chameleon", "iguana", "skink", "corn snake", "ball python", "king snake"]
        chelonians = ["turtle", "tortoise"]
        with tabs[0]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() in snakes_lizards])
        with tabs[1]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() in chelonians])
        with tabs[2]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() not in snakes_lizards and p.species.lower() not in chelonians])

    elif "Fish & Invertebrates" in selected_group:
        tab_titles = ["💧 Freshwater", "🌊 Saltwater"]
        tabs = st.tabs(tab_titles)
        saltwater = ["clownfish", "damselfish", "goby", "blenny"]
        with tabs[0]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() not in saltwater])
        with tabs[1]:
            render_patient_cards([(o, p) for o, p in filtered_group_patients if p.species.lower() in saltwater])

st.caption("Data is auto-saved to `data.json` after every change, so it persists between app runs.")