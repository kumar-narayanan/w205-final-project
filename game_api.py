#!/usr/bin/env python
import json
from kafka import KafkaProducer
from flask import Flask, request

app = Flask(__name__)
producer = KafkaProducer(bootstrap_servers='kafka:29092')

def log_to_kafka(topic, event):
    event.update(request.headers)
    producer.send(topic, json.dumps(event).encode())

@app.route("/")
def default_response():
    default_event = {'user_id': 'None', 'event_type': 'None', 'item': 'None', 'desc': 'None'}
    log_to_kafka('events', default_event)
    return "Welcome to Online Games, agitated_darwin : join the guild and buy interesting items !\n"

# For all purchases default user id is 'agitated_darwin' if query parameter uid is not specified.
# Invocation: curl http://localhost:5000/purchase_sword?uid=<user1>

@app.route("/purchase_sword")
def purchase_sword():
    user_id = request.args.get('uid')
    if (user_id is None):
        user_id = "agitated_darwin"
    purchase_event = {'user_id': user_id, 'event_type': 'buy', 'item': 'sword', 'desc': 'None'}
    log_to_kafka('events', purchase_event) 
    return "Sword Purchased - you bought a Samurai Sword!\n"

@app.route("/purchase_knife")
def purchase_knife():
    user_id = request.args.get('uid')
    if (user_id is None):
        user_id = "agitated_darwin"
    purchase_event = {'user_id': user_id, 'event_type': 'buy', 'item': 'knife', 'desc': 'None'}
    log_to_kafka('events', purchase_event)
    return "Knife Purchased - you bought a Forged Knife!\n"

@app.route("/purchase_crossbow")
def purchase_crossbow():
    user_id = request.args.get('uid')
    if (user_id is None):
        user_id = "agitated_darwin"
    purchase_event = {'user_id': user_id, 'event_type': 'buy', 'item': 'crossbow', 'desc': 'None'}
    log_to_kafka('events', purchase_event)
    return "Crossbow Purchased - you bought a Rifle Crossbow!\n"

@app.route("/join_guild", methods = ['POST'])
# Invocation: curl -d "name=name&uid=user1&email=user3@xyz.com" -X POST http://localhost:5000/join_guild
def join_guild():
    if request.method == 'POST':
        user_name = request.form.get('name')
        user_id = request.form.get('uid')
        email_id = request.form.get('email')
        if (user_name is None or user_id is None or email_id is None):
            join_event = {'user_id': 'None', 'event_type': 'failed_guild', 'item': 'None', 'desc': 'missing user parameters'}
            return_msg = "Failed to join the guild, missing user parameters -  user_name, user_id, or email_id"
        else:
            join_event = {'user_id': user_id, 'event_type': 'join_guild', 'item': 'NA', 'desc': user_name + ':' + email_id}
            return_msg = "Welcome to the guild... join succesful for " + user_name
    else:
        join_event = {'user_id': 'None', 'event_type': 'failed_guild', 'item': 'None', 'desc': 'None'}
        return_msg = "Failed to join the guild, incorrect HTTP method - must be POST"
        
    log_to_kafka('events', join_event)
    return return_msg + "!\n"

@app.route("/delete_item")
# Invocation: curl http://localhost:5000/delete_item?uid=<user1>\&item=crossbow
# curl http://localhost:5000/delete_item?item=crossbow
# If uid parameter is skipped then the deafult will be set to agitated_darwin.
def delete_item():
    user_id = request.args.get('uid') 
    if (user_id is None):
        user_id = "agitated_darwin"
    item = request.args.get('item')
    if (item is None):
        del_event = {'user_id': user_id, 'event_type': 'fail_delete', 'item': 'NA', 'desc': 'missing item'}
        return_msg = "Failed to delete items in cart, missing item"
    else:
        del_event = {'user_id': user_id, 'event_type': 'delete', 'item': item, 'desc': 'NA'}
        return_msg = "Deleted from your cart item: " + item

    log_to_kafka('events', del_event)
    return return_msg + "!\n"

@app.route("/sell_item")
# Invocation: curl http://localhost:5000/sell_item?uid=<user1>\&item=crossbow
# If uid parameter is skipped then the deafult will be set to agitated_darwin.
def sell_item():
    user_id = request.args.get('uid') 
    if (user_id is None):
        user_id = "agitated_darwin"
    item = request.args.get('item')
    if (item is None):
        sell_event = {'user_id': user_id, 'event_type': 'fail_sell', 'item': 'NA', 'desc': 'missing item'}
        return_msg = "Failed to sell items in cart, missing item"
    else:
        sell_event = {'user_id': user_id, 'event_type': 'sell', 'item': item, 'desc': 'None'}
        return_msg = "Sold your item: " + item

    log_to_kafka('events', sell_event)
    return return_msg + "!\n"

@app.route("/play_game")
# Invocation: curl http://localhost:5000/play_game?uid=<user1>\&weapon=<sword|knife|crossbow>
# If uid parameter is skipped then the deafult will be set to agitated_darwin.
# If weapon parameter is skipped then the deafult will be set to sword.
def play_game():
    user_id = request.args.get('uid') 
    if (user_id is None):
        user_id = "agitated_darwin"
    weapon = request.args.get('weapon') 
    if (weapon is None):
        weapon = "sword"
    game_event = {'user_id': user_id, 'event_type': 'play_game', 'item': weapon, 'desc': 'None'}
    return_msg = "You played well with " + weapon

    log_to_kafka('events', game_event)
    return return_msg + "!\n"




