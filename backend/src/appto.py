from flask import Flask, request, jsonify
from flask_pymongo import PyMongo, ObjectId
# from bson.objectid import ObjectId
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost/pythonreactdb'
mongo = PyMongo(app)

db = mongo.db.users

CORS(app)  # Opcional: permite solicitudes CORS

# create user
@app.route('/users', methods=['POST'])
def createUser():
    inserted_id = db.insert_one({
        'name': request.json['name'],
        'host': request.json['host'],
        'email': request.json['email'],
        'password': request.json['password']
    }).inserted_id
    mostrarId = str(inserted_id)
    print(f"This is a {request.json} {mostrarId}") 
    return jsonify({'_id': mostrarId})

# get users
@app.route('/users', methods = ['GET'])
def getUsers():
    users = []
    for doc in db.find():
        users.append({
            '_id': str(ObjectId(doc['_id'])),
            'name': doc['name'],
            'host': doc['host'],
            'email': doc['email'],
            'password': doc['password']

        })
    return jsonify(users)
   

# get a single user
@app.route('/users/<_id>', methods = ['GET'])
def getSigngleUser(_id):
    user = db.find_one({'_id': ObjectId(_id)})
    print(user)
    if (user):
        return jsonify({
        '_id': str(ObjectId(user['_id'])),
        'name': user['name'],
        'host': user['host'],
        'email': user['email'],
        'password': user['password']
    })
    else:
        return jsonify({'msg': 'User not found '})

# delete user
@app.route('/users/<_id>', methods = ['DELETE'])
def deleteUser(_id):
    userToDelete = db.find_one({'_id': ObjectId(_id)})
    if (userToDelete):
        db.delete_one({'_id': ObjectId(userToDelete['_id'])})
        return jsonify({'msg': "user succesfully deleted"})
    else:
        return jsonify({'msg': 'User not found'})

# update user
@app.route('/users/<_id>', methods = ['PUT'])
def updateUser(_id):
    userToUpdate = db.find_one({'_id': ObjectId(_id)})
    if (userToUpdate):
        db.update_one({'_id': ObjectId(_id)}, {'$set': {
            'name': request.json['name'],
            'host': request.json['host'],
            'email': request.json['email'],
            'password': request.json['password']
        }})
        return jsonify({'msg': 'User updated', 'Previos name': userToUpdate['name'], 'New name': request.json['name']})
        # print(_id,request.json)
        # return jsonify({'msg': 'There is an user', 'userName': userToUpdate['name']})
    else:
        return jsonify({'msg': ' There is no user'})
    # print(_id)
    # print(request.json)
    # return "received"


# create notes collection for a user
@app.route('/users/<user_id>/create_notes', methods=['POST'])
def createNotes(user_id):
    user = db.find_one({'_id': ObjectId(user_id)})
    if not user:
        return jsonify({'error': 'User not found'})

    notes_collection = mongo.db.notes

    # Insert the note document into the collection, associating it with the user ID
    inserted_id = notes_collection.insert_one({
        'user_id': user_id,
        # '_id': _id,
        'title': request.json['title'],
        'description': request.json['description'],
        'created_at': datetime.now(),
        'updated_at': None,
        'finished_at': None
    }).inserted_id

    # return (console.log({'msg': 'Note created succesfully','_id': str(inserted_id)}))
    return jsonify({'msg': 'Note created succesfully','_id': str(inserted_id)})


# get all notes for a user
@app.route('/users/<user_id>/notes', methods=['GET'])
def getNotes(user_id):
    notes_collection = mongo.db.notes

    # Find all notes associated with the user ID
    notes = notes_collection.find({'user_id': user_id})

    # Convert the MongoDB Cursor to a list of dictionaries
    notes_list = []
    for note in notes:
        note['_id'] = str(note['_id'])
        notes_list.append(note)

    # print(console.log())
    return jsonify({'notes': notes_list})

# DELETE AN SINGLE NOTE BASED ON THE NOTE'S ID
@app.route('/users/<user_id>/delete_notes/<_id>', methods=['DELETE'])
def deleteSingleNote(user_id, _id):
    notes_collection = mongo.db.notes

    # Find the note associated with the user ID and note ID
    noteToDelete = notes_collection.find_one({'user_id': user_id, '_id': ObjectId(_id)})
    if noteToDelete:
        # delete it
        notes_collection.delete_one(noteToDelete)

        return jsonify({'msg': 'Note have been deleted successfully'})
    else:
        return jsonify({'msg': 'No note was found!'})

# UPDATE SINGLE NOTE BASED ON THE NOTE'S ID
@app.route('/users/<user_id>/update_notes/<_id>', methods=['POST'])
def updateSingleNote(user_id, _id):
    notes_collection = mongo.db.notes

    # Find the note associated with the user ID and note ID
    noteToUpdate = notes_collection.find_one({'user_id': user_id, '_id': ObjectId(_id)})
    if noteToUpdate:
        # update it
        notes_collection.update_one(noteToUpdate)

        return jsonify({'msg': 'Note have been updated successfully'})
    else:
        return jsonify({'msg': 'No note was found!'})




if __name__ == '__main__':
    app.run(debug=True)