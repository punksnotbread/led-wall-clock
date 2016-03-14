#!/usr/bin/env python
import argparse
import os
import sys
from daemonify import Daemon
from weather import Weather
from display import Display
from apscheduler.schedulers.blocking import BlockingScheduler


class LedClockDaemon(Daemon):
    def __init__(self, args):
        super(LedClockDaemon, self).__init__(pidfile=args["pidfile"])
        self._args = args

    def run(self):
        weather = Weather(zip=self._args['zip'], station=self._args['station'])

        sched = BlockingScheduler()
        sched.add_job(weather.update, 'cron', minute='*/15')

        display = Display(weather)

        display.start()
        sched.start()


def process_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pidfile", help="PID file name", type=str, default="/var/lock/ledclock.pid")
    parser.add_argument("-d", "--daemon", help="start stop restart", type=str)
    parser.add_argument("-s", "--station", help="NOAA station ID for current weather conditions", default="KLOU")
    parser.add_argument("-z", "--zip", help="ZIP code for weather forecast", default="40207")

    return vars(parser.parse_args())


# Main function
if __name__ == "__main__":
    # Process command line arguments
    args = process_args()

    # Verify running as root.  Unfortunately, this is required to access /dev/mem by the rgbmatrix lib
    if os.getuid() != 0:
        print "Must run as root!"
        sys.exit(-1)

    daemon = LedClockDaemon(args)

    if args['daemon'] is None:
        try:
            print("Press CTRL-C to exit")
            daemon.run()
        except KeyboardInterrupt:
            print "Exiting\n"
            sys.exit(0)
    elif args['daemon'] == 'start':
        daemon.start()
    elif args['daemon'] == 'stop':
        daemon.stop()
    elif args['daemon'] == 'restart':
        daemon.restart()
    else:
        print "Invalid daemon action"
