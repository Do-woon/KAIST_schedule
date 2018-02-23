import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "schedule.settings")
import django
django.setup()
from schedule_crawler.models import ScheduleInfo
from datetime import datetime


#get all upcomming schedules
upcommings = ScheduleInfo.objects.all()
#filter today's schedules
todays = [schedule for schedule in upcommings if schedule.dateStart.date() == datetime.now().date()]
with open('log/today_schedule','a') as f:
    f.write(datetime.now().strftime("[%Y-%m-%d-%H:%M:%S]") + "\n" + "\n".join([schedule.name for schedule in todays]))



#send message
import telegram

with open('token','r') as f:
    my_token = f.read().strip()

bot = telegram.Bot(token=my_token)

try:
    updates = bot.getUpdates()
except telegram.error.TimedOut:
    with open('log/error.log','a') as f:
        f.write('TimedOut Error : connection failure' + datetime.now().strftime("[%Y-%m-%d-%H:%M:%S]"))
    quit()


#get the list of users to send
id_list = [up.message.chat.id for up in updates]
id_list = list(set(id_list))
with open('log/send.log','a') as f:
    f.write(datetime.now().strftime("[%Y-%m-%d-%H:%M:%S]") + " : " + ', '.join([str(your_id) for your_id in id_list]))

for your_id in id_list:
    for schedule in todays:
        try:
            bot.sendMessage(chat_id=your_id, text=schedule.name)
        except telegram.error.TimedOut:
            with open('log/error.log','a') as f: 
                f.write('TimedOut Error : sending failure to ' + str(your_id) + datetime.now().strftime("[%Y-%m-%d-%H:%M:%S]"))



