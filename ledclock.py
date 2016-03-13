#!/usr/bin/env python
import argparse
import os
import sys
from daemonify import Daemon
from weather import Weather
from display import Display
from apscheduler.schedulers.blocking import BlockingScheduler


class LedClockDaemon(Daemon):
    def __init__(self, *args, **kwargs):
        super(LedClockDaemon, self).__init__(*args, **kwargs)
        self._args = {}

    def process_args(self):
        parser = argparse.ArgumentParser()
#        parser.add_argument("-p", "--pid", help="PID file name", type=str)
        parser.add_argument("-d", "--daemon", help="start stop restart", type=str)
        self._args = vars(parser.parse_args())

        if self._args['daemon'] is None:
            try:
                print("Press CTRL-C to exit")
                self.run()
            except KeyboardInterrupt:
                print "Exiting\n"
                sys.exit(0)
        elif self._args['daemon'] == 'start':
            self.start()
        elif self._args['daemon'] == 'stop':
            self.stop()
        elif self._args['daemon'] == 'restart':
            self.restart()
        else:
            print "Invalid daemon action"

    def run(self):
        weather = Weather(zip="40207", station="KLOU")

        sched = BlockingScheduler()
        sched.add_job(weather.update, 'cron', minute='*/15')

        display = Display(weather)

        display.start()
        sched.start()

# Main function
if __name__ == "__main__":
    if os.getuid() != 0:
        print "Must run as root!"
        sys.exit(-1)

    daemon = LedClockDaemon("/var/lock/ledclock.pid")
    daemon.process_args()
