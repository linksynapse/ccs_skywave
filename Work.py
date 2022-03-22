import sqlite3
import RPi.GPIO as GPIO
import time
import threading
import datetime
import Cache
import Log
import Mapper
import sys
import psutil
import os
import json
import ftplib

from io import BytesIO
from flask import Flask, render_template, request, jsonify, send_file, Response, session, redirect, url_for

class handler:
	def __init__(self, config):
		#initalize config
		self.config = config
		#initalize logging service
		self.log = Log.Logging(self.config)
		#initalize PIN Map
		self.pinmaps = Cache.LOAD_DUMPS(self.config.PIN_LAYOUT())
		#initalize edge event
		self.boe = self.config.EDGE_BOUNCE()
		#initalize thread manager
		self.lock = threading.Lock()
		#initalize web service
		self.app = None
		#initalize ftp service
		self.ip = self.config.FTP_SERVER_IP()
		self.port = self.config.FTP_SERVER_PORT()
		self.id = self.config.FTP_SERVER_ID()
		self.pw = self.config.FTP_SERVER_PW()
		self.interval = self.config.FTP_SERVER_INTERVAL()
		self.wpw = self.config.WEB_SERVER_PW()

	#
	#
	#
	#	FTP AUTO UPLOAD Service
	#
	#
	#
	def __ftp__(self):
		t = threading.Thread(target=self.__ftp__proc__, args=[])
		t.start()

	def __ftp__proc__(self):
		try:
			while True:
				while datetime.datetime.now().minute % self.interval != 0:
					time.sleep(0.1)
				print('start automatic send data to ftp server')
				start = (datetime.datetime.now() - datetime.timedelta(minutes = self.interval)).timestamp()
				end = datetime.datetime.now().timestamp()

				conn = sqlite3.connect(self.config.DATABASE())
				c = conn.cursor()

				csv = "StartTime,EndTime,Device,SensorName,TotalCount\r\n"
				for pin in self.pinmaps:
					if pin['Active']:
						c.execute(Mapper.GetSensorCount(),(pin['GPIO'], start, end))
						TotalCount = c.fetchall()[0][0]
						csv += str(datetime.datetime.fromtimestamp(start))
						csv += ","
						csv += str(datetime.datetime.fromtimestamp(end))
						csv += ","
						csv += self.config.DEVICE_NAME()
						csv += ","
						csv += pin["Name"]
						csv += ","
						csv += str(TotalCount)
						csv += "\r\n"

				timea = datetime.datetime.now().strftime("%Y%m%d%H%M")
				filename = 'DATA/FTP/' + self.config.DEVICE_NAME() + '_' + timea + '.csv'
				f = open(filename,'w')
				f.write(csv)
				f.close()

				ftp=ftplib.FTP()
				ftp.connect(self.ip, self.port)
				ftp.login(self.id,self.pw)
				ftp.cwd("./")
				myfile = open(filename,'rb')
				ftp.storbinary('STOR ' + timea + "_" + self.config.DEVICE_NAME() + '.csv', myfile)
				myfile.close()
				ftp.close()
				time.sleep(60)
				print('Complete send to server')
		except Exception as err:
			print(str(err))
			return
	#
	#
	#
	#	Device Service
	#
	#
	#

	def __start__(self):
		#Setup BCM Mode
		GPIO.setmode(GPIO.BCM)

		for pin in self.pinmaps:
			try:
				if pin['Active']:
					self.log.info("GPIO" + "{}".format(pin['GPIO']) + " initalize start")
					self.log.debug("GPIO" + "{}".format(pin['GPIO']) + " IN/Pullup")
					GPIO.setup(pin['GPIO'],GPIO.IN, pull_up_down=GPIO.PUD_UP)

					self.log.debug("GPIO" + "{}".format(pin['GPIO']) + " create add_event_detect /event=FALLING /callback=falling_callbak /bouncetime=" "{}".format(self.config.EDGE_BOUNCE()))
					GPIO.add_event_detect(pin['GPIO'], GPIO.FALLING, callback=self.falling_callbak, bouncetime=self.config.EDGE_BOUNCE())
					self.log.debug("GPIO" + "{}".format(pin['GPIO']) + " create add_event_callback ")
					#GPIO.add_event_callback(pin['GPIO'], callback=self.falling_callbak)
				else:
					self.log.info("GPIO" + "{}".format(pin['GPIO']) + " not use")
			except KeyboardInterrupt:
				GPIO.cleanup()

			except Exception as e:
				self.log.error("GPIO" + "{}".format(pin['GPIO']) + " initalize fail" + "\r\n" + __name__ + "::" + str(sys.exc_info()[-1].tb_lineno) + " " + repr(e))
				#Disable Pin
				pin['Active'] = False
				#Save Pin data
				Cache.SAVE_DUMPS(self.config.PIN_LAYOUT(),self.pinmaps)

	def falling_callbak(self, channel):
		try:
			conn = sqlite3.connect(self.config.DATABASE())
			c = conn.cursor()
			c.execute(Mapper.GetStoreTimeQuery(),(channel, datetime.datetime.now().timestamp()))
			conn.commit()
			self.log.info("Insert row id : " + "{}".format(c.lastrowid))

			conn.close()

			self.log.info("GPIO" + "{}".format(channel) + " falling.")
		except Exception as e:
			self.log.error("GPIO" + "{}".format(channel) + " count record fail" + "\r\n" + __name__ + "::" + str(sys.exc_info()[-1].tb_lineno) + " " + repr(e))

	#
	#
	#
	#	Web Service
	#
	#
	#

	def __flask__(self):
		#Initalize Flask Engine
		self.app = Flask("WebSYS",template_folder=self.config.TEMPLATE_DIR(),static_folder=self.config.STATIC_DIR())

		#Initalize View Controller
		self.app.secret_key = "thisisaccsserverversion3"
		self.app.add_url_rule('/','MainPage', methods=['GET',], view_func=self.view_index)
		self.app.add_url_rule('/getSysinfo','JSON Query', methods=['GET',], view_func=self.view_status)
		self.app.add_url_rule('/export','Data Export', methods=['GET',], view_func=self.view_export)
		self.app.add_url_rule('/toCsv','CSV Export',methods=['POST',], view_func=self.view_csv)
		self.app.add_url_rule('/setting','Setting Page',methods=['GET',], view_func=self.view_setting)
		self.app.add_url_rule('/sethwconfig','Set HW Config',methods=['POST',], view_func=self.view_hwconfig)
		self.app.add_url_rule('/setsvrconfig','Set SVR Config',methods=['POST',], view_func=self.view_svrconfig)
		self.app.add_url_rule('/setsensor','Set sensor config',methods=['POST',], view_func=self.view_sensor)
		self.app.add_url_rule('/restart','System Restart',methods=['GET',], view_func=self.view_exit)
		self.app.add_url_rule('/network','setting nw page',methods=['GET',], view_func=self.view_network)
		self.app.add_url_rule('/setnwconfig','set network',methods=['POST',], view_func=self.view_nwconfig)
		self.app.add_url_rule('/require', 'login page', methods=['GET','POST'], view_func=self.view_login)
		self.app.add_url_rule('/logout', 'logout page', methods=['GET'], view_func=self.view_logout)
		self.app.run(host=self.config.BIND_SERVER(),port=self.config.BIND_PORT())

	def view_login(self):
		if request.method == 'POST':
			session['userpass'] = request.form['password']
			if session['userpass'] == self.wpw:
				return redirect('/')
			else:
				return redirect('/require')
		else:
			return render_template('login.html')

	def view_logout(self):
		session.pop('userpass', None)
		return redirect('/require')

	def view_index(self):
		try:
			if session['userpass'] == self.wpw:
				return render_template('index.html')
			else:
				return redirect('/require')
		except:
			return redirect('/require')

	def view_status(self):
		pid = os.getpid()
		diskInfo  = os.statvfs('/')

		cpu_usage = os.popen("ps aux | grep " + str(pid) + " | grep -v grep | awk '{print $3}'").read().replace("\n","")
		memory_usage = dict(psutil.virtual_memory()._asdict())['percent']
		disk_usage = round(((diskInfo.f_blocks - diskInfo.f_bavail) / diskInfo.f_blocks) * 100,1)
		cpu_temp = round(int(os.popen("cat /sys/class/thermal/thermal_zone0/temp").read()) / 1000,1)

		resource = {"CPU":cpu_usage, "RAM":memory_usage, "DISK":disk_usage, "TEMP":cpu_temp}
		sensor = self.pinmaps
		result = {"resource":resource,"sensor":sensor}
		return result

	def view_export(self):
		try:
			if session['userpass'] == self.wpw:
				return render_template('export.html',sensors=self.pinmaps)
			else:
				return redirect('/require')
		except:
			return redirect('/require')

	def view_csv(self):
		data = request.form.to_dict(flat=False)

		start = time.mktime(datetime.datetime.strptime(data['StartTime'][0], "%Y-%m-%d %H:%M").timetuple())
		end = time.mktime(datetime.datetime.strptime(data['EndTime'][0], "%Y-%m-%d %H:%M").timetuple())
		sensor = json.loads(data['sensors'][0])

		conn = sqlite3.connect(self.config.DATABASE())
		c = conn.cursor()

		csv = "StartTime,EndTime,Device,SensorName,TotalCount\r\n"
		for key in sensor:
			if sensor[key] == "on":
				c.execute(Mapper.GetSensorCount(),(key.replace("GPIO","",1), start, end))
				TotalCount = c.fetchall()[0][0]
				for item in self.pinmaps:
					if item["GPIO"] == int(key.replace("GPIO","",1)):
						csv += str(datetime.datetime.strptime(data['StartTime'][0], "%Y-%m-%d %H:%M"))
						csv += ","
						csv += str(datetime.datetime.strptime(data['EndTime'][0], "%Y-%m-%d %H:%M"))
						csv += ","
						csv += self.config.DEVICE_NAME()
						csv += ","
						csv += item["Name"]
						csv += ","
						csv += str(TotalCount)
						csv += "\r\n"

		response = Response(
			csv,
			mimetype="text/csv",
			content_type='application/octet-stream'
		)

		response.headers["Content-Disposition"] = "attachment; filename=export.csv"
		conn.close()

		return response
	def view_setting(self):
		try:
			if session['userpass'] == self.wpw:
				return render_template('setting.html',config=self.config, sensors=self.pinmaps)
			else:
				return redirect('/require')
		except:
			return redirect('/require')

	def view_hwconfig(self):
		try:
			if session['userpass'] == self.wpw:
				data = request.form.to_dict(flat=False)

				DEVICE_NAME = data['device_name'][0]
				self.config.SET_DEVICE_NAME(DEVICE_NAME)
				BOUNCETIME = data['bouncetime'][0]
				self.config.SET_EDGE_BOUNCE(BOUNCETIME)
				LOG_LEVEL = data['loglevel'][0]
				self.config.SET_LOG_LEVEL(LOG_LEVEL)
				LOGIN_PASS = data['wPassword'][0]
				self.config.SET_WEB_SERVER_PW(LOGIN_PASS)
				self.wpw = LOGIN_PASS
				return render_template('setting.html',config=self.config, sensors=self.pinmaps)
			else:
				return redirect('/require')
		except Exception as err:
			print(str(err))
			return redirect('/require')

	def view_svrconfig(self):
		try:
			if session['userpass'] == self.wpw:
				data = request.form.to_dict(flat=False)

				SERVER_IP = data['serverip'][0]
				self.config.SET_BIND_SERVER(SERVER_IP)
				SERVER_PORT = data['serverport'][0]
				self.config.SET_BIND_PORT(SERVER_PORT)
				FTP_IP = data['ftpip'][0]
				self.config.SET_FTP_SERVER_IP(FTP_IP)
				FTP_PORT = data['ftpport'][0]
				self.config.SET_FTP_SERVER_PORT(FTP_PORT)
				FTP_ID = data['ftpid'][0]
				self.config.SET_FTP_SERVER_ID(FTP_ID)
				FTP_PW = data['ftppw'][0]
				self.config.SET_FTP_SERVER_PW(FTP_PW)
				FTP_INTERVAL = data['ftpinterval'][0]
				self.config.SET_FTP_SERVER_INTERVAL(FTP_INTERVAL)

				return render_template('setting.html',config=self.config, sensors=self.pinmaps)
			else:
				return redirect('/require')
		except:
			return redirect('/require')

	def view_sensor(self):
		try:
			if session['userpass'] == self.wpw:
				data = request.form.to_dict(flat=False)

				for key in data:
					for i in range(len(self.pinmaps)):
						if self.pinmaps[i]["GPIO"] == int(key.replace("GPIO","",1)):
							self.pinmaps[i]["Name"] = data[key][0]

				Cache.SAVE_DUMPS(self.config.PIN_LAYOUT(),self.pinmaps)
				return render_template('setting.html',config=self.config, sensors=self.pinmaps)
			else:
				return redirect('/require')
		except:
			return redirect('/require')

	def view_exit(self):
		try:
			if session['userpass'] == self.wpw:
				os.system("sudo reboot")
				return "Restart"
			else:
				return redirect('/require')
		except:
			return redirect('/require')
		

	def view_nwconfig(self):

		try:
			if session['userpass'] == self.wpw:
				data = request.form.to_dict(flat=False)
				IP = data['ipaddr'][0]
				MASK = data['netmask'][0]
				GATEWAY = data['gateway'][0]

				if IP != "":
					if MASK != "":
						if GATEWAY != "":
							SETUP_STR = ""
							SETUP_STR += "auto eth0\r\n"
							SETUP_STR += "allow-hotplug eth0\r\n"
							SETUP_STR += "iface eth0 inet static\r\n"
							SETUP_STR += "address " + IP + "\r\n"
							SETUP_STR += "netmask " + MASK + "\r\n"
							SETUP_STR += "gateway " + GATEWAY + "\r\n"

							f = open("/etc/network/interfaces.d/eth0","w")
							f.write(SETUP_STR)

							os.system("sudo /etc/init.d/networking restart")
				else:
					os.system("sudo rm -rf /etc/network/interfaces.d/eth0")
					os.system("sudo /etc/init.d/networking restart")

				return render_template('index.html')
			else:
				return redirect('/require')
		except:
			return redirect('/require')

	def view_network(self):
		try:
			if session['userpass'] == self.wpw:
				return render_template('network.html')
			else:
				return redirect('/require')
		except:
			return redirect('/require')
