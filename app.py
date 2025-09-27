import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import os
import time

# Initialize Firebase with env vars
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

if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred, {
        'databaseURL': os.getenv("FIREBASE_DATABASE_URL")
    })

tourists_ref = db.reference('tourists')
alerts_ref = db.reference('alerts')

st.set_page_config(page_title="Tourist Safety App", layout="wide")

st.title("🧭 Tourist Safety App Prototype")

with st.sidebar:
    st.header("User Info & Uploads")
    user_id = st.text_input("Enter User ID:", value="user1")
    lat = st.number_input("Latitude", value=28.6139, format="%.7f")  # default New Delhi
    lng = st.number_input("Longitude", value=77.2090, format="%.7f") # default New Delhi
    st.markdown("---")
    st.subheader("Upload User Documents")
    uploaded_files = st.file_uploader("Choose files", accept_multiple_files=True, type=['pdf','png','jpg','jpeg'])
    uploaded_file_names = []
    if uploaded_files:
        for uploaded_file in uploaded_files:
            save_path = f"/tmp/{user_id}_{uploaded_file.name}"
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            uploaded_file_names.append(uploaded_file.name)
    st.markdown("---")

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

col1, col2 = st.columns(2)

with col1:
    if st.button("🚩 Update Location"):
        update_location(user_id, lat, lng)
        st.success(f"Location updated for {user_id}: ({lat}, {lng})")

with col2:
    if st.button("🚨 Send SOS Alert"):
        send_sos(user_id, lat, lng)
        st.error("SOS Alert Sent!")

st.markdown("---")

st.subheader("🌍 Current Tourist Locations")
tourists, alerts = get_data()
tourist_locations = []
for user, data in tourists.items():
    loc = data.get('location')
    if loc:
        tourist_locations.append({'lat': loc['lat'], 'lon': loc['lng'], 'name': user})

if tourist_locations:
    st.map(tourist_locations)
else:
    st.info("No location data available yet.")

st.subheader("⚠️ Recent SOS Alerts")
if alerts:
    alert_list = []
    for alert_key, alert_data in list(alerts.items())[-5:]:
        alert_list.append(
            f"User: {alert_data['user']}, Location: ({alert_data['lat']:.5f}, {alert_data['lng']:.5f})"
        )
    for alert_text in alert_list:
        st.warning(alert_text)
else:
    st.info("No alerts")

if uploaded_file_names:
    st.subheader("📄 Uploaded User Documents")
    for fname in uploaded_file_names:
        st.write(f"- {fname}")
else:
    st.info("No documents uploaded.")
