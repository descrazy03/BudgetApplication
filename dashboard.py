import streamlit as st

pgs = st.navigation(pages=[st.Page('routes/dashboard_home.py', title='Home', default=True), 
                           st.Page('routes/dashboard_categories.py', title='Categories'),  
                            st.Page('routes/dashboard_goals.py', title='Goals'),
                            st.Page('routes/dashboard_transactions.py', title='Transactions')])
pgs.run()