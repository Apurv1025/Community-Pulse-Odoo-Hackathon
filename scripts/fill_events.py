import requests
import json
from datetime import datetime
import os
import mimetypes

# Base URL for the API
BASE_URL = "http://localhost:8000"

# User credentials
USERS = {
    "asiesjhot": {"username": "asiesjhot", "password": "asies123"},
    "johndoe": {"username": "johndoe", "password": "secret"},
    "apurv": {"username": "apurv", "password": "apurv1234"},
    "admin": {"username": "admin", "password": "admin"},
}

# Event data
EVENTS = [
    {
        "event_name": "Mulund Monsoon Music Fest",
        "event_description": "A lively open-air evening with indie bands, jazz ensembles and rain-dance zones celebrating the city's monsoon spirit.",
        "start_date": "2025-06-29T17:00:00Z",
        "end_date": "2025-06-29T21:00:00Z",
        "category": "Music",
        "registration_start": "2025-06-01T00:00:00Z",
        "registration_end": "2025-06-28T23:59:00Z",
        "address": "139 Gokhale Road, Mulund, Mumbai",
        "city": "Mumbai",
        "state": "Maharashtra",
        "latitude": 19.173598,
        "longitude": 72.925203,
        "max_capacity": 250,
        "type": "Free",
    },
    {
        "event_name": "Colours of Canvas Art Expo",
        "event_description": "A day-long exhibition featuring emerging painters, live mural sessions and hands-on workshops in acrylic, water-colour and mixed media.",
        "start_date": "2025-08-10T11:00:00Z",
        "end_date": "2025-08-10T19:00:00Z",
        "category": "Art",
        "registration_start": "2025-07-15T00:00:00Z",
        "registration_end": "2025-08-08T23:59:00Z",
        "address": "193 Korum Mall Road, Mulund, Mumbai",
        "city": "Mumbai",
        "state": "Maharashtra",
        "latitude": 19.204949,
        "longitude": 72.917735,
        "max_capacity": 300,
        "type": "Paid",
    },
    {
        "event_name": "TechTomorrow Hackathon",
        "event_description": "A 12-hour coding sprint where developers, designers and entrepreneurs build AI-driven solutions to real-world civic problems.",
        "start_date": "2025-07-20T09:00:00Z",
        "end_date": "2025-07-20T21:00:00Z",
        "category": "Technology",
        "registration_start": "2025-06-22T00:00:00Z",
        "registration_end": "2025-07-18T23:59:00Z",
        "address": "10 LBS Marg, Mulund, Mumbai",
        "city": "Mumbai",
        "state": "Maharashtra",
        "latitude": 19.19784,
        "longitude": 72.988663,
        "max_capacity": 350,
        "type": "Free",
    },
    {
        "event_name": "Street Food Fiesta",
        "event_description": "More than 40 stalls dishing out Mumbai's favourite chaats, kebabs and desserts, along with live music and cooking masterclasses.",
        "start_date": "2025-09-14T12:00:00Z",
        "end_date": "2025-09-14T22:00:00Z",
        "category": "Food & Drink",
        "registration_start": "2025-08-20T00:00:00Z",
        "registration_end": "2025-09-12T23:59:00Z",
        "address": "166 Mulund West, Mulund, Mumbai",
        "city": "Mumbai",
        "state": "Maharashtra",
        "latitude": 19.17374,
        "longitude": 72.966556,
        "max_capacity": 400,
        "type": "Paid",
    },
    {
        "event_name": "Mulund Half Marathon",
        "event_description": "Scenic 21 km, 10 km and 5 km runs looping around Sanjay Gandhi National Park gates, with RFID timing and medical support.",
        "start_date": "2025-08-18T06:00:00Z",
        "end_date": "2025-08-18T11:00:00Z",
        "category": "Sports",
        "registration_start": "2025-06-25T00:00:00Z",
        "registration_end": "2025-08-15T23:59:00Z",
        "address": "96 MG Road, Mulund, Mumbai",
        "city": "Mumbai",
        "state": "Maharashtra",
        "latitude": 19.190138,
        "longitude": 72.940975,
        "max_capacity": 800,
        "type": "Free",
    },
    {
        "event_name": "STEM Bootcamp for Teens",
        "event_description": "Hands-on robotics, Arduino and 3-D printing sessions aimed at high-schoolers, mentored by IIT-B alumni and industry engineers.",
        "start_date": "2025-07-08T10:00:00Z",
        "end_date": "2025-07-08T16:00:00Z",
        "category": "Education",
        "registration_start": "2025-06-10T00:00:00Z",
        "registration_end": "2025-07-05T23:59:00Z",
        "address": "111 Eastern Express Highway, Mulund, Mumbai",
        "city": "Mumbai",
        "state": "Maharashtra",
        "latitude": 19.148333,
        "longitude": 72.965511,
        "max_capacity": 120,
        "type": "Paid",
    },
    {
        "event_name": "Wellness & Yoga Retreat",
        "event_description": "Sunrise yoga, guided meditation, and nutrition talks conducted by certified trainers beside the Powai Lake view pavilion.",
        "start_date": "2025-06-30T07:00:00Z",
        "end_date": "2025-06-30T13:00:00Z",
        "category": "Health & Wellness",
        "registration_start": "2025-06-01T00:00:00Z",
        "registration_end": "2025-06-28T23:59:00Z",
        "address": "132 Shivaji Nagar, Mulund, Mumbai",
        "city": "Mumbai",
        "state": "Maharashtra",
        "latitude": 19.172371,
        "longitude": 73.001603,
        "max_capacity": 200,
        "type": "Free",
    },
    {
        "event_name": "Startup Networking Mixer",
        "event_description": "An after-work social where founders, investors and mentors exchange ideas over craft beer, speed-pitches and panel chats.",
        "start_date": "2025-10-05T18:00:00Z",
        "end_date": "2025-10-05T21:00:00Z",
        "category": "Networking",
        "registration_start": "2025-09-05T00:00:00Z",
        "registration_end": "2025-10-03T23:59:00Z",
        "address": "48 Eastern Express Highway, Mulund, Mumbai",
        "city": "Mumbai",
        "state": "Maharashtra",
        "latitude": 19.163245,
        "longitude": 72.93139,
        "max_capacity": 250,
        "type": "Paid",
    },
    {
        "event_name": "Backyard Theatre Night",
        "event_description": "An intimate alfresco stage hosting contemporary Marathi plays followed by director Q&A and acoustic music sessions.",
        "start_date": "2025-08-28T19:00:00Z",
        "end_date": "2025-08-28T22:00:00Z",
        "category": "Theater",
        "registration_start": "2025-08-01T00:00:00Z",
        "registration_end": "2025-08-26T23:59:00Z",
        "address": "39 Lal Bahadur Shastri Road, Mulund, Mumbai",
        "city": "Mumbai",
        "state": "Maharashtra",
        "latitude": 19.132843,
        "longitude": 72.966135,
        "max_capacity": 150,
        "type": "Free",
    },
    {
        "event_name": "Community Winter Carnival",
        "event_description": "A festive market with craft stalls, kids' games, carol performances and an evening snow-foam show for families.",
        "start_date": "2025-12-12T15:00:00Z",
        "end_date": "2025-12-12T20:00:00Z",
        "category": "Community",
        "registration_start": "2025-11-15T00:00:00Z",
        "registration_end": "2025-12-10T23:59:00Z",
        "address": "152 Mulund West, Mulund, Mumbai",
        "city": "Mumbai",
        "state": "Maharashtra",
        "latitude": 19.149999,
        "longitude": 72.947366,
        "max_capacity": 500,
        "type": "Paid",
    },
]

