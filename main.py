# import streamlit as st
# import os
# import sys

# # Add the current directory to the path so Python can find your modules
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# # Import the page modules
# from pages import about, analisis_teks, visualisasi

# # Configure page
# st.set_page_config(
#     page_title="Analisis Topik Dashboard",
#     page_icon="📊",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # Create a sidebar for navigation
# st.sidebar.title("Navigasi")
# page = st.sidebar.radio("Pilih Halaman:", ["About", "Analisis Teks", "Visualisasi"])

# # Display the selected page
# if page == "About":
#     about.show_about()
# elif page == "Analisis Teks":
#     analisis_teks.show()
# elif page == "Visualisasi":
#     visualisasi.show()