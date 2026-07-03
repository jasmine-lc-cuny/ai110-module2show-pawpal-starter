import streamlit as st

from app_common import A_LA_BARK_MENU, render_category_page

# The "special_services" category covers the feeding tasks (Breakfast/Lunch/
# Dinner) plus anything task_type_icon() can't categorize — presented as
# "Dog Cafes". Singular display_name keeps the woven-in phrases natural
# ("Schedule a Dog Cafe Task", "Dog Cafe Schedule"). The RSVP form's
# Menu -> Item picker and its "Dog Cafe RSVP" button live inside
# render_category_page's special_services branch.
render_category_page("special_services", "Dog Cafe", "🍖", page_title="🍖 Dog Cafes")

st.divider()
st.subheader("🍽️ A La Bark Menu")

menu_tabs = st.tabs([section_name for section_name, _, _ in A_LA_BARK_MENU])
for menu_tab, (section_name, tagline, items) in zip(menu_tabs, A_LA_BARK_MENU):
    with menu_tab:
        st.caption(tagline)
        for item_name, price, description in items:
            st.markdown(f"**{item_name}** — {price}")
            st.caption(description)

st.markdown("*Bone Apetit!* 🐾")
