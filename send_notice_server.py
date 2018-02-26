import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "schedule.settings")
import django
django.setup()
from schedule_crawler.models import ScheduleInfo
from django.utils import timezone

#get all upcomming schedules
upcommings = ScheduleInfo.objects.all()
#filter today's schedules
todays = [schedule for schedule in upcommings if timezone.localtime(schedule.dateStart).date() == timezone.localtime().date()]
with open('/home/DoWoonKim/KAIST_schedule/log/today_schedule.log','a') as f:
    f.write(timezone.localtime().strftime("[%Y-%m-%d-%H:%M:%S]") + "\n" + "\n".join([schedule.name for schedule in todays]))
    f.write('\n')



#send message
import telegram

with open('/home/DoWoonKim/KAIST_schedule/token','r') as f:
    my_token = f.read().strip()

bot = telegram.Bot(token=my_token)

try:
    updates = bot.getUpdates(timeout=5)
except telegram.error.TimedOut:
    with open('/home/DoWoonKim/KAIST_schedule/log/error.log','a') as f:
        f.write('TimedOut Error : connection failure' + timezone.localtime().strftime("[%Y-%m-%d-%H:%M:%S]"))
        f.write('\n')
    quit()


#get the list of users to send
id_list = [up.message.chat.id for up in updates]
id_list = list(set(id_list))
with open('/home/DoWoonKim/KAIST_schedule/log/send_to.log','a') as f:
    f.write(timezone.localtime().strftime("[%Y-%m-%d-%H:%M:%S]") + " : " + ', '.join([str(your_id) for your_id in id_list]))
    f.write('\n')

for your_id in id_list:
    for schedule in todays:
        try:
            bot.sendMessage(chat_id=your_id, text=schedule.__str__())
        except telegram.error.TimedOut:
            with open('/home/DoWoonKim/KAIST_schedule/log/error.log','a') as f: 
                f.write('TimedOut Error : sending failure to ' + str(your_id) + timezone.localtime().strftime("[%Y-%m-%d-%H:%M:%S]"))
                f.write('\n')



