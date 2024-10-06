from flask import Flask, request, jsonify

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from hf import call_llm

import certifi

app = Flask(__name__)

uri = "mongodb+srv://cdc236:bigredhacksken@clusterbigredhacks.rohyu.mongodb.net/?retryWrites=true&w=majority&appName=ClusterBigRedHacks"

# Create a new client and connect to the server
client = MongoClient(uri, tlsCAFile=certifi.where(), server_api=ServerApi('1'))
db = client["YarnDatabase"]
users_collection = db["UsersTable"]
journal_entries_collection = db["JournalEntriesTable"]
feelings_entries_collection = db["FeelingsEntriesTable"]
conversations_collection = db["ConversationsTable"]

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


@app.route('/getUser', methods=['GET'])
def get_user():
    data = request.get_json()  # Get the JSON data from the request body
    if not data or 'userId' not in data:
        return jsonify({"error": "userId is required"}), 400  # Return 400 if entry_id is missing
    
    user_id = data['userId']  # Extract the entry_id from the request data
    
    try:
        entry = journal_entries_collection.find_one({"_id": ObjectId(user_id)})
        
        if entry:
            entry['_id'] = str(entry['_id'])  # Convert ObjectId to string for JSON serialization
            return jsonify(entry['name']), 200  # Return the entry data
        else:
            return jsonify({"error": "Entry not found"}), 404  # Return 404 if the entry doesn't exist
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Handle other errors


