import streamlit as st
import app_logic
from app_dependencies import CategoryBase, EndpointTable
import pandas as pd

#---categories section---
st.title('Categories')

#---new category section---
st.subheader('All Categories')

with st.popover('New Category', use_container_width=True):
    new_cat_title = st.text_input('New Category Name:', placeholder='Category Name')
    new_cat_type = st.selectbox('Category Type (Income or Expense)', ('Income', 'Expense'), index=None, placeholder="Select Type...")

    types = {
                'Income': True, 
                'Expense': False
            }
    
    if st.button('Create Category'):

        if new_cat_title is not None and new_cat_type is not None:
            to_input = CategoryBase(category=new_cat_title, income_cat=types[new_cat_type])
            EndpointTable('categories').new_entry(to_input)
            st.rerun()

        else:
            st.write('Invalid Input!')

#categories tables
try:
    all_cats = EndpointTable('categories').get_entries().copy()
    inverse_types = {
        True: 'Income',
        False: 'Expense'
    }
    all_cats['Type'] = all_cats.apply(lambda row: inverse_types[row['income_cat']], axis=1)
    all_cats = all_cats.sort_values(by='Type')
except:
    st.write('No categories yet!')
    st.stop()

cat_table = st.dataframe(all_cats.drop('income_cat', axis=1).set_index('category').sort_values(by='Type'), use_container_width=True, on_select='rerun', selection_mode='single-row')

if cat_table.selection.rows:

    with st.popover('Update Category'):
        idx = cat_table.selection.rows[0]
        entry = all_cats.iloc[idx]['category']
        
        #update category section
        st.write(entry)
        cats = app_logic.get_categories('expense') + app_logic.get_categories('income')
        updated_cat_title = st.text_input('Updated Category Name:', placeholder='New Category Name')
        updated_cat_type = st.selectbox('Updated Category Type (Income or Expense)', ('Income', 'Expense'), index=None, placeholder="Select Type...")
        
        if st.button('Update Category'):
            if entry is not None:
                original = EndpointTable('categories').get_entry(entry)
                cat_update = original['category']
                type_update = original['income_cat']
        
                if updated_cat_title is not None and updated_cat_title != '' and updated_cat_title.isspace() == False:
                   cat_update = updated_cat_title

                if updated_cat_type is not None:
                   type_update = types[updated_cat_type]

                try:
                    updated_entry = CategoryBase(category=cat_update, income_cat=type_update)
                    EndpointTable('categories').update_entry(entry, updated_entry)
                    st.rerun()

                except:
                    st.rerun()
            #---delete category section---
    if st.button('Delete Record'):
        if entry in cats:
            EndpointTable('categories').delete_entry(entry)
            st.rerun()
            
        else:
            st.rerun()
#---categories table/graph section---
st.header('Categories Breakdown', divider=True)

#categories graphs
st.subheader('Select Date Range:')
start_date = st.date_input('Start Date:', value=None)
end_date = st.date_input('End Date:', value=None)

