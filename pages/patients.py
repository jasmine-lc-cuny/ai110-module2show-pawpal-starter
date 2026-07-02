import streamlit as st

from pawpal_system import Owner, Pet, pet_species_icon
from app_common import NEW_OWNER_CHOICE, get_owners, save_owners

SPECIES_OPTIONS = ["dog", "cat", "bunny", "other"]
SEX_OPTIONS = ["Female", "Male"]
SPAYED_NEUTERED_OPTIONS = ["Unknown", "Yes", "No"]
STATUS_OPTIONS = ["Alive", "Deceased"]

owners = get_owners()

st.title("🧾 Patients")
st.caption("Register, edit, and search patients (pets and their owners).")
st.page_link("pages/pets_and_schedule.py", label="View the Pet Profile directory", icon="🐾")

st.subheader("New Patient Registration")

# Outside the form so choosing "+ Add new owner" immediately reveals the
# "New owner name" field below — same reveal trick used for "Other (custom)"
# task titles elsewhere in the app, since widgets inside st.form don't
# trigger a rerun until the whole form is submitted.
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

with st.form("register_patient_form", clear_on_submit=True):
    st.markdown("**Basic Info**")
    basic_cols = st.columns(4)
    with basic_cols[0]:
        pet_name = st.text_input("Name*")
    with basic_cols[1]:
        pet_species = st.selectbox("Species*", SPECIES_OPTIONS)
    with basic_cols[2]:
        pet_breed = st.text_input("Breed")
    with basic_cols[3]:
        pet_age = st.number_input("Age", min_value=0, max_value=40, value=1)
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
                species=pet_species,
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
            )
        )
        save_owners(owners)
        st.success(f"Registered {pet_name.strip()} under {target_owner.name}.")
        st.rerun()

st.divider()
st.subheader("Edit a Patient")

all_patients = [(owner, pet) for owner in owners for pet in owner.pets]

if not all_patients:
    st.info("No patients yet.")
