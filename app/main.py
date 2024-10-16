import smartcar
from flask import Flask, redirect, request, jsonify, render_template
from flask_cors import CORS

# SETUP: Export your client id, secret, and redirect URI as environment variables.
# #
# # Open your terminal
# # export SMARTCAR_CLIENT_ID=<your client id>
# # export SMARTCAR_CLIENT_SECRET=<your client secret>
# # export SMARTCAR_REDIRECT_URI=<your redirect URI>


app = Flask(__name__)
CORS(app)

# global variable to save our access_token
access = None

# Ensure SETUP is completed, then instantiate an AuthClient
client = smartcar.AuthClient(mode="simulated")

# scope of permissions
scope = ["read_vehicle_info",
         "read_location",
          "read_charge_locations",
          "read_charge",
          "read_battery"]

# Route for the webpage with title and button
@app.route("/Noblet_Groupe", methods=["GET"])
def Noblet_Groupe():
    return render_template("Noblet_Groupe.html")  # Render HTML template

@app.route("/login", methods=["GET"])
def login():
    auth_url = client.get_auth_url(scope)
    return redirect(auth_url)



@app.route("/exchange", methods=["GET"])
def exchange_code():
    """
    To work, this route must be in your Smartcar developer dashboard as a Redirect URI.

    i.e. "http://localhost:8000/exchange"
    """
    code = request.args.get("code")

    # access our global variable and store our access tokens
    global access

    # in a production app you'll want to store this in some kind of
    # persistent storage
    access = client.exchange_code(code)
    return redirect("/vehicle_dashboard")


@app.route("/vehicle", methods=["GET"])
def get_vehicle():
    # access our global variable to retrieve our access tokens
    global access

    # receive a `Vehicles` NamedTuple, which has an attribute of 'vehicles' and 'meta'
    result = smartcar.get_vehicles(access.access_token)
    print(result)
    # get the first vehicle
    id_of_first_vehicle = result.vehicles[0]

    # instantiate the first vehicle in the vehicle id list
    vehicle = smartcar.Vehicle(id_of_first_vehicle, access.access_token)
    print('Vehicle object')
    print(vehicle.__dict__)
    # use the attributes() method to call to Smartcar API and get information about the vehicle.
    # These vehicle methods return NamedTuples with attributes
    attributes = vehicle.attributes()

    print(attributes)

    return jsonify(
        {"make": attributes.make, "model": attributes.model, "year": attributes.year, "type_attribute": str(type(attributes))}
    )

@app.route("/vehicle_dashboard", methods=["GET"])
def vehicle_dashboard():
    return render_template("vehicle_dashboard.html")


@app.route("/check_battery", methods=["GET"])
def check_battery():
    global access
    vehicle_id = smartcar.get_vehicles(access.access_token).vehicles[0]
    vehicle = smartcar.Vehicle(vehicle_id, access.access_token)

    battery =  vehicle.battery()  # Request the charge status
    
    return jsonify({"Percentage": battery.percentRemaining, "range": battery.range})

@app.route("/check_location", methods=["GET"])
def check_location():
    global access
    vehicle_id = smartcar.get_vehicles(access.access_token).vehicles[0]
    vehicle = smartcar.Vehicle(vehicle_id, access.access_token)

    location = vehicle.location()  # Assuming Smartcar provides a `location` method
    return jsonify({"location": f"Latitude: {location.latitude}, Longitude: {location.longitude}"})

@app.route("/check_attributes", methods=["GET"])
def check_attributes():
    global access
    vehicle_id = smartcar.get_vehicles(access.access_token).vehicles[0]
    vehicle = smartcar.Vehicle(vehicle_id, access.access_token)

    attributes = vehicle.attributes()
    return jsonify({
        "make": attributes.make,
        "model": attributes.model,
        "year": attributes.year
    })

@app.route("/check_energy", methods=["GET"])
def check_energy():
    global access
    vehicle_id = smartcar.get_vehicles(access.access_token).vehicles[0]
    vehicle = smartcar.Vehicle(vehicle_id, access.access_token)

    energy = vehicle.charge()  # Assuming Smartcar provides a `charge` method
    return jsonify({"energy_added": energy.energy_added})



if __name__ == "__main__":
    #app.run(port=8000)
    app.run(host='localhost', port=8000)
