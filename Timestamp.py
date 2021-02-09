#!/usr/bin/python3
from dateutil.parser import parse
import time


class MyTimestamp:
    def __init__(self, now):
        self.now = now

    def updateTimestamp(self):
        self.now += 3600
        if self.getHour() == 0:
            print("Today is ", self.getDay(), self.getMonth(), self.getYear(), "and is", self.dayOfWeek())
        else:
            print(self.getHour())

    def getYear(self):
        return int(time.strftime('%Y', time.gmtime(self.now)))

    def getMonth(self):
        return int(time.strftime('%m', time.gmtime(self.now)))

    def getDay(self):
        return int(time.strftime('%d', time.gmtime(self.now)))

    def getHour(self):
        return int(time.strftime('%H', time.gmtime(self.now)))

    def getMinutes(self):
        return int(time.strftime('%M', time.gmtime(self.now)))

    def getSeconds(self):
        return int(time.strftime('%S', time.gmtime(self.now)))

    def dayOfWeek(self):
        return time.strftime('%A', time.gmtime(self.now))

    def getFullTs(self):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(self.now))

    def _nextDay(self):
        if self.hour % 24 == 0:
            self.day += 1
            self.hour = 0
            self.day_week += 1
            print("It's midnight, a new day has been started.")

    def _nextMonth(self):
        # TODO: months with different days
        if self.day == 31:
            self.month += 1
            self.day = 1
            print("new month number: ", self.month)

    def _nextYear(self):
        if self.month % 13 == 0:
            self.year += 1
            self.month = 1
            print("Happy new year!!!", self.year)
