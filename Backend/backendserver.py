import os

from flask import Flask, request, jsonify
import DataStorage.datastorage
import usersignon
from werkzeug.utils import secure_filename
import documentparsing

app = Flask(__name__)

@app.route('/addUser', methods=['POST'])
def add_user():
    #Form parsing
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    location = request.form['location']

    return jsonify({"message": usersignon.add_user(username, email, password, location)}), 200

@app.route('/addDoctor', methods=['POST'])
def add_doctor():
    #Form parsing
    name = request.form['name']
    password = request.form['password']
    specialty = request.form['specialty']
    email = request.form['email']
    workplace = request.form['workplace']

    #Degree download
    try:
        degree = request.files.get('document')
    except:
        return jsonify({"message": "Degree document is required!"}), 400
    if not degree:
        return jsonify({"message": "Degree document is required!"}), 400
    degree_path = secure_filename(degree.filename)
    degree_path = os.path.join(os.path.join(os.path.dirname(__file__), 'temp'), degree_path)
    degree.save(degree_path)

    result = jsonify({"message": usersignon.add_doctor(name, password, specialty, email, workplace, degree_path)}), 200

    #Delete temp file & return
    os.remove(degree_path)
    return result

@app.route('/verifyUser')
def verify_user():
    #Parse form
    username = request.args.get('username')
    password = request.args.get('password')

    #Authenticate
    if DataStorage.datastorage.verify_user(username, password):
        return f"User {username} verified successfully!"
    else:
        return f"User {username} verification failed!"
    
@app.route('/verifyDoctor')
def verify_doctor():
    #Parse form
    name = request.args.get('name')
    password = request.args.get('password')

    #Authenticate
    if DataStorage.datastorage.verify_doctor(name, password):
        return f"Doctor {name} verified successfully!"
    else:
        return f"Doctor {name} verification failed!"
    
@app.route('/uploadDocument', methods=['POST'])
def upload_document():
    #Parse form
    user = request.form['username']
    password = request.form['password']
    caption = request.form['caption']

    #Save document
    try:
        document = request.files.get('document')
    except:
        return jsonify({"message": "Document is required!"}), 400
    if not document:
        return jsonify({"message": "Document is required!"}), 400
    document_path = secure_filename(document.filename)
    document_path = os.path.join(os.path.join(os.path.dirname(__file__), 'documents'), document_path)
    document.save(document_path)

    #Authenticate
    if not DataStorage.datastorage.verify_user(user, password):
        os.remove(document_path)
        return jsonify({"message": f"User {user} verification failed!"}), 401
    
    #Parse document
    result = documentparsing.parse_document(document_path, caption)

    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True)