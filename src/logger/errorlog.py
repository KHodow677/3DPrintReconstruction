import datetime
from time import sleep

f = open('Swarm\errorfile.txt', "a")

def error_message(type):
    current_time = datetime.datetime.now()
    message = '[' + str(current_time) + ']\t' + type + '\n'
    return message

for i in range(0,100):
    f.write(error_message('stringing'))
    sleep(1)

f.close()