from sqlalchemy import create_engine, Engine, text
import pandas as pd

def execute_sql(engine: Engine, sql_response: text):
    with engine.connect() as connection:
        result = pd.read_sql(sql=sql_response,
                             con=connection,
                             )
        return result