try:
    expense_sums_graph = app_logic.category_sum_counts(app_logic.get_record_type('expense'))[0]
    expense_counts_graph = app_logic.category_sum_counts(app_logic.get_record_type('expense'))[1]
    income_sums_graph = app_logic.category_sum_counts(app_logic.get_record_type('income'))[0]
    income_counts_graph = app_logic.category_sum_counts(app_logic.get_record_type('income'))[1]
    rec_entries = EndpointTable('records').get_entries().copy()
    is_date_filtered = False

    if start_date is not None and end_date is not None:

        start = [int(val) for val in start_date.isoformat().split('-')]
        end = [int(val) for val in end_date.isoformat().split('-')]

        expense_sums_graph = app_logic.category_sum_counts(app_logic.records_date(start[0], start[1], start[2], end[0], end[1], end[2], cat_type='expense').drop('date', axis=1))[0]
        expense_counts_graph = app_logic.category_sum_counts(app_logic.records_date(start[0], start[1], start[2], end[0], end[1], end[2], cat_type='expense').drop('date', axis=1))[1]
        income_sums_graph = app_logic.category_sum_counts(app_logic.records_date(start[0], start[1], start[2], end[0], end[1], end[2], cat_type='income').drop('date', axis=1))[0]
        income_counts_graph = app_logic.category_sum_counts(app_logic.records_date(start[0], start[1], start[2], end[0], end[1], end[2], cat_type='income').drop('date', axis=1))[1]
        rec_entries = app_logic.records_date(start[0], start[1], start[2], end[0], end[1], end[2]).drop('date', axis=1)
        is_date_filtered = True

    if is_date_filtered == True:
        sum_totals = {
            'income': app_logic.records_sum(app_logic.records_date(start[0], start[1], start[2], end[0], end[1], end[2], cat_type='income').drop('date', axis=1)),
            'expense': app_logic.records_sum(app_logic.records_date(start[0], start[1], start[2], end[0], end[1], end[2], cat_type='expense').drop('date', axis=1))
        }
    else:
        sum_totals = {
            'income': app_logic.records_sum(app_logic.get_record_type('income')),
            'expense': app_logic.records_sum(app_logic.get_record_type('expense'))
        }

    sums = pd.DataFrame(rec_entries.groupby('category').sum()['amount'])
    counts = pd.DataFrame(rec_entries.groupby('category').count()['amount'])
    sums_counts = sums.join(counts, lsuffix='_sums', rsuffix='_counts').rename({'amount_sums': "Total ($)", 'amount_counts': "Number of Transactions"}, axis=1).reset_index()
    all_cats_sums_counts = pd.merge(all_cats, sums_counts, how='outer')
    all_cats_sums_counts['Percentage of Total'] = all_cats_sums_counts.apply(lambda row: f"{(row['Total ($)'] / sum_totals[row.Type.lower()] * 100):.2f}", axis=1)
    all_cats_sums_counts = all_cats_sums_counts.replace('nan', '0.0')

    expense_col, income_col = st.tabs(['Expense', 'Income'])

    with expense_col:

        st.subheader('Amount Spent Per Expense Category')

        if is_date_filtered == False and len(app_logic.get_record_type('expense')) > 0:
            st.altair_chart(expense_sums_graph, use_container_width=True)
            st.subheader('Number of Transactions Per Expense Category')
            st.altair_chart(expense_counts_graph, use_container_width=True)
            st.dataframe(all_cats_sums_counts.where(all_cats_sums_counts['Type'] == 'Expense')
                         .dropna()
                         .drop('income_cat', axis=1), hide_index=True)

        elif is_date_filtered == True and len(app_logic.records_date(start[0], start[1], start[2], end[0], end[1], end[2], cat_type='expense')):
            st.altair_chart(expense_sums_graph, use_container_width=True)
            st.subheader('Number of Transactions Per Expense Category')
            st.altair_chart(expense_counts_graph, use_container_width=True)
            st.dataframe(all_cats_sums_counts.where(all_cats_sums_counts['Type'] == 'Expense').
                         dropna().
                         drop('income_cat', axis=1),
                         hide_index=True)

        else:
            st.write('No expense transactions!')

    with income_col:

        st.subheader('Amount Spent Per Income Source')
        if is_date_filtered == False and len(app_logic.get_record_type('income')) > 0:
            st.altair_chart(income_sums_graph, use_container_width=True)
            st.subheader('Number of Transactions Per Income Source')
            st.altair_chart(income_counts_graph, use_container_width=True)
            st.dataframe(all_cats_sums_counts.where(all_cats_sums_counts['Type'] == 'Income').
                         dropna().
                         drop('income_cat', axis=1), 
                         hide_index=True)

        elif is_date_filtered == True and len(app_logic.records_date(start[0], start[1], start[2], end[0], end[1], end[2], cat_type='income')):
            st.altair_chart(income_sums_graph, use_container_width=True)
            st.subheader('Number of Transactions Per Income Source')
            st.altair_chart(income_counts_graph, use_container_width=True)
            st.dataframe(all_cats_sums_counts.where(all_cats_sums_counts['Type'] == 'Income').dropna().
                         drop('income_cat', axis=1), 
                         hide_index=True)

        else:
            st.write('No income transactions!')
        
except:
    st.write('No transactions!')