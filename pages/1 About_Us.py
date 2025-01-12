import streamlit as st

# Page Title
st.title("About Us")

# Create two columns for team member introductions
col1, col2 = st.columns(2)

# Team Member 1
with col1:
    st.header("Naveen Elliott")
    st.write("""   
    **Bio:** John specializes in developing machine learning models and AI-driven solutions. With a passion for innovation, he has contributed to several cutting-edge projects.
    """)
    st.markdown("[LinkedIn Profile](https://www.linkedin.com/in/naveen-elliott-86ba7620a/)", unsafe_allow_html=True)

# Team Member 2
with col2:
    st.header("Atif Siddiqui")
    st.write("""
    **Bio:** Jane focuses on building scalable applications and improving user experience. Her expertise lies in full-stack development and software optimization.
    """)
    st.markdown("[LinkedIn Profile](https://www.linkedin.com/in/atifsiddiqui10/)", unsafe_allow_html=True)

# Divider Line
st.markdown("---")

# Version Docs Section
st.header("Version Documentation")
st.write("""
Here are the release notes for the current and previous versions of our project:
- **Version 1.0.0**: Initial release with core functionalities.
""")