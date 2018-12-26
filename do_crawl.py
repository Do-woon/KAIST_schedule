from schedule_crawler.crawler_core.parser import *
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "schedule.settings")
import django
django.setup()
from django.utils import timezone
from schedule_crawler.models import ScheduleInfo

parsed_data = GetParsedData(timezone.now().year+1)
db_saved_schedule = ScheduleInfo.objects.all()

for (dateStart, dateEnd, description) in parsed_data:
    new_schedule = ScheduleInfo(name=description,
    dateStart=dateStart,
    dateEnd=dateEnd)
    if new_schedule not in db_saved_schedule:
        with open("log/db_update.log","a") as f:
            f.write( timezone.localtime().strftime("[%Y-%m-%d-%H:%M:%S]") + " : " + new_schedule.name + " added \n" )
        new_schedule.save()

with open("log/db_update.log","a") as f:
    f.write( timezone.localtime().strftime("[%Y-%m-%d-%H:%M:%S]") + " : " )
    f.write("Crawling compledted \n\n")

