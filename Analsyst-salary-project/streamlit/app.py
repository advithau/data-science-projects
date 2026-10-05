import streamlit as st

# Cheat sheet: https://docs.streamlit.io/develop/quick-reference/cheat-sheet
# Streamlit emojis: https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app
# Emoji finder: https://emojifinder.com/

q1 = st.Page('pages/q1.py', title='How do cost-of-living adjusted median salaries for Data Analysts vary across U.S. states in 2023?')
q2 = st.Page('pages/q2.py', title='How did the median advertised salary for Data Analysts change from Nov 2022 to April 2025?')
q3 = st.Page('pages/q3.py', title='How do salaries differ across seniority levels?')
q4 = st.Page('pages/q4.py', title='Do remote data analyst positions pay differently than onsite positions, and has this difference evolved?')
q5 = st.Page('pages/q5.py', title='Are certain skills associated with higher or lower salaries?')


chat_page = st.Page('pages/chat.py', title = 'AI Chat Assistant')

pg = st.navigation([q1, q2, q3, q4, q5, chat_page])

pg.run()