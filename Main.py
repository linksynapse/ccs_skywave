import Work
import time
import Config

if __name__ == '__main__':
    conf = Config.Config("Config/Config.ini")
    h = Work.handler(conf)
    h.__start__()
    h.__ftp__()
    h.__flask__()
