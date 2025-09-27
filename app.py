import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import os
import time

# Load Firebase credentials from environment variables for secure deployment
firebase_config = {
    "type": os.getenv("FIREBASE_TYPE"),
    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
    "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
    "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
    "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL"),
    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
}

# Initialize Firebase app (singleton)
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred, {
        'databaseURL': os.getenv("FIREBASE_DATABASE_URL")
    })

# Firebase references
tourists_ref = db.reference('tourists')
alerts_ref = db.reference('alerts')

st.title("Tourist Safety App - Streamlit Prototype")

user_id = st.text_input("Enter User ID:", value="user1")

lat = st.number_input("Latitude", value=37.4219999, format="%.7f")
lng = st.number_input("Longitude", value=-122.0840575, format="%.7f")

def update_location(user, lat, lng):
    tourists_ref.child(user).child('location').set({
        'lat': lat,
        'lng': lng,
        'timestamp': int(time.time())
    })

def send_sos(user, lat, lng):
    alerts_ref.push({
        'user': user,
        'lat': lat,
        'lng': lng,
        'type': 'sos',
        'timestamp': int(time.time())
    })

def get_data():
    tourists = tourists_ref.get() or {}
    alerts = alerts_ref.get() or {}
    return tourists, alerts

if st.button("Update Location"):
    update_location(user_id, lat, lng)
    st.success(f"Location updated for {user_id}: ({lat}, {lng})")

if st.button("Send SOS"):
    send_sos(user_id, lat, lng)
    st.error("SOS Alert Sent!")

st.subheader("Tourists Current Locations")
tourist_locations = []
tourists, alerts = get_data()
for user, data in tourists.items():
    loc = data.get('location')
    if loc:
        tourist_locations.append({'lat': loc['lat'], 'lon': loc['lng'], 'name': user})

if tourist_locations:
    st.map(tourist_locations)
else:
    st.write("No location data available yet.")

st.subheader("Recent SOS Alerts")
if alerts:
    alert_list = []
    for alert_key, alert_data in list(alerts.items())[-5:]:
        text = f"User: {alert_data['user']}, Location: ({alert_data['lat']:.5f}, {alert_data['lng']:.5f})"
        alert_list.append(text)
    for alert_text in alert_list:
        st.warning(alert_text)
else:
    st.write("No alerts")