# Tier data for paid events
TIERS = {
    "Colours of Canvas Art Expo": [
        {"tier_name": "Early Bird", "tier_price": 300, "quantity": 50},
        {"tier_name": "Regular", "tier_price": 500, "quantity": 100},
    ],
    "Street Food Fiesta": [
        {"tier_name": "Foodie Pass", "tier_price": 150, "quantity": 200},
        {"tier_name": "VIP Tasting", "tier_price": 400, "quantity": 50},
    ],
    "STEM Bootcamp for Teens": [
        {"tier_name": "Student Pass", "tier_price": 600, "quantity": 100},
        {"tier_name": "Mentor Pass", "tier_price": 1200, "quantity": 20},
    ],
    "Startup Networking Mixer": [
        {"tier_name": "Early Investor", "tier_price": 250, "quantity": 80},
        {"tier_name": "Regular", "tier_price": 400, "quantity": 120},
    ],
    "Community Winter Carnival": [
        {"tier_name": "Entry Pass", "tier_price": 100, "quantity": 300},
        {"tier_name": "All-Access", "tier_price": 250, "quantity": 100},
    ],
}

# User assignment pattern: asiesjhot, johndoe, apurv, asiesjhot, johndoe, apurv, asiesjhot, johndoe, apurv, admin
USER_PATTERN = [
    "asiesjhot",
    "johndoe",
    "asiesjhot",
    "apurv",
    "johndoe",
    "asiesjhot",
    "apurv",
    "johndoe",
    "admin",
    "apurv",
]