else:
    # Index-based, then re-fetch owner.pets[i] fresh — st.selectbox() isn't
    # guaranteed to hand back the same live object across reruns, so a copy
    # would silently discard edits instead of updating the real Pet.
    edit_index = st.selectbox(
        "Patient to edit",
        range(len(all_patients)),
        format_func=lambda i: f"{pet_species_icon(all_patients[i][1].species)} {all_patients[i][1].name} — owned by {all_patients[i][0].name}",
        key="edit_patient_select",
    )
    edit_owner, edit_pet = all_patients[edit_index]

    with st.form("edit_patient_form"):
        st.markdown("**Basic Info**")
        edit_basic_cols = st.columns(4)
        with edit_basic_cols[0]:
            edited_name = st.text_input("Name*", value=edit_pet.name, key="edit_pet_name")
        with edit_basic_cols[1]:
            edited_species = st.selectbox(
                "Species*",
                SPECIES_OPTIONS,
                index=SPECIES_OPTIONS.index(edit_pet.species)
                if edit_pet.species in SPECIES_OPTIONS
                else SPECIES_OPTIONS.index("other"),
                key="edit_pet_species",
            )
        with edit_basic_cols[2]:
            edited_breed = st.text_input("Breed", value=edit_pet.breed or "", key="edit_pet_breed")
        with edit_basic_cols[3]:
            edited_age = st.number_input(
                "Age", min_value=0, max_value=40, value=edit_pet.age or 0, key="edit_pet_age"
            )
        edited_sex = st.selectbox(
            "Sex*",
            SEX_OPTIONS,
            index=SEX_OPTIONS.index(edit_pet.sex) if edit_pet.sex in SEX_OPTIONS else 0,
            key="edit_pet_sex",
        )

        st.markdown("**Physical Traits**")
        edit_physical_cols = st.columns(3)
        with edit_physical_cols[0]:
            edited_weight = st.text_input(
                "Weight", value=edit_pet.weight or "", key="edit_pet_weight"
            )
        with edit_physical_cols[1]:
            edited_height = st.text_input(
                "Height", value=edit_pet.height or "", key="edit_pet_height"
            )
        with edit_physical_cols[2]:
            edited_color_markings = st.text_input(
                "Color/Markings", value=edit_pet.color_markings or "", key="edit_pet_color_markings"
            )

        st.markdown("**Health & Safety**")
        edit_health_cols = st.columns(2)
        with edit_health_cols[0]:
            edited_microchip = st.text_input(
                "Microchip #", value=edit_pet.microchip_number or "", key="edit_pet_microchip"
            )
            edited_spayed_neutered = st.selectbox(
                "Spayed/Neutered",
                SPAYED_NEUTERED_OPTIONS,
                index=SPAYED_NEUTERED_OPTIONS.index(edit_pet.spayed_neutered)
                if edit_pet.spayed_neutered in SPAYED_NEUTERED_OPTIONS
                else 0,
                key="edit_pet_spayed_neutered",
            )
        with edit_health_cols[1]:
            edited_allergies = st.text_input(
                "Allergies", value=edit_pet.allergies or "", key="edit_pet_allergies"
            )
            edited_blood_type = st.text_input(
                "Blood group", value=edit_pet.blood_type or "", key="edit_pet_blood_type"
            )
        edited_behavioral_notes = st.text_area(
            "Behavioral Notes", value=edit_pet.behavioral_notes or "", key="edit_pet_behavioral_notes"
        )
        edited_medical_history = st.text_area(
            "Medical history (one condition per line)",
            value="\n".join(edit_pet.chronic_conditions),
            key="edit_pet_medical_history",
        )

        st.markdown("**Diet**")
        edit_diet_cols = st.columns(2)
        with edit_diet_cols[0]:
            edited_diet_good = st.text_area(
                "Diet should contain (one per line)",
                value="\n".join(edit_pet.diet_good),
                key="edit_pet_diet_good",
            )
        with edit_diet_cols[1]:
            edited_diet_bad = st.text_area(
                "Diet should not contain (one per line)",
                value="\n".join(edit_pet.diet_bad),
                key="edit_pet_diet_bad",
            )

        edited_status = st.selectbox(
            "Status",
            STATUS_OPTIONS,
            index=STATUS_OPTIONS.index(edit_pet.status) if edit_pet.status in STATUS_OPTIONS else 0,
            key="edit_pet_status",
        )

        submitted_edit = st.form_submit_button("Save changes")

    if submitted_edit and edited_name.strip():
        edit_pet.name = edited_name.strip()
        edit_pet.species = edited_species
        edit_pet.breed = edited_breed.strip() or None
        edit_pet.age = int(edited_age)
        edit_pet.sex = edited_sex
        edit_pet.weight = edited_weight.strip() or None
        edit_pet.height = edited_height.strip() or None
        edit_pet.color_markings = edited_color_markings.strip() or None
        edit_pet.microchip_number = edited_microchip.strip() or None
        edit_pet.spayed_neutered = (
            edited_spayed_neutered if edited_spayed_neutered != "Unknown" else None
        )
        edit_pet.allergies = edited_allergies.strip() or None
        edit_pet.blood_type = edited_blood_type.strip() or None
        edit_pet.behavioral_notes = edited_behavioral_notes.strip() or None
        edit_pet.chronic_conditions = [
            line.strip() for line in edited_medical_history.splitlines() if line.strip()
        ]
        edit_pet.diet_good = [
            line.strip() for line in edited_diet_good.splitlines() if line.strip()
        ]
        edit_pet.diet_bad = [
            line.strip() for line in edited_diet_bad.splitlines() if line.strip()
        ]
        edit_pet.status = edited_status
        save_owners(owners)
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

st.divider()
st.subheader("Patients List")
search_query = st.text_input("Search by pet or owner name")

visible_patients = all_patients
if search_query.strip():
    query_lower = search_query.strip().lower()
    visible_patients = [
        (owner, pet)
        for owner, pet in visible_patients
        if query_lower in pet.name.lower() or query_lower in owner.name.lower()
    ]

if visible_patients:
    for index, (owner, pet) in enumerate(visible_patients):
        status_flag = "" if pet.status == "Alive" else " 🪦"
        with st.expander(f"{pet_species_icon(pet.species)} {pet.name}{status_flag} — owned by {owner.name}"):
            info_cols = st.columns(4)
            info_cols[0].metric("Species", pet.species)
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
            st.write(f"**Owner phone:** {owner.phone or '—'}")
            st.write(f"**Owner email:** {owner.email or '—'}")
            st.write(f"**Owner address:** {owner.address or '—'}")
            if pet.chronic_conditions:
                st.write("**Medical history:**")
                for entry in pet.chronic_conditions:
                    st.markdown(f"- {entry}")
            else:
                st.write("**Medical history:** —")
else:
    st.info("No patients found.")

# No render-time save: mutations save inline. A render-time save would
# let a stale browser session silently overwrite the data file just by
# sitting open.
st.caption("Data is auto-saved to `data.json` after every change, so it persists between app runs.")
