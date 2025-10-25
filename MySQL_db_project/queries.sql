/*  For this section of script, which lists all my queries,  I have written them in a question and answer style.
I tried to think of what questions an owner of a bike shop would ask. 
I also thought about what transactions would need to happen too. 
*/


-- Please can give me a list of all of the bikes we sell?
SELECT 
	product_name AS `Bike Name` 
FROM products AS p
WHERE (p.product_type = 'Bike')
;

 
-- What is the most popular bike we sold last week (and how many)?
SELECT 
	(SELECT DISTINCT CASE WHEN p.product_type = 'Bike' THEN p.product_name END) as Bike,
	COUNT(DISTINCT CASE WHEN p.product_type = 'Bike' THEN oi.order_id END) as Sold
FROM order_items AS oi
LEFT JOIN products AS p
	ON oi.product_id = p.product_id
GROUP BY Bike
ORDER BY Sold DESC
LIMIT 1;


-- Please can you print off a list of all the current prices of bike accessories?
SELECT p.product_name AS Accessory,
	pp.product_price AS Price
FROM products AS p
INNER JOIN product_prices AS pp
	ON p.product_id = pp.product_id
WHERE p.product_type = 'Accessory'
ORDER BY PRICE ASC
;

    
/*Can you create an Orders Information table? 
So staff can easily view a customer's order when they arrive in store. 
It's ok for this to be read-only I don't need anything to be modified using this view.
I want one row per order! */
CREATE VIEW vw_orders_information AS    
SELECT c.customer_name as Customer,
	c.customer_id AS `Customer ID`,
	oi.order_id AS `Order Number`,
	GROUP_CONCAT(CONCAT(p.product_name, ': ', oi.quantity, ' @ £', pp.product_price)
		ORDER BY o.order_id SEPARATOR ', ') AS Items,
	SUM(oi.quantity * pp.product_price) AS `Total Price`,
    DATE_FORMAT(o.order_date, '%a %D %M %y') AS `Date`,
    e.employee_name AS `Sold By`
FROM products AS p

LEFT JOIN product_prices AS pp
	ON p.product_id = pp.product_id
LEFT JOIN order_items AS oi
	ON oi.product_id = pp.product_id
LEFT JOIN orders AS o
	ON oi.order_id = o.order_id
LEFT JOIN employee_names AS e
	on e.employee_id = o.employee_id
LEFT JOIN customer_names AS c
	ON c.customer_id = o.customer_id
GROUP BY oi.order_id
;

SELECT * FROM vw_orders_information;

-- Can you find the customer's phone number from the most expensive order on Tuesday please?
SELECT 
	vw_oi.Customer,
	vw_oi.`Order Number`,
	vw_oi.`Total Price`,
    cp.customer_phone_number AS `Phone Number`
FROM vw_orders_information AS vw_oi

LEFT JOIN customer_names
	ON vw_oi.`Customer ID` = customer_names.customer_id  
LEFT JOIN customer_phone_numbers AS cp
	ON customer_names.customer_id = cp.customer_id

WHERE vw_oi.`Date` = 'Tue 2nd September 25' 
ORDER BY vw_oi.`Total Price` DESC
LIMIT 1
;


-- On what day did we have the most individual orders (and how many)?
SELECT COUNT(order_id) AS `Total Orders`, 
	DAYNAME(o.order_date) AS `Date`
FROM orders as o 
GROUP BY `Date`
ORDER BY (`Total Orders`) DESC
LIMIT 1
;

/* I need to find the Employee of the Month! Which employee had the highest number of orders?
(Remember, employees need 4 or more orders to be eligible)
I then need their contact details to tell them the good news! */
SELECT e.employee_name AS `Employee of the Month`,
	o.employee_id AS `Employee ID`,
    COUNT(o.customer_id) AS `Number of Orders`,
    ee.employee_email AS `Email`,
    ep.employee_phone_number AS `Phone Number`
FROM orders AS o
INNER JOIN employee_names AS e
	ON o.employee_id = e.employee_id
INNER JOIN employee_emails AS ee
	ON e.employee_id = ee.employee_id
INNER JOIN employee_phone_numbers AS ep
	ON ee.employee_id = ep.employee_id
GROUP BY o.employee_id
	HAVING COUNT(o.customer_id) >= 4 
ORDER BY COUNT(o.customer_id) DESC
LIMIT 1
;


/* I need to check whether we hit our KPIs. 
Overall, orders need 75% accessory attachment and 30% maintenance plan attachment.
Print out whether we hit our KPIs this week please. 
Oh and I need to know what employees DIDN'T hit these BOTH sales targets this week (meeting one is ok).
Oh and our KPIs arent yet saved in the database, but you know what they are?
Is there a way you could make this easier in the future?
*/

