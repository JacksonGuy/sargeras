import psutil
import subprocess
import setproctitle
from time import sleep

setproctitle.setproctitle("check")

while True:
    sleep(3)
    running = False
    for proc in psutil.process_iter():
        process = proc.as_dict(attrs=['name', 'pid'])
        if (process['name'] == 'master'):
            running = True
    if (running == False):
        try:
            result = subprocess.Popen(
                "python3 master.py",
                shell=True,
                text=True,
                universal_newlines=True,
                start_new_session=True
            )
            print("[Check] Relauched master process")
        except subprocess.CalledProcessError as exc:
            print(exc.output)
