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

def resolve_airports(target, airports_config):
    """Permet passar un codi directe ('LAX'), una regió ('Barcelona') o una llista (['LAX', 'SFO'])."""
    if isinstance(target, list):
        resolved = []
        for item in target:
            resolved.extend(resolve_airports(item, airports_config))
        return list(dict.fromkeys(resolved))  # Eliminar duplicats mantenint l'ordre
    
    regions = airports_config.get("regions", {})
    
    # 1. Comprovació per clau directa (ex: 'Costa_Oest_EUA', 'Barcelona')
    if target in regions:
        return regions[target].get("airports", [])
        
    # 2. Comprovació pel nom descriptiu (ex: 'Costa Oest dels EUA (Internacionals)')
    target_clean = target.strip().lower()
    for reg_key, reg_val in regions.items():
        if reg_val.get("name", "").strip().lower() == target_clean:
            return reg_val.get("airports", [])
    
    return [target]

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
                    print(f"Cercant: {orig} -> {dest} el {d} (Max stops: {max_stops})")
                    res = search_one_way(orig, dest, d, max_stops, market)
                    if "itineraries" in res:
                        all_itineraries.extend(res["itineraries"])
                    time.sleep(0.3) # Rate limit respect
                except Exception as e:
                    print(f"Error a la cerca {orig}-{dest}-{d}: {e}")
    max_layover_minutes = route_config.get("max_layover_minutes")
                    
    # Filtrar per temps màxim d'escala (si està definit)
    valid_itineraries = []
    for it in all_itineraries:
        if max_layover_minutes is None:
            valid_itineraries.append(it)
            continue
            
        segments = it.get("outbound", {}).get("segments", [])
        valid_layover = True
        for j in range(len(segments) - 1):
            try:
                arr_local = segments[j].get('arrival_time_local', '').split('+')[0].replace('Z', '')
                dep_local = segments[j+1].get('departure_time_local', '').split('+')[0].replace('Z', '')
                arr_dt = datetime.datetime.fromisoformat(arr_local)
                dep_dt = datetime.datetime.fromisoformat(dep_local)
                layover_mins = int((dep_dt - arr_dt).total_seconds() / 60)
                if layover_mins > max_layover_minutes:
                    valid_layover = False
                    break
            except:
                pass
        
        if valid_layover:
            valid_itineraries.append(it)

    # Ordenar per preu i agafar el Top N
    valid_itineraries.sort(key=lambda x: x.get("price", {}).get("amount", 999999))
    
    # Deduplicar per ID o característiques similars per evitar redundància exacta
    seen_ids = set()
    top_itineraries = []
    for it in valid_itineraries:
        ignav_id = it.get("ignav_id")
        if ignav_id not in seen_ids:
            seen_ids.add(ignav_id)
            top_itineraries.append(it)
            if len(top_itineraries) >= top_n:
                break
                
    return top_itineraries
