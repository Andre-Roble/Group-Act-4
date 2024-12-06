import requests
import urllib.parse
from tkinter import Tk, Label, Entry, Button, StringVar, OptionMenu, Text, END, messagebox
from tkinter import ttk

# Constants
API_KEY = "909ac5a3-1a61-4773-bda0-1f5772aad2ad"  # Replace with your API key
GEOCODE_URL = "https://graphhopper.com/api/1/geocode?"
ROUTE_URL = "https://graphhopper.com/api/1/route?"

# Geocoding function with error handling
def geocoding(location):
    if not location.strip():
        return None, None, "Invalid location entered"
    url = GEOCODE_URL + urllib.parse.urlencode({"q": location, "limit": "1", "key": API_KEY})
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["hits"]:
            lat = data["hits"][0]["point"]["lat"]
            lng = data["hits"][0]["point"]["lng"]
            return lat, lng, data["hits"][0].get("name", location)
        else:
            return None, None, f"No results for '{location}'"
    except requests.exceptions.RequestException as e:
        return None, None, f"Error: {e}"

# Routing function with error handling
def get_route(lat1, lng1, lat2, lng2, vehicle, avoid):
    # Prepare the points as a list of lat, lng pairs
    points = [
        f"{lat1},{lng1}",
        f"{lat2},{lng2}"
    ]
    # Prepare the parameters
    params = {
        "point": points,  # This is now a list of points
        "vehicle": vehicle,
        "key": API_KEY,
        "ch.disable": "true",  # Enable alternative routes
        "avoid": avoid
    }
    
    # URL encode the parameters
    url = ROUTE_URL + urllib.parse.urlencode(params, doseq=True)

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

# GUI functionality
def calculate_route():
    # Clear previous output
    output_text.delete(1.0, END)
    
    origin = entry_origin.get().strip()
    destination = entry_destination.get().strip()
    
    if not origin or not destination:
        messagebox.showerror("Input Error", "Please enter both origin and destination")
        return
    
    vehicle = vehicle_var.get()
    avoid = avoid_var.get()

    # Geocode origin and destination
    lat1, lng1, origin_name = geocoding(origin)
    lat2, lng2, destination_name = geocoding(destination)

    if not lat1 or not lat2:
        if not lat1:
            messagebox.showerror("Error", f"Error with origin: {origin_name}")
        if not lat2:
            messagebox.showerror("Error", f"Error with destination: {destination_name}")
        return

    # Get route from API
    result = get_route(lat1, lng1, lat2, lng2, vehicle, avoid)
    if "error" in result:
        messagebox.showerror("Routing Error", f"Routing Error: {result['error']}")
        return

    paths = result.get("paths", [])
    if paths:
        path = paths[0]
        distance_km = path["distance"] / 1000
        time_seconds = path["time"] / 1000
        output_text.insert(END, f"Route from {origin_name} to {destination_name}:\n")
        output_text.insert(END, f"Distance: {distance_km:.2f} km\n")
        output_text.insert(END, f"Duration: {int(time_seconds // 3600)}h {int((time_seconds % 3600) // 60)}m\n")
        output_text.insert(END, "Instructions:\n")
        for instruction in path["instructions"]:
            output_text.insert(END, f"- {instruction['text']} ({instruction['distance'] / 1000:.2f} km)\n")
    else:
        messagebox.showerror("No Route Found", "No route found for the given locations.")

# GUI setup
root = Tk()
root.title("Route Planner")

# Styling
root.configure(bg="#f0f0f0")
root.geometry("600x500")

# Font style for labels and buttons
label_font = ("Arial", 12)
button_font = ("Arial", 10, "bold")
text_font = ("Arial", 10)

# Origin input
Label(root, text="Origin:", font=label_font, bg="#f0f0f0").grid(row=0, column=0, padx=10, pady=10)
entry_origin = Entry(root, width=40, font=text_font)
entry_origin.grid(row=0, column=1, padx=10, pady=10)

# Destination input
Label(root, text="Destination:", font=label_font, bg="#f0f0f0").grid(row=1, column=0, padx=10, pady=10)
entry_destination = Entry(root, width=40, font=text_font)
entry_destination.grid(row=1, column=1, padx=10, pady=10)

# Vehicle input
Label(root, text="Vehicle:", font=label_font, bg="#f0f0f0").grid(row=2, column=0, padx=10, pady=10)
vehicle_var = StringVar(value="car")
OptionMenu(root, vehicle_var, "car", "bike", "foot").grid(row=2, column=1, padx=10, pady=10)

# Avoid input
Label(root, text="Avoid:", font=label_font, bg="#f0f0f0").grid(row=3, column=0, padx=10, pady=10)
avoid_var = StringVar(value="")
OptionMenu(root, avoid_var, "", "ferries", "highways", "tollroads").grid(row=3, column=1, padx=10, pady=10)

# Calculate button
Button(root, text="Get Route", font=button_font, bg="#4CAF50", fg="white", command=calculate_route).grid(row=4, column=0, columnspan=2, pady=20)

# Output text area for results
output_text = Text(root, width=60, height=15, font=text_font, wrap="word")
output_text.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

# Main loop
root.mainloop()

###TESTING!!!