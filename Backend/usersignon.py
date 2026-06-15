import DataStorage.datastorage

def add_user(username, email, password, location):
    result = DataStorage.datastorage.add_user(username, email, password, location)
    if not result:
        return f"User {username} already exists!"
    return f"User {username} added successfully!"

def add_doctor(name, password, specialty, email, workplace, degree):
    result = DataStorage.datastorage.add_doctor(name, password, specialty, email, workplace, degree)
    if not result:
        return f"Doctor {name} already exists!"
    return f"Doctor {name} added successfully!"