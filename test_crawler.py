from parser import *
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "schedule.settings")
import django
django.setup()
from schedule_crawler.models import ScheduleInfo
parsed_data = GetParsedData(2018)


for (dateStart, dateEnd, description) in parsed_data:
    ScheduleInfo(name=description,
    dateStart=dateStart,
    dateEnd=dateEnd).save()

