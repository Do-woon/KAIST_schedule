import requests
from bs4 import BeautifulSoup
from bs4.element import NavigableString
import re
import pytz
from datetime import datetime

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE","schedule.settings")
from django.utils import timezone

from .crawl_exception import *


def ValidYearRange(year):
    if year > 2015:
        return True
    else:
        return False


def GetRawData( year ):
    if type(year) != int:
        raise ArgumentError("year parameter is not integer")
    elif not ValidYearRange(year):
        raise ArgumentError("year is not in valid range")

    target_url = 'http://www.kaist.edu/en/html/edu/03100101.html'

    req = requests.get(target_url)
    html = req.text
    soup = BeautifulSoup(html, 'html.parser')


    year_sch = soup.select("div#txt > div > div > div > table[class='schedule_table']")
    if len(year_sch) != 12:
        raise PageSchemeException("number of month entry is not 12")

    raw_data = []
    for month_sch in year_sch:
        if len(month_sch) == 0:
            raise PageSchemeException("failed to find monthly schedule")

        for time_slot in month_sch:
            if '<td>' not in time_slot.__str__():
                continue

            try:
                date_info = str(time_slot.contents[1].text)
                indv_sch = time_slot.contents[3].contents
            except (AttributeError, IndexError):
                raise PageSchemeException("failed to find each time slot")

            indv_sch = [ detail.__str__() for detail in indv_sch if type(detail)==NavigableString ]
            raw_data.append([date_info, indv_sch])

    return raw_data


def ParseDateInfo(date_info, year):
    if type(year) != int:
        raise ArgumentError("year parameter is not integer")
    elif not ValidYearRange(year):
        raise ArgumentError("year is not in valid range")

    if type(date_info) != str:
        raise ArgumentError("Parsing date info failed : argument is not string : {0}".format(date_info))

    if "~" not in date_info: #one-day schedule
        date_pattern = re.compile("\d{,2}\D\d{,2}\([a-zA-Z]{3}\)")
        result = date_pattern.findall(date_info)
        if len(result) != 1:
            raise PageSchemeException("date format is not valid : {0}, {1}".format(date_info, result))
        result = result[0].split("(")[0].split('-')
        if len(result) != 2:
            raise PageSchemeException("date format is not valid : {0}, {1}".format(date_info, result))
        
        try:
            month_info = int(result[0].strip())
            day_info = int(result[1].strip())
        except ValueError:
            raise PageSchemeException("unable to change date info : {0} -> {1}, {2}".format(date_info, result[0], result[1]))

        date_start = timezone.make_aware(datetime(year, month_info, day_info))
        date_end = date_start

    else:
        if len(date_info.split("~")) != 2:
            raise PageSchemeException("date format is not valid : {0}".format(date_info))
        date_pattern = re.compile("\d{,2}\D\d{,2}\([a-zA-Z]{3}\)")
        date_info = date_info.split("~")

        for i in range(2):
            result = date_pattern.findall(date_info[i])
            if len(result) != 1:
                raise PageSchemeException("date format is not valid : {0}, {1}".format(date_info,result))
            result = result[0].split("(")[0].split('-')
            if len(result) != 2:
                raise PageSchemeException("date format is not valid : {0}, {1}".format(date_info,result)) 
            try:
                month_info = int(result[0].strip())
                day_info = int(result[1].strip())
            except ValueError:
                raise PageSchemeException("unable to change date info : {0} -> {1}, {2}".format(date_info, result[0], result[1]))

            if i==0:
                date_start = timezone.make_aware(datetime(year, month_info, day_info))
            else:
                date_end = timezone.make_aware(datetime(year, month_info, day_info))

    return (date_start, date_end)




def GetParsedData(year):
    if type(year) != int:
        raise ArgumentError("year parameter is not integer")
    elif not ValidYearRange(year):
        raise ArgumentError("year is not in valid range")


    raw_data = GetRawData(year)
    parsed_data = []
    for sch in raw_data:
        date_info = sch[0] #string with date format
        desc_list = sch[1] #list
        
        (date_start, date_end) = ParseDateInfo(date_info, year)
            
        for desc in desc_list:
            desc = desc.strip().strip('-').strip()
            parsed_data.append([date_start,date_end,desc])

    return parsed_data



