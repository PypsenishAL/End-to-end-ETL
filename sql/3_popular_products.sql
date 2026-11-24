select 
	product_name, 
	sum(quantity) as total_units,
	count(*) as total_orders
from
	products inner join orders
	on products.product_id = orders.order_id
where status = 'completed'
group by product_name
order by total_units desc, total_orders desc