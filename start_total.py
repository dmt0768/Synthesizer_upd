#!/home/debian/server_synth/venv/bin/python3
import os
import time

time.sleep(20)
os.system('git -C /home/debian/server_synth/ stash')
os.system('git -C /home/debian/server_synth/ pull')
os.system('/home/debian/server_synth/synth_init.py')
os.system('/home/debian/server_synth/server/manage.py runserver 192.168.7.2:8080')


