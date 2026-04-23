import requests


MADRID_LAT = 40.4168
MADRID_LON = -3.7038


def fetch_madrid_weather_forecast():
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={MADRID_LAT}&longitude={MADRID_LON}"
        "&daily=temperature_2m_max,temperature_2m_min,windspeed_10m_max"
        "&timezone=Europe%2FMadrid"
    )

    r = requests.get(url, timeout=20)
    r.raise_for_status()
    data = r.json()

    result = {}
    dates = data.get("daily", {}).get("time", [])
    tmax = data.get("daily", {}).get("temperature_2m_max", [])
    tmin = data.get("daily", {}).get("temperature_2m_min", [])
    wind = data.get("daily", {}).get("windspeed_10m_max", [])

    for i, d in enumerate(dates):
        avg_temp = None
        if i < len(tmax) and i < len(tmin):
            avg_temp = (tmax[i] + tmin[i]) / 2

        result[d] = {
            "avg_temp": avg_temp,
            "wind_kmh": wind[i] if i < len(wind) else None
        }

    return result


def ace_weather_factor(avg_temp, wind_kmh):
    factor = 1.0

    if avg_temp is not None:
        factor *= 1 + ((avg_temp - 20) * 0.01)

    if wind_kmh is not None:
        factor *= max(0.8, 1 - wind_kmh * 0.01)

    return round(factor, 3)


def break_weather_factor(avg_temp, wind_kmh):
    factor = 1.0

    if avg_temp is not None and avg_temp < 18:
        factor *= 1.03

    if wind_kmh is not None:
        factor *= 1 + min(0.12, wind_kmh * 0.005)

    return round(factor, 3)
