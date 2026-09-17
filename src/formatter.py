from datetime import datetime

def format_duration(minutes):
    if not minutes: return ""
    h = minutes // 60
    m = minutes % 60
    return f"{h}h {m}m"

def format_time(time_str):
    try:
        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        return dt.strftime("%H:%M")
    except:
        return time_str

def format_date(date_str):
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except:
        return date_str

def generate_telegram_message(route_name, top_itineraries, route_dates, links_dict):
    dates_str = ", ".join([format_date(d) for d in route_dates]) if isinstance(route_dates, list) else route_dates
    
    msg = f"✈️ <b>RUTA: {route_name}</b>\n"
    msg += f"📅 Dates analitzades: {dates_str}\n"
    msg += "Top opcions més econòmiques:\n\n━━━━━━━━━━━━━━━━━━━━\n"
    
    medals = ["🥇", "🥈", "🥉", "4.", "5."]
    
    for i, it in enumerate(top_itineraries):
        medal = medals[i] if i < len(medals) else f"{i+1}."
        price = it.get("price", {}).get("amount", "?")
        currency = "€" if it.get("price", {}).get("currency") == "EUR" else it.get("price", {}).get("currency", "")
        
        # Extreure primer segment de sortida per la data
        outbound = it.get("outbound", {})
        segments = outbound.get("segments", [])
        if not segments:
            continue
            
        first_seg = segments[0]
        departure_date = first_seg.get("departure_time_local", "").split("T")[0]
        
        msg += f"{medal} <b>{price:.2f} {currency}</b> | {format_date(departure_date)}\n"
        
        for j, seg in enumerate(segments):
            dep_apt = seg.get('departure_airport')
            arr_apt = seg.get('arrival_airport')
            dep_time = format_time(seg.get('departure_time_local', ''))
            arr_time = format_time(seg.get('arrival_time_local', ''))
            carrier = seg.get('operating_carrier_name') or seg.get('marketing_carrier_code')
            
            msg += f"🛫 {dep_apt} {dep_time} -> 🛬 {arr_apt} {arr_time} ({carrier})\n"
            
            # Temps d'escala amb el següent segment
            if j < len(segments) - 1:
                next_seg = segments[j+1]
                layover_str = ""
                try:
                    # S'usa l'hora local (mateix aeroport d'escala = mateixa zona horària)
                    arr_local = seg.get('arrival_time_local', '').split('+')[0].replace('Z', '')
                    dep_local = next_seg.get('departure_time_local', '').split('+')[0].replace('Z', '')
                    arr_dt = datetime.fromisoformat(arr_local)
                    dep_dt = datetime.fromisoformat(dep_local)
                    layover_mins = int((dep_dt - arr_dt).total_seconds() / 60)
                    layover_str = f" de {format_duration(layover_mins)}"
                except Exception:
                    pass
                msg += f"⏳ Escala a {arr_apt}{layover_str}\n"
                
        total_duration = format_duration(outbound.get("duration_minutes", 0))
        if len(segments) == 1:
            msg += f"⏱ Durada: {total_duration} (Directe)\n"
        else:
            msg += f"⏱ Durada total: {total_duration}\n"
            
        ignav_id = it.get("ignav_id")
        link = links_dict.get(ignav_id)
        if link:
            msg += f"🔗 <a href='{link}'>Reservar vol</a>\n"
        
        msg += "\n"
        
    msg += "━━━━━━━━━━━━━━━━━━━━\n"
    return msg
