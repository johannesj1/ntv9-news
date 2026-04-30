import requests
from datetime import datetime, timedelta
import re
from html.parser import HTMLParser

# Fetch weather data from Open-Meteo API (free, no key needed)
url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 60.4518,
    "longitude": 22.2666,
    "daily": "weather_code,temperature_2m_max,temperature_2m_min,wind_speed_10m_max",
    "timezone": "Europe/Helsinki",
    "forecast_days": 7
}

response = requests.get(url, params=params)
data = response.json()

# Weather code to emoji mapping
def get_weather_emoji(code):
    if code == 0:
        return "☀️"  # Clear sky
    elif code == 1 or code == 2:
        return "🌤️"  # Partly cloudy
    elif code == 3:
        return "☁️"  # Overcast
    elif code == 45 or code == 48:
        return "🌫️"  # Foggy
    elif code in [51, 53, 55, 61, 63, 65, 80, 81, 82]:
        return "🌧️"  # Rain
    elif code in [71, 73, 75, 77, 80, 81, 82]:
        return "❄️"  # Snow
    elif code in [80, 81, 82]:
        return "⛈️"  # Thunderstorm
    else:
        return "☁️"  # Default

# Get daily data
daily = data["daily"]
temps_max = daily["temperature_2m_max"]
temps_min = daily["temperature_2m_min"]
weather_codes = daily["weather_code"]

# Generate weather cards
days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
today = datetime.now()

cards = ""
for i in range(7):
    date = today + timedelta(days=i)
    day_name = days[i]
    day_date = date.strftime("%d.%m.")
    emoji = get_weather_emoji(weather_codes[i])
    temp_high = int(temps_max[i])
    temp_low = int(temps_min[i])
    wind = int(daily["wind_speed_10m_max"][i])
    
    card = f'''            <div class="weather-card">
                <h3>{day_name}</h3>
                <p class="day-date">{day_date}</p>
                <div class="weather-icon">{emoji}</div>
                <p class="temp-high">+{temp_high}°</p>
                <p class="temp-low">{temp_low}°</p>
                <p class="wind">💨 {wind} m/s</p>
            </div>
'''
    cards += card

# Calculate date range
start_date = today.strftime("%d.%m.")
end_date = (today + timedelta(days=6)).strftime("%d.%m.")

# Read the current HTML file
with open("weather.html", "r", encoding="utf-8") as f:
    content = f.read()

# Replace the date range
content = re.sub(
    r'<p id="weather-week">.*?</p>',
    f'<p id="weather-week">{start_date}–{end_date}.2026</p>',
    content
)

# Replace weather cards
content = re.sub(
    r'<div id="weather-grid">.*?</div>\s*</div>',
    f'<div id="weather-grid">\n{cards}        </div>\n    </div>',
    content,
    flags=re.DOTALL
)

# Add "Last updated" info before closing div
updated_time = datetime.now().strftime("%d.%m.%Y %H:%M")
info = f'<p style="font-size: 0.75rem; color: #aaa; margin-top: 1rem;">Last updated: {updated_time}</p>'
content = content.replace('        </div>\n    </div>\n\n    <footer>', f'            {info}\n        </div>\n    </div>\n\n    <footer>')

# Write the updated HTML
with open("weather.html", "w", encoding="utf-8") as f:
    f.write(content)

print(f"✅ Weather data updated for {start_date}–{end_date}.2026")
