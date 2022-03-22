import configparser
import base64

class Config:
	def __init__(self, path):
		self.path = path
		self.config = configparser.ConfigParser()
		self.config.read_file(open(path))

	def PIN_LAYOUT(self):
		return self.config.get('HARDWARE','SYSTEM_GPIO_PIN_LAYOUT')

	def EDGE_BOUNCE(self):
		return int(self.config.get('HARDWARE','FALLING_EDGE_BOUNCE_TIME'))

	def ERR_LOG(self):
		return self.config.get('SYSTEM','ERROR_LOG_FILE')

	def DBG_LOG(self):
		return self.config.get('SYSTEM','DEBUG_LOG_FILE')

	def INFO_LOG(self):
		return self.config.get('SYSTEM','INFO_LOG_FILE')

	def LOG_LEVEL(self):
		return int(self.config.get('SYSTEM','SYS_LOG_LEVEL'))

	def DATABASE(self):
		return self.config.get('SYSTEM','DATABASE_FILE')

	def BIND_PORT(self):
		return int(self.config.get('SERVER','DEFAULT_BIND_PORT'))

	def BIND_SERVER(self):
		return self.config.get('SERVER','DEFAULT_BIND_ADDRESS')

	def STATIC_DIR(self):
		return self.config.get('SERVER','DEFAULT_STATIC_DIR')

	def TEMPLATE_DIR(self):
		return self.config.get('SERVER','DEFAULT_TEMPLATE_DIR')

	def DEVICE_NAME(self):
		return self.config.get('DEVICE','DEVICE_NAME')

	def FTP_SERVER_IP(self):
		return self.config.get('SERVER','DEFAULT_SERVER_UPLOAD_IP')

	def FTP_SERVER_PORT(self):
		return int(self.config.get('SERVER','DEFAULT_SERVER_UPLOAD_PORT'))

	def FTP_SERVER_ID(self):
		return self.config.get('SERVER','DEFAULT_SERVER_UPLOAD_ID')

	def FTP_SERVER_PW(self):
		return self.config.get('SERVER','DEFAULT_SERVER_UPLOAD_PW')

	def FTP_SERVER_INTERVAL(self):
		return int(self.config.get('SERVER','DEFAULT_SERVER_UPLOAD_INTERVAL'))


	def SET_FTP_SERVER_IP(self, ip):
		self.config.set('SERVER','DEFAULT_SERVER_UPLOAD_IP',ip)
		with open(self.path, 'w') as configfile:    # save
			self.config.write(configfile)
		return True

	def SET_FTP_SERVER_PORT(self,port):
		self.config.set('SERVER','DEFAULT_SERVER_UPLOAD_PORT',str(port))
		with open(self.path, 'w') as configfile:    # save
			self.config.write(configfile)
		return True

	def SET_FTP_SERVER_ID(self, id):
		self.config.set('SERVER','DEFAULT_SERVER_UPLOAD_ID',id)
		with open(self.path, 'w') as configfile:    # save
			self.config.write(configfile)
		return True

	def SET_FTP_SERVER_PW(self, pw):
		self.config.set('SERVER','DEFAULT_SERVER_UPLOAD_PW',pw)
		with open(self.path, 'w') as configfile:    # save
			self.config.write(configfile)
		return True

	def SET_FTP_SERVER_INTERVAL(self, time):
		self.config.set('SERVER','DEFAULT_SERVER_UPLOAD_INTERVAL',str(time))
		with open(self.path, 'w') as configfile:    # save
			self.config.write(configfile)
		return True


	def SET_LOG_LEVEL(self, level):
		self.config.set('SYSTEM','SYS_LOG_LEVEL',str(level))
		with open(self.path, 'w') as configfile:    # save
			self.config.write(configfile)
		return True

	def SET_BIND_PORT(self,port):
		self.config.set('SERVER','DEFAULT_BIND_PORT',str(port))
		with open(self.path, 'w') as configfile:    # save
			self.config.write(configfile)
		return True

	def SET_BIND_SERVER(self, ipaddr):
		self.config.set('SERVER','DEFAULT_BIND_ADDRESS',ipaddr)
		with open(self.path, 'w') as configfile:    # save
			self.config.write(configfile)
		return True

	def SET_DEVICE_NAME(self, name):
		self.config.set('DEVICE','DEVICE_NAME',name)
		with open(self.path, 'w') as configfile:    # save
			self.config.write(configfile)
		return True

	def SET_EDGE_BOUNCE(self, time):
		self.config.set('HARDWARE','FALLING_EDGE_BOUNCE_TIME',str(time))
		with open(self.path, 'w') as configfile:    # save
			self.config.write(configfile)
		return True

	def WEB_SERVER_PW(self):
		return self.config.get('SERVER','DEFAULT_ADMIN_PASSWORD')

	def SET_WEB_SERVER_PW(self, password):
		self.config.set('SERVER','DEFAULT_ADMIN_PASSWORD',str(password))
		with open(self.path, 'w') as configfile:    # save
			self.config.write(configfile)
		return True