import pymysql, requests
from baseObject import baseObject
from string import ascii_lowercase

class playersList(baseObject):
    #this is the assignment
    def __init__(self):
        self.setupObject('palmerba_players')
        self.agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}


    def importPlayers(self):
        print("Begin Import")
        self.connect()
        cur = self.conn.cursor(pymysql.cursors.DictCursor)

        print("Clear Players")
        dropquery = '''DROP TABLE IF EXISTS `palmerba_players`'''
        createquery = '''CREATE TABLE IF NOT EXISTS `palmerba_players` (
            `pid` INT NOT NULL AUTO_INCREMENT,
            `playername` varchar(30),
            `playerposition` varchar(4),
            `playerpicture` varchar(200),
            `playerteam` varchar(50) NOT NULL,
            PRIMARY KEY(`pid`),
            FOREIGN KEY(`playerteam`) REFERENCES palmerba_nfl_teams(`Team_Name`)
            )ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1;
                '''
        cur.execute(dropquery)
        cur.execute(createquery)

        print("Scrap Players")
        tokens = self.scrapPlayers()

        insertquery = "INSERT INTO `palmerba_players`(`playername`, `playerposition`, `playerpicture`, `playerteam`) VALUES (%s,%s,%s,%s) "
        cur.executemany(insertquery, tokens)

        print("Import Complete")

    def scrapPlayers(self):
        t = []
        for c in ascii_lowercase:
            print("Grabbing players with last name starting with: " + str(c))
            r = requests.get("https://www.footballdb.com/players/current.html?letter=" + c, headers=self.agent)

            file = open("temp.txt", "w")
            file.write(r.text)
            file.close()

            file = open("temp.txt", "r")
            i = 0
            while True:
                line = file.readline()
                if 'href="/players/' in line and "html" not in line:
                    player = self.scrapPlayer("/players/" + line.split('/players/')[1].split('"')[0])
                    if player[0] != "":
                        t.append(player)
                if "<script>" in line and i == 1:
                    break
                elif "<script>" in line:
                    i = 1


        return t

    def scrapPlayer(self,url):
        player = {}
        r = requests.get("https://www.footballdb.com" + url, headers=self.agent)
        lines = r.text.split('\n')
        for line in lines:
            if "playerimg" in line:
                player["image"] = line.split('"')[1]
                player["name"] = line.split('"')[3]
            elif 'a href="/teams/nfl' in line and "roster" in line:
                player["team"] = line.split(">")[2].split("<")[0]
            elif "Position:" in line:
                player["position"] = line.split('</b>')[1].split("<")[0]
                print(str(player))
                if "team" not in player.keys() or "name" not in player.keys():
                    return ("", "", "", "")
                return (player["name"], player["position"].strip(), player["image"], player["team"])
        return ("", "", "", "")
