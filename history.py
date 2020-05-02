import pymysql, requests
from baseObject import baseObject

class historyList(baseObject):

    def __init__(self):
        self.setupObject('palmerba_history_stats')
