import pyrebase

firebase_project_id = 'manu-smart-farm'
config = {
    "apiKey": "AIzaSyCCYpXxKwlT_-D76x2BdwSTUAADcNYZxd8",
    "authDomain": firebase_project_id + ".firebaseapp.com",
    "databaseURL": "https://" + firebase_project_id + ".firebaseio.com",
    "storageBucket": firebase_project_id + ".appspot.com"
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()

device = 'device1'
db_sensor_data_loc = device + '/sensor_data'
db_control_data_loc = device + '/control_data'


def get_data(loc):
    return db.child(loc).get().val()

def set_data(loc, value):
    return db.child(loc).set(value)
