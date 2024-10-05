
from flask import Flask, request, jsonify

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId


import certifi



app = Flask(__name__)

uri = "mongodb+srv://cdc236:bigredhacksken@clusterbigredhacks.rohyu.mongodb.net/?retryWrites=true&w=majority&appName=ClusterBigRedHacks"

# Create a new client and connect to the server
client = MongoClient(uri, tlsCAFile=certifi.where(), server_api=ServerApi('1'))
db = client["YarnDatabase"]
users_collection = db["UsersTable"]
entries_collection = db["EntriesTable"]

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


@app.route("/")
def home():
    return "Welcome to Yarn"


@app.route("/createUser", methods=['POST'])
def create_user():
    try:
        data = request.get_json()  # Get the data from the POST request
        result = users_collection.insert_one(data)  # Insert the journal entry into the collection
        return jsonify({"message": "User added", "id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/createEntry', methods=['POST'])
def create_entry():
    try:
        data = request.get_json()  # Get the data from the POST request
        result = entries_collection.insert_one(data)  # Insert the journal entry into the collection
        return jsonify({"message": "Journal entry added", "id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/getEntry', methods=['GET'])
def get_entry():
    data = request.get_json()  # Get the JSON data from the request body
    if not data or 'entryId' not in data:
        return jsonify({"error": "entryId is required"}), 400  # Return 400 if entry_id is missing
    
    entry_id = data['entryId']  # Extract the entry_id from the request data
    
    try:
        entry = entries_collection.find_one({"_id": ObjectId(entry_id)})
        
        if entry:
            entry['_id'] = str(entry['_id'])  # Convert ObjectId to string for JSON serialization
            return jsonify(entry['entry']), 200  # Return the entry data
        else:
            return jsonify({"error": "Entry not found"}), 404  # Return 404 if the entry doesn't exist
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Handle other errors


@app.route('/getEntriesByUserAndDate', methods=['GET'])
def get_entries_by_user_and_date():
    data = request.get_json()
        
    user_id = data['userId']
    date = data['date']
    if not user_id or not date:
        return jsonify({"error": "Both userId and date are required"}), 400  # Return 400 if either is missing

    try:
        # Find all entries that match the provided userId and date
        entries = entries_collection.find({"userId": user_id, "date": date})
        
        # Convert the entries to a list and ensure _id is a string
        entries_list = []
        for entry in entries:
            entry['_id'] = str(entry['_id'])
            entries_list.append(entry['entry'])
        
        if entries_list:
            return jsonify(entries_list), 200  # Return the entries data
        else:
            return jsonify({"error": "No entries found for the specified user and date"}), 404  # Return 404 if no entries are found
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Handle other errors


if __name__ == "__main__":
    app.run(port=8000, debug=True)


