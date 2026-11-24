import csv
import json
from pathlib import Path
from decimal import Decimal
from xml.etree import ElementTree
import openpyxl

import pandas as pd

def read_order(path: Path) -> pd.DataFrame:
    with open(file=path,
              encoding='utf-8') as read_file:
        orders = json.load(read_file, parse_float=Decimal)

    return pd.DataFrame(orders)



def read_events(path: Path) -> pd.DataFrame:
    root = ElementTree.parse(path).getroot()
    records = [
        {field.tag: field.text for field in event}
        for event in root.findall("event")
    ]
    return pd.DataFrame(records)


def full_extract(data_dir: Path) -> list[pd.DataFrame]:
    '''
        Функция для полной загрузки всех сырых табличек и всякого остального
    '''
    customers = pd.read_csv(data_dir / 'customers.csv',
                            encoding='utf-8')
    payments = pd.read_csv(data_dir / 'payments.csv',
                           sep='^',
                           encoding='utf-8')
    products = pd.read_excel(data_dir / 'products.xlsx')
    orders = read_order(data_dir / 'orders.json')
    events = read_events(data_dir / 'events.xml')

    return {'customers': customers,
            'payments': payments,
            'products': products,
            'orders': orders,
            'events': events}