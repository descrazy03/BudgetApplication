import streamlit as st
import app_logic
import altair as alt
from datetime import date, timedelta

st.markdown(
    r"""
    <style>
    .stDeployButton {
            visibility: hidden;
        }
    </style>
    """, unsafe_allow_html=True
)

st.title("Dezzy's Budget App")

#---main monthly summary section---
st.header('Monthly Summary', divider=True)

#---most expenses categories and income sources section---

#define tables
current_month = date.today().month
previous_month = (date.today().replace(day=1) - timedelta(days=1)).month
try:
    expense_df = app_logic.per_month('expense')
    expense_df['month'] = expense_df.index.month
    if previous_month in list(expense_df['month']) and (expense_df.where(expense_df['month'] == previous_month).dropna()).iloc[0]['amount'] != 0 :
        current_month_spent = (expense_df.where(expense_df['month'] == current_month).dropna()).iloc[0]['amount']
        previous_month_spent = (expense_df.where(expense_df['month'] == previous_month).dropna()).iloc[0]['amount']
        spent_percent_change = ((current_month_spent - previous_month_spent) / previous_month_spent) * 100
    else:
        current_month_spent = expense_df.iloc[0]['amount']
        spent_percent_change = 100
except:
    previous_month_spent=0
    current_month_spent=0
    spent_percent_change=0

try:
    income_df = app_logic.per_month('income')
    income_df['month'] = income_df.index.month
    if previous_month in list(income_df['month']) and (income_df.where(income_df['month'] == previous_month).dropna()).iloc[0]['amount'] != 0 :
        current_month_earned = (income_df.where(income_df['month'] == current_month).dropna()).iloc[0]['amount']
        previous_month_earned = (income_df.where(income_df['month'] == previous_month).dropna()).iloc[0]['amount']
        earned_percent_change = ((current_month_earned - previous_month_earned) / previous_month_earned) * 100
    else:
        current_month_earned = income_df.iloc[0]['amount']
        earned_percent_change = 100
except:
    previous_month_earned=0
    current_month_earned=0
    earned_percent_change=0

#metrics
spent_metric_col, earned_metric_col = st.columns(2)
with spent_metric_col:
    st.metric('Amount Spent This Month', f"${current_month_spent: .2f}", delta=f"{round(spent_percent_change)}%", delta_color='inverse')
with earned_metric_col:
    st.metric('Amount Earned This Month', f"${current_month_earned: .2f}", delta=f"{round(earned_percent_change)}%")
    
col1, col2 = st.columns(2, gap='large')

#define start and end date for charts --> first of the month to current day
month_start = [int(val) for val in date.today().replace(day=1).isoformat().split('-')]
current_date = [int(val) for val in date.today().isoformat().split('-')]

#expense categories
with col1:
    st.subheader('Categories Most Spent This Month')
    #expense dataframe
    try:
        monthly_expense_categories = app_logic.get_most(app_logic.records_date(*month_start, *current_date, cat_type='expense')).reset_index()
        monthly_expense_categories = monthly_expense_categories.rename(columns={'amount': 'Amount Spent ($)', 'category': 'Category Name'})
        if len(monthly_expense_categories) > 0:
        #expense graph
            monthly_expense_graph = alt.Chart(monthly_expense_categories).mark_bar().encode(x=alt.X('Amount Spent ($)'), y=alt.Y('Category Name').sort('-x')).properties(height=300)
            st.altair_chart(monthly_expense_graph, use_container_width=True)
            st.dataframe(monthly_expense_categories, hide_index=True, use_container_width=True)
        else:
            st.write('No expense transactions!')
    except:
        st.write('No expense transactions!')

#income sources
with col2:
    st.subheader('Sources Most Earned From This Month')
    try: 
    #income dataframe
        monthly_income_categories = app_logic.get_most(app_logic.records_date(*month_start, *current_date, cat_type='income')).reset_index()
        monthly_income_categories = monthly_income_categories.rename(columns={'amount': 'Amount Spent ($)', 'category': 'Category Name'})
        if len(monthly_income_categories) > 0:
        #income graph
            monthly_income_graph = alt.Chart(monthly_income_categories).mark_bar().encode(x=alt.X('Amount Spent ($)'), y=alt.Y('Category Name').sort('-x')).properties(height=300)
            st.altair_chart(monthly_income_graph, use_container_width=True)
            st.dataframe(monthly_income_categories, hide_index=True, use_container_width=True)
        else:
            st.write('No income transactions!')
    except:
        st.write('No income transactions!')


#---per month summmary section---
st.header('Cash Flow Per Month', divider=True)

#expenses per month graph
st.subheader('Money Spent Per Month')
try:
    expense_df['date_labels'] = expense_df.index.strftime("%b '%y")
    expense_df = expense_df.rename(columns={'date_labels':'Month', 'amount': 'Amount Spent ($)'})
    if len(expense_df) > 0:
        expense_per_month = alt.Chart(expense_df).mark_bar().encode(x=alt.X('Month', sort=None), y='Amount Spent ($)')
        st.altair_chart(expense_per_month, use_container_width=True)
    else:
        st.write('No expense transactions!')
except:
    st.write('No expense transactions!')
#income per month graph
st.subheader('Money Earned Per Month')
try:
    income_df['date_labels'] = income_df.index.strftime("%b '%y")
    income_df = income_df.rename(columns={'date_labels':'Month', 'amount': 'Amount Spent ($)'})
    if len(income_df) > 0:
        income_per_month = alt.Chart(income_df).mark_bar().encode(x=alt.X('Month', sort=None), y='Amount Spent ($)')
        st.altair_chart(income_per_month, use_container_width=True)
    else:
        st.write('No income transactions!')
except:
    st.write('No income transactions!')