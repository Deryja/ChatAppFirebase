import socket
import threading
import firebase_admin
from firebase_admin import credentials, db, auth
import hashlib
import binascii
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
 'databaseURL': 'https://chatappfirebase-b4652-default-rtdb.europe-west1.firebasedatabase.app'
})
# create a reference to the Firebase Realtime Database
db_ref = db.reference()
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 8000))


def receive_messages():
    while True:
        message = client.recv(1024).decode()
        if not message:
            break
        print(f"Received message: {message}")

def authenticate_user():
    while True:
        email = input("Enter your email: ")
        password = input("Enter your password: ")
        try:
            # retrieve the user's data from the Realtime Database
            user_data = db_ref.child('users').order_by_child('email').equal_to(email).get()
            if user_data:
                # get the first user in the list (there should only be one)
                user_id = list(user_data.keys())[0]
                user = user_data[user_id]
                password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
                if user['password_hash'] == password_hash:
                    print("Authentication successful")
                    return user_id, user
                else:
                    print("Invalid password")
            else:
                print("Invalid email or password")
        except Exception as e:
            print(f"Error: {e}")

# call the authenticate_user function to get the authenticated user's id and data
auth_user_id, auth_user_data = authenticate_user()

# start a separate thread to receive messages from the server
receive_thread = threading.Thread(target=receive_messages)
receive_thread.start()

# continuously prompt the user for a message to send to the server
while True:
    message = input("Enter a message: ")
    client.sendall(message.encode())
