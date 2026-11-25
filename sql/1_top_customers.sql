WITH grouped_revenue AS (
    SELECT
        c.customer_id,
        c.customer_name,
        o.currency,
        SUM(o.order_total) AS total_revenue
    FROM block3_it_gorod_vozmite_pz_na_stazirovky.customers AS c
    JOIN block3_it_gorod_vozmite_pz_na_stazirovky.orders AS o
        ON o.customer_id = c.customer_id
    WHERE o.status = 'completed'
    GROUP BY c.customer_id, c.customer_name, o.currency
),
ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY currency
            ORDER BY total_revenue DESC, customer_id
        ) AS ranker
    FROM grouped_revenue
)
SELECT customer_id, customer_name, currency, total_revenue
FROM ranked
WHERE ranker <= 10
ORDER BY currency, ranker;