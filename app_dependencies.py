from sqlite_db_dependencies import CategoryBase, RecordBase, GoalBase
import pandas as pd
import sqlite3
from uuid import uuid4
from datetime import date
import json

def db_conn(stmt: str):
    conn = sqlite3.connect('budget_application.db')
    c = conn.cursor()
    c.execute('PRAGMA foreign_keys = ON')
    c.execute(stmt)
    conn.commit()
    conn.close()

class Endpoint():
    
    def __init__(self):
        self.id_col = ''
        self.table = ''

    def get_all(self):
        entries = pd.read_sql(f'SELECT * FROM {self.table}', 'sqlite:///budget_application.db').to_json(orient='records')
        parsed = json.loads(entries)
        if len(parsed) > 0:
            return parsed
        return {'detail': 'No entries found'}
    
    def get_one(self, searched:str):
        entry = pd.read_sql(f"SELECT * FROM {self.table} WHERE {self.id_col} = '{searched}'", 'sqlite:///budget_application.db').to_json(orient='records')
        parsed = json.loads(entry)
        if len(parsed) > 0:
            return parsed[0]
        return {'detail: entry not found'}
    
    def delete_one(self, searched: str):
        try:
            stmt = f"DELETE FROM {self.table} WHERE {self.id_col} = '{searched}'"
            db_conn(stmt)
            return {'detail': 'entry deleted'}
        except:
            return {'detail': 'entry not found'} 

    def delete_all(self):
        try:
            stmt = f"DELETE FROM {self.table}"
            db_conn(stmt)
            return {'detail': 'all entries deleted'}
        except:
            return {'detail': 'no entries found'} 
        
    def post(self, data: CategoryBase | GoalBase | RecordBase):
        try: 
            values = tuple(data.model_dump().values())
            stmt = f"INSERT INTO {self.table} VALUES {values}"
            db_conn(stmt)
            return {'detail': 'entry posted'}
        except sqlite3.IntegrityError:
            return {'detail': 'entry already exists'}

class CategoriesEndpoint(Endpoint):
    def __init__(self):
        super().__init__()
        self.id_col = 'category'
        self.table = 'categories'

    def update(self, searched: str, updates: CategoryBase):
        if searched in pd.DataFrame(self.get_all())['category'].to_list():
            values = tuple(updates.model_dump().values())
            stmt = f"UPDATE {self.table} SET category = '{values[0]}', income_cat = {values[1]} WHERE category = '{searched}'"
            db_conn(stmt)
            return {'detail': 'entry updated'}
        return {'detail': 'entry not found'}

class GoalsEndpoint(Endpoint):
    def __init__(self):
        super().__init__()
        self.id_col='title'
        self.table='savings_goals'

    def update(self, searched: str, updates: GoalBase):
        if searched in pd.DataFrame(self.get_all())['title'].to_list():
            values = tuple(updates.model_dump().values())
            stmt = f"UPDATE {self.table} SET title = '{values[0]}', amount = {values[1]}, priority = {values[2]} WHERE title = '{searched}'"
            db_conn(stmt)
            return {'detail': 'entry updated'}
        return {'detail': 'entry not found'}

class RecordsEndpoint(Endpoint):
    def __init__(self):
        super().__init__()
        self.id_col='record_id'
        self.table='records'

    def post(self, data: RecordBase):
        to_post = data.model_dump()
        to_post['record_id'] = str(uuid4())
        to_post['date'] = date.today().isoformat()
        if to_post['description'] is None:
            to_post['description'] = 'None'
        values = tuple(to_post.values())
        try:
            stmt = f"INSERT INTO {self.table} VALUES {values}"
            db_conn(stmt)
            return {'detail': 'entry posted'}
        except sqlite3.IntegrityError:
            return {'detail': 'category not found'}
        
    def update(self, searched: str, updates: RecordBase):
        if searched in pd.DataFrame(self.get_all())['record_id'].to_list():
            og = RecordBase(**self.get_one(searched))
            new = og.model_copy(update=updates.model_dump(exclude_unset=True))
            values = tuple(new.model_dump().values())
            stmt = f"UPDATE {self.table} SET record_id = '{values[0]}', date = '{values[1]}', category = '{values[2]}', description = '{values[3]}', amount = {values[4]} WHERE record_id = '{searched}'"
            db_conn(stmt)
            return {'detail': 'entry updated'}
        return {'detail': 'entry not found'}

class EndpointTable():

    endpoints = {
        'categories': CategoriesEndpoint(),
        'records': RecordsEndpoint(),
        'goals': GoalsEndpoint()
    }

    def __init__(self, endpoint: str):
        self.type = endpoint.capitalize()
        self.table = EndpointTable.endpoints[endpoint]

    def new_entry(self, data: CategoryBase | RecordBase | GoalBase):
        return self.table.post(data)

    def get_entry(self, searched: str):
        entry = self.table.get_one(searched)
        return pd.Series(entry)

    def get_entries(self):
        entries = self.table.get_all()
        if type(entries) is list:
            return pd.DataFrame(entries)
        return pd.Series(entries)

    def delete_entry(self, searched:str):
        return self.table.delete_one(searched)

    def delete_entries(self):
        return self.table.delete_all() 
    
    def update_entry(self, searched: str, up: CategoryBase | RecordBase | GoalBase):
        return self.table.update(searched, up)
    
if __name__ == '__main__':
    print('haha')
