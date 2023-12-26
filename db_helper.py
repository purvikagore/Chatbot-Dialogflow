import mysql.connector
global cnx

cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Root@123",
    database="pandeyji_eatery"
)



def get_next_order_id():
    cursor = cnx.cursor()

    query = "SELECT MAX(order_id) FROM orders"
    cursor.execute(query)

    result = cursor.fetchone()[0]

    cursor.close()

    if result is None:
        return 1
    else:
        return result + 1



# Function to fetch the order status from the order_tracking table
def get_order_status(order_id   ):
    
    cursor = cnx.cursor()

    # Executing the SQL query to fetch the order status
    query = f"SELECT status FROM order_tracking WHERE order_id = {order_id}"
    # #print(query)
    # query = (f"SELECT status FROM order_tracking WHERE order_id = {order_id}")

    # cursor.execute(query, (order_id,))
    
    cursor.execute(query)
    # Fetching the result
    result = cursor.fetchone()
    #print(result)

    # Closing the cursor
    cursor.close()

    if result is not None:
        return result[0]
    else:
        return None


def insert_order_item(food_item, quantity, order_id):

    try:
        cursor = cnx.cursor()

        cursor.callproc('insert_order_item',(food_item, quantity, order_id))

        cnx.commit()

        cursor.close()

        #print("Order item inserted successfully")

        return 1

    except mysql.connector.Error as err:
        #print(f"Error inserting order item : {err}")

        cnx.rollback()

        return -1
    
    except Exception as e:
        #print(f"An error occurred: {e}")

        cnx.rollback()

        return -1


def get_total_order_price(order_id):
    cursor = cnx.cursor()

    query = f"SELECT get_total_order_price({order_id})"
    cursor.execute(query)

    result = cursor.fetchone()[0]

    cursor.close()

    return result


def insert_order_tracking(order_id, status):
    cursor = cnx.cursor()

    insert_query = "INSERT INTO order_tracking (order_id, status) VALUES (%s,%s)"
    cursor.execute(insert_query,(order_id,status))

    cnx.commit()

    cursor.close()


# if __name__ == '__main__':
#     #print(get_str_from_food_dict({'samosa':2, 'chhole':5}))
#     #print(extract_session_id("projects/pupu-chatbot-food-deliver-luju/agent/sessions/acd987d9-fb07-237d-1c51-3b45e5716544/contexts/ongoing-order"))
    
