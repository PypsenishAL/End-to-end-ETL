from sqlalchemy import create_engine, connectors, Engine
from sqlalchemy import text
from pathlib import Path
import pandas as pd

SCHEMA = "block3_it_gorod_vozmite_pz_na_stazirovky"
TABLE_NAMES = ["customers", "products", "orders", "payments", "events"]

def load(full_tablichki: dict[str, pd.DataFrame], engine: Engine, ddl_path: Path):
    with open(ddl_path, 'r', encoding='utf-8') as read_file:
        sql_ddl_text = read_file.read()
    table_names = [f'{SCHEMA}.{table_name}' for table_name in TABLE_NAMES]
    clear_tables_sql = "TRUNCATE TABLE " + ", ".join(table_names)

    with engine.begin() as zestkaya_transaction:
        zestkaya_transaction.execute(text(sql_ddl_text))
        zestkaya_transaction.execute(text(clear_tables_sql))

        for table_name in TABLE_NAMES:
            df = full_tablichki[table_name]
            df.to_sql(
                name=table_name,
                con=zestkaya_transaction,
                schema=SCHEMA,
                if_exists='append',
                index=False
            )