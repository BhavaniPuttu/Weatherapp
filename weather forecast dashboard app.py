import tkinter as tk
from tkinter import messagebox
import requests
from datetime import datetime
from io import BytesIO
from urllib.request import urlopen
from tkinter import PhotoImage

API_KEY = "4641a44f0322409ca531f20de46b6ddd" # Replace this with your actual OpenWeatherMap API key

def toggle_theme():
    bg = "#2e2e2e" if is_dark_mode.get() else "SystemButtonFace"
    fg = "white" if is_dark_mode.get() else "black"

    root.config(bg=bg)
    city_entry.config(bg=bg, fg=fg, insertbackground=fg)
    get_button.config(bg=bg, fg=fg)
    unit_menu.config(bg=bg, fg=fg)
    weather_result.config(bg=bg, fg=fg)
    theme_toggle.config(bg=bg, fg=fg, selectcolor=bg)

def get_weather():
    city = city_entry.get()
    if not city:
        return

    unit = "metric" if temp_unit.get() == "Celsius" else "imperial"
    symbol = "°C" if unit == "metric" else "°F"
    wind_unit = "m/s" if unit == "metric" else "mph"

    current_url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units={unit}"
    forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units={unit}"

    try:
        current_data = requests.get(current_url).json()
        forecast_data = requests.get(forecast_url).json()

        if current_data["cod"] != 200:
            messagebox.showerror("Error", current_data["message"])
            return

        # Current weather
        weather = current_data["weather"][0]["description"].title()
        temperature = current_data["main"]["temp"]
        humidity = current_data["main"]["humidity"]
        wind_speed = current_data["wind"]["speed"]
        icon_code = current_data["weather"][0]["icon"]

        sunrise = datetime.fromtimestamp(current_data["sys"]["sunrise"]).strftime('%I:%M %p')
        sunset = datetime.fromtimestamp(current_data["sys"]["sunset"]).strftime('%I:%M %p')

        # Weather icon
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        with urlopen(icon_url) as u:
            raw_data = u.read()
        icon_image = PhotoImage(data=raw_data)
        icon_label.config(image=icon_image)
        icon_label.image = icon_image

        result_text = (
            f"--- Current Weather ---\n"
            f"Weather: {weather}\n"
            f"Temperature: {temperature}{symbol}\n"
            f"Humidity: {humidity}%\n"
            f"Wind Speed: {wind_speed} {wind_unit}\n"
            f"Sunrise: {sunrise}\n"
            f"Sunset: {sunset}\n"
        )

        # Forecast
        result_text += "\n--- 3-Day Forecast ---\n"
        days_shown = 0
        last_date = ""
        for item in forecast_data["list"]:
            dt_txt = item["dt_txt"]
            date, time = dt_txt.split()
            if time == "12:00:00" and date != last_date:
                desc = item["weather"][0]["description"].title()
                temp = item["main"]["temp"]
                day = datetime.strptime(date, "%Y-%m-%d").strftime("%A")
                result_text += f"{day}: {desc}, {temp}{symbol}\n"
                last_date = date
                days_shown += 1
                if days_shown == 3:
                    break

        weather_result.config(text=result_text)

    except Exception as e:
        messagebox.showerror("Error", str(e))

# GUI setup
root = tk.Tk()
root.title("Weather App")
root.geometry("400x550")

is_dark_mode = tk.BooleanVar(value=False)

city_entry = tk.Entry(root, width=25, font=("Arial", 12))
city_entry.pack(pady=10)

get_button = tk.Button(root, text="Get Weather", command=get_weather, font=("Arial", 11))
get_button.pack(pady=5)

temp_unit = tk.StringVar(value="Celsius")
unit_menu = tk.OptionMenu(root, temp_unit, "Celsius", "Fahrenheit")
unit_menu.pack(pady=5)

# Auto-refresh on unit change
temp_unit.trace_add("write", lambda *args: get_weather() if city_entry.get() else None)

theme_toggle = tk.Checkbutton(root, text="Dark Mode", variable=is_dark_mode, command=toggle_theme)
theme_toggle.pack(pady=5)

icon_label = tk.Label(root)
icon_label.pack()

weather_result = tk.Label(root, text="", font=("Helvetica", 11), justify="left", wraplength=350)
weather_result.pack(pady=10)

toggle_theme()
root.mainloop()
