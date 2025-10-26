from flask import Flask, jsonify, request
from db_utils import view_orders, fetch_employee_list, remove_employee_data, create_order, retrieve_new_order


app = Flask(__name__)

#This app.route is there to serve as an easy way to check the server is running
@app.route("/")
def hello():
    return jsonify("Welcome: to the management system")

#This takes the employee name from the client side and then runs the appropriate function from db_utils to execute the query
@app.route("/<employee>")
def get_orders(employee):
    orders = view_orders(employee)
    return jsonify(orders)

#This gets the current employee list from the DB
@app.route("/employee_list")
def get_employee_list():
    employee_list = fetch_employee_list()
    return jsonify(employee_list)

#This has two methods, DELETE to remove the selected employee's data and PUT to reassign existing data to prevent foreign key errors
@app.route("/employee_data_for_<int:employee_to_delete_id>", methods=["DELETE", "PUT"])
def delete_employee_data(employee_to_delete_id):
    employee_to_delete_data = remove_employee_data(employee_to_delete_id)
    return jsonify(employee_to_delete_data)

#This POSTs a new order (via a payload) to the DB and returns that new order's ID
@app.route('/new_order', methods=['POST'])
def new_order():
    order_info = request.get_json()
    order_id = create_order(order_info)
    return jsonify({"order_id": order_id}), 201

# This uses the new order_id to show the user that the new order has been successfully posted.
@app.route("/view_new_order/<int:order_id>")
def fetch_new_order(order_id):
    new_order_info = retrieve_new_order(order_id)
    return jsonify(new_order_info)



if __name__ == '__main__':
    app.run(debug=True, port=5004)