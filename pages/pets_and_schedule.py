import streamlit as st

from app_common import get_owners

owners = get_owners()

st.title("🐾 Pet Profile")
st.caption("A quick directory of every pet and its owner.")
st.page_link("pages/patients.py", label="Go to Patients to add, edit, or delete a pet", icon="🧾")

rows = [
    {"Pet Name": pet.name, "Owner Name": owner.name}
    for owner in owners
    for pet in owner.pets
]
if rows:
    st.table(rows)
else:
    st.info("No pets registered yet.")
    st.page_link("pages/patients.py", label="Go to Patients", icon="🧾")
