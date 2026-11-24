select customer_name,
		customers.customer_id, 
		count(*) as total_orders,
		max(ordered_at) as last_activity
from
	customers inner join orders
	on customers.customer_id = orders.customer_id
where
	status = 'completed'
group by
	customers.customer_id,
	customer_name 
order by 
	total_orders desc
limit 5