from flask import Flask
import DataStorage.datastorage

app = Flask(__name__)

@app.route('/addUser/<username>/<email>/<password>')
def add_user(username, email, password):
    DataStorage.datastorage.add_user(username, email, password)
    return f"User {username} added successfully!"

@app.route('/addDoctor/<name>/<password>/<specialty>/<email>/<workplace>/<degree>')
def add_doctor(name, password, specialty, email, workplace, degree):
    DataStorage.datastorage.add_doctor(name, password, specialty, email, workplace, degree)
    return f"Doctor {name} added successfully!"

@app.route('/verifyUser/<username>/<password>')
def verify_user(username, password):
    if DataStorage.datastorage.verify_user(username, password):
        return f"User {username} verified successfully!"
    else:
        return f"User {username} verification failed!"
    
@app.route('/verifyDoctor/<name>/<password>')
def verify_doctor(name, password):
    if DataStorage.datastorage.verify_doctor(name, password):
        return f"Doctor {name} verified successfully!"
    else:
        return f"Doctor {name} verification failed!"

if __name__ == '__main__':
    app.run(debug=True)