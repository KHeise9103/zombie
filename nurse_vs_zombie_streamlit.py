st.markdown("## 🩺 Nurse vs 🧟 Zombie")
st.markdown("### Choose difficulty")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Easy"):
        st.session_state.difficulty = "Easy"
        st.session_state.difficulty_set = True
        st.experimental_rerun()

with col2:
    if st.button("Medium"):
        st.session_state.difficulty = "Medium"
        st.session_state.difficulty_set = True
        st.experimental_rerun()

with col3:
    if st.button("Hard"):
        st.session_state.difficulty = "Hard"
        st.session_state.difficulty_set = True
        st.experimental_rerun()
