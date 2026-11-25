
import argparse
import logging
from pathlib import Path
from xml.etree.ElementTree import ParseError
import pandas as pd

from sqlalchemy import create_engine
from sqlalchemy import text

from .sql_execute import execute_sql
from .extract import full_extract
from .transform import transform
from .load import load

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def main():
    parser = argparse.ArgumentParser(
        description='Извлечение, преобразования и загрузка данных в постгрес для третьего блока ДЗ || P.S. возьмите на стажировку пжпжпжп <3')
    parser.add_argument('--data-dir', 
                        type=Path,
                        default=PROJECT_ROOT / 'data',
                        help='папка с данными')
    parser.add_argument('--db-name', default='retail_etl',
                        help='имя этой бдшки в постгресе')
    parser.add_argument('--db-user',
                        default='postgres',
                        help='имя пользователя для постгреса')
    parser.add_argument('--db-port',
                        type=int,
                        default=5432,
                        help='порт для базы данных')
    args = parser.parse_args()
    log_data = PROJECT_ROOT / 'logs' / 'etl.log'
    log_data.parent.mkdir(exist_ok=True)
    logging.basicConfig(
        filename=log_data,
        filemode="w",
        level=logging.INFO,
        format="%(levelname)s %(message)s",
        encoding="utf-8"
    )

    try:
        raw_data = full_extract(args.data_dir)
        logging.info('Успешно извлекли данные')
    except Exception as error:
        print(f'Возникла ошибка {error} на этапе извлечения')

    try:
        full_tablichki = transform(raw_data)
        logging.info('Преобразования успешно отработали')
    except Exception as error:
        print(f'Возникла ошибка {error} на этапе трансформаций')

    password = input('Введите пароль для постгреса: ')
    engine = create_engine(
        f'postgresql+psycopg2://localhost:{args.db_port}',
        connect_args={
            'user': args.db_user,
            'database': args.db_name,
            'password': password
        },
        hide_parameters=True
    )
    try:
        load(full_tablichki, engine, PROJECT_ROOT / 'ddl' / 'schema.sql')
        print(f'Загрузка данных в БД прошла успешно')
        logging.info('Загрузка данных в БД прошла успешно')

        sql_dir = PROJECT_ROOT / 'sql'
        sql_results_dir = PROJECT_ROOT / 'data' / 'sql_results'
        sql_results_dir.mkdir(exist_ok=True)
        sql_files = sorted([path for path in sql_dir.glob(pattern='*.sql')])
        for sql_file in sql_files:
            with open(sql_file, 'r', encoding='utf-8') as read_file:
                sql_text = read_file.read()
                result: pd.DataFrame = execute_sql(engine, text(sql_text))

                sql_file_name = str(sql_file.name)
                filtered_file_name = sql_file_name[:sql_file_name.find('.')] + '_' + 'result' + '.csv'

                with open(sql_results_dir / filtered_file_name, 'w', encoding='utf-8', newline='') as write_file:
                    result.to_csv(write_file,
                                  sep=',',
                                  encoding='utf-8')
        logging.info('Выполнение аналитических запросов прошло успешно')

    except Exception as error:
        print(f"Возникла ошибка {error} на этапе загрузке в БД и выполнение аналитических запросов")
    finally:
        engine.dispose()


if __name__ == '__main__':
    main()