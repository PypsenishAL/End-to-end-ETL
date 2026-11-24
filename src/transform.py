import logging
import pandas as pd

def log_rows(filenam, reason, stroki):
    if len(stroki) != 0:
        logging.warning("%s - %s. Записи: %s", filenam, reason, stroki.tolist())

def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns={'full_name': 'customer_name'})


def transform(raw: list[pd.DataFrame]):
    data = {}

    for name, df in raw.items():
        df = df.astype("string")
        for column in df.columns:
            df[column] = df[column].str.strip().replace("", pd.NA)
        data[name] = df
    for df in data.values():
        for column in df.columns:
            if column.endswith("_id"):
                ids = pd.to_numeric(df[column], errors="coerce")
                valid = ids.between(-2_147_483_648, 2_147_483_647) & ids.mod(1).eq(0)
                df[column] = ids.where(valid).astype("Int64")
    currencies = ["RUB", "USD", "EUR"]

    customers: pd.DataFrame = data['customers']
    customers = customers.rename(columns={'full_name': 'customer_name'})
    filtered_customers = customers["customer_id"].isna() | customers["customer_name"].isna()
    log_rows("customers.csv", "отклонены: неверный ID или пустое имя", customers.index[filtered_customers])
    customers = customers.loc[~filtered_customers].copy()
    # customers['customer_id'] = customers['customer_id'].astype('int32')

    duplicates = customers['customer_id'].duplicated()
    log_rows("customers.csv", "отклонены: дубли ID", customers.index[duplicates])
    customers = customers.drop_duplicates(subset='customer_id')

    customers['created_at'] = pd.to_datetime(customers['created_at'],
                                             errors='coerce')
    log_rows('customers.csv', 'неверная дата', customers.index[customers['created_at'].isna()])


    products: pd.DataFrame = data['products']
    products['is_active'] = products['is_active'].str.lower().map({'false': False, 'true': True})
    nado_filtrit = (
        products['product_name'].isna() |
        ~products['currency'].isin(currencies) |
        products['is_active'].isna() |
        products['currency'].isna() |
        products["product_id"].isna()
    )
    log_rows("products.xlsx", 'отклонены: неверный ID, имя, валюта или is_active', products.index[nado_filtrit])
    products = products.loc[~nado_filtrit].copy()
    duplicated = products.duplicated(subset='product_id')
    log_rows("products.xlsx", "отклонены: дубли ID", products.index[duplicated])
    filtered_products = products.drop_duplicates(subset="product_id")
    filtered_products['price'] = filtered_products['price'].str.replace(',', '.')
    filtered_products['price'] = pd.to_numeric(filtered_products['price'],
                                               errors='coerce')
    log_rows('products.xlsx', 'пустая или неверная цена', filtered_products.index[filtered_products["price"].isna()])

    orders: pd.DataFrame = data['orders']
    orders = orders.rename(columns={"order_timestamp": "ordered_at"})

    numeric_columns_orders = ['quantity', 'customer_id',
                        'order_id', 'product_id','unit_price']
    for column in numeric_columns_orders:
        orders[column] = pd.to_numeric(orders[column],
                                       errors='coerce')
    quantity = orders["quantity"] 
    valid_quantity = quantity.ge(0) & quantity.mod(1).eq(0)
    bad_quantity = ~valid_quantity.fillna(False)
    nado_filter_orders = (
        orders["order_id"].isna() | 
        ~orders["status"].isin(["completed", "processing", "cancelled"]) |
        ~orders['currency'].isin(currencies) | 
        orders['unit_price'].isna() |
        bad_quantity
    )
    log_rows("orders.json", "отклонены: статус, валюта, количество или цена", orders.index[nado_filter_orders])
    filtered_orders = orders.loc[~nado_filter_orders].copy()
    orders_duplicated = filtered_orders.duplicated(subset='order_id')
    log_rows("orders.json", "удалены дубли до order_id", filtered_orders.index[orders_duplicated])
    filtered_orders = filtered_orders.drop_duplicates(subset='order_id')

    filtered_orders['quantity'] = filtered_orders['quantity'].astype('Int64')
    filtered_orders['order_total'] = filtered_orders['quantity'] * filtered_orders['unit_price']
    filtered_orders['ordered_at'] = pd.to_datetime(
        filtered_orders['ordered_at'], errors='coerce')

    unknown_customers = ~filtered_orders['customer_id'].isin(customers['customer_id'])
    unknown_products = ~filtered_orders['product_id'].isin(filtered_products['product_id'])

    log_rows("orders.json", "пустой или неизвестный клиент", filtered_orders.index[unknown_customers])
    log_rows("orders.json", "пустой или неизвестный товар", filtered_orders.index[unknown_products])
    filtered_orders.loc[unknown_customers, 'customer_id'] = pd.NA
    filtered_orders.loc[unknown_products, 'product_id'] = pd.NA

    payments: pd.DataFrame = data['payments']
    payments = payments.rename(columns={'payment_timestamp': 'paid_at'})
    payments['paid_at'] = pd.to_datetime(payments['paid_at'],
                                         errors='coerce')
    numeric_columns_payments = ['payment_id', 'order_id', 'amount']
    for column in numeric_columns_payments:
        payments[column] = pd.to_numeric(payments[column],
                                         errors='coerce')
    
    payments_to_delete = (
        ~payments['currency'].isin(currencies) |
        payments["payment_id"].isna() |
        payments['paid_at'].isna() |
        payments['amount'].isna() |
        payments["amount"].lt(0)
    )
    log_rows("payments.csv", "отклонены: неверный ID, дата или валюта", payments.index[payments_to_delete])
    payments_filtered = payments.loc[~payments_to_delete].copy()
    payments_duplicated = payments_filtered.duplicated(subset='payment_id')
    log_rows("payments.csv", 'убраны дубли по payment_id', payments_filtered.index[payments_duplicated])

    payments_filtered = payments_filtered.drop_duplicates(subset='payment_id')
    unknown_orders = ~payments_filtered['order_id'].isin(filtered_orders['order_id'])
    log_rows("payments.csv", 'пустой или неизвестный заказ', payments_filtered.index[unknown_orders])
    payments_filtered.loc[unknown_orders, 'order_id'] = pd.NA


    events = data['events'].rename(columns={"event_timestamp": "event_at"})
    events["event_at"] = pd.to_datetime(
        events["event_at"], errors="coerce")
    numeric_columns_events = ['event_id', 'customer_id', 'product_id']
    for column in numeric_columns_events:
        events[column] = pd.to_numeric(events[column],
                                       errors='coerce')
    events_to_drop = (
        events["event_id"].isna()
        | events["event_at"].isna()
        | events["event_type"].isna()
    )
    log_rows("events.xml", 'отклонены: неверный ID, дата или тип события', events.index[events_to_drop])
    filtered_events = events.loc[~events_to_drop].copy()

    duplicated_events = filtered_events.duplicated(subset='event_id')
    log_rows("events.xml", "удаляем полные дубли", filtered_events.index[duplicated_events])
    filtered_events = filtered_events.drop_duplicates(subset='event_id')

    unknown_customers = ~filtered_events["customer_id"].isin(customers["customer_id"])
    unknown_products = ~filtered_events["product_id"].isin(filtered_products["product_id"])
    log_rows("events.xml", "пустой или неизвестный клиент", filtered_events.index[unknown_customers])
    log_rows("events.xml", "пустой или неизвестный товар", filtered_events.index[unknown_products])
    filtered_events.loc[unknown_customers, "customer_id"] = pd.NA
    filtered_events.loc[unknown_products, "product_id"] = pd.NA

    return {"customers": customers[["customer_id", "customer_name", "city", "created_at"]],
        "products": filtered_products,
        "orders": filtered_orders,
        "payments": payments_filtered,
        "events": filtered_events}