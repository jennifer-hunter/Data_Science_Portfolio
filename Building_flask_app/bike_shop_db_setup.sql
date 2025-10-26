CREATE DATABASE bike_shop;

USE bike_shop;

    
CREATE TABLE employee_names(
	employee_id INT AUTO_INCREMENT,
    employee_name VARCHAR(30) NOT NULL,
	PRIMARY KEY (employee_id)
);

CREATE TABLE employee_emails(
	employee_id INT AUTO_INCREMENT,
    employee_email VARCHAR(50),
    PRIMARY KEY (employee_id),
    CONSTRAINT fk_employee_email_id FOREIGN KEY (employee_id) 
    REFERENCES employee_names(employee_id)
);

CREATE TABLE employee_phone_numbers(
	employee_id INT AUTO_INCREMENT,
    employee_phone_number VARCHAR(11) UNIQUE,
    PRIMARY KEY (employee_id),
    CONSTRAINT fk_employee_phone_number_id FOREIGN KEY (employee_id) 
    REFERENCES employee_names(employee_id)
);

CREATE TABLE customer_names(
	customer_id INT AUTO_INCREMENT,
    customer_name VARCHAR(30),
	PRIMARY KEY (customer_id)
);

CREATE TABLE customer_emails(
	customer_id INT AUTO_INCREMENT,
    customer_email VARCHAR(50),
    PRIMARY KEY (customer_id),
    CONSTRAINT fk_customer_email_id FOREIGN KEY (customer_id) 
    REFERENCES customer_names(customer_id)
);

CREATE TABLE customer_phone_numbers(
	customer_id INT AUTO_INCREMENT,
    customer_phone_number VARCHAR(11),
    PRIMARY KEY (customer_id),
    CONSTRAINT fk_customer_phone_number_id FOREIGN KEY (customer_id) 
    REFERENCES customer_names(customer_id)
);


CREATE TABLE products(
	product_id INT AUTO_INCREMENT,
    product_type VARCHAR(20),
    product_name VARCHAR(50) UNIQUE,
    PRIMARY KEY (product_id)
);


CREATE TABLE product_prices(
	product_id INT AUTO_INCREMENT,
    product_price DECIMAL(6,2) NOT NULL,
    PRIMARY KEY (product_id),
	CONSTRAINT fk_product_price FOREIGN KEY (product_id) 
    REFERENCES products(product_id)
);
  

CREATE TABLE orders(
	order_id INT AUTO_INCREMENT,
    customer_id INT NOT NULL,
    order_date DATE NOT NULL,
    employee_id INT NOT NULL,
    PRIMARY KEY (order_id),
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id)
    REFERENCES customer_names(customer_id),
	CONSTRAINT fk_orders_employee FOREIGN KEY (employee_id)
    REFERENCES employee_names(employee_id)
);


CREATE TABLE order_items(
	order_items_id INT AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL,
    PRIMARY KEY (order_items_id),
    CONSTRAINT fk_order_items_orders FOREIGN KEY (order_id)
    REFERENCES orders(order_id),
    CONSTRAINT fk_order_items_product FOREIGN KEY (product_id)
    REFERENCES products(product_id)
);
    
CREATE TABLE kpis(
 		kpi_id INT AUTO_INCREMENT,
		kpi_type VARCHAR(50),
 		kpi_percentage DECIMAL (3,2) DEFAULT '0.3',
 	PRIMARY KEY (kpi_id)
 );
 

INSERT INTO employee_names
VALUES ('1', 'Claire Smith'),
	('2', 'John Richards'), 
	('3', 'Jessica Cooper'), 
	('4', 'Sebastian Clarke'), 
	('5', 'Alice Sykes'), 
	('6', 'Faye Jones'), 
	('7', 'James Wilkinson'),  
	('8', 'Thomas Williams'), 
	('9', 'Gemma Hutchinson'), 
	('10', 'Douglas Cooke'),
    ('11', 'Previous Employee')
;

INSERT INTO employee_emails
VALUES ('1', 'c.smith@email.com'), 
	('2', 'johnrichards@email.com'),
	('3', 'jcoop1990@email.com'),
	('4', 'seb_clark@email.com'),
	('5', 'a.l.sykes@email.com'),
	('6', 'fayejones1@email.com'),
	('7', 'jameswilks230@email.com'),
	('8', 'tw@email.com'), 
	('9', 'g_hutch91@email.com'),
	('10', 'dougcooke123@email.com'),
    ('11', 'None')
; 
 
INSERT INTO employee_phone_numbers
VALUES ('1', '06123456789'),
	('2', '06234567890'), 
	('3', '06274283377'),
	('4', '06825374809'),
	('5', '06127356789'),
	('6', '06789012345'),
	('7', '06765432109'),
	('8', '06987654310'),
	('9', '06123568907'),
	('10', '06372894673'),
    ('11', 'None')
