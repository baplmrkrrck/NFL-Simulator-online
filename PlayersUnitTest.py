from players import playersList
import pymysql

import config
conn = pymysql.connect(host=config.DB['host'], port=config.DB['port'],
user=config.DB['user'],passwd=config.DB['passwd'], db=config.DB['db'],
autocommit=True)
cur = conn.cursor(pymysql.cursors.DictCursor)

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

p = playersList()
p.importPlayers()
