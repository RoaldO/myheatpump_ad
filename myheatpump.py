import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime, timedelta
import requests
import base64


class MyHeatPump(hass.Hass):
    def initialize(self):
        self.log("initializing")

        self._username = self.args['username']
        self._password = self.args['password']
        self._jsession_url = self.args['session_url']
        self._mn = self.args['mn']
        self._devid = self.args['devid']

        self._session = None

        self._update_states()
        self.run_every(
            self._update_states,
            datetime.now(),
            timedelta(minutes=1).total_seconds(),
        )

        self.log("started")

    def _update_states(self, *kwargs):
        if not self._session:
            self._start_session()
        fetched_data = self._fetch_data()
        self._send_data_so_sensors(fetched_data)

    def _start_session(self):
        if self._session:
            self.log(f"Already have a session")
        self._session = requests.Session()

        response = self._session.post(
            "https://www.myheatpump.com/a/login",
            data={
                'username': base64.b64encode(self._username.encode("UTF-8")),
                'password': base64.b64encode(self._password.encode("UTF-8")),
                'validCode': "",
                'loginValidCode': "",
                '__url': "",
            },
        )
        if '<title>Login</title>' in response.text:
            self.log("Authentication failed")
            self._session = None

        try:
            response = self._session.get("https://www.myheatpump.com/a/index")
            response.raise_for_status()
            response = self._session.get(self._jsession_url)
            response.raise_for_status()
        except Exception as exception:
            self.log("No session created")
            self._session = None
            raise exception

    def _fetch_data(self):
        response = self._session.post("https://www.myheatpump.com/a/amt/realdata/get", {"mn":self._mn, "devid":self._devid})
        return response.json()

    def _send_data_so_sensors(self, data):
        self.log(f"_send_data_so_sensors: {data}")
        for device_id, device_configuration in self.args['entities'].items():
            value = data[device_configuration['parameter']]
            unit_of_measurement = device_configuration['unit_of_measurement']
            self.set_state(device_id, state=value, attributes={"unit_of_measurement": unit_of_measurement})
