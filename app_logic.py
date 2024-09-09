from app_dependencies import EndpointTable
import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
import altair as alt

#create methods to analyze Tables

def get_categories(cat_type: str):
    types = {
        'income': True,
        'expense': False
    }
    table = EndpointTable('categories').get_entries()
    income = table.where(table['income_cat'] == types[cat_type]).dropna()
    return list(income['category'].values)

def get_record_type(cat_type: str):
    categories = get_categories(cat_type)
    records = EndpointTable('records').get_entries()
    return records.loc[records['category'].isin(categories)]

def get_records_category(category: str):
    table = EndpointTable('records').get_entries().sort_values(by='date', ascending=False, ignore_index=True)
    return table.loc[table['category'] == category]

def records_sum(records):
    table = records
    return table['amount'].sum()

def records_date(y1, m1, d1, y2, m2, d2, cat_type=None):
    types = {
        None: EndpointTable('records').get_entries().copy().sort_values(by='date', ascending=False, ignore_index=True),
        'income': get_record_type('income'),
        'expense': get_record_type('expense')
    }
    table = types[cat_type]
    table['date'] = pd.to_datetime(table['date'])
    start_date = datetime(y1, m1, d1)
    end_date = datetime(y2, m2, d2)
    return table.loc[(table['date'] >= start_date) & (table['date'] <= end_date)]

def get_most(records):
    cat_groups = records.groupby(['category'])
    return cat_groups['amount'].sum().sort_values(ascending=False).to_frame()

def remaining_budget():
    income = get_record_type('income')
    expense = get_record_type('expense')
    return records_sum(income) - records_sum(expense)

def per_month(cat_type: str):
    table = get_record_type(cat_type)
    table['date'] = pd.to_datetime(table['date'])
    return table.groupby(pd.Grouper(key='date', freq='ME')).sum()['amount'].to_frame()

def get_goals():
    table = EndpointTable('goals').get_entries()
    return table.sort_values(by='priority')

def goal_priority(priority: int):
    table = EndpointTable('goals').get_entries()
    found = table.loc[table['priority'] == priority]
    if len(found) > 0:
        return found
    return None

def available_goals(priority: int = 5):
    leftover = remaining_budget()
    goals = get_goals()
    return goals.loc[(goals['amount'] <= leftover) & (goals['priority'] <= priority)]

def in_progress_goals(priority: int = 5):
    leftover = remaining_budget()
    goals = get_goals()
    return goals.loc[(goals['amount'] > leftover) & (goals['priority'] <= priority)]

def goal_price_range(min_price:float, max_price:float):
    table = EndpointTable('goals').get_entries()
    found = table.loc[(table['amount'] >= min_price) & (table['amount'] <= max_price)]
    if len(found) > 0:
        return found
    return None

#graph categories most spent/earned

def category_sum_counts(df):
    entries = df
    sums = pd.DataFrame(entries.groupby('category').sum()['amount'])
    counts = pd.DataFrame(entries.groupby('category').count()['amount'])
    sums_counts = sums.join(counts, lsuffix='_sums', rsuffix='_counts').rename({'amount_sums': "Total Spent", 'amount_counts': "Number of Transactions"}, axis=1).reset_index()

    sums_graph = alt.Chart(sums_counts).mark_arc(innerRadius=75).encode(
        theta=alt.Theta(field="Total Spent", type="quantitative"),
        color=alt.Color(field="category", type="nominal"))
    
    counts_graph = alt.Chart(sums_counts).mark_arc(innerRadius=75).encode(
        theta=alt.Theta(field="Number of Transactions", type="quantitative"),
        color=alt.Color(field="category", type="nominal"))

    return sums_graph, counts_graph

if __name__ == '__main__':
    expense_df = per_month('expense')
    expense_df['month'] = expense_df.index.month
    current_month = expense_df.where(expense_df['month'] == date.today().month).dropna()
    previous_month = expense_df.where(expense_df['month'] == (date.today().replace(day=1) - timedelta(days=1)).month).dropna()
    #print(current_month.iloc[0]['amount'])
    #print(previous_month.iloc[0]['amount'])
    if (date.today().replace(day=1) - timedelta(days=1)).month in list(expense_df['month']):
        print("we're so back")
    else:
        print('nah dude')