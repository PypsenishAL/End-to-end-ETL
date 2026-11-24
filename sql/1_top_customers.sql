with grouped_revenue as (
	select 
		customers.customer_id,
		customer_name,
		currency,
		sum(order_total) as total_revenue 
	from 
		customers inner join orders
		on customers.customer_id = orders.order_id
	where status = 'completed'
	group by customers.customer_id, customer_name, currency
	order by total_revenue desc
), ranked as (
	select *,
			row_number() over (partition by currency order by total_revenue desc) as ranker
	from 
		grouped_revenue
)
select customer_id, customer_name, currency, total_revenue
from ranked
where ranker <= 10