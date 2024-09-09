import streamlit as st
import app_logic
from app_dependencies import RecordBase, EndpointTable

st.title('Transactions')
st.header('All Transaction Records', divider=True)

#---new transaction section---
with st.popover('New Transaction Record', use_container_width=True):
    try:
        cats = app_logic.get_categories('expense') + app_logic.get_categories('income')
        new_tran_cat = st.selectbox('Category:',cats, index=None, placeholder="Select Category...",)
        new_tran_amt = st.number_input('Amount:')
        new_tran_desc = st.text_input('Description:', placeholder='Brief Description')
        if st.button('Create Record'):
            if new_tran_amt > 0 and new_tran_cat is not None:
                try:
                    to_input = RecordBase(category=new_tran_cat, description=new_tran_desc, amount=new_tran_amt)
                    EndpointTable('records').new_entry(to_input)
                except:
                    st.write('Incorrect Input!')
    except:
        st.write('No categories yet! Create a new one on the Categories page.')
            
#---transaction table---
try:
    transactions_graph = app_logic.EndpointTable('records').get_entries().sort_values(by='date', ascending=False)
    tran_df = transactions_graph.set_index('record_id')
    table = st.dataframe(tran_df, use_container_width=True, on_select='rerun', selection_mode='single-row', hide_index=True)
except:
    st.write('No transactions recorded!')
    st.stop()
if table is not None:
    if table.selection.rows:
        idx = table.selection.rows[0]
        entry = tran_df.iloc[idx].name
        #update record
        with st.popover('Update Selection'):
            st.write(entry)
            updated_tran_cat = st.selectbox('Updated Category:', cats, index=None, placeholder="Select Category...",)
            updated_tran_amt = st.number_input('Updated amount:')
            updated_tran_desc = st.text_input('Updated description:', placeholder='Brief Description')
            updated_tran_date = st.date_input('New Date:', value=None)
            if st.button('Update Record'):
                try:
                    original_tran = EndpointTable('records').get_entry(entry)
                    updated_cat = original_tran['category']
                    updated_amt = original_tran['amount']
                    updated_desc = original_tran['description']
                    updated_date = original_tran['date']
                    if updated_tran_cat is not None:
                        updated_cat = updated_tran_cat
                    if updated_tran_amt > 0:
                        updated_amt = updated_tran_amt
                    if updated_tran_desc is not None and updated_tran_desc != '' and updated_tran_desc.isspace() == False:
                        updated_desc = updated_tran_desc
                    if updated_tran_date is not None:
                        updated_date = updated_tran_date.isoformat()
                    
                    updated_record = RecordBase(date=updated_date, category=updated_cat, description=updated_desc, amount=updated_amt)
                    EndpointTable('records').update_entry(entry, updated_record)
                    st.rerun()
                except:
                    st.rerun()
        #delete record
        if st.button('Delete Record'):
            EndpointTable('records').delete_entry(entry)
            st.rerun()
#---transaction filters---
st.header('Filter Transactions', divider=True)
#category filter
st.subheader('Filter By Category:')
try:
    cat_filter = st.selectbox('Category:',cats, index=None, placeholder="Select...",)
    if cat_filter is not None:
        filtered_cat = app_logic.get_records_category(cat_filter)
        filtered_cat_df = filtered_cat.set_index('record_id')
        if len(filtered_cat_df) > 0:
            st.dataframe(filtered_cat_df, use_container_width=True)
        else:
            st.write('No transactions!')
except:
    st.write('No transactions!')
#date filter
st.subheader('Filter By Date:')
try:
    start_date = st.date_input('Start Date:', value=None)
    end_date = st.date_input('End Date:', value=None)
    if start_date is not None and end_date is not None:
        start_list = [int(num.lstrip()) for num in start_date.isoformat().split('-')]
        end_list = [int(num.lstrip()) for num in end_date.isoformat().split('-')]
        filtered_date = app_logic.records_date(*start_list, *end_list)
        filtered_date_df = filtered_date.set_index('record_id')
        filtered_date_df['date'] = filtered_date_df['date'].astype(str)
        if len(filtered_date_df) > 0:
            st.dataframe(filtered_date_df, use_container_width=True)
        else:
            st.write('No transactions!')
except:
    st.write('No transactions!')