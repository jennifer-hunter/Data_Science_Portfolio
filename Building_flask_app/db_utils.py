import mysql.connector
from mysql.connector.errors import IntegrityError #this error can be raised to let the user know they have entered invalid information to the DB (rather than generic error)
from config import USER, PASSWORD, HOST  #imports the user's credentials

#creates a general exception that can handle db connection errors
class ConnectionErrorDb(Exception):
    pass


def _connect_to_db(db_name):
    '''This function connects to the DB and takes the database name as an argument
    '''
    cnx = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        auth_plugin='mysql_native_password',
        database=db_name
    )
    return cnx


def view_orders(employee):
    '''This function queries the DB for pertinent information on order by a specified employee'''
   #a try block is used to attempt to connect to the db and submit a query
    try:
        db_name = "bike_shop"
        db_connection = _connect_to_db(db_name)
        cursor = db_connection.cursor()
        print(f"Successful connection to {db_name} database")

        # the %s parameterises the user inputted information to prevent SQL injection
        query = """SELECT `Items`,
         `Total Price`,
         `Date`
         FROM vw_orders_information 
         WHERE `Sold By` = %s"""

        #the cursor executes the above SQL query and inserts the parameter
        cursor.execute(query, (employee,))
        #the information is fetched from the DB
        orders = cursor.fetchall()
        #the cursor is closed to prevent a leak
        cursor.close()
        #the order information is returned
        return orders

    # if the employee_id doesn't match one within the DB an integrity error is raised to let the user know they entered invalid information
    except IntegrityError:
        print("DB Integrity Error: Please enter valid information")
    #raises a general error for syntax or connection issues
    except Exception:
        raise ConnectionErrorDb("Connection to database failed!")

    #this block will always run, it closes the database connection
    finally:
        if db_connection:
            db_connection.close()
            print("closed connection to database")


def fetch_employee_list():
    '''This function retrieves the current list of employees from the DB'''
    try:
        db_name = "bike_shop"
        db_connection = _connect_to_db(db_name)
        cursor = db_connection.cursor()
        print(f"Successful connection to {db_name} database")

        query = """SELECT employee_id, 
        employee_name 
        FROM employee_names
        WHERE employee_id <> 11"""

        cursor.execute(query)
        employee_list = cursor.fetchall()
        cursor.close()
        return employee_list

    except Exception:
        raise ConnectionErrorDb("Connection to database failed!")

    finally:
        if db_connection:
            db_connection.close()
            print("Closed connection to database")


def create_order(order_info):
    '''This function takes the payload of order information and then passes this to the SQL query1
     (populates orders table), the new order_id is saved and passed to query2 to populate the order_items table'''
    try:
        db_name = "bike_shop"
        db_connection = _connect_to_db(db_name)
        cursor = db_connection.cursor()
        print(f"Successful connection to {db_name} database")

    # the '%s' parameterises the user input to the query to prevent SQL injection.
        query1 = """INSERT INTO orders (customer_id, order_date, employee_id)
            VALUES (%(customer_id)s, %(order_date)s, %(employee_id)s)"""

        cursor.execute(query1, order_info)

        #this captures the last row id entered into the DB
        order_id = cursor.lastrowid
        # the new order_id is saved to the dict
        order_info.update({"order_id":order_id})
            
        query2 = """INSERT INTO order_items (order_id, product_id, quantity)
        VALUES (%(order_id)s, %(product_id)s, %(quantity)s)"""

        cursor.execute(query2, order_info)
        # since the DB is being updated a .commit() is needed.
        db_connection.commit()
        cursor.close()

        return order_id

    # raises an error if information inputted by the user doesn't match the DB (e.g. a customer_id that doesn't exist)
    except IntegrityError:
        print("DB Integrity Error: Please enter valid information")

    # a catch-all exception that raises an error due to connection issues or syntax errors.
    except Exception:
        raise ConnectionErrorDb("Connection to database failed!")

    finally:
        if db_connection:
            db_connection.close()
            print("Closed connection to database")



def retrieve_new_order(order_id):
    '''This function takes the newly created order_id and returns the new order information'''
    try:
        db_name = "bike_shop"
        db_connection = _connect_to_db(db_name)
        cursor = db_connection.cursor()
        print(f"Successful connection to {db_name} database")

        query = """SELECT *
         FROM vw_orders_information 
         WHERE `Order Number` = %s"""

        cursor.execute(query, (order_id,))
        new_order_info = cursor.fetchall()

        cursor.close()
        return new_order_info

    except Exception:
        raise ConnectionErrorDb("Connection to database failed!")

    finally:
        if db_connection:
            db_connection.close()
            print("closed connection to database")


def remove_employee_data(employee_to_delete_id):
    '''This function takes an employee_id and then removes all their information from the DB.
    Where their name is attached to an order it reassigns it to a new ID with name "Previous Employee"'''
    try:
        db_name = "bike_shop"
        db_connection = _connect_to_db(db_name)
        cursor = db_connection.cursor()
        print(f"Successful connection to {db_name} database")

        # this query reassigns the employee_id to 11 (previous employee code)
        query0 = """UPDATE orders
        SET employee_id = 11
        WHERE employee_id = %s"""

        # the next few queries then remove the employee data from child tables up to parent.
        query1 = """DELETE
        FROM employee_emails
        WHERE employee_id = %s"""
        
        query2 = """DELETE 
        FROM employee_phone_numbers
        WHERE employee_id = %s"""
        
        query3 = """DELETE
        FROM employee_names
        WHERE employee_id = %s"""


        cursor.execute(query0, (employee_to_delete_id,))
        cursor.execute(query1, (employee_to_delete_id,))
        cursor.execute(query2, (employee_to_delete_id,))
        cursor.execute(query3, (employee_to_delete_id,))

        db_connection.commit()

        cursor.close()

    except Exception:
        raise ConnectionErrorDb("Connection to database failed!")

    finally:
        if db_connection:
            db_connection.close()
            print("Closed connection to database")


