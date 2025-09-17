import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# main url of api
API_BASE_URL = "http://api.weatherapi.com/v1/forecast.json"

class skyWeatherApp(tk.Tk):
    def __init__(self, api_key, skyfavorites_file="favorites_cities_list.json"):
        super().__init__()
        self.title("Weather Forecast App")
        self.geometry("450x800")
        self.configure(bg="#e9f0f7")
            #api links
        self.api_key = api_key

        self.api_url =API_BASE_URL
        self.skyfavorites_file = skyfavorites_file

        self.favorites = self.load_myfavorites()

        #   theme of app
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton",
                        font=("Segoe UI", 11, "bold"),
                        padding=8,
                        relief="flat",
                        background="#FF9800",
                        foreground="white")
        style.map("TButton",
                  background=[("active", "#357ABD")])

        style.configure("TLabel",
                        font=("Segoe UI", 10),
                        background="#e9f0f7",
                        foreground="#333")
        style.configure("Header.TLabel",
                        font=("Segoe UI", 12, "bold"),
                        background="#e9f0f7",
                        foreground="#222")


        entry_frame = tk.Frame(self, bg="#e9f0f7")
        entry_frame.pack(pady=10)

        self.city_entry = ttk.Entry(entry_frame, font=("Segoe UI", 12), width=30)
        self.city_entry.pack(side="left", padx=8)

        ttk.Button(entry_frame, text="Get Weather", command=self.get_weather).pack(side="left", padx=5)


        btn_frame = tk.Frame(self, bg="#FF9800")
        btn_frame.pack(pady=8)
# Butoon of app for favorites
        ttk.Button(btn_frame, text="Add to Favorite ", command=self.add_myfavorite).pack(side="left", padx=15)
        ttk.Button(btn_frame, text="Remove Favorite", command=self.remove_myfavorite).pack(side="left", padx=10)

        #Label for helpping the user how to work with app
        self.info_label = ttk.Label(self, text="Type a city name to check the weather", style="Header.TLabel")
        self.info_label.pack(pady=10)

        self.forecast_label = ttk.Label(self, text="", style="TLabel", justify="left")
        self.forecast_label.pack(pady=6)


        fav_frame = tk.Frame(self, bg="#e9f0f7")

        fav_frame.pack(pady=7, fill="x")

        ttk.Label(fav_frame, text="Favorite Cities", style="Header.TLabel").pack(anchor="w", padx=5)

        self.listbox = tk.Listbox(fav_frame,
                                  font=("Segoe UI", 11),
                                  height=6,
                                  selectmode="single",
                                  bg="white",
                                  fg="#333",
                                  relief="flat",
                                  highlightthickness=1,
                                  highlightcolor="#4a90e2")
        self.listbox.pack(fill="x", pady=6, padx=5)
        self.listbox.bind("<Double-1>", self.load_myfavorite_weather)

        self.refresh_myfavorites()

        #Charts
        chart_frame = tk.Frame(self, bg="#e9f0f7")

        chart_frame.pack(fill="both", expand=True, pady=11)

        self.fig, self.ax = plt.subplots(figsize=(4, 3))
        self.fig.patch.set_facecolor("#AEC6CF")

        self.ax.set_facecolor("#f7f9fb")
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)

        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=13, pady=15)

    #   # --- API and Data Handling ---
    def fetch_weather(self, city, days=3):
        try:
            r = requests.get(
                self.api_url,
                params={"key": self.api_key, "q": city, "days": days},
                timeout=10
            )
            r.raise_for_status()
            return r.json(), None
        except requests.RequestException as e:
            return None, str(e)

    def get_weather(self, city=None):
        if city is None:
            city = self.city_entry.get()
        if not city:
            messagebox.showwarning("Warning", "Please enter a city")
            return

        data, err = self.fetch_weather(city)
        if err:
            messagebox.showerror("Error", err)
            return

        # the current weather data handler
        loc, cur = data["location"], data["current"]
        self.info_label.config(
            text=f"{loc['name']}, {loc['country']}\n"
                 f"{cur['temp_c']}°C | {cur['condition']['text']}"
        )

        # 3 days forcast data handler
        forecast_text = "3-Day Forecast:\n"
        for d in data["forecast"]["forecastday"]:
            date = datetime.strptime(d["date"], "%Y-%m-%d").strftime("%a %d %b")

            forecast_text += f"{date}: {d['day']['maxtemp_c']}°C / {d['day']['mintemp_c']}°C, {d['day']['condition']['text']}\n"
        self.forecast_label.config(text=forecast_text)


        self.update_mychart(data["forecast"]["forecastday"])


    def update_mychart(self, forecast):
        self.ax.clear()
        days = [datetime.strptime(d["date"], "%Y-%m-%d").strftime("%a") for d in forecast]
        max_t = [d["day"]["maxtemp_c"] for d in forecast]
        min_t = [d["day"]["mintemp_c"] for d in forecast]

        self.ax.plot(days, max_t, "o-", label="Max Temp", color="#e74c3c")
        self.ax.plot(days, min_t, "o-", label="Min Temp", color="#3498db")

        self.ax.set_ylabel("°C")

        self.ax.set_title("Temperature Trend")
        self.ax.legend()

        self.canvas.draw()


    def load_myfavorites(self):
        try:
            with open(self.skyfavorites_file, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_myfavorites(self):
        try:
            with open(self.skyfavorites_file, "w") as f:
                json.dump(self.favorites, f, indent=4)
        except Exception as e:
            print("Error: can not save favorites:", e)

    def add_myfavorite(self):
        city = self.city_entry.get()
        if city and city not in self.favorites:
            self.favorites.append(city)
            self.save_myfavorites()
            self.refresh_myfavorites()

    def remove_myfavorite(self):
        sel = self.listbox.curselection()

        if sel:
            city = self.listbox.get(sel[0])
            self.favorites.remove(city)
            self.save_myfavorites()
            self.refresh_myfavorites()

    def refresh_myfavorites(self):
        self.listbox.delete(0, tk.END)
        for city in self.favorites:
            self.listbox.insert(tk.END, city)

    def load_myfavorite_weather(self, event):
        sel = self.listbox.curselection()
        if sel:
            city = self.listbox.get(sel[0])
            self.get_weather(city)

#  runing the main function
if __name__ == "__main__":
    # url api code...
    WEATHER_API_KEY = "a54640bf4c104345a9e54546250309"
    app = skyWeatherApp(WEATHER_API_KEY)
    app.mainloop()
