import pandas as pd
from sqlalchemy import create_engine, text
from utils.config import database_connection


#postgres query executer 
class Query_Executer:
    def __init__(self):
        self.database = database_connection['postgres']['database']
        self.user = database_connection['postgres']['user']
        self.password = database_connection['postgres']['password']
        self.host = database_connection['postgres']['host']
        self.port = database_connection['postgres']['port']
        self.db_schema = database_connection['postgres']['schema']


    def execute_query(self, query: str):
        try:
            db_url = f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
            engine = create_engine(db_url)
            m_query = query.replace('db_name', self.db_schema)
            # with engine.connect() as connection:
            #     result = connection.execute(text(m_query))
            #     return result.fetchall()
            return pd.read_sql_query(m_query, engine)
           
        except Exception as e:
            return e
    
    

'''
from concurrent.futures import ThreadPoolExecutor, as_completed

class QueryExecutor_:
    def __init__(self, db_connection_string, max_workers=5):
        self.engine = create_engine(db_connection_string)
        self.max_workers = max_workers

    def execute_query(self, query):
        with self.engine.connect() as connection:
            result = pd.read_sql(query, connection)
        return result.to_dict(orient='records')

    def execute_queries_parallel(self, queries):
        results = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.execute_query, query) for query in queries]
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
        return results
'''