def login_user(username, password):
    """Login user and return access token"""
    login_data = {"username": username, "password": password}

    response = requests.post(f"{BASE_URL}/api/login", json=login_data)
    if response.status_code == 200:
        token_data = response.json()
        return token_data["access_token"]
    else:
        print(f"Login failed for {username}: {response.status_code} - {response.text}")
        return None


def create_event(event_data, token):
    """Create an event and return event ID"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    response = requests.post(
        f"{BASE_URL}/event/create", json=event_data, headers=headers
    )
    if response.status_code == 200:
        event_response = response.json()
        return event_response["id"]
    else:
        print(f"Event creation failed: {response.status_code} - {response.text}")
        return None


def create_tiers(event_id, tiers, token):
    """Create tiers for a paid event"""
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    for tier in tiers:
        response = requests.post(
            f"{BASE_URL}/event/{event_id}/tiers", json=tier, headers=headers
        )
        if response.status_code == 200:
            print(f"Created tier: {tier['tier_name']}")
        else:
            print(f"Tier creation failed: {response.status_code} - {response.text}")


def upload_image(event_id, image_path, token):
    """Upload image for an event with proper content type detection"""
    headers = {"Authorization": f"Bearer {token}"}

    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        return False

    # Detect the content type using mimetypes
    content_type, _ = mimetypes.guess_type(image_path)
    if content_type is None:
        # Default to a common image type if detection fails
        content_type = "image/jpeg"

    filename = os.path.basename(image_path)

    with open(image_path, "rb") as image_file:
        # Specify the content type explicitly in the files tuple
        files = {"file": (filename, image_file, content_type)}
        response = requests.post(
            f"{BASE_URL}/event/{event_id}/upload", files=files, headers=headers
        )

        if response.status_code == 200:
            print(f"Image uploaded successfully for event {event_id}")
            return True
        else:
            print(
                f"Image upload failed for event {event_id}: {response.status_code} - {response.text}"
            )
            return False


def main():
    """Main function to create all events"""
    print("Starting event creation process...")

    created_events = []

    for i, event in enumerate(EVENTS):
        print(f"\n=== Creating Event {i+1}: {event['event_name']} ===")

        # Get the user for this event
        user_key = USER_PATTERN[i]
        user_creds = USERS[user_key]

        print(f"Logging in as: {user_creds['username']}")

        # Login
        token = login_user(user_creds["username"], user_creds["password"])
        if not token:
            print(f"Failed to login as {user_creds['username']}, skipping event")
            continue

        # Create event
        event_id = create_event(event, token)
        if not event_id:
            print(f"Failed to create event: {event['event_name']}")
            continue

        print(f"Event created with ID: {event_id}")
        created_events.append(
            {
                "id": event_id,
                "name": event["event_name"],
                "user": user_creds["username"],
                "type": event["type"],
            }
        )

        # Create tiers if it's a paid event
        if event["type"].lower() == "paid" and event["event_name"] in TIERS:
            print(f"Creating tiers for paid event...")
            create_tiers(event_id, TIERS[event["event_name"]], token)

        # Upload image - try multiple common extensions
        image_extensions = [".jpg", ".jpeg", ".png", ".webp", ".bmp"]
        image_uploaded = False

        for ext in image_extensions:
            image_path = f"{i+1}{ext}"
            if os.path.exists(image_path):
                print(f"Attempting to upload image: {image_path}")
                if upload_image(event_id, image_path, token):
                    image_uploaded = True
                    break

        if not image_uploaded:
            print(
                f"No image found for event {i+1} (tried extensions: {image_extensions})"
            )

    # Summary
    print("\n=== SUMMARY ===")
    print(f"Successfully created {len(created_events)} events:")
    for event in created_events:
        print(
            f"- ID: {event['id']}, Name: {event['name']}, User: {event['user']}, Type: {event['type']}"
        )


if __name__ == "__main__":
    main()
