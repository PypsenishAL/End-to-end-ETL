create schema if not EXISTS block3_IT_gorod_vozmite_pz_na_stazirovky;

create table if not exists block3_IT_gorod_vozmite_pz_na_stazirovky.customers (
    customer_id int primary key,
    customer_name text not NULL,
    city text,
    created_at timestamp
);

create table if not exists block3_IT_gorod_vozmite_pz_na_stazirovky.products (
    product_id int primary key,
    product_name text not null,
    category text,
    price numeric(10, 2) check (price >= 0),
    currency text not null,
    is_active boolean
);

create table if not exists block3_IT_gorod_vozmite_pz_na_stazirovky.orders (
    order_id int primary key,
    customer_id int REFERENCES block3_IT_gorod_vozmite_pz_na_stazirovky.customers (customer_id),
    product_id int REFERENCES block3_IT_gorod_vozmite_pz_na_stazirovky.products (product_id),
    ordered_at timestamp,
    status text not null check (status IN ('completed', 'processing', 'cancelled')),
    quantity bigint not null check (quantity >= 0),
    unit_price numeric(10, 2) not null,
    currency text not null,
    order_total numeric(10, 2) not null
);

create table if not exists block3_IT_gorod_vozmite_pz_na_stazirovky.payments (
    payment_id int primary key,
    order_id int REFERENCES block3_IT_gorod_vozmite_pz_na_stazirovky.orders (order_id),
    paid_at timestamp not null,
    payment_method text,
    amount numeric(14, 2) not null check(amount >=0),
    currency text not null
);

create table if not exists block3_IT_gorod_vozmite_pz_na_stazirovky.events (
    event_id int primary key,
    customer_id int references block3_IT_gorod_vozmite_pz_na_stazirovky.customers(customer_id),
    product_id int references block3_IT_gorod_vozmite_pz_na_stazirovky.products(product_id),
    event_at timestamp,
    event_type text not null
);