CREATE TABLE kpis(
 		kpi_id INT AUTO_INCREMENT,
		kpi_type VARCHAR(50),
 		kpi_percentage DECIMAL (3,2) DEFAULT '0.3',
 	PRIMARY KEY (kpi_id)
 );

INSERT INTO kpis (kpi_id, kpi_type, kpi_percentage)
VALUES ('1', 'Accessories Attachment Rate', '0.75'),
 ('2', 'Maintenance Plan Attachment Rate', DEFAULT)
 ;
 

DELIMITER //
CREATE FUNCTION hit_kpis(total_orders INT, total_kpi_orders INT, kpi_percentage DECIMAL(3,2))
	RETURNS VARCHAR(30)
    DETERMINISTIC 
    
    BEGIN
     DECLARE hit_kpis VARCHAR(30); 
     IF total_kpi_orders / total_orders > kpi_percentage THEN
		SET hit_kpis = 'KPI: exceeded' ;
	ELSEIF total_kpi_orders / total_orders = kpi_percentage THEN
		SET hit_kpis = 'KPI: met';
	ELSEIF total_kpi_orders / total_orders < kpi_percentage THEN
		SET hit_kpis = 'KPI: failed to meet';
	END IF ;
    
    RETURN hit_kpis ;
END//
DELIMITER ;

CREATE VIEW vw_kpis_store
AS
SELECT
	hit_kpis(
		COUNT(DISTINCT o.order_id),
		COUNT(DISTINCT CASE WHEN p.product_type ='Accessory' THEN o.order_id END),
		(SELECT 
			CASE WHEN kpis.kpi_type = 'Accessories Attachment Rate' 
			THEN kpis.kpi_percentage END
			FROM kpis
			WHERE kpis.kpi_type = 'Accessories Attachment Rate' 
			LIMIT 1)
	) AS `Accessories Result`,

	hit_kpis(
		COUNT(DISTINCT o.order_id),
		COUNT(DISTINCT CASE WHEN p.product_type ='Plan' THEN o.order_id END),
		(SELECT 
			CASE WHEN kpis.kpi_type = 'Maintenance Plan Attachment Rate'
			THEN kpis.kpi_percentage END
			FROM kpis
			WHERE kpis.kpi_type = 'Maintenance Plan Attachment Rate'
			LIMIT 1)
	) AS `Plans Result`,

	COUNT(DISTINCT o.order_id) AS `Total Orders`,
	COUNT(DISTINCT CASE WHEN p.product_type ='Accessory' THEN o.order_id END) AS `Total Accessories Sold`,
	COUNT(DISTINCT CASE WHEN p.product_type ='Plan' THEN o.order_id END) AS `Total Plans Sold`
FROM orders AS o

RIGHT JOIN order_items AS oi 
	ON o.order_id = oi.order_id
LEFT JOIN products AS p
	ON oi.product_id = p.product_id
;

SELECT * FROM vw_kpis_store;


CREATE VIEW vw_kpis_employees
AS
SELECT
	en.employee_name,
	o.employee_id,
	hit_kpis(
		COUNT(DISTINCT o.order_id),
		COUNT(DISTINCT CASE WHEN p.product_type ='Accessory' THEN o.order_id END),
		(SELECT
			CASE WHEN kpis.kpi_type = 'Accessories Attachment Rate' 
			THEN kpis.kpi_percentage END
			FROM kpis
			WHERE kpis.kpi_type = 'Accessories Attachment Rate' 
			LIMIT 1)
	) AS `Accessories Result`,

	hit_kpis(
		COUNT(DISTINCT o.order_id),
		COUNT(DISTINCT CASE WHEN p.product_type ='Plan' THEN o.order_id END),
		(SELECT 
			CASE WHEN kpis.kpi_type = 'Maintenance Plan Attachment Rate'
			THEN kpis.kpi_percentage END
			FROM kpis
			WHERE kpis.kpi_type = 'Maintenance Plan Attachment Rate'
			LIMIT 1)
	) AS `Plan Result`,

	COUNT(DISTINCT o.order_id) AS `Total Orders`,
	COUNT(DISTINCT CASE WHEN p.product_type ='Accessory' THEN o.order_id END) AS `Total Accessories Sold`,
	COUNT(DISTINCT CASE WHEN p.product_type ='Plan' THEN o.order_id END) AS `Total Plans Sold` 
FROM orders AS o

INNER JOIN employee_names as en
	ON en.employee_id = o.employee_id