;

INSERT INTO customer_names
VALUES ('1', 'Jane Dawson'),
    ('2', 'James Walker'),
    ('3', 'Sophie Turner'),
    ('4', 'Daniel Harris'),
    ('5', 'Emily Clarke'),
    ('6', 'Thomas Wright'),
    ('7', 'Olivia Johnson'),
    ('8', 'George Evans'),
    ('9', 'Charlotte Brown'),
    ('10', 'Henry Cooper'),
    ('11', 'Amelia Davis'),
    ('12', 'Matthew Baker'),
    ('13', 'Lucy Parker'),
    ('14', 'Benjamin Forder'),
    ('15', 'Isabelle Hall'),
    ('16', 'Edward Mitchell'),
    ('17', 'Grace Phillips'),
    ('18', 'William Carter'),
    ('19', 'Hannah Ward'),
    ('20', 'Sam Bennett')
;


INSERT INTO customer_emails
VALUES ('1', 'janedawson@email.com'),
    ('2', 'jwalker@email.com'),
    ('3', 'sophie123456@email.com'),
    ('4', 'dan.h2002@email.com'),
    ('5', 'emily_alice_clarke@email.com'),
    ('6', 'wright_tm@email.com'),
    ('7', 'olivia.j@email.com'),
    ('8', 'gevans@email.com'),
    ('9', 'charlotte_brown@email.com'),
    ('10', 'henry.cooper@email.com'),
    ('11', 'amelia.davis@email.com'),
    ('12', 'mattbaker90@email.com'),
    ('13', 'lparks@email.com'),
    ('14', 'ben_foster1982@email.com'),
    ('15', 'isahall123@email.com'),
    ('16', 'eddymitchell@email.com'),
    ('17', 'gkphillips@email.com'),
    ('18', 'willcarter29@email.com'),
    ('19', 'hanna_.ward@email.com'),
    ('20', 's.bennett@email.com')
;

INSERT INTO customer_phone_numbers
VALUES  ('1', '0612345678'),
    ('2', '0623456789'),
    ('3', '0634567890'),
    ('4', '0645678901'),
    ('5', '0656789012'),
    ('6', '0667890123'),
    ('7', '0678901234'),
    ('8', '0689012345'),
    ('9', '0690123456'),
    ('10', '0611234567'),
    ('11', '0622345678'),
    ('12', '0633456789'),
    ('13', '0644567890'),
    ('14', '0655678901'),
    ('15', '0666789012'),
    ('16', '0677890123'),
    ('17', '0688901234'),
    ('18', '0699012345'),
    ('19', '0610123456'),
    ('20', '0621234567')
;

INSERT INTO products
VALUES ('1', 'Bike', 'Gravel1'),
	('2', 'Bike', 'Road1'),
	('3', 'Bike', 'Hybrid1'),
    ('4', 'Bike', 'Mountain1'),
	('5', 'Bike', 'Gravel2'),
	('6', 'Bike', 'Road2'),
	('7', 'Bike', 'Hybrid2'),
	('8', 'Bike', 'Mountain2'),
	('9', 'Plan', 'Bronze'),
	('10', 'Plan', 'Silver'),
	('11', 'Plan', 'Gold'),
	('12', 'Accessory', 'Track Pump'),
	('13', 'Accessory', 'Hand Pump'),
	('14', 'Accessory', 'Pannier Rack'),
	('15', 'Accessory', 'Pannier Bag'),
	('16', 'Accessory', 'Lights'),
	('17', 'Accessory', 'D Lock'),
	('18', 'Accessory', 'Cable Lock'),
	('19', 'Accessory', 'Helmet1'),
	('20', 'Accessory', 'Helmet2'),
	('21', 'Accessory', 'Jacket'),
	('22', 'Accessory', 'Grips')
;

INSERT INTO product_prices
VALUES ('1', '545.00'),
	('2', '435.00'),
	('3', '385.00'),
    ('4', '750.00'),
	('5', '1350.00'),
	('6', '1999.00'),
	('7', '600.00'),
	('8', '1050.00'),
	('9', '30.00'),
	('10', '60.00'),
	('11', '85.00'),
	('12', '22.00'),
	('13', '8.50'),
	('14', '34.99'),
	('15', '30.00'),
	('16', '15.00'),
	('17', '35.00'),
	('18', '16.00'),
	('19', '49.99'),
	('20', '249.99'),
	('21', '21.99'),
	('22', '5.00')
;

