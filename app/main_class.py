import smartcar
from flask import Flask, redirect, request, jsonify, render_template
from flask_cors import CORS
import json
import time
import threading

class SmartcarApp:
    def __init__(self, name):
        self.app = Flask(name)
        CORS(self.app)
        self.client = smartcar.AuthClient(mode="simulated")
        self.access_token = None
        self.sampling_thread = None
        self.scope = ["read_vehicle_info", "read_location", "read_charge_locations", "read_charge", "read_battery"]
        self.setup_routes()

    def save_tokens(self, tokens):
            """Save access and refresh tokens to a file (or use a database here)."""
            tokens_dict = {
                'access_token': tokens.access_token,
                'refresh_token': tokens.refresh_token,
                'expires_in': tokens.expires_in
            }
            tokens_dict['expires_at'] = time.time() + tokens.expires_in  # Add expiration time
            with open('tokens.json', 'w') as f:
                json.dump(tokens_dict, f)


    def load_tokens(self):
        """Load access and refresh tokens from a file (or use a database here)."""
        try:
            with open('tokens.json', 'r') as f:
                tokens = json.load(f)
                # Check if the access token has expired
                print(tokens)
                if time.time() > tokens['expires_at']:
                    # Refresh the access token if expired
                    tokens = self.refresh_access_token(tokens['refresh_token'])
                return tokens
        except FileNotFoundError:
            return None
    
    def refresh_access_token(self, refresh_token):
        """Refresh access token using the refresh token."""
        new_tokens = self.client.exchange_refresh_token(refresh_token)
        self.save_tokens(new_tokens)
        return new_tokens
    
    def start_sampling(self):
        """Function that samples battery level every 3 hours."""
        while True:
            print("Checking battery level...")
            vehicle = self.get_vehicle()
            if vehicle:
                battery = vehicle.battery()
                print(f"Battery Level: {battery.percent_remaining}")
            time.sleep(3 * 60 * 60)  # Sleep for 3 hours


    def setup_routes(self):
        """Define all routes for the Flask app"""

        @self.app.route("/Noblet_Groupe", methods=["GET"])
        def noblet_groupe():
            return render_template("Noblet_Groupe.html")

        @self.app.route("/login", methods=["GET"])
        def login():
            auth_url = self.client.get_auth_url(self.scope)
            return redirect(auth_url)

        @self.app.route("/exchange", methods=["GET"])
        def exchange_code():
            code = request.args.get("code")
            # Exchange the authorization code for access and refresh tokens
            tokens = self.client.exchange_code(code)
            print(tokens.access_token)
            self.access_token = tokens.access_token
            self.save_tokens(tokens)
            return redirect("/vehicle_dashboard")

        @self.app.route("/vehicle_dashboard", methods=["GET"])
        def vehicle_dashboard():
            return render_template("vehicle_dashboard_v2.html")

        @self.app.route("/check_battery", methods=["GET"])
        def check_battery():
            vehicle = self.get_vehicle()
            battery = vehicle.battery()
            print(battery)
            return jsonify({"percent_remaining": battery.percent_remaining, "range": battery.range})

        @self.app.route("/check_location", methods=["GET"])
        def check_location():
            vehicle = self.get_vehicle()
            print(self.access_token)
            location = vehicle.location()
            return jsonify({"location": f"Latitude: {location.latitude}, Longitude: {location.longitude}"})

        @self.app.route("/check_attributes", methods=["GET"])
        def check_attributes():
            vehicle = self.get_vehicle()
            attributes = vehicle.attributes()
            return jsonify({"make": attributes.make, "model": attributes.model, "year": attributes.year})

        @self.app.route("/check_energy", methods=["GET"])
        def check_energy():
            vehicle = self.get_vehicle()
            charge =  vehicle.request("GET", "Tesla/charge")
            return jsonify({"Energy Added": charge.energy_added})
        
        @self.app.route("/start_sampling", methods=["GET"])
        def start_sampling():
            if not self.sampling_thread or not self.sampling_thread.is_alive():
                self.sampling_thread = threading.Thread(target=self.start_sampling)
                self.sampling_thread.daemon = True  # Ensure the thread exits when the app stops
                self.sampling_thread.start()
                return jsonify({"message": "Battery sampling started!"})
            return jsonify({"message": "Battery sampling is already running."})


    def get_vehicle(self):
        """Retrieve the first vehicle and instantiate it with the access token"""
        if not self.access_token:
            self.access_tokens_file = self.load_tokens()
            self.access_token = self.access_tokens_file['access_token']
        if not self.access_token:
            return redirect("/login")

        result = smartcar.get_vehicles(self.access_token)
        vehicle_id = result.vehicles[0]
        return smartcar.Vehicle(vehicle_id, self.access_token)



    def run(self, host='localhost', port=8000):
        self.app.run(host=host, port=port)

if __name__ == "__main__":
    app_instance = SmartcarApp(__name__)
    app_instance.run()