INNER JOIN order_items AS oi 
	ON o.order_id = oi.order_id
LEFT JOIN products AS p
	ON oi.product_id = p.product_id
GROUP BY o.employee_id
HAVING `Accessories Result` = 'KPI: failed to meet' AND `Plan Result` = 'KPI: failed to meet'
;

SELECT * FROM vw_kpis_employees;


/* Bit of a problem, I need you to find a customer's details as I need to get in contact with them, 
but I only wrote down their initials.. MB.. 
*/
SELECT cn.customer_name AS `Name`,
	cp.customer_phone_number AS `Number`,
	ce.customer_email AS Email
FROM customer_names AS cn

INNER JOIN customer_phone_numbers AS cp
	ON cn.customer_id = cp.customer_id
INNER JOIN customer_emails AS ce
	ON cp.customer_id = ce.customer_id
WHERE cn.customer_name LIKE 'M% B%'
;


-- We are introducing a new loyalty scheme, I have this list of customers that have signed up, I need you to add this to the database.
CREATE TABLE loyalty(
		customer_id INT,
		loyalty_opt_in BOOL DEFAULT FALSE,
    PRIMARY KEY (customer_id),
    CONSTRAINT fk_loyalty FOREIGN KEY (customer_id)
		REFERENCES customer_names(customer_id)
);

INSERT INTO loyalty (customer_id)
SELECT 
	customer_id
FROM 
	customer_names
;

UPDATE loyalty
SET loyalty_opt_in = TRUE
WHERE customer_id IN ('2', '3', '6', '8', '14', '17', '19')
;


-- I've been contacted by a customer (Olivia Johnson, new no is: 06098765432) who changed her phone number, please can you update this?
UPDATE 
	customer_phone_numbers AS cp
INNER JOIN customer_names AS cn
	ON cn.customer_name = 'Olivia Johnson'
SET cp.customer_phone_number = '06098765432' 
WHERE cn.customer_id = cp.customer_id 
;


-- I need to know what the average order price was over the weekend please
SELECT 
	ROUND(AVG(`Total Price`), 2) AS `Average Weekend Spend`
FROM vw_orders_information AS vw_oi
WHERE vw_oi.`Date` = '2025-09-06' OR '2025-09-07'
;


-- What was our revenue this week?
SELECT 
	FORMAT(ROUND(SUM(`Total Price`), 2), 2) AS Revenue
FROM vw_orders_information AS vw_oi;


-- I have had a customer cancel an order, I need you to remove it from the system, the Order ID was 5.
DELETE
FROM order_items AS oi
WHERE oi.order_id = '5';

DELETE 
FROM orders AS o
WHERE o.order_id = '5'
;


/*I've had a message from the DPO and need to do a GDPR customer data removal.  The customer ID is 19.
I need you to make sure that everything is deleted (not a partial delete) and make this simpler for next time. 
*/
DELIMITER //
CREATE PROCEDURE gdpr_delete(enter_customer_id INT)
BEGIN
START TRANSACTION; 

DELETE oi
	FROM order_items AS oi
	LEFT JOIN orders AS o
	ON oi.order_id = o.order_id
WHERE (oi.order_id = o.order_id) AND (o.customer_id = enter_customer_id);

DELETE
	FROM loyalty AS l
WHERE l.customer_id = enter_customer_id;

DELETE 
	FROM orders AS o
WHERE o.customer_id = enter_customer_id;

DELETE 
	FROM customer_phone_numbers AS cp
WHERE cp.customer_id = enter_customer_id;

DELETE 
	FROM customer_emails AS ce
WHERE ce.customer_id = enter_customer_id;

DELETE
	FROM customer_names AS cn
WHERE cn.customer_id = enter_customer_id;

COMMIT;
END//
DELIMITER ;

CALL gdpr_delete(19);


/*We have some new bikes being added to the range, can you add these in 
and make sure anyone typing in different cases doesn't break future queries?*/
DELIMITER //
CREATE TRIGGER correct_case
BEFORE INSERT ON products
FOR EACH ROW
BEGIN	
SET NEW.product_type = CONCAT(UPPER(SUBSTRING(NEW.product_type, 1, 1)), LOWER(SUBSTRING(NEW.product_type, 2)));    
END//
DELIMITER ;

INSERT INTO products (product_type, product_name)
VALUES ('bikE', 'Gravel3'),
	('BiKE', 'FullSuspension1'),
    ('BikE', 'BMX1'),
    ('BIke', 'BMX2'),
    ('bike', 'Adventure1');
    
SELECT * FROM products AS p
WHERE p.product_type = 'Bike';