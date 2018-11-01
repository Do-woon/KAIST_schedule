import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "schedule.settings")
import django
django.setup()

from schedule_crawler.models import ScheduleInfo
from django.contrib.auth.models import User
from client_config.models import Client
from django.utils import timezone



import telegram
from itertools import groupby
import random
import string

def GetActiveStatus(updates):
    assert( type(updates) == list )
    if len(updates) == 0:
        return [],[]
    else:
        assert( type(updates[0]) == telegram.update.Update )

    #classify by chat_id
    updates_grouped = groupby(updates, key=lambda up: up.message.chat_id)
    newly_disabled = []
    newly_enabled = []

    for chat_id,ups in updates_grouped:
        #current message has higher priority
        for up in reversed(list(ups)):
            if '/disable' in up.message.text:
                newly_disabled.append((chat_id, up.message.chat.first_name, up.message.chat.last_name))
                break
            elif '/start' in up.message.text:
                newly_enabled.append((chat_id, up.message.chat.first_name, up.message.chat.last_name))
                break

    #check same chat_id contained in both list
    assert( not list(set(newly_disabled).intersection(newly_enabled)) )
    return newly_disabled, newly_enabled


def ModifyActiveStatus(bot):
    assert( type(bot) == telegram.bot.Bot )
    
    try:
        updates = bot.getUpdates(timeout=5)
    except telegram.error.TimedOut:
        with open('log/error.log','a') as f:
            f.write( timezone.localtime().strftime("[%Y-%m-%d-%H:%M:%S]") + " : TimeOut Error. Update failure \n\n")

    disabled, enabled = GetActiveStatus(updates)

    newly_disabled = []
    newly_enabled = []
    newly_added = []

    #assume user must send /start first time
    for chat_id, f_name, l_name in disabled:
        target = Client.objects.filter(chat_id = chat_id)

        #if not found in client
        if not target:
            with open('log/error.log','a') as f:
                f.write( timezone.localtime().strftime("[%Y-%m-%d-%H:%M:%S]") + " : {0} is not found in Client \n\n".format(chat_id))
            continue
        
        #because chat_id is unique primary key
        if not target[0].is_active():
            continue #if alarm is already disabled, continue

        target[0].disable_alarm()
        with open('log/disabled.log','a') as f:
            f.write( timezone.localtime().strftime("[%Y-%m-%d-%H:%M:%S]") + " : {0} is deactivated \n".format(chat_id) )
        newly_disabled.append( (chat_id, f_name, l_name) )


    #don't know whether user is registered already or not
    for chat_id, f_name, l_name in enabled:
        target = Client.objects.filter(chat_id=chat_id)
        if len(target) == 0:
            new_password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))
            new_user = User( username = l_name + f_name, first_name = f_name, last_name = l_name, password = new_password )
            new_user.save()

            new_client = Client( user = new_user, chat_id = chat_id )
            new_client.save()
            
            with open('log/client_added.log','a') as f:
                f.write( timezone.localtime().strftime("[%Y-%m-%d-%H:%M:%S]") + " : {0} is added \n".format(chat_id) )
            newly_added.append( (chat_id, f_name, l_name) )

        else:
            #because chat_id is unique primary key
            if target[0].is_active():
                continue #if alarm is already abled, continue
            target[0].enable_alarm()
            with open('log/enabled.log','a') as f:
                f.write( timezone.localtime().strftime("[%Y-%m-%d-%H:%M:%S]") + " : {0} is enabled \n".format(chat_id) )
            newly_enabled.append( (chat_id, f_name, l_name) )

    return newly_disabled, newly_enabled, newly_added



def assert_msg_func_param(bot, user_list):
    assert( type(user_list) == list )

    if len(user_list) == 0:
        return

    assert( len(user_list[0]) == 3 )
    assert( type(user_list[0][0]) == int )
    assert( type(user_list[0][1]) == str and type(newly_added[2]) == str )
    assert( type(bot) == telegram.bot.Bot )

def SendWelcomeMsg(bot, newly_added):
    #assert_msg_func_param( bot, newly_added )

    for chat_id, f_name, l_name in newly_added:
        try:
            bot.sendMessage(chat_id=chat_id, text="Welecom to Schedule Noticer Bot {0} {1}. You are successfully registerd.".format(f_name, l_name))
            bot.sendMessage(chat_id=chat_id, text="You can unregister by giving /disable command. User DB update will be done every 9AM(Asia/Seoul)")
        except telegram.error.TimedOut:
            continue


def SendDisabledNotice(bot, disabled):
    #assert_msg_func_param( bot, newly_disabled )

    for chat_id, f_name, l_name in disabled:
        try:
            bot.sendMessage(chat_id=chat_id, text="{0} {1}, you are successfully unregisterd.".format(f_name, l_name))
        except telegram.error.TimedOut:
            continue


def SendEnabledNotice(bot, enabled):
    #assert_msg_func_param( bot, newly_enabled )

    for chat_id, f_name, l_name in enabled:
        try:
            bot.sendMessage(chat_id=chat_id, text="{0} {1}, you are successfully registerd.".format(f_name, l_name))
        except telegram.error.TimedOut:
            continue

def SendScheduleNotice(bot, today_schedules):
    assert( type(bot) == telegram.bot.Bot )

    receivers = Client.objects.filter(alarm_active=True)
    with open('log/send_to.log','a') as f:
        f.write( timezone.localtime().strftime("[%Y-%m-%d-%H:%M:%S]") + " : {0} \n\n".format(', '.join([str(p.chat_id) for p in receivers])))


    for client in receivers:
        for schedule in today_schedules:
            try:
                bot.sendMessage(chat_id=client.chat_id, text=schedule.__str__())
            except telegram.error.TimedOut:
                with open('log/error.log','a') as f:
                    f.write( timezone.localtime().strftime("[%Y-%m-%d-%H:%M:%S]") + " : TimeOut Error. Message sending failure \n\n" ) 
            except telegram.error.Unauthorized:
                with open('log/error.log','a') as f:
                    f.write(  timezone.localtime().strftime("[%Y-%m-%d-%H:%M:%S]") + " : User Unauthorized Error. Message sending failure \n\n" ) 







#get all upcomming schedules
upcommings = ScheduleInfo.objects.all()
#filter today's schedules
todays = [schedule for schedule in upcommings if timezone.localtime(schedule.dateStart).date() == timezone.localtime().date()]
with open('log/today_schedule.log','a') as f:
    f.write(timezone.localtime().strftime("[%Y-%m-%d-%H:%M:%S]") + "\n" + "\n".join([schedule.name for schedule in todays]))
    f.write('\n')


with open('token','r') as f:
    my_token = f.read().strip()

bot = telegram.Bot(token=my_token)
        

new_disabled, new_enabled, new_added = ModifyActiveStatus(bot)
print( new_disabled, 'are disabled')
print( new_enabled, 'are enabled')
print( new_added, 'are added')
SendDisabledNotice(bot, new_disabled)
SendEnabledNotice(bot, new_enabled)
SendWelcomeMsg(bot, new_added)
SendScheduleNotice(bot, todays)
