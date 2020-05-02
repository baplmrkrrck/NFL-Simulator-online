import pymysql
from baseObject import baseObject
class usersList(baseObject):
    #this is the assignment
    def __init__(self):
        self.setupObject('palmerba_users')

    def verifyNew(self,n=0):
        self.errorList = []

        c = usersList()
        c.getByField('username',self.data[n]['username'])
        if len(c.data) > 0:
            self.errorList.append("Username is already registered.")

        c.getByField('email',self.data[n]['email'])
        if len(c.data) > 0:
            self.errorList.append("Username is already registered.")

        if len(self.data[n]['fname']) == 0:
            self.errorList.append("First name cannot be blank.")
        if len(self.data[n]['lname']) == 0:
            self.errorList.append("Last name cannot be blank.")
        #Add if statements for validation of other fields

        if len(self.errorList) > 0:
            return False
        else:
            return True
    def verifyChange(self,n=0):
        self.errorList = []

        c = usersList()
        c.getByField('username',self.data[n]['username'])
        #print(c.data)
        if len(c.data) > 0:
            print(self.data[n])
            print(c.data[0])
            if str(self.data[n]['id']) != str(c.data[0]['id']):
                self.errorList.append("Username is already registered.")


        if len(self.data[n]['fname']) == 0:
            self.errorList.append("First name cannot be blank.")
        if len(self.data[n]['lname']) == 0:
            self.errorList.append("Last name cannot be blank.")

        if len(self.errorList) > 0:
            return False
        else:
            return True
    def tryLogin(self,username,pw):
        sql = 'SELECT * FROM `' + self.tn + '` WHERE `username` = %s AND `password` = %s;'
        tokens = (username,pw)
        self.connect()
        cur = self.conn.cursor(pymysql.cursors.DictCursor)
        #print(sql)
        #print(tokens)
        cur.execute(sql,tokens)
        self.data = []
        n=0
        for row in cur:
            self.data.append(row)
            n+=1
        if n > 0:
            return True
        else:
            return False
