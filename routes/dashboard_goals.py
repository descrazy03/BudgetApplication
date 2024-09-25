import streamlit as st
import app_logic
from app_dependencies import GoalBase, EndpointTable

st.markdown(
    r"""
    <style>
    .stDeployButton {
            visibility: hidden;
        }
    </style>
    """, unsafe_allow_html=True
)

#---goals page---
st.title('Savings Goals')

#---goals tables/metrics section---
st.header('All Savings Goals', divider=True)

#goals metrics section
remaining_budget, total_cost, goal_progress = st.columns(3)
try:
    with remaining_budget:
        budget = app_logic.remaining_budget()
        st.metric('Remaining Budget', value=f"${budget: .2f}")
except:
    with remaining_budget:
        st.metric('Remaining Budget', value=f"${0: .2f}")
try:
    with total_cost:
        total = app_logic.get_goals()['amount'].sum()
        st.metric('Total Cost of All Savings Goals', value=f"${total: .2f}")
except:
    with total_cost:
        st.metric('Total Cost of All Savings Goals', value=f"${0: .2f}")

try:
    with goal_progress:
        st.metric('Progress Towards Savings Goals', value=f"{abs(budget / total) * 100: .2f}%")
except:
    with goal_progress:
        st.metric('Progress Towards Savings Goals', value=f"{0: .2f}%")

#---new goal section---
with st.popover('New Savings Goal', use_container_width=True):
    new_goal_title = st.text_input('New Savings Goal Name:', placeholder="Goal Name")
    new_goal_amt = st.number_input('New Savings Goal Amount:')
    new_goal_priority = st.select_slider('New Savings Goal Priority:', (1,2,3,4,5))
    if st.button('Create Savings Goal'):
        if new_goal_title is not None and new_goal_title != '' and new_goal_amt > 0:
            new_goal_entry = GoalBase(title=new_goal_title, amount=new_goal_amt, priority=new_goal_priority)
            EndpointTable('goals').new_entry(new_goal_entry)
            st.rerun()
        else:
            st.write('Invalid Input!')

#all goals
try:
    goals_table = app_logic.get_goals().sort_values(by='priority').set_index('title')
    goals_df = st.dataframe(goals_table, use_container_width=True, on_select='rerun', selection_mode='single-row')
except:
    st.write('No savings goals yet!')
    st.stop()
if goals_df is not None:
    if goals_df.selection.rows:
        idx = goals_df.selection.rows[0]
        entry = goals_table.iloc[idx].name
        #update goal section
        with st.popover('Update Selection'):
            st.write(entry)
            updated_title = st.text_input('Updated Savings Goal Title:', placeholder='Goal Name')
            updated_amt = st.number_input('Updated Savings Goal Amount:')
            updated_priority = st.select_slider('Updated Savings Goal Priority:', (1,2,3,4,5))
            if st.button('Update Savings Goal'):
                original = EndpointTable('goals').get_entry(entry)
                title_update = original['title']
                amt_update = original['amount']
                priority_update = original['priority']
                if updated_title is not None and updated_title != '' and updated_title.isspace() == False:
                    title_update = updated_title
                if updated_amt > 0:
                    amt_update = updated_amt
                if updated_priority != priority_update:
                    priority_update = updated_priority
                try:
                    updated_goal = GoalBase(title=title_update, amount=amt_update, priority=priority_update)
                    EndpointTable('goals').update_entry(entry, updated_goal)
                    st.rerun()
                except:
                    st.rerun()
        #delete goal section
        if st.button('Delete Savings Goal'):
            EndpointTable('goals').delete_entry(entry)
            st.rerun()

#---goal filters section---
st.header('Filter Savings Goals', divider=True)
#available and in progress tables
st.subheader('Filter By Goal Status:')
available_vs_in_progress = st.selectbox('Available Goals or Goals in Progress', ('Available Goals', 'Goals in Progress'), index=None, placeholder="Select Goal Status")
if available_vs_in_progress == 'Available Goals':
    st.subheader('Available Goals')
    available = app_logic.available_goals().sort_values(by='priority').set_index('title')
    if len(available) > 0:
        st.dataframe(available, use_container_width=True)
    else:
        st.write('No goals available!')
elif available_vs_in_progress == 'Goals in Progress':
    st.subheader('Goals in Progress')
    in_progress = app_logic.in_progress_goals().sort_values(by='priority').set_index('title')
    if len(in_progress) > 0:
        st.dataframe(in_progress, use_container_width=True)
    else:
        st.write('No goals in progress')
#priority filter
st.subheader('Filter By Priority:')
priority_filter = st.select_slider('Select Savings Goal Priority:', (1,2,3,4,5))
if st.button('Filter Priority'):
    if app_logic.goal_priority(priority_filter) is not None:
        st.dataframe(app_logic.goal_priority(priority_filter), hide_index=True)
    else:
        st.write('No Goals Found!')
#price filter
st.subheader('Filter By Price:')
min_price = st.number_input('Minimum Price:')
max_price = st.number_input('Maximum Price:')

if max_price > 0:
    if app_logic.goal_price_range(min_price, max_price) is not None:
        st.dataframe(app_logic.goal_price_range(min_price, max_price), hide_index=True)
    else:
        st.write('No goals found!')