INSERT INTO orders
VALUES ('1', '3', '2025-09-01', '1'),
	('2', '3', '2025-09-01', '6'),
	('3', '6', '2025-09-01', '2'),
	('4', '20', '2025-09-01', '10'),
	('5', '2', '2025-09-02', '9'),
	('6', '4', '2025-09-02', '9'),
	('7', '8', '2025-09-02', '2'),
	('8', '5', '2025-09-02', '8'),
	('9', '19', '2025-09-02', '3'),
	('10', '18', '2025-09-03', '4'),
	('11', '16', '2025-09-03', '2'),
	('12', '17', '2025-09-03', '1'),
	('13', '1', '2025-09-04', '2'),
	('14', '19', '2025-09-04', '10'),
	('15', '11', '2025-09-05', '7'),
	('16', '12', '2025-09-06', '6'),
	('17', '13', '2025-09-06', '1'),
	('18', '14', '2025-09-06', '3'),
	('19', '10', '2025-09-06', '5'),
	('20', '2', '2025-09-06', '8'),
	('21', '3', '2025-09-06', '9'),
	('22', '7', '2025-09-06', '1'),
	('23', '8', '2025-09-06', '2'),
	('24', '1', '2025-09-06', '10'),
	('25', '9', '2025-09-06', '7'),
	('26', '15', '2025-09-07', '2'),
	('27', '15', '2025-09-07', '4'),
	('28', '7', '2025-09-07', '7'),
	('29', '19', '2025-09-07', '9'),
	('30', '4', '2025-09-07', '1')
;


INSERT INTO order_items
VALUES ('1', '1', '9', '1'),
	('2', '1', '12', '1'),
	('3', '1', '20', '1'),
	('4', '2', '4', '1'),
	('5', '2', '22', '1'),
	('6', '3', '3', '1'),
	('7', '3', '7', '1'),
	('8', '3', '11', '1'),
	('9', '3', '12', '1'),
	('10', '3', '20', '1'),
	('11', '3', '17', '2'),
	('12', '3', '21', '3'),
	('13', '4', '4', '2'),
	('14', '4', '6', '1'),
	('15', '4', '12', '1'),
	('16', '4', '16', '3'),
	('17', '5', '14', '1'),
	('18', '5', '15', '1'),
	('19', '6', '18', '1'),
	('20', '6', '20', '1'),
	('21', '7', '21', '3'),
	('22', '8', '15', '2'),
	('23', '9', '1', '1'),
	('24', '9', '2', '1'),
	('25', '9', '3', '1'),
	('26', '10', '8', '1'),
	('27', '10', '6', '1'),
	('28', '11', '11', '1'),
	('29', '12', '13', '4'),
	('30', '12', '11', '1'),
	('31', '13', '9', '1'),
	('32', '14', '6', '1'),
	('33', '15', '1', '1'),
	('34', '15', '16', '1'),
	('35', '15', '17', '1'),
	('36', '15', '18', '2'),
	('37', '15', '19', '3'),
	('38', '15', '20', '4'),
	('39', '16', '11', '3'),
	('40', '16', '8', '2'),
	('41', '17', '8', '1'),
	('42', '17', '21', '1'),
	('43', '17', '14', '1'),
	('44', '18', '8', '3'),
	('45', '19', '11', '4'),
	('46', '20', '11', '1'),
	('47', '20', '14', '1'),
	('48', '20', '22', '2'),
	('49', '21', '18', '4'),
	('50', '21', '16', '5'),
	('51', '22', '7', '2'),
	('52', '23', '4', '2'),
	('53', '23', '1', '1'),
	('54', '23', '5', '1'),
	('55', '23', '11', '4'),
	('56', '23', '13', '4'),
	('57', '23', '17', '8'),
	('58', '23', '20', '2'),
	('59', '24', '8', '1'),
	('60', '24', '10', '1'),
	('61', '25', '1', '1'),
	('62', '25', '4', '1'),
	('63', '26', '17', '1'),
	('64', '27', '19', '2'),
	('65', '28', '5', '1'),
	('66', '28', '6', '1'),
	('67', '28', '9', '1'),
	('68', '28', '13', '1'),
	('69', '29', '11', '2'),
	('70', '30', '7', '1'),
	('71', '30', '21', '2'),
	('72', '30', '17', '2'),
	('73', '30', '16', '2')
;

INSERT INTO kpis (kpi_id, kpi_type, kpi_percentage)
VALUES ('1', 'Accessories Attachment Rate', '0.75'),
 ('2', 'Maintenance Plan Attachment Rate', DEFAULT)
 ;
 
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


CREATE VIEW vw_orders_information AS    
SELECT c.customer_name as Customer,
	c.customer_id AS `Customer ID`,
	oi.order_id AS `Order Number`,
	GROUP_CONCAT(CONCAT(p.product_name, ': ', oi.quantity, ' at ', pp.product_price)
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
