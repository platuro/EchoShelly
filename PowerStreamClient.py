import requests
import json
import base64
import uuid
import paho.mqtt.client as mqtt
import logging
import ssl

# Configure logging
logging.basicConfig(level=logging.DEBUG)


class PowerStreamClient:
    def __init__(self, email, password):
        self.sn = None
        self.email = email
        self.password = password
        self.token = None
        self.userid = None
        self.mqtt_data = {}
        self.client = None

    def get_auth_token(self):
        url = 'https://api.ecoflow.com/auth/login'
        headers = {
            'Host': 'api.ecoflow.com',
            'lang': 'de-de',
            'platform': 'android',
            'sysversion': '11',
            'version': '4.1.2.02',
            'phonemodel': 'SM-X200',
            'content-type': 'application/json',
            'user-agent': 'okhttp/3.14.9'
        }
        data = {
            "appVersion": "4.1.2.02",
            "email": self.email,
            "os": "android",
            "osVersion": "30",
            "password": base64.b64encode(self.password.encode()).decode(),
            "scene": "IOT_APP",
            "userType": "ECOFLOW"
        }

        response = requests.post(url, headers=headers, data=json.dumps(data))
        response_data = response.json()

        if response.status_code == 200:
            self.token = response_data['data']['token']
            self.userid = response_data['data']['user']['userId']
            logging.debug("Auth token received: %s", self.token)
        else:
            raise Exception("Failed to get auth token: " + response_data.get('msg', 'Unknown error'))

    def get_mqtt_credentials(self):
        url = f'https://api.ecoflow.com/iot-auth/app/certification?userId={self.userid}'
        headers = {
            'authorization': f'Bearer {self.token}',
            'Host': 'api.ecoflow.com',
            'lang': 'de-de',
            'platform': 'android',
            'sysversion': '11',
            'version': '4.1.2.02',
            'phonemodel': 'SM-X200',
            'content-type': 'application/json',
            'user-agent': 'okhttp/3.14.9'
        }

        response = requests.get(url, headers=headers)
        response_data = response.json()

        if response.status_code == 200:
            self.mqtt_data = {
                "password": response_data['data']['certificatePassword'],
                "port": int(response_data['data']['port']),
                "userid": self.userid,
                "user": response_data['data']['certificateAccount'],
                "url": response_data['data']['url'],
                "protocol": response_data['data']['protocol'],
                "clientID": f"ANDROID_{self.uuidv4()}_{self.userid}"
            }
            logging.debug("MQTT Credentials: %s", self.mqtt_data)
        else:
            raise Exception("Failed to get MQTT credentials: " + response_data.get('msg', 'Unknown error'))

    @staticmethod
    def uuidv4():
        return str(uuid.uuid4())

    def connect_mqtt(self):
        try:
            self.client = mqtt.Client(client_id=self.mqtt_data['clientID'])
            self.client.username_pw_set(self.mqtt_data['user'], self.mqtt_data['password'])

            # Enable SSL/TLS
            self.client.tls_set(cert_reqs=ssl.CERT_NONE)
            self.client.tls_insecure_set(True)

            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.on_disconnect = self.on_disconnect

            self.client.connect(self.mqtt_data['url'], self.mqtt_data['port'], 60)
            self.client.loop_start()
        except Exception as e:
            logging.error("Failed to connect to MQTT Broker: %s", e)
        return self.client

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("Connected to MQTT Broker!")
        else:
            logging.error("Failed to connect, return code %d\n", rc)

    def on_message(self, client, userdata, msg):
        logging.info("Received `%s` from `%s` topic", msg.payload.decode(), msg.topic)

    def on_disconnect(self, client, userdata, rc):
        logging.info("Disconnected from MQTT Broker")

    def read_data(self, topic):
        self.client.subscribe(topic)

    def write_data(self, topic, payload):
        self.client.publish(topic, payload)

    def set_base_power(self, serial_number, power):
        topic = f'/open/{self.mqtt_data["user"]}/{serial_number}/set'
        payload = {
            "id": uuid.uuid4().int >> 64,  # Unique identifier for the message
            "version": "1.0",
            "cmdCode": "WN511_SET_PERMANENT_WATTS_PACK",
            "params": {
                "permanentWatts": power
            }
        }
        self.write_data(topic, json.dumps(payload))
