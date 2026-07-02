import streamlit as st

from pawpal_system import Service
from app_common import COMMON_SERVICES, get_clinic, save_clinic

clinic = get_clinic()
common_service_names = [name for name, _ in COMMON_SERVICES]
common_service_costs = dict(COMMON_SERVICES)

st.title("💲 Services")
st.caption("Maintain the price list of services the clinic can bill.")

# Outside the form so picking "Other (custom)" immediately reveals the
# custom-name field below, and so the Cost field can pre-fill with that
# service's typical price — widgets inside st.form don't trigger a rerun
# until the whole form is submitted.
service_choice = st.selectbox("Service", common_service_names + ["Other (custom)"])
custom_service_name = (
    st.text_input("Custom service name") if service_choice == "Other (custom)" else None
)
default_cost = common_service_costs.get(service_choice, 0.0)

with st.form("add_service_form", clear_on_submit=True):
    service_cost = st.number_input("Cost ($)", min_value=0.0, step=1.0, value=default_cost)
    submitted_service = st.form_submit_button("Add Service")

if submitted_service:
    service_name = (
        (custom_service_name or "").strip()
        if service_choice == "Other (custom)"
        else service_choice
    )
    if service_name:
        clinic.services.append(Service(service_name, float(service_cost)))
        save_clinic(clinic)
        st.success(f"Added {service_name}.")
        st.rerun()

if clinic.services:
    st.table(
        [
            {"Service Name": service.name, "Cost ($)": f"${service.cost:.2f}"}
            for service in clinic.services
        ]
    )

    delete_service_index = st.selectbox(
        "Delete a service",
        range(len(clinic.services)),
        format_func=lambda i: clinic.services[i].name,
        key="delete_service_select",
    )
    if st.button("Delete service", key="delete_service_button"):
        removed = clinic.services.pop(delete_service_index)
        save_clinic(clinic)
        st.success(f"Deleted {removed.name}.")
        st.rerun()
else:
    st.info("No services yet.")

# No render-time save: mutations save inline. A render-time save would
# let a stale browser session silently overwrite the data file just by
# sitting open.
st.caption("Data is auto-saved to `clinic.json` after every change, so it persists between app runs.")
