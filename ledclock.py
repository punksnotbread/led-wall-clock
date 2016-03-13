#!/usr/bin/env python
import sys
from weather import Weather
from display import Display
from apscheduler.schedulers.blocking import BlockingScheduler

weather = Weather(zip="40207", station="KLOU")

sched = BlockingScheduler()
sched.add_job(weather.update, 'cron', minute='*/15')

display = Display(weather)

try:
    display.start()
    sched.start()
except KeyboardInterrupt:
    print "Exiting\n"
    sys.exit(0)
