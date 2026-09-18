import os
import requests

IGNAV_BASE_URL = "https://ignav.com/api"

def get_headers():
    api_key = os.getenv("IGNAV_API_KEY", "").strip("\"' \t\r\n")
    if not api_key:
        raise ValueError("L'entorn IGNAV_API_KEY no està definit.")
    return {
        "X-Api-Key": api_key,
        "Content-Type": "application/json"
    }

def search_one_way(origin, destination, date, max_stops=None, market="ES"):
    """Crida a l'endpoint de One-Way d'Ignav."""
    url = f"{IGNAV_BASE_URL}/fares/one-way"
    payload = {
        "origin": origin,
        "destination": destination,
        "departure_date": date,
        "adults": 1,
        "cabin_class": "economy",
        "market": market
    }
    if max_stops is not None:
        payload["max_stops"] = max_stops

    response = requests.post(url, headers=get_headers(), json=payload, timeout=20)
    response.raise_for_status()
    return response.json()

def get_booking_link(ignav_id):
    """Obté el link de reserva per a un itinerari."""
    url = f"{IGNAV_BASE_URL}/fares/booking-links"
    payload = {"ignav_id": ignav_id}
    
    response = requests.post(url, headers=get_headers(), json=payload, timeout=20)
    if response.status_code == 200:
        data = response.json()
        options = data.get("booking_options", [])
        if options and options[0].get("links"):
            return options[0]["links"][0].get("url")
    return None
