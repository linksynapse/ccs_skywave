#
#	Module Create by LEE GYEONG TAE
#					2020. 04. 16
#			Module Version 1.0.1
#					

import datetime

class Logging:
	def __init__(self,config):
		self.err = config.ERR_LOG()
		self.dbg = config.DBG_LOG()
		self.inf0 = config.INFO_LOG()
		self.level = config.LOG_LEVEL()

	def info(self,message):
		if self.level > 3:
			output = open(self.inf0,'a')
			sput = "[Info - {}] {}\r\n".format(datetime.datetime.now().strftime('%H:%M:%S'), message)
			output.write(sput)
			print(sput,end='')
			output.close()

	def debug(self,message):
		if self.level > 2:
			output = open(self.dbg,'a')
			sput = "[Debug - {}] {}\r\n".format(datetime.datetime.now().strftime('%H:%M:%S'), message)
			output.write(sput)
			print(sput,end='')
			output.close()

	def error(self,message):
		if self.level > 1:
			output = open(self.err,'a')
			sput = "[Error - {}] {}\r\n".format(datetime.datetime.now().strftime('%H:%M:%S'), message)
			output.write(sput)
			print(sput,end='')
			output.close()