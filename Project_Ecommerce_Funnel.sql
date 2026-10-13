SELECT
	stage_rank,
    CASE
		WHEN stage_rank =1 THEN '1. Homepage View'
        WHEN stage_rank =2 THEN '2. Product Detail View'
        WHEN stage_rank =3 THEN '3. Add to Cart'
        WHEN stage_rank =4 THEN '4. Initiate Checkout'
        WHEN stage_rank =5 THEN '5. Purchase Success'
	END AS stage_name,
    COUNT(DISTINCT session_id) AS unique_sessions
FROM ecommerce_events
GROUP BY stage_rank, stage_name
ORDER BY stage_rank;

WITH funnel_counts AS (
	SELECT
		stage_rank,
        CASE
			WHEN stage_rank = 1 THEN '1.Homepage View'
            WHEN stage_rank = 2 THEN '2.Peoduct Detail View'
            WHEN stage_rank = 3 THEN '3.Add to Cart'
            WHEN stage_rank = 4 THEN '4.Initiate Checkout'
            WHEN stage_rank = 5 THEN '5.Purchase Success'
		END AS stage_name,
        COUNT(DISTINCT session_id) AS unique_sessions
	FROM ecommerce_events
    GROUP BY stage_rank, stage_name
)
SELECT
	stage_rank,
    stage_name,
    unique_sessions,
    ROUND(
		(unique_sessions*100)/(SELECT unique_sessions FROM funnel_counts WHERE stage_rank=1),
        2
        ) AS pct_of_homepage_visitors
	FROM funnel_counts
    ORDER BY stage_rank;
    
/*Query 2: Stage_by_Stage Drop_Off Rate (LAG() Window Functions)*/

WITH funnel_counts AS(
	SELECT
		stage_rank,
        COUNT(DISTINCT session_id) AS current_stage_sessions
	FROM ecommerce_events
    GROUP BY stage_rank
)
SELECT
	stage_rank,
    current_stage_sessions,
    LAG(current_stage_sessions,1) OVER (ORDER BY stage_rank) AS previous_stage_sessions
FROM funnel_counts;

/*Step 3: Chaining CTEs for Clean Math*/

WITH funnel_counts AS (
	SELECT
		stage_rank,
        COUNT(DISTINCT session_id) AS current_stage_sessions
	FROM ecommerce_events
    GROUP BY stage_rank
),
funnel_lag AS (
	SELECT
		stage_rank,
        current_stage_sessions,
        LAG(current_stage_sessions,1) OVER (ORDER BY stage_rank) AS previous_stage_sessions
	FROM funnel_counts
)
SELECT
	stage_rank,
    previous_stage_sessions,
    current_stage_sessions,
    (previous_stage_sessions-current_stage_sessions) AS dropped_sessions,
    ROUND(
		((previous_stage_sessions-current_stage_sessions)*100.0)/previous_stage_sessions,
        2
	) AS drop_off_pct
FROM funnel_lag
ORDER By stage_rank;

/* Query3 : Marketing Channel Attribution and Revenue (Multi-Table JOIN)*/

SELECT
	e.traffic_channel,
    COUNT(DISTINCT e.session_id) AS total_sessions,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(o.net_revenue),2) AS total_net_revenue
FROM ecommerce_events e
LEFT JOIN ecommerce_orders o
	ON e.session_id=o.session_id
GROUP BY e.traffic_channel
ORDER BY total_net_revenue DESC;

SELECT
	e.traffic_channel,
    COUNT(DISTINCT e.session_id) AS total_sessions,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(o.net_revenue),2) AS total_net_revenue,
    ROUND(
		(COUNT(DISTINCT o.order_id)*100.0)/COUNT(DISTINCT e.session_id),
        2
	) AS conversion_rate_pct,
    ROUND(
		SUM(o.net_revenue)/NULLIF(COUNT(DISTINCT o.order_id),0),
        2
	) AS average_order_value
FROM ecommerce_events e
LEFT JOIN ecommerce_orders o
	ON e.session_id = o.session_id
GROUP BY e.traffic_channel
ORDER BY total_net_revenue DESC;
	
    



