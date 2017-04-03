import sqlite3
import datetime
import CHIP_IO.GPIO as gpio
import sys
import json

with open(sys.argv[1],'r+') as f:
	launch_params = json.loads(f.read())
	f.close()

def dateOfNextWeekday(weekday):
	daysFromWeekday = weekday - datetime.datetime.now().weekday()
	if daysFromWeekday < 0:
		daysFromWeekday = daysFromWeekday + 7
	daysFromWeekday = datetime.timedelta(days=daysFromWeekday)
	return datetime.datetime.now() + daysFromWeekday

def putEvent(connection,severity,message):
	cursor = connection.cursor()
	timeStamp = datetime.datetime.now().isoformat()
	cursor.execute('INSERT INTO tEvents (timeStamp,severity,message) VALUES (?,?,?)',(timeStamp,severity,message))
	connection.commit()

def getEvents(connection):
	cursor = connection.cursor()
	cursor.execute('SELECT * FROM vEvents')
	fields = ['id','timeStamp','severity','message']
	dicts = [dict(zip(fields, d)) for d in cursor.fetchall()]
	return dicts

def getLastEvent(connection):
	cursor = connection.cursor()
	cursor.execute('SELECT * FROM vEvents ORDER BY timeStamp DESC LIMIT 1')
	fields = ['id','timeStamp','severity','message']
	dicts = [dict(zip(fields, d)) for d in cursor.fetchall()]
	if len(dicts) > 0:
		return dicts[0]
	else:
		return {}

def putSchedule(connection,zone,day,duration_minutes,start_time,one_shot):
	try:
		cursor = connection.cursor()
		start_time = datetime.datetime.strptime(start_time,'%H:%M') 
		start_time = start_time.strftime('%H:%M')	# start_time is a datetime.time() object
		cursor.execute('INSERT INTO tSchedule (zone,day,duration_minutes,start_time,one_shot) VALUES (?,?,?,?,?)',(zone,day,duration_minutes,start_time,one_shot))
		putEvent(connection,0,'putSchedule('+str(zone)+','+str(day)+','+str(duration_minutes)+','+start_time+','+str(one_shot)+')')
		connection.commit()
	except Exception as e:
		putEvent(connection,2,'putSchedule('+str(zone)+','+str(day)+','+str(duration_minutes)+','+start_time+','+str(one_shot)+'): ' + str(e))

def deleteSchedule(connection,id):
	try:
		cursor = connection.cursor()
		cursor.execute('DELETE FROM tSchedule WHERE pk_id=?',(id,))
		putEvent(connection,0,'deleteSchedule('+str(id)+')')
		connection.commit()
	except Exception as e:
		putEvent(connection,2,'deleteSchedule('+str(id)+'): ' + str(e))


def getSchedulesByZone(connection,zone):
	cursor = connection.cursor()
	cursor.execute('SELECT * FROM vSchedules WHERE zone=?',(zone,))
	fields = ['id','zone','zone_label','day','day_label','duration_minutes','start_time','one_shot']
	dicts = [dict(zip(fields, d)) for d in cursor.fetchall()]
	return dicts

def getSchedules(connection):
	cursor = connection.cursor()
	cursor.execute('SELECT * FROM vSchedules')
	fields = ['id','zone','zone_label','day','day_label','duration_minutes','start_time','one_shot']
	dicts = [dict(zip(fields, d)) for d in cursor.fetchall()]
	return dicts

def putZone(connection, zone, label):
	try:
		cursor = connection.cursor()
		cursor.execute('INSERT INTO tZone VALUES (?,?,?,?)',(zone,label,0,1))
		print('putZone('+zone+','+label+')')
		putEvent(connection,0,'putZone('+zone+','+label+')')
		connection.commit()
	except Exception as e:
		putEvent(connection,2,'putZone('+zone+','+label+'): ' + str(e))

def deleteZone(connection, zone):
	try:
		cursor = connection.cursor()
		cursor.execute('DELETE FROM tZone WHERE pk_zone=?',(zone,))
		putEvent(connection,0,'deleteZone('+str(zone)+')')
		connection.commit()
	except Exception as e:
		putEvent(connection,2,'deleteZone('+str(zone)+'): ' + str(e))

def setZoneStatus(connection,zone,status):
	cursor = connection.cursor()
	cursor.execute('UPDATE tZone SET status = ? WHERE pk_zone = ?',(status,zone))
	connection.commit()

def setZoneEnabled(connection,zone,enabled):
	cursor = connection.cursor()
	cursor.execute('UPDATE tZone SET enabled = ? WHERE pk_zone = ?',(enabled,zone))
	connection.commit()

def getZones(connection):
	cursor = connection.cursor()
	cursor.execute('SELECT * FROM vZones')
	fields = ['id','zone_label','status','status_label','enabled','enabled_label']
	dicts = [dict(zip(fields, d)) for d in cursor.fetchall()]
	for z in dicts:
		z['nextRunTime'] = None
		schedules = getSchedulesByZone(connection,z['id'])
		for sch in schedules:
			start_date = dateOfNextWeekday(sch['day'])
			start_time = datetime.datetime.strptime(sch['start_time'],'%H:%M').time()
			start_datetime = datetime.datetime.combine(start_date,start_time)
			if z['nextRunTime'] == None:
				z['nextRunTime'] = start_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')
			elif (start_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f') < z['nextRunTime']):
				z['nextRunTime'] = start_datetime.strftime('%Y-%m-%dT%H:%M:%S.%f')
			z['nextRunTimeFormatted'] = datetime.datetime.strptime(z['nextRunTime'],'%Y-%m-%dT%H:%M:%S.%f').strftime('%A %I:%M %p')
				
	return dicts

def zoneOn(connection,zone):
	setZoneStatus(connection,zone,1)
	print('zoneOn(' + str(zone) + ')')
	# pin=next(x for x in launch_params['pinMap'] if x['id']==zone)['pin']
	pin=zone
	gpio.output(pin,gpio.LOW)
	putEvent(connection,0,'zoneOn(' + str(zone) + ')')

def zoneOff(connection,zone):
	setZoneStatus(connection,zone,0)
	print('zoneOff(' + str(zone) + ')')
	# pin=next(x for x in launch_params['pinMap'] if x['id']==zone)['pin']
	pin=zone
	gpio.output(pin,gpio.HIGH)
	putEvent(connection,0,'zoneOff(' + str(zone) + ')')