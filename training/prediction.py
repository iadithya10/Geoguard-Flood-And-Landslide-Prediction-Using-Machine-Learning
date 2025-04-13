import csv
import datetime
import pickle
import requests

import requests

def get_data(lat, lon):
    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{lat},{lon}?unitGroup=us&key=BWGMFZVJGFRMYPG92N9MNYJ9G&contentType=json"
    
    response = requests.get(url)
    data = response.json()['days']
    
    final = [0, 0, 0, 0, 0, 0]  # [avg_temp, max_temp, avg_wind_speed, avg_cloud_cover, total_precip, avg_humidity]

    for day in data:
        final[0] += day['temp']
        if day['tempmax'] > final[1]:
            final[1] = day['tempmax']
        final[2] += day['windspeed']
        final[3] += day['cloudcover']
        final[4] += day['precip']
        final[5] += day['humidity']

    days_count = len(data)
    final[0] /= days_count
    final[2] /= days_count
    final[3] /= days_count
    final[5] /= days_count

    return final

# Example usage
api_key = 'BWGMFZVJGFRMYPG92N9MNYJ9G'
latitude = 37.7749
longitude = -122.4194
weather_data = get_data(latitude, longitude)
print(weather_data)


def testConnection():
    return "yo"