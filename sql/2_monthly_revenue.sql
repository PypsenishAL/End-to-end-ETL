select date_trunc('month', ordered_at) as timing,
		currency,
		sum(order_total) as monthly_revenue
from 
	orders
where 
	status = 'completed' and ordered_at is not null
group by
	date_trunc('month', ordered_at), currency
order by timing, currency