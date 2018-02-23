from schedule_crawler.crawler_core.parser import *
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "schedule.settings")
import django
django.setup()
from schedule_crawler.models import ScheduleInfo

from datetime import datetime

parsed_data = GetParsedData(datetime.now().year)
db_saved_schedule = ScheduleInfo.objects.all()

for (dateStart, dateEnd, description) in parsed_data:
    new_schedule = ScheduleInfo(name=description,
    dateStart=dateStart,
    dateEnd=dateEnd)
    if new_schedule not in db_saved_schedule:
        new_schedule.save()

