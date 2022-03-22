def GetStoreTimeQuery():
	Query = """
		INSERT INTO STORE_TICK_TIME VALUES(?,?)
	"""
	return Query


def GetSensorCount():
	Query = """
		SELECT COUNT(*) AS Count FROM STORE_TICK_TIME WHERE channel = ? AND time BETWEEN ? AND ?
	"""
	return Query