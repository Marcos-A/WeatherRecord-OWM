#!/usr/bin/python3
# encoding: utf-8

"""WeatherRecordGenerator_1.3.py
"""

import csv
import os
import pyowm
import re
from datetime import datetime
from time import sleep

RESULT_FILE = '/home/pi/Documents/Python Projects/\
Weather-OWM/weather_record.csv'
BACKUP_FILE = "/home/pi/Documents/Python\ Projects/\
Weather-OWM/WeatherRecordGeneratorDropboxSync_1.0.py"

RECORDING_HOURS_LIST = [7, 10, 13, 16, 19, 22]


def get_record():
    owm = pyowm.OWM('c3535d8ffea52c2766f8333a9a3c7640')  # Valid API key

    # Get current date
    current_date = datetime.now().date()

    # Get current hour and minute
    time = datetime.strptime(str(datetime.now().time()), '%H:%M:%S.%f')
    hour_minute = str(time.hour).zfill(2) + ':' + str(time.minute).zfill(2)

    cities_dict = {
                   'Barcelona': {'apiId': '6356055', 'country': 'Spain'},

                   'Geneve': {'apiId': '2660646', 'country': 'Switzerland'},
                   'Lausanne': {'apiId': '7286283', 'country': 'Switzerland'},
                   'Thun': {'apiId': '2658377', 'country': 'Switzerland'},
                   'Interlaken': {'apiId': '2660253',
                                  'country': 'Switzerland'},
                   'Lauterbrunnen': {'apiId': '7286285',
                                     'country': 'Switzerland'},
                   'Lucerne (Luzern)': {'apiId': '7286409',
                                        'country': 'Switzerland'},
                   'Zurich': {'apiId': '2657896', 'country': 'Switzerland'},
                   'Neuhausen am Rheinfall': {'apiId': '7286627',
                                              'country': 'Switzerland'},

                   'Innsbruck': {'apiId': '2775220', 'country': 'Austria'},
                   'Hall in Tirol': {'apiId': '7873622', 'country': 'Austria'},
                   'Salzburg': {'apiId': '2766824', 'country': 'Austria'},
                   'Morzg (Hellbrunn)': {'apiId': '7286283',
                                         'country': 'Austria'},
                   'Vienna': {'apiId': '2761369', 'country': 'Austria'}
                  }

    # User-sorted list
    cities_list = ['Barcelona', 'Geneve', 'Lausanne', 'Thun', 'Interlaken',
                   'Lauterbrunnen', 'Lucerne (Luzern)', 'Zurich',
                   'Neuhausen am Rheinfall', 'Innsbruck', 'Hall in Tirol',
                   'Salzburg', 'Morzg (Hellbrunn)', 'Vienna']

    weather_record_writer = csv.writer(open(RESULT_FILE, 'a'))

    for city in cities_list:
        city_values = cities_dict.get(city)
        obs = owm.weather_at_id(int(city_values['apiId']))
        w = obs.get_weather()
        weather_record_writer.writerow([current_date, hour_minute,
                                        city_values['country'], city,
                                        w.get_detailed_status(),
                                        w.get_temperature(unit='celsius')[
                                                                        'temp'
                                                                        ],
                                        w.get_temperature(
                                                        unit='celsius'
                                                        )['temp_max'],
                                        w.get_temperature(
                                                        unit='celsius'
                                                        )['temp_min'],
                                        w.get_humidity(),
                                        w.get_wind()['speed'],
                                        get_summer_timezone_time(
                                                            w.get_sunrise_time
                                                            ('iso')
                                                            ),
                                        get_summer_timezone_time(
                                                            w.get_sunset_time
                                                            ('iso')
                                                            )
                                        ])

    open(RESULT_FILE).close()


def get_summer_timezone_time(timeString):
    hourRegex = re.compile(r'\d\d:')
    minuteRegex = re.compile(r':\d\d')

    hour = hourRegex.search(timeString)
    summerTimeZoneUpdate = int(hour.group()[0:2]) + 2

    minute = minuteRegex.search(timeString)

    return str(summerTimeZoneUpdate).zfill(2) + minute.group()


def initialize_record_file():
    if os.path.exists(RESULT_FILE) is False:
        csv.writer(open(RESULT_FILE, 'w')).writerow(['DATE', 'TIME', 'COUNTRY',
                                                     'CITY', 'STATUS',
                                                     'TEMPERATURE', 'MAX TEMP',
                                                     'MIN TEMP', 'HUMIDITY',
                                                     'WIND (m/s)', 'SUNRISE',
                                                     'SUNSET'])
        open(RESULT_FILE).close()


if __name__ == '__main__':
    initialize_record_file()

    # Check every hour if a new record must be registered
    while True:
        current_time = datetime.strptime(str(datetime.now().time()),
                                         '%H:%M:%S.%f')
        current_hour = current_time.hour

        data_recorded = False

        for hour in RECORDING_HOURS_LIST:
            if hour == current_hour:
                get_record()
                # Wait for 1 minute and upload record file to Dropbox
                sleep(30)
                os.system("python3 " + BACKUP_FILE)
                data_recorded = True

        if data_recorded is True:
            sleep(3570)
        else:
            sleep(3600)
