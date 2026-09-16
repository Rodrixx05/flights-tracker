import os
from dotenv import load_dotenv

# Carregar variables d'entorn des de .env (si existeix) abans de la resta
load_dotenv()

from src.config_loader import load_config, load_airports
from src.flight_search import search_route_combinations, get_dates_in_range
from src.ignav_client import get_booking_link
from src.formatter import generate_telegram_message
from src.telegram_bot import send_telegram_message

def main():
    print("Iniciant el Tracker de Vols...")
    
    config = load_config()
    airports = load_airports()
    market = config.get("market", "ES")
    
    routes = config.get("routes", [])
    if not routes:
        print("No hi ha rutes configurades.")
        return

    for route in routes:
        route_name = route.get("name", route.get("id"))
        print(f"\n--- Processant Ruta: {route_name} ---")
        
        # 1. Cerca combinatòria de la ruta
        top_itineraries = search_route_combinations(route, airports, market)
        
        if not top_itineraries:
            print(f"No s'han trobat vols per la ruta {route_name}.")
            continue
            
        print(f"S'han trobat les {len(top_itineraries)} millors opcions.")
        
        # 2. Obtenir els links de reserva exclusivament pel Top 5
        links_dict = {}
        for it in top_itineraries:
            ignav_id = it.get("ignav_id")
            if ignav_id:
                link = get_booking_link(ignav_id)
                if link:
                    links_dict[ignav_id] = link
                    
        # 3. Formatejar
        # Calcular el text de dates
        if "date_range" in route:
            dates_display = f"Del {route['date_range']['start']} al {route['date_range']['end']}"
        else:
            dates_display = route.get("dates", [])
            
        message = generate_telegram_message(route_name, top_itineraries, dates_display, links_dict)
        
        # 4. Enviar
        print(message)
        send_telegram_message(message)

if __name__ == "__main__":
    main()
