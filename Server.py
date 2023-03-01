import socket
import threading
import hashlib
import firebase_admin
from firebase_admin import credentials, db, auth

# Initialize Firebase app with credentials and database URL
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://chatappfirebase-b4652-default-rtdb.europe-west1.firebasedatabase.app'
})
# create a reference to the Firebase Realtime Database
db_ref = db.reference()

# Create a socket and start listening for clients
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('127.0.0.1', 8000))
server.listen(2)

clients = []


def handle_client(client_socket, client_id):
    clients.append(client_socket)
    while True:
        message = client_socket.recv(1024)
        if not message:
            break
        for myself in clients:
            # myself is referred to the specific user, so long his not sending messages to himself, others will receive it
            if myself != client_socket:
                myself.sendall(f"{address}: {message.decode()}".encode())
                # This is so that other users will see his message instead of only him writing to himself
    clients.remove(client_socket)
    client_socket.close()


def register_user():
    while True:
        email = input('Enter your email: ')
        password = input('Enter your password: ')
        try:
            # hash the password
            password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
            # create a new user with the provided email and hashed password
            user = auth.create_user(
                email=email,
                password=password
            )

            # store the user data in the Realtime Database along with the hashed password
            user_data = {
                'email': email,
                'username': input('Enter your username: '),
                'password_hash': password_hash
            }
            db_ref.child('users').child(user.uid).set(user_data)
            print('User registered successfully')
        except Exception as e:
            print(f'Error: {e}')


# start a thread for registering users
register_thread = threading.Thread(target=register_user)
register_thread.start()

while True:
    client_socket, address = server.accept()
    print(f'Connected to {address[0]}:{address[1]}')
    client_thread = threading.Thread(target=handle_client, args=(client_socket, len(clients)))
    client_thread.start()
