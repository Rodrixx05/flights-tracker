import datetime
import time
from .ignav_client import search_one_way

def get_dates_in_range(start_str, end_str):
    start = datetime.datetime.strptime(start_str, "%Y-%m-%d").date()
    end = datetime.datetime.strptime(end_str, "%Y-%m-%d").date()
    dates = []
    delta = datetime.timedelta(days=1)
    while start <= end:
        dates.append(start.strftime("%Y-%m-%d"))
        start += delta
    return dates

def resolve_airports(region_name, airports_config):
    if region_name in airports_config.get("regions", {}):
        return airports_config["regions"][region_name].get("airports", [])
    return [region_name]

def search_route_combinations(route_config, airports_config, market="ES"):
    origin_region = route_config.get("origin")
    dest_region = route_config.get("destination")
    
    origins = resolve_airports(origin_region, airports_config)
    destinations = resolve_airports(dest_region, airports_config)
    
    dates = []
    if "date_range" in route_config:
        dates = get_dates_in_range(route_config["date_range"]["start"], route_config["date_range"]["end"])
    elif "dates" in route_config:
        dates = route_config["dates"]
        
    max_stops = route_config.get("max_stops", 2)
    top_n = route_config.get("top_n", 5)
    
    all_itineraries = []
    
    for orig in origins:
        for dest in destinations:
            for d in dates:
                try:
                    print(f"Cercant: {orig} ➔ {dest} el {d} (Max stops: {max_stops})")
                    res = search_one_way(orig, dest, d, max_stops, market)
                    if "itineraries" in res:
                        all_itineraries.extend(res["itineraries"])
                    time.sleep(0.3) # Rate limit respect
                except Exception as e:
                    print(f"Error a la cerca {orig}-{dest}-{d}: {e}")
                    
    # Ordenar per preu i agafar el Top N
    all_itineraries.sort(key=lambda x: x.get("price", {}).get("amount", 999999))
    
    # Deduplicar per ID o característiques similars per evitar redundància exacta
    seen_ids = set()
    top_itineraries = []
    for it in all_itineraries:
        ignav_id = it.get("ignav_id")
        if ignav_id not in seen_ids:
            seen_ids.add(ignav_id)
            top_itineraries.append(it)
            if len(top_itineraries) >= top_n:
                break
                
    return top_itineraries
