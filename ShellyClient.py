import requests
import json


class ShellyClient:
    def __init__(self, ip, username, password):
        self.ip = ip
        self.username = username
        self.password = password

    def connect(self):
        if not self.username or not self.password:
            # No authentication required
            return

        url = f'http://{self.ip}/settings/login?unprotected=1&username={self.username}&password={self.password}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to Shelly device: {e}")

    def get_total_power_consumption(self):
        url = f'http://{self.ip}/status'
        try:
            response = requests.get(url, auth=(self.username, self.password))
            response.raise_for_status()
            data = response.json()

            total_power = 0.0
            for meter in data.get('meters', []):
                total_power += meter.get('power', 0.0)

            return total_power
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get power consumption: {e}")
        except (KeyError, IndexError) as e:
            raise Exception(f"Unexpected response format: {e}")
