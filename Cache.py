import queue
import pickle as pkl

def SAVE_DUMPS(PATH, TEMP):
	f = open(PATH,'wb+')
	pkl.dump(TEMP, f)
	f.close()
	
def LOAD_DUMPS(PATH):
	temp = []
	try:
		f = open(PATH,'rb')
		temp = pkl.load(f)
		f.close()
	except:
		CREATE_DUMPS(PATH)
		f = open(PATH,'rb')
		temp = pkl.load(f)
		f.close()
	finally:
		return temp

def CREATE_DUMPS(PATH):
	temp = [
			{'Mapper':1,'GPIO':14,'Name':'Sensor #1','Active':True},
			{'Mapper':2,'GPIO':15,'Name':'Sensor #2','Active':True},
			{'Mapper':3,'GPIO':18,'Name':'Sensor #3','Active':True},
			{'Mapper':4,'GPIO':23,'Name':'Sensor #4','Active':True},
			{'Mapper':5,'GPIO':24,'Name':'Sensor #5','Active':True},
			{'Mapper':6,'GPIO':25,'Name':'Sensor #6','Active':True},
			{'Mapper':7,'GPIO':2,'Name':'Sensor #7','Active':True},
			{'Mapper':8,'GPIO':3,'Name':'Sensor #8','Active':True},
			{'Mapper':9,'GPIO':12,'Name':'Sensor #9','Active':True},
			{'Mapper':10,'GPIO':16,'Name':'Sensor #10','Active':True},
			{'Mapper':11,'GPIO':20,'Name':'Sensor #11','Active':True},
			{'Mapper':12,'GPIO':21,'Name':'Sensor #12','Active':True},
			{'Mapper':13,'GPIO':17,'Name':'Sensor #13','Active':True},
			{'Mapper':14,'GPIO':27,'Name':'Sensor #14','Active':True},
			{'Mapper':15,'GPIO':22,'Name':'Sensor #15','Active':True},
			{'Mapper':16,'GPIO':10,'Name':'Sensor #16','Active':True}
		]
	f = open(PATH,'wb+')
	pkl.dump(temp, f)
	f.close()