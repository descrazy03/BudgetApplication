import sys
from streamlit.web import cli as stcli
import sqlite_db_dependencies
from sqlite_db_setup import engine

if __name__ == '__main__':

    sqlite_db_dependencies.Base.metadata.create_all(bind=engine) 
    
    sys.argv = ["streamlit", "run", "dashboard.py"]
    sys.exit(stcli.main())