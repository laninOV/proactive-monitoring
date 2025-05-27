from datetime import datetime
from threading import Timer, Lock
import logic
import config

# Шаг с которым скрипт будет запускаться в минутах, используется так же и как шаг за который запрашиваются метрики
step = config.step

counter = {}
groups = {}
lock = Lock()

def wite_time(step):
    s_now = datetime.now().second
    m_now = (step - datetime.now().minute % step)
    if m_now > 0:
        wait = m_now * 60 - s_now
    else:
        wait = step * 60 - s_now
    return wait

def every_n_minute(step):
    global counter
    global groups
    logic.main_logic(counter, groups, step)

def shedule(func, step):
    with lock:
        wait = wite_time(step[0])
        Timer(wait, func, step).start()
        Timer(wait + 1, lambda: shedule(func, step)).start()

if __name__ == "__main__":
    shedule(every_n_minute, [step])
    print("ok")
