select customer_id,
	customer_name
from
	customers
where not exists (
	select order_id
	from orders
	where orders.customer_id = customers.customer_id 
)
order by customer_id 