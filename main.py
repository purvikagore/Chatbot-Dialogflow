# Author: Dhaval Patel. Codebasics YouTube Channel

from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper
import re

app = FastAPI()

inprogress_orders = {}
n = 0 
@app.post("/")
async def handle_request(request: Request):
    # Retrieve the JSON data from the request
    payload = await request.json()

    # Extract the necessary information from the payload
    # based on the structure of the WebhookRequest from Dialogflow
  
    intent = payload['queryResult']['intent']['displayName']
    parameters = payload['queryResult']['parameters']
    output_context = payload['queryResult']['outputContexts']
    print(intent)
    
    
    session_id = generic_helper.extract_session_id(output_context[0]['name'])

    if intent == 'new.order':
        if session_id in inprogress_orders:
            del inprogress_orders[session_id] 
        intent = 'order.add context:ongoing'

    intent_handler_dict = {
        'order.add context:ongoing': add_to_order,
        'order.remove context:ongoing': remove_from_order,
        'order.complete context:ongoing': complete_order,
        'track.order context:ongoing': track_order
    }
    
    return intent_handler_dict[intent](parameters, session_id)






def add_to_order(parameters:dict, session_id:str):
    # print("yo")
    food_items = parameters['food_items']
    quantities = parameters['number']
    
    # session_id1 = generic_helper.extract_session_id(output_context[0]['name'])
    # if session_id1!=session_id:
    #     add_to_order(parameters, session_id1)
    if len(food_items) != len(quantities): 
        fulfillment_text = "Sorry could not understand. Please specify number along with the food item."
    
    else:

        new_food_dict = dict(zip(food_items,quantities))
        
        if session_id in inprogress_orders:
            # print(session_id)
            # print(inprogress_orders)
            current_food_dict = inprogress_orders[session_id]
            current_food_dict.update(new_food_dict)
            inprogress_orders[session_id] = current_food_dict
            
            
        else:
            inprogress_orders[session_id] = new_food_dict

        order_str = generic_helper.get_str_from_food_dict(inprogress_orders[session_id])

        fulfillment_text = f"So far you have {order_str}. Do you need anything else?"

    return JSONResponse(content = {
        "fulfillmentText": fulfillment_text
    })



def track_order(parameters:dict, session_id :str):
    order_id = int(parameters['order-id'])
    order_status = db_helper.get_order_status(order_id)
    if order_status:
        fulfillment_text = f"The order status for order id: {order_id} is: {order_status}"
    else:
        fulfillment_text = f"No order found with order id: {order_id}"

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })


def complete_order(parameters:dict, session_id :str):
    if session_id not in inprogress_orders:
        fulfillment_text = "I am hvaing trouble finding your order. Could you place another order?"
    else:
        order = inprogress_orders[session_id]
        order_id = save_to_db(order)

        if order_id == -1:
            fulfillment_text = "Sorry. Repeat your order again lmao"
    
        else:
            order_total = db_helper.get_total_order_price(order_id)
            fulfillment_text = f"We have placed your order yeet. \n Here is your order id {order_id}. \n YOur order total is {order_total} which you can pay at the time of your delivery!"


        del inprogress_orders[session_id]
    return JSONResponse(content={
        "fulfillmentText":fulfillment_text
    })


# we just need max + 1 to get next order id
def save_to_db(order:dict):

    # order : {"pizza":1, "chhole":2}

    next_order_id = db_helper.get_next_order_id()

    for food_item, quantity in order.items():
        rcode = db_helper.insert_order_item(
            food_item,
            quantity,
            next_order_id
        )

        if rcode == -1:
            return -1

    db_helper.insert_order_tracking(next_order_id,"in progres")

    return next_order_id


# step-1 : locate session id
# strep-2: get te value from the dictionary
# step-3: remove the food items. request : ['vada paav','pizza']

def remove_from_order(parameters, session_id):
    if session_id not in inprogress_orders:
        return JSONResponse(content = {
            "fulfillmentText": "I am having trouble finding your order"
        })
    
    
    food_items = []
    food_items.append(parameters['food_items'])
    #print(food_items)
    current_order = inprogress_orders[session_id]
    #print(current_order)
    
    removed_items = []
    no_such_items = []


    for item in food_items:
        # #print(item)
        if item not in current_order:
            no_such_items.append(item)
        else:
            removed_items.append(item)
            del current_order[item]

    if len(removed_items) > 0:
        fulfillment_text = f'Removed {",".join(removed_items)} from your order!'

    if len(no_such_items) > 0:
        # fulfillment_text = f' Your current order does not have {",".join(no_such_items)}'
        fulfillment_text = f' Your current order does not have {(no_such_items)}'

    if len(current_order.keys()) == 0:
        fulfillment_text += " Your order is empty!"
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text += f" Here is what is left in your order: {order_str}"

    

    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })
