import time

from PowerStreamClient import PowerStreamClient
from ShellyClient import ShellyClient
from config import *


def loop():
    client = PowerStreamClient(email, password)
    client.get_auth_token()
    client.get_mqtt_credentials()
    mqtt_client = client.connect_mqtt()

    # Wait for the connection to be established
    time.sleep(5)

    # Check if the device is online
    if not mqtt_client.is_connected():
        raise Exception("Failed to connect to MQTT")

    total_power = 0.0
    for shelly_client in shelly_clients:
        shelly_client.connect()
        power_consumption = shelly_client.get_total_power_consumption()
        total_power += power_consumption

    print(f"Total power consumption: {total_power} W")

    # Send total power consumption to PowerStream rounded to up to 10 Watts
    total_power = round_up_to_nearest_10(total_power)
    client.set_base_power(serial_number, total_power)


def round_up_to_nearest_10(n):
    return int(n + 9) // 10 * 10


if __name__ == "__main__":
    loop()
    # Run the loop every 1 minute
    while True:
        loop()
        time.sleep(60)
