import pymysql

create_table = '''CREATE TABLE `palmerba_players` (
    `pid` int NOT NULL AUTO_INCREMENT,
    `playername` varchar(30) NOT NULL,
    `playerposition` varchar(4) NOT NULL,
    `playerpicture` varchar(200) NOT NULL,
    `playerteam` varchar(50) NOT NULL,
    PRIMARY KEY (`pid`),
    FOREIGN KEY (`playerteam`) REFERENCES `palmerba_nfl_teams`(`Team_Name`)
)ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1;'''

import config
conn = pymysql.connect(host=config.DB['host'], port=config.DB['port'],
user=config.DB['user'],passwd=config.DB['passwd'], db=config.DB['db'],
autocommit=True)

cur = conn.cursor(pymysql.cursors.DictCursor)
cur.execute(create_table)

print("Work Dammit")
