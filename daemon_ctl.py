#!/usr/bin/env python3.7

import logging
import os
import sys

from monitor.monitoring_core.monitor_daemon import CourseMonitorDaemon

if __name__ == '__main__':

    action = sys.argv[1]
    logfile = os.path.join(os.getcwd(), "logs/eku_course_monitor.log")
    pidfile = os.path.join(os.getcwd(), "pid/eku_course_monitor.pid")

    logging.basicConfig(filename=logfile, level=logging.DEBUG)
    d = CourseMonitorDaemon(pidfile)

    if action == "start":

        d.start()

    elif action == "stop":

        d.stop()

    elif action == "restart":

        d.restart()