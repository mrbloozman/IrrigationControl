import sqlite3
# import scheduleRunTime
# import weatherLog
import functions
import sys
import os
import json
import datetime
import time
from flask import Flask, render_template, request
# from flask.ext.basicauth import BasicAuth
import pyjade
# import threading
# import CHIP_IO.GPIO as gpio
import requests


with open(sys.argv[1],'r+') as f:
	launch_params = json.loads(f.read())
	f.close()


# webapp
app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')
# app.config['BASIC_AUTH_USERNAME'] = 'mark'
# app.config['BASIC_AUTH_PASSWORD'] = 'password'

# basic_auth = BasicAuth(app)

class results:
	def __init__(self):
		self.page=0
		self.size=10
		self.results=[]

	def load(self,data):
		self.results=data

	def resize(self,newsize):
		cursor = self.page*self.size
		self.size = newsize
		self.page = int(cursor/self.size)

	def current(self):
		start = self.page*self.size
		end = start+self.size
		return self.results[start:end]

	def next(self):
		if ((self.page+1)*self.size) < len(self.results):
			self.page = self.page+1
		return self.current()

	def previous(self):
		if (self.page-1) >= 0:
			self.page = self.page-1
		return self.current()

eventsResults = results()


@app.route("/")
def home():
	try:
		# r = requests.get(launch_params['temp'])
		# temp = r.text
		# r = requests.get(launch_params['humidity'])
		# humidity = r.text
		# weatherData = {'temp':temp,'humidity':humidity}
		weatherData = {'temp':0,'humidity':0}

		conn = sqlite3.connect(launch_params['db'])
		zones = functions.getZones(conn)
		lastEvent = functions.getLastEvent(conn)
		schedules = functions.getSchedules(conn)
		
		return render_template('home.jade',lp=launch_params,weatherData=weatherData)
	except Exception as e:
		print(str(e))
		return str(e)

@app.route('/putZone', methods=['POST'])
def putZone():
	try:
		if request.method == 'POST':
			conn = sqlite3.connect(launch_params['db'])
			print(request.form)
			functions.putZone(conn,request.form['zoneId'],request.form['zoneLabel'])
			event = functions.getLastEvent(conn)
		return zones(event)
	except Exception as e:
		return zones(str(e))

@app.route('/deleteZone', methods=['POST'])
def deleteZone():
	try:
		if request.method == 'POST':
			conn = sqlite3.connect(launch_params['db'])
			functions.deleteZone(conn,request.form['zoneId'])
			event = functions.getLastEvent(conn)
			return zones(event)
	except Exception as e:
		return zones(str(e))

@app.route('/setZoneEnabled',methods=['POST'])
def setZoneEnabled():
	try:
		if request.method == 'POST':
			conn = sqlite3.connect(launch_params['db'])
			print(request.form)
			functions.setZoneEnabled(conn,request.form['zoneId'],int(request.form['enabled']))
			return zones()
	except Exception as e:
		return zones(str(e))	

@app.route('/putSchedule', methods=['POST'])
def putSchedule():
	try:
		if request.method == 'POST':
			conn = sqlite3.connect(launch_params['db'])
			print(request.form)
			functions.putSchedule(conn,request.form['zoneId'],int(request.form['day']),int(request.form['duration_minutes']),request.form['start_time'],int(request.form['one_shot']))
			event = functions.getLastEvent(conn)
		return schedules(event)
	except Exception as e:
		return schedules(str(e))

@app.route('/editSchedule', methods=['POST'])
def editSchedule():
	try:
		if request.method == 'POST':
			conn = sqlite3.connect(launch_params['db'])
			print(request.form)
			functions.editSchedule(conn,request.form['sch_id'],request.form['zoneId'],int(request.form['day']),int(request.form['duration_minutes']),request.form['start_time'],int(request.form['one_shot']))
			event = functions.getLastEvent(conn)
		return schedules(event)
	except Exception as e:
		return schedules(str(e))

@app.route('/deleteSchedule', methods=['POST'])
def deleteSchedule():
	try:
		if request.method == 'POST':
			conn = sqlite3.connect(launch_params['db'])
			print(request.form)
			functions.deleteSchedule(conn,int(request.form['id']))
			event = functions.getLastEvent(conn)
		return schedules(event)
	except Exception as e:
		return schedules(str(e))

@app.route('/zones')
# @basic_auth.required
def zones(event=None):
	conn = sqlite3.connect(launch_params['db'])
	zones = functions.getZones(conn)
	return render_template('zones.jade',zones=zones,event=event,pinMap=launch_params['pinMap'])

@app.route('/schedules')
# @basic_auth.required
def schedules(event=None):
	conn = sqlite3.connect(launch_params['db'])
	zones = functions.getZones(conn)
	# print str(zones)
	schedules = functions.getSchedules(conn)
	# print str(schedules)
	return render_template('schedules.jade',schedules=schedules,zones=zones,event=event)

@app.route('/events')
def events():
	conn = sqlite3.connect(launch_params['db'])
	events = functions.getEvents(conn)
	eventsResults.load(events)

	if request.args.get('size'):
		eventsResults.resize(int(request.args.get('size')))

	if request.args.get('page'):
		if request.args.get('page')=='next':
			pageResults=eventsResults.next()
		elif request.args.get('page')=='previous':
			pageResults=eventsResults.previous()
	else:
		pageResults=eventsResults.current()
	return render_template('events.jade',events=pageResults)


if __name__ == '__main__':
	print('*** webservRunTime ***')
	app.run(host='0.0.0.0', port=80)

