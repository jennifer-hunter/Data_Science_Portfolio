import requests
import json
from tabulate import tabulate # this allows tables to be printed in a readable manner

#this gets the current employee list and returns as a json
def get_employee_list():
    result = requests.get(
        "http://127.0.0.1:5004/employee_list"
    )
    return result.json()

#This calls the api using a specific employee_id and returns the order information for that employee only
def get_orders_by_employee(employee):
    result = requests.get(
        "http://127.0.0.1:5004/{}".format(employee)
    )
    return result.json()

#this uses a payload to send to the api to post a new order
def new_order(order_info):
    result = requests.post(
        "http://127.0.0.1:5004/new_order", json=order_info
    )

    return result.json()

#this takes the newly created order ID from the function above and uses it to retrieve the order.
def view_new_order(new_order_id):
    result = requests.get(
        "http://127.0.0.1:5004/view_new_order/{}".format(new_order_id)
    )
    return result.json()

#This sends a particular employee ID to the api to remove from the DB
def delete_employee(employee_id):
    delete_result = requests.delete(
        "http://127.0.0.1:5004/employee_data_for_{}".format(employee_id)
    )
    return delete_result.json()

#This function runs all the client side messages to the user
def run():
    #prints welcome message
    welcome_msg = "BIKE SHOP MANAGEMENT INTERFACE"

    print("=~" * int(len(welcome_msg) / 2))
    print(welcome_msg)
    print("~=" * int(len(welcome_msg) / 2))
    print()


    #runs the employee sales management part of the client side
    monitoring_msg = "MONITOR EMPLOYEE SALES PERFORMANCE"

    print("=*" * int(len(monitoring_msg) / 2))
    print(monitoring_msg)
    print("*=" * int(len(monitoring_msg) / 2))

    #displays the current list of employees to the user
    employee_list = get_employee_list()
    print(tabulate(employee_list))

    # asks the user to input an employee's name and returns their order information pertinent to performance
    employee_orders = get_orders_by_employee(input("Which employee's orders would you like to track?\nEnter employee name (type full name EXACTLY as it appears on the list): "))

    #tabulate allows the information to be presented in a neat table with chosen headers
    print(tabulate(employee_orders, headers=["Orders", "Value (£)", "Date"]))
    print()

    #The following section allows a user to enter a new order to the DB
    order_msg = "NEW ORDERS"

    print("=+" * int(len(order_msg) / 2))
    print(order_msg)
    print("+=" * int(len(order_msg) / 2))

    #informs the user they can only enter existing information and one item currently
    print("Add an order to the system\nNOTE: THIS SYSTEM IS STILL IN DEVELOPMENT\nWhich will only allow entry of an existing customer_id and one item per order.")

    #sets up the variables ready for the payload based on user input
    customer_id = int(input("Enter a customer_id (1-20): "))
    order_date = input("Enter a sale date in YYYY-MM-DD: ")
    employee_id = int(input("Enter an employee_id (1-10): "))
    product_id = int(input("Enter a product_id (1-22): "))
    quantity = int(input("Enter a quantity: "))

    #creates a dictionary based on that information
    order_info = {"customer_id": customer_id,
                   "order_date": order_date,
                   "employee_id": employee_id,
                   "product_id": product_id,
                   "quantity": quantity}

    #passes the payload to the api call
    new_order_id = new_order(order_info)

    #allows the user to view the new order
    view_new_order_answer = (input("Would you like to view the new order? (y/n): "))
    if view_new_order_answer == 'y':
        new_order_info = view_new_order(new_order_id["order_id"])
        print(tabulate(new_order_info, headers=["Customer Name", "Customer ID", "Order ID", "Items: (£)", "Total (£)", "Date", "Sold By"]))
    else:
        pass

    #This next section allows the user to remove an employee's data once they have resigned.
    removal_msg = "REMOVE PREVIOUS EMPLOYEE'S DATA"

    print()
    print("!¬" * int(len(removal_msg) / 2))
    print(removal_msg)
    print("¬!" * int(len(removal_msg) / 2))

    print("Whose data would you like to remove?")

    #fetches a fresh employee list
    print(tabulate(employee_list))

    #asks the user which employee to delete
    delete_employee(input("Which employee_id to delete? (Enter number): "))

    #allows the user to see the new employee list (with removal) if they wish
    answer = (input("Would you like to view the updated list? (y/n): "))
    if answer == 'y':
        print(tabulate(get_employee_list()))
    else:
        pass




if __name__ == '__main__':
    run()