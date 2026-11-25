select customer_id,
	customer_name
from
	block3_it_gorod_vozmite_pz_na_stazirovky.customers
where not exists (
	select order_id
	from block3_it_gorod_vozmite_pz_na_stazirovky.orders
	where orders.customer_id = customers.customer_id
)
order by customer_id