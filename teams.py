import pymysql
from baseObject import baseObject
class teamsList(baseObject):
    #this is the assignment
    def __init__(self):
        self.setupObject('palmerba_nfl_teams')
