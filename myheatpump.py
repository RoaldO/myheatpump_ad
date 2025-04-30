import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime, timedelta
import requests
import base64


_SENSOR_FIELDS_TO_COPY = (
    'device_class',
    'friendly_name',
    'state_class',
    'unit_of_measurement',
    'state_color',
)
_SENSOR_FIELDS_TO_MAP = {
    'icon_mapping': 'icon',
    'color_mapping': 'icon_color',
}

class MyHeatPump(hass.Hass):
    def initialize(self):
        self.log("initializing")

        self._username = self.args['username']
        self._password = self.args['password']
        self._jsession_url = self.args['session_url']
        self._mn = self.args['mn']
        self._devid = self.args['devid']

        self._session = None

        self._previous_values = {}
        self._update_states()
        self.run_every(
            self._update_states,
            datetime.now(),
            timedelta(minutes=1).total_seconds(),
        )

        self._heatpump_power_entity = "input_boolean.heatpump_power"
        self.listen_state(self.state_changed_event, self._heatpump_power_entity)
        self.log("started")

    def state_changed_event(self, entity, attribute, old, new, kwargs):
        self.log(f"{attribute!r} van {entity!r} gewijzigd van {old!r} naar {new!r}")
        value_mapping = {
            "off": 0,
            "on": 1,
        }
        value = value_mapping[new]
        self._post_a_value(value)

    def _post_a_value(self, value):
        post_body = {
            "value": value,
        }
        url = 'https://url.blah'
        self.log(f'about to post {post_body=} to {url=} and make sure i got a session')

    def _update_states(self, *kwargs):
        if not self._session:
            self._start_session()
        fetched_data = self._fetch_data()
        changed_values = {
            k: v
            for k, v in fetched_data.items()
            if v != self._previous_values.get(k)
        }
        self._send_values_to_sensors(changed_values)
        self._previous_values = fetched_data

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

    def _send_values_to_sensors(self, data):
        self.log(f"_send_values_to_sensors: {data}")
        for device_id, device_configuration in self.args['sensors'].items():
            parameters_name = device_configuration['parameter']
            if parameters_name in data:
                value = data[parameters_name]

                attributes = {
                    field_name: device_configuration[field_name]
                    for field_name in _SENSOR_FIELDS_TO_COPY
                    if field_name in device_configuration
                }
                mapped_attrs = {
                    field_name: device_configuration[config_name].get(value)
                    for config_name, field_name in _SENSOR_FIELDS_TO_MAP.items()
                    if config_name in device_configuration
                }
                attributes={**attributes, **mapped_attrs}

                self.log(f"{attributes=}")

                if 'value_mapping' in device_configuration:
                    mapping = device_configuration['value_mapping']
                    value = mapping.get(value)

                self.set_state(device_id, state=value, attributes=attributes)
