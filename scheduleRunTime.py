import sqlite3
import sys
import json
import datetime
import time
# import CHIP_IO.GPIO as gpio
import wiringpi
import functions

with open(sys.argv[1],'r+') as f:
	launch_params = json.loads(f.read())
	f.close()

# setup gpio
wiringpi.wiringPiSetup()
for p in launch_params['pinMap']:
	# gpio.setup(p['pin'],gpio.OUT)
	wiringpi.pinMode(int(p['pin']), wiringpi.OUTPUT)
	# gpio.output(p['pin'],gpio.HIGH)
	wiringpi.digitalWrite(int(p['pin']), wiringpi.HIGH)

# connect to db
conn = sqlite3.connect(launch_params['db'])

# main
print('*** scheduleRunTime ***')
	# avg_rain = 0.0

while True:
	conn = sqlite3.connect(launch_params['db'])
	try:
		now = datetime.datetime.now()

		# run schedules
		schedules = functions.getSchedules(conn)
		print schedules
		zones = functions.getZones(conn)
		print zones
		for zone in zones:
			zone['status']=0

		for sch in schedules:
			sch_zone = next((item for item in zones if item['id'] == sch['zone']))
			start_date = functions.dateOfNextWeekday(sch['day'])
			start_time = datetime.datetime.strptime(sch['start_time'],'%H:%M').time()
			start_datetime = datetime.datetime.combine(start_date,start_time)
			# print('start_datetime: ' + str(start_datetime))

			end_datetime = start_datetime + datetime.timedelta(minutes=sch['duration_minutes'])
			# print('end_datetime: ' + str(end_datetime))

			if start_datetime <= now <= end_datetime:
				sch_zone['status']=1

			if sch_zone['enabled']==0:
				sch_zone['status']=0

			if ((start_datetime < now) and (end_datetime < now) and (sch['one_shot'] == 'yes')):
				functions.deleteSchedule(conn,sch['id'])

		# run zones
		current_zones = functions.getZones(conn)

		for zone in zones:
			current_zone = next((item for item in current_zones if item['id'] == zone['id']))
			if zone['status'] != current_zone['status']:
				if zone['status'] == 0:
					functions.zoneOff(conn,zone['id'])
				elif (zone['status'] == 1):
					functions.zoneOn(conn,zone['id'])
	except Exception as e:
		print('Critical Exception: ' + str(e))
		raise
	time.sleep(10)

