import os

from flask import Flask, request, jsonify, send_file
import DataStorage.datastorage
import usersignon
from werkzeug.utils import secure_filename
import documentparsing
from flask_cors import CORS
import threading

app = Flask(__name__)
CORS(app)

@app.route('/addUser', methods=['POST'])
def add_user():
    #Form parsing
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    location = request.form['location']
    msg = usersignon.add_user(username, email, password, location)
    print(msg)

    if "already exists" in msg:
        return jsonify({"message": msg}), 400
    return jsonify({"message": msg}), 200

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
    msg = usersignon.add_doctor(name, password, specialty, email, workplace, degree_path)
    result = jsonify({"message": msg})

    #Delete temp file & return
    os.remove(degree_path)
    if "already exists" in msg:
        return result, 400
    return result, 200

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
    print("request received")

    # ----------------------------
    # SAFE FORM PARSING
    # ----------------------------
    user = request.form.get('username')
    password = request.form.get('password')
    caption = request.form.get('caption')

    document = request.files.get('document')

    if not user or not password:
        return jsonify({"message": "Missing credentials"}), 400

    if not document:
        return jsonify({"message": "Document is required!"}), 400

    # ----------------------------
    # SAVE FILE IMMEDIATELY
    # ----------------------------
    filename = secure_filename(document.filename)

    document_path = os.path.join(
        os.path.dirname(__file__),
        'documents',
        filename
    )

    document.save(document_path)

    # ----------------------------
    # AUTH CHECK (BEFORE HEAVY WORK)
    # ----------------------------
    if not DataStorage.datastorage.verify_user(user, password):
        os.remove(document_path)
        return jsonify({"message": "User verification failed"}), 401

    user_id = DataStorage.datastorage.get_user_by_username(user)[0]

    # ----------------------------
    # BACKGROUND PROCESS FUNCTION
    # ----------------------------
    def process_document(path, caption_text, uid):
        try:
            print("background processing started")

            result = documentparsing.parse_document(path, caption_text)

            print("ML processing complete")

            DataStorage.datastorage.add_document(
                path,
                caption_text,
                result,
                uid
            )

            print("database save complete")

        except Exception as e:
            print("background processing error:", e)

    # ----------------------------
    # SPAWN THREAD (NON-BLOCKING)
    # ----------------------------
    thread = threading.Thread(
        target=process_document,
        args=(document_path, caption, user_id),
        daemon=True
    )

    thread.start()

    # ----------------------------
    # IMMEDIATE RESPONSE
    # ----------------------------
    return jsonify({
        "message": "Upload received. Processing started in background."
    }), 200

@app.route('/getDoctorDocuments', methods=['GET'])
def get_doctor_documents():
    #Parse form
    name = request.args.get('name')
    password = request.args.get('password')

    #Authenticate
    if not DataStorage.datastorage.verify_doctor(name, password):
        return jsonify({"message": f"Doctor {name} verification failed!"}), 401
    
    doctor = DataStorage.datastorage.get_doctor_by_name(name)
    doctor_id = doctor[0]
    documents = DataStorage.datastorage.get_all_documents_for_doctor(doctor_id)
    document_list = []
    for document in documents:
        document_dict = {
            "id": document[0],
            "document_path": document[1],
            "summary": document[2],
            "user_id": document[3]
        }
        for i in range(DataStorage.datastorage.number_of_doctors):
            document_dict[f'matched_doctor_{i+1}'] = document[4+2*i]
            document_dict[f'similarity_score_{i+1}'] = document[5+2*i]
        document_list.append(document_dict)

    return jsonify(document_list), 200

@app.route('/get-file/<int:doc_id>', methods=['GET'])
def get_file(doc_id):
    doc = DataStorage.datastorage.get_document_by_id(doc_id)

    if not doc:
        return jsonify({"message": "Document not found"}), 404

    file_path = doc[1]  # assuming column 1 is path

    if not os.path.exists(file_path):
        return jsonify({"message": "File missing"}), 404

    return send_file(file_path, as_attachment=False)

@app.route('/getDocumentMeta', methods=['GET'])
def get_document_meta():
    doc_id = request.args.get('id')

    if not doc_id:
        return jsonify({"message": "Missing document id"}), 400

    try:
        doc_id = int(doc_id)
    except:
        return jsonify({"message": "Invalid document id"}), 400

    # Fetch document
    document = DataStorage.datastorage.get_document_by_id(doc_id)

    if not document:
        return jsonify({"message": "Document not found"}), 404

    file_path = document[1]
    summary = document[2]
    user_id = document[3]

    filename = os.path.basename(file_path)

    best_match = 0.0

    for i in range(DataStorage.datastorage.number_of_doctors):
        score = document[5 + 2*i] if len(document) > (5 + 2*i) else None
        if score is not None:
            try:
                best_match = max(best_match, float(score))
            except:
                pass

    question_text = summary if summary else "No question available"

    return jsonify({
        "id": doc_id,
        "filename": filename,
        "question": question_text,
        "match": best_match
    }), 200

@app.route('/addAnswer', methods=['POST'])
def add_answer():
    doc_id = request.form.get('doc_id')
    answer_text = request.form.get('answer')

    if not doc_id or not answer_text:
        return jsonify({"message": "Missing required fields"}), 400

    try:
        doc_id = int(doc_id)
    except:
        return jsonify({"message": "Invalid document id"}), 400

    DataStorage.datastorage.add_answer_to_document(doc_id, answer_text)

    return jsonify({"message": "Answer added successfully!"}), 200

@app.route('/getDocumentsForUser', methods=['GET'])
def get_documents_for_user():
    username = request.args.get('username')
    password = request.args.get('password')
    print(username)
    print(password)

    if not username or not password:
        return jsonify({"message": "Missing credentials"}), 400

    if not DataStorage.datastorage.verify_user(username, password):
        return jsonify({"message": "User verification failed"}), 401

    user_id = DataStorage.datastorage.get_user_by_username(username)[0]

    documents = DataStorage.datastorage.get_documents_for_user(user_id)

    document_list = []
    for document in documents:
        document_dict = {
            "id": document[0],
            "document_path": document[1],
            "summary": document[2],
            "user_id": document[3]
        }
        for i in range(DataStorage.datastorage.number_of_doctors):
            document_dict[f'matched_doctor_{i+1}'] = document[4+2*i]
            document_dict[f'similarity_score_{i+1}'] = document[5+2*i]
        document_list.append(document_dict)

    return jsonify(document_list), 200

if __name__ == '__main__':
    app.run(debug=False)