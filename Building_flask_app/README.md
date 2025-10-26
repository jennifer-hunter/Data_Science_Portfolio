# Bike Shop Management API

### Author: Jennifer Hunter

A Flask REST API with command-line client for managing bike shop operations, including employee
performance tracking, order creation, and employee data management.

## Features
- REST API endpoints for operations on orders and employees
- View employee sales performance by tracking their orders
- Create new orders via POST requests with JSON payloads
- Delete employee data with database integrity handling
- Command-line client interface with tabulated output
- Database utility layer for MySQL interactions

## Setup
- Run `bike_shop_db_setup.sql` to create the database and populate with sample data
- Update `config.py` with your MySQL credentials
- Install dependencies: `pip install flask requests tabulate mysql-connector-python`
- Start the Flask server: `python app.py` (runs on port 5004)
- Run the client interface: `python client_side.py`

## API Endpoints
- `GET /` - Health check
- `GET /<employee>` - View orders by employee name
- `GET /employee_list` - Fetch all employees
- `POST /new_order` - Create new order
- `GET /view_new_order/<order_id>` - View newly created order
- `DELETE /employee_data_for_<employee_id>` - Remove employee data

## Notes
- Client-side interface demonstrates API consumption with requests library
- Uses tabulate for formatted console output
- Database layer separated into `db_utils.py` for modularity
- All data is fictitious and generated for demonstration purposes only
- Any resemblance to real persons, businesses, or entities is purely coincidental
