def weather_factor(temp_c=20.0, wind_kmh=5.0):
    temp_factor = 1 + (temp_c - 20.0) * 0.008
    wind_factor = max(0.80, 1 - (wind_kmh * 0.01))
    return temp_factor * wind_factor

def ace_weather_factor(temp_c=20.0, wind_kmh=5.0):
    return weather_factor(temp_c, wind_kmh)

def break_weather_factor(temp_c=20.0, wind_kmh=5.0):
    # più vento/freddo -> più break
    temp_adj = 1 - (temp_c - 20.0) * 0.004
    wind_adj = 1 + (wind_kmh * 0.008)
    return max(0.85, min(1.20, temp_adj * wind_adj))
