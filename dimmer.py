import ephem
import logging
import time


class Dimmer(object):
    def __init__(self, scheduler):
        self._observer = ephem.Observer()
        self._observer.pressure = 0
        self._observer.horizon = '-6'
        self._observer.lat = '54.687157'
        self._observer.lon = '25.279652'

        self.brightness = 100

        self.update()

        # Run every 5 minutes
        scheduler.add_job(self.update, 'cron', minute='*/5')

    def update(self):
        self._observer.date = ephem.now()

        morning = self._observer.next_rising(ephem.Sun(), use_center=True)
        night = self._observer.next_setting(ephem.Sun(), use_center=True)

        if morning < night:
            # Morning is sooner, so it must be night
            logging.info("It is night time")
            self.brightness = 20
        else:
            logging.info("It is day time")
            self.brightness = 50
