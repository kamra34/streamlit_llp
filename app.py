import streamlit as st
import importlib.util
import os
import sys

st.set_page_config(page_title="Simulator Selection", layout="wide")

# Mapping of page identifiers to their human-readable names and ordering.
PAGE_MAPPING = {
    #"home": "Home",
    "add_edit": "Add/Edit",
    "grouped_alphabetically": "Grouped Alphabetically",
    "grouped_categorically": "Grouped Categorically",
}

def load_module(page_path, module_name):
    try:
        if module_name in sys.modules:
            del sys.modules[module_name]
        
        spec = importlib.util.spec_from_file_location(module_name, page_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        st.error(f"Failed to load module {page_path}. Error: {str(e)}")
        return None


# Sidebar navigation
st.sidebar.title("Navigation")
selection = st.sidebar.radio("Go to", options=list(PAGE_MAPPING.keys()), format_func=lambda x: PAGE_MAPPING[x])

# Dynamic page loading
# Get the directory of the current script
current_script_dir = os.path.dirname(__file__)
page_path = os.path.join(current_script_dir, f"sources/{selection}.py")

# Clear any page-specific session state when navigating between pages
if "last_page" not in st.session_state:
    st.session_state["last_page"] = selection
elif st.session_state["last_page"] != selection:
    for key in list(st.session_state.keys()):
        if key != "last_page":
            del st.session_state[key]
    st.session_state["last_page"] = selection

# Load the selected module dynamically
if os.path.isfile(page_path):
    module_name = f"sources.{selection}"  # Create a unique module name for each page
    load_module(page_path, module_name)
else:
    st.error(f"Page not found: {selection}")
