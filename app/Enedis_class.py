import requests
import json



class EnedisAPI:

    def __init__(self) -> None:
        pass

    
    def get_access_token(self, credential_path):
        """
        Retrieve the access token from the Enedis API
        """

        with open(credential_path, 'r') as json_file:
            credential_json = json.load(json_file)

        client_ID = credential_json['client_ID']
        client_secret = credential_json['client_secret']


        url = "https://gw.ext.prod-sandbox.api.enedis.fr/oauth2/v3/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {
            "grant_type": "client_credentials",
            "client_id": client_ID,  # Replace with your actual client ID
            "client_secret": client_secret  # Replace with your actual client secret
        }

        response = requests.post(url, headers=headers, data=data)

        # To get the response data
        if response.status_code == 200:
            token = response.json()  # Extract the JSON response
            print("Access Token:", token)
        else:
            print(f"Failed to get token, Status code: {response.status_code}, Response: {response.text}")