@app.route('/createJournalEntry', methods=['POST'])
def create_journal_entry():
    try:
        data = request.get_json()  # Get the data from the POST request
        result = journal_entries_collection.insert_one(data)  # Insert the journal entry into the collection
        return jsonify({"message": "Journal entry added", "id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/getJournalEntry', methods=['GET'])
def get_journal_entry():
    data = request.get_json()  # Get the JSON data from the request body
    if not data or 'journalEntryId' not in data:
        return jsonify({"error": "entryId is required"}), 400  # Return 400 if entry_id is missing
    
    journal_entry_id = data['journalEntryId']  # Extract the entry_id from the request data
    
    try:
        entry = journal_entries_collection.find_one({"_id": ObjectId(journal_entry_id)})
        
        if entry:
            entry['_id'] = str(entry['_id'])  # Convert ObjectId to string for JSON serialization
            return jsonify(entry['entry']), 200  # Return the entry data
        else:
            return jsonify({"error": "Entry not found"}), 404  # Return 404 if the entry doesn't exist
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Handle other errors


@app.route('/updateJournalEntry', methods=['PUT'])
def update_journal_entry():
    data = request.get_json()  # Get the updated data from the request body

    journal_entry_id = data['journalEntryId']
    updated_entry = data['updatedEntry']
    if not data or not journal_entry_id or not updated_entry:
        return jsonify({"error": "No data provided for update"}), 400  # Return 400 if no data is provided
    
    try:
        # Find the journal entry by _id and update with new data
        result = journal_entries_collection.update_one(
            {"_id": ObjectId(journal_entry_id)},  # Find entry by _id
            {"$set": { 'entry': updated_entry }}  # Set the updated fields
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "Entry not found"}), 404  # Return 404 if entry not found
        
        return jsonify({"message": "Entry updated successfully"}), 200  # Return success message
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Handle other errors


@app.route('/deleteJournalEntry', methods=['DELETE'])
def delete_journal_entry():
    data = request.get_json()  # Get the data from the request body

    # Ensure that '_id' is provided in the data
    journal_entry_id = data['journalEntryId']
    if not data or not journal_entry_id:
        return jsonify({"error": "Entry ID is required"}), 400  # Return 400 if no _id is provided

    try:
        # Find the journal entry by _id and delete it
        result = journal_entries_collection.delete_one({"_id": ObjectId(journal_entry_id)})
        
        if result.deleted_count == 0:
            return jsonify({"error": "Entry not found"}), 404  # Return 404 if no entry was found
        
        return jsonify({"message": "Entry deleted successfully"}), 200  # Return success message
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Handle other errors


@app.route('/getJournalEntriesByUserAndDate', methods=['GET'])
def get_journal_entries_by_user_and_date():
    data = request.get_json()
        
    user_id = data['userId']
    date = data['date']
    if not user_id or not date:
        return jsonify({"error": "Both userId and date are required"}), 400  # Return 400 if either is missing

    try:
        # Find all entries that match the provided userId and date
        entries = journal_entries_collection.find({"userId": user_id, "date": date})
        
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


@app.route('/getAllJournalEntries', methods=['GET'])
def get_journal_entries():
    try:
        # Find all journal entries
        entries = journal_entries_collection.find()
        
        # Convert the entries to a list and ensure _id is a string
        entries_list = []
        for entry in entries:
            entry['_id'] = str(entry['_id'])
            entries_list.append({
                "id": entry['_id'],
                "content": entry['content'],
                "title": entry['title'],  # Assuming 'title' exists in your entries
                "date": entry['date']     # Assuming 'date' exists in your entries
            })
        
        if entries_list:
            return jsonify(entries_list), 200  # Return the entries data
        else:
            return jsonify({"error": "No entries found"}), 404  # Return 404 if no entries are found
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Handle other errors


@app.route('/createFeelingsEntry', methods=['POST'])
def create_feelings_entry():
    try:
        data = request.get_json()  # Get the data from the POST request
        result = feelings_entries_collection.insert_one(data)  # Insert the journal entry into the collection
        return jsonify({"message": "Feelings entry added", "id": str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/getFeelingsEntry', methods=['GET'])
def get_feelings_entry():
    data = request.get_json()  # Get the JSON data from the request body
    if not data or 'feelingsEntryId' not in data:
        return jsonify({"error": "entryId is required"}), 400  # Return 400 if entry_id is missing
    
    feelings_entry_id = data['feelingsEntryId']  # Extract the entry_id from the request data
    
    try:
        entry = feelings_entries_collection.find_one({"_id": ObjectId(feelings_entry_id)})
        
        if entry:
            entry['_id'] = str(entry['_id'])  # Convert ObjectId to string for JSON serialization
            return jsonify(entry['rating']), 200  # Return the entry data
        else:
            return jsonify({"error": "Entry not found"}), 404  # Return 404 if the entry doesn't exist
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Handle other errors


@app.route('/getFeelingsEntriesByUser', methods=['GET'])
def get_feelings_entries_by_user():
    data = request.get_json()
        
    user_id = data['userId']
    if not user_id:
        return jsonify({"error": "userId is required"}), 400  # Return 400 if either is missing

    try:
        # Find all entries that match the provided userId and date
        entries = feelings_entries_collection.find({"userId": user_id})
        
        # Convert the entries to a list and ensure _id is a string
        entries_list = []
        for entry in entries:
            entry['_id'] = str(entry['_id'])
            entries_list.append(entry['rating'])
        
        if entries_list:
            return jsonify(entries_list), 200  # Return the entries data
        else:
            return jsonify({"error": "No entries found for the specified user and date"}), 404  # Return 404 if no entries are found
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Handle other errors
    

@app.route('/getFeelingsEntriesByUserAndDate', methods=['GET'])
def get_feelings_entries_by_user_and_date():
    data = request.get_json()
        
    user_id = data['userId']
    date = data['date']
    if not user_id or not date:
        return jsonify({"error": "Both userId and date are required"}), 400  # Return 400 if either is missing

    try:
        # Find all entries that match the provided userId and date
        entries = feelings_entries_collection.find({"userId": user_id, "date": date})
        
        # Convert the entries to a list and ensure _id is a string
        entries_list = []
        for entry in entries:
            entry['_id'] = str(entry['_id'])
            entries_list.append(entry['rating'])
        
        if entries_list:
            return jsonify(entries_list), 200  # Return the entries data
        else:
            return jsonify({"error": "No entries found for the specified user and date"}), 404  # Return 404 if no entries are found
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Handle other errors
    

@app.route('/updateFeelingsEntry', methods=['PUT'])
def update_feelings_entry():
    data = request.get_json()  # Get the updated data from the request body

    feelings_entry_id = data['feelingsEntryId']
    updated_rating = data['updatedRating']
    if not data or not feelings_entry_id or not updated_rating:
        return jsonify({"error": "No data provided for update"}), 400  # Return 400 if no data is provided
    
    try:
        # Find the journal entry by _id and update with new data
        result = feelings_entries_collection.update_one(
            {"_id": ObjectId(feelings_entry_id)},  # Find entry by _id
            {"$set": { 'rating': updated_rating }}  # Set the updated fields
        )
        
        if result.matched_count == 0:
            return jsonify({"error": "Entry not found"}), 404  # Return 404 if entry not found
        
        return jsonify({"message": "Entry updated successfully"}), 200  # Return success message
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Handle other errors


@app.route('/deleteFeelingsEntry', methods=['DELETE'])
def delete_feelings_entry():
    data = request.get_json()  # Get the data from the request body

    # Ensure that '_id' is provided in the data
    feelings_entry_id = data['feelingsEntryId']
    if not data or not feelings_entry_id:
        return jsonify({"error": "Entry ID is required"}), 400  # Return 400 if no _id is provided

    try:
        # Find the journal entry by _id and delete it
        result = feelings_entries_collection.delete_one({"_id": ObjectId(feelings_entry_id)})
        
        if result.deleted_count == 0:
            return jsonify({"error": "Entry not found"}), 404  # Return 404 if no entry was found
        
        return jsonify({"message": "Entry deleted successfully"}), 200  # Return success message
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Handle other errors
    
@app.route('/callCompanion', methods=['POST'])
def call_companion():
    data = request.get_json()
    message = data['message']

    if not data or not message:
        return jsonify({"error": "Message is required"}), 400
    
    try:
        instruction = "Respond to this statement empathetically"
        result = call_llm(instruction, message)
        if not result or result == "":
            return jsonify({"error": "LLM did not return a valid result"}), 400
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/sendJournalEntryToCompanion', methods=['POST'])
def send_entry_to_companion():
    data = request.get_json()
    journal_entry_id = data['journalEntryId']

    if not data or not journal_entry_id:
        return jsonify({"error": "journalEntryId is required"}), 400
    
    try:
        entry = journal_entries_collection.find_one({"_id": ObjectId(journal_entry_id)})

        if not entry:
            return jsonify({"error": "Entry not found"}), 404  # Return 404 if the entry doesn't exist
        
        instruction = "Here is a recap of my day: " + entry['content'] + " Please respond empathetically"

        result = call_llm(instruction, "")

        if not result or result == "":
            return jsonify({"error": "LLM did not return a valid result"}), 400

        return jsonify(result), 200  # Return the entry data
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Handle other errors


# @app.route('/createQuestion', methods=['POST'])
# def create_question():
#     try:
#         data = request.get_json()  # Get the data from the POST request
#         result = feelings_entries_collection.insert_one(data)  # Insert the journal entry into the collection
#         return jsonify({"message": "Feelings entry added", "id": str(result.inserted_id)}), 201
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)



















