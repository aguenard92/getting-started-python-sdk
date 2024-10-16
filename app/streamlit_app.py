import streamlit as st

# First horizontal layout
left_column_1, right_column_1 = st.columns([1, 3])

with left_column_1:
    st.write("Text above Button 1")  # Add text above the button
    if st.button('Button 1'):
        st.write('Button 1 clicked!')

with right_column_1:
    st.title("Big Title on the Right - First Layout")

# Add a divider for visual separation
st.markdown("---")  # Creates a horizontal line

# Second horizontal layout
left_column_2, right_column_2 = st.columns([1, 3])

with left_column_2:
    st.write("Text above Button 2")  # Add text above the button
    if st.button('Button 2'):
        st.write('Button 2 clicked!')

with right_column_2:
    st.title("Big Title on the Right - Second Layout")
