import appdaemon.plugins.hass.hassapi as hass
from datetime import datetime, timedelta


class TimePredictor(hass.Hass):
    def initialize(self):
        self.log("initializing")

        self._recalc()
        self.run_every(
            self._recalc,
            datetime.now(),
            timedelta(minutes=1).total_seconds(),
        )

    def _recalc(self, *kwargs):
        for calculation in self.args['calculations']:
            self.log(f"perform calculation for {calculation=}")
            derivative_sensor = calculation['derivative_sensor']
            target_value_sensor = calculation['target_value_sensor']
            current_value_sensor = calculation['current_value_sensor']
            output_sensor = calculation['output_sensor']

            derivative = self.get_state(derivative_sensor)
            target_value = self.get_state(target_value_sensor)
            current_value = self.get_state(current_value_sensor)
            try:
                value_delta = float(target_value) - float(current_value)
                if float(derivative) != 0:
                    output_value = max(int(value_delta / float(derivative)), 0)
                # else: set to `unknown`

                self.log(f"{target_value=}")
                self.log(f"{current_value=}")
                self.log(f"-> {value_delta=}")
                self.log(f"   {derivative=}")
                self.log(f"   -> {output_value=}")

                self.set_state(
                    output_sensor,
                    state=output_value,
                    attributes={
                        'device_class': 'duration',
                        'unit_of_measurement': 'm',
                    },
                )
            except TypeError as exception:
                pass
        self.log("calculations done")
