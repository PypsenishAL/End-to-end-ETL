from sqlalchemy import create_engine, Engine, text

def execute_sql(engine: Engine, sql_response: text):
    with engine.connect() as connection:
        result = connection.execute(sql_response)
        return result