import pymysql, requests
import scipy.stats as st
import numpy as np
import random
import math

class simulatorRunner():
    def __init__(self,home,away,muid):
        self.hometeam = home
        self.awayteam = away
        if home == away:
            self.awayteam += " 2"
        self.muid = muid
        self.team_stats = []
        self.aggregated_team_stats = []
        self.homestatline = {'Team_Name': home, 'Rush_Attempts': 0, 'Rush_Yards': 0, 'Rush_TDs': 0, 'Passing_Completions': 0, 'Passing_Attempts': 0, 'Pass_Yards': 0, 'Pass_TDs': 0, 'Interceptions': 0, 'Sacks_Allowed': 0, 'Sacked_Yards': 0, 'Fumbles': 0, 'Penalties': 0, 'Penalty_Yards': 0, 'Time_Of_Possession': 0, 'matchupid': muid}
        self.awaystatline = {'Team_Name': away, 'Rush_Attempts': 0, 'Rush_Yards': 0, 'Rush_TDs': 0, 'Passing_Completions': 0, 'Passing_Attempts': 0, 'Pass_Yards': 0, 'Pass_TDs': 0, 'Interceptions': 0, 'Sacks_Allowed': 0, 'Sacked_Yards': 0, 'Fumbles': 0, 'Penalties': 0, 'Penalty_Yards': 0, 'Time_Of_Possession': 0, 'matchupid': muid}
        self.homescore = 0
        self.awayscore = 0
        self.conn = None
        self.matchtable = "palmerba_match_history"
        self.historystats = "palmerba_history_stats"
        self.connect()

    def connect(self):
        import config
        self.conn = pymysql.connect(host=config.DB['host'], port=config.DB['port'],
        user=config.DB['user'],passwd=config.DB['passwd'], db=config.DB['db'],
        autocommit=True)

    def format_sql_return(self, fetched, index):
        temp = []
        for value in fetched:
            for key in value.keys():
                if key != "id":
                    temp.append(value[key])
        return temp

    def grabStats(self):
        print("Grabbing Stats")
        cur = self.conn.cursor(pymysql.cursors.DictCursor)

        games_headers = ['Rush_Attempts', 'Rush_Yards', 'Rush_TDs', 'Passing_Completions', 'Passing_Attempts', 'Pass_Yards', 'Pass_TDs', 'Interceptions', 'Sacks_Allowed', 'Sacked_Yards', 'Fumbles', 'Penalties', 'Penalty_Yards']
        games_select_query = '''SELECT * FROM (SELECT id, {field} FROM palmerba_nfl_game_offense as off WHERE Team_Name LIKE %s) AS Offense UNION (SELECT id, {field} FROM palmerba_nfl_game_defense as def WHERE Team_Name LIKE %s) '''
        time_query = '''SELECT id, `Time_Of_Possession` FROM palmerba_nfl_game_offense WHERE Team_Name LIKE %s '''

        print("Getting Stats")
        home_offensive_stats = []
        away_offensive_stats = []
        for header in games_headers:
            if header == "Time_Of_Possession":
                break
            query = games_select_query.format(field=header)
            cur.execute(query, ("%" + self.hometeam + "%", "%" + self.awayteam + "%"))
            home_offensive_stats.append(self.format_sql_return(cur.fetchall(), 1))
            cur.execute(query, ("%" + self.hometeam + "%", "%" + self.awayteam + "%"))
            away_offensive_stats.append(self.format_sql_return(cur.fetchall(), 1))


        cur.execute(time_query, ("%" + self.hometeam + "%"))
        home_offensive_stats.append(self.format_sql_return(cur.fetchall(), 1))
        cur.execute(time_query, ("%" + self.awayteam + "%"))
        away_offensive_stats.append(self.format_sql_return(cur.fetchall(), 1))

        self.team_stats.append({"Team": self.hometeam, "Stats": home_offensive_stats})
        self.team_stats.append({"Team": self.awayteam, "Stats": away_offensive_stats})

    def createAggregates(self):
        self.grabStats()
        for team in self.team_stats:
            rush_averages = []
            rush_total_att = 0
            i = 0
            for rush_att in team["Stats"][0]:
                rush_total_att += rush_att
                rush_yards = team["Stats"][1][i]
                rush_averages.append(rush_yards/float(rush_att))
                i += 1

            pass_averages = []
            pass_total_comp = 0
            i = 0
            for pass_comp in team["Stats"][3]:
                pass_total_comp += pass_comp
                pass_averages.append(team["Stats"][5][i]/float(pass_comp))
                i += 1

            pass_total_att = 0
            int_averages = []
            sack_averages = []
            penalty_averages = []
            fumble_averages = []
            play_time = []
            i = 0
            for pass_att in team["Stats"][4]:
                int_averages.append(team["Stats"][7][i]/float(pass_att))
                sack_averages.append(team["Stats"][8][i]/float(pass_att))
                pass_total_att += pass_att
                total_plays = pass_att + team["Stats"][0][i]
                fumble_averages.append(team["Stats"][10][i]/float(total_plays))
                penalty_averages.append(team["Stats"][11][i]/float(total_plays))
                if i < len(team["Stats"][13]):
                    t_o_p = int(team["Stats"][13][i][0:2])*60 + int(team["Stats"][13][i][3:5])
                    play_time.append(t_o_p/float(total_plays))
                i += 1

            sack_yards_average = []
            i = 0
            for sacks in team["Stats"][8]:
                if int(sacks) != 0:
                    sack_yards_average.append(team["Stats"][9][i]/float(sacks))
                else:
                    sack_averages.append(0)

            team_stats_all = {"Team": team["Team"], "Rush_Stats": {"Mean_Rush": np.mean(rush_averages), "Std_Rush": np.std(rush_averages), "Rush_Attempts": rush_total_att}, "Passing_Stats": {"Mean_Pass": np.mean(pass_averages), "Std_Pass": np.std(pass_averages), "Passing_Completions": pass_total_comp, "Passing_Attempts": pass_total_att, "Mean_Int": np.mean(int_averages), "Std_Int": np.std(int_averages), "Mean_Sack": np.mean(sack_averages), "Std_Sack": np.std(sack_averages), "Mean_Sack_Yards": np.mean(sack_yards_average), "Std_Sack_Yards": np.mean(sack_yards_average)}, "Per_Play_Stats": {"Mean_Fumbles": np.mean(fumble_averages), "Std_Fumbles": np.std(fumble_averages), "Mean_TOP": np.mean(play_time), "Std_TOP": np.std(play_time), "Rush_To_Pass": rush_total_att/float(pass_total_att + rush_total_att)}}

            self.aggregated_team_stats.append(team_stats_all)

    def runPoss(self,team_stats, statline, yardline):
        has_poss = True
        down = 1
        first_down_line = yardline + 10
        drive_time = 0
        while has_poss:
            if down >= 4:
                if yardline > 60:
                    return "Score@3@Kick@" + str(drive_time), statline
                else:
                    return "Turnover@25@Down@" + str(drive_time), statline
            run_pass = random.random()

            if run_pass <= team_stats["Per_Play_Stats"]["Rush_To_Pass"]:
                statline["Rush_Attempts"] += 1

                yards = random.normalvariate(team_stats["Rush_Stats"]["Mean_Rush"], team_stats["Rush_Stats"]["Std_Rush"])
                yardline += yards
                statline["Rush_Yards"] += yards

                t = random.normalvariate(team_stats["Per_Play_Stats"]["Mean_TOP"], team_stats["Per_Play_Stats"]["Std_TOP"])
                drive_time += t
                statline["Time_Of_Possession"] += t

                if random.normalvariate(team_stats["Per_Play_Stats"]["Mean_Fumbles"], team_stats["Per_Play_Stats"]["Std_Fumbles"]) > 1:
                    statline["Fumbles"] += 1
                    return "Turnover@" + str(yardline)+ "@Fumble@" + str(drive_time), statline
                else:
                    down += 1
                    if yardline >= 100:
                        statline["Rush_TDs"] += 1
                        return "Score@7@Rush@" + str(drive_time), statline
                    elif yardline >= first_down_line:
                        down = 1
                        first_down_line = yardline + 10
            else:
                statline["Passing_Attempts"] += 1

                if random.normalvariate(team_stats["Passing_Stats"]["Mean_Sack"], team_stats["Passing_Stats"]["Std_Sack"]) > 1:
                    statline["Sacks_Allowed"] += 1

                    sackyard = random.normalvariate(team_stats["Passing_Stats"]["Mean_Sack_Yards"], team_stats["Passing_Stats"]["Std_Sack_Yards"])
                    yardline -= sackyard
                    statline["Sacked_Yards"] += sackyard

                    t = random.normalvariate(team_stats["Per_Play_Stats"]["Mean_TOP"], team_stats["Per_Play_Stats"]["Std_TOP"])
                    drive_time += t
                    statline["Time_Of_Possession"] += t

                    if random.normalvariate(team_stats["Per_Play_Stats"]["Mean_Fumbles"], team_stats["Per_Play_Stats"]["Std_Fumbles"]) > 1:
                        statline["Fumbles"] += 1
                        return "Turnover@" + str(yardline) + "@Fumble@" + str(drive_time), statline

                    down += 1

                elif random.random() > team_stats["Passing_Stats"]["Passing_Completions"]/float(team_stats["Passing_Stats"]["Passing_Attempts"]):
                    drive_time += 5
                    down += 1
                elif random.normalvariate(team_stats["Passing_Stats"]["Mean_Int"], team_stats["Passing_Stats"]["Std_Int"]) > 1:
                    statline["Interceptions"] += 1
                    return "Turnover@" + str(yardline) + "@Interception@" + str(drive_time), statline
                else:
                    statline["Passing_Completions"] += 1

                    pass_yard = random.normalvariate(team_stats["Passing_Stats"]["Mean_Pass"], team_stats["Passing_Stats"]["Std_Pass"])
                    yardline += pass_yard
                    statline["Pass_Yards"] += pass_yard

                    t = random.normalvariate(team_stats["Per_Play_Stats"]["Mean_TOP"], team_stats["Per_Play_Stats"]["Std_TOP"])
                    drive_time += t
                    statline["Time_Of_Possession"] += t

                    if random.normalvariate(team_stats["Per_Play_Stats"]["Mean_Fumbles"], team_stats["Per_Play_Stats"]["Std_Fumbles"]) > 1:
                        statline["Fumbles"] += 1
                        return "Turnover@" + str(yardline) + "@Fumble@" + str(drive_time), statline
                    else:
                        down += 1
                        if yardline >= 100:
                            statline["Pass_TDs"] += 1
                            return "Score@7@Pass@" + str(drive_time), statline
                        elif yardline >= first_down_line:
                            down = 1
                            first_down_line = yardline + 10

    def runSim(self):
        print("Creating Aggregates")
        self.createAggregates()

        print("Game Time!")
        game_time = 0
        kick_off = random.random()

        score = {self.hometeam: 0, self.awayteam: 0}
        curr_possession = self.hometeam
        if kick_off > .5:
            curr_possession = self.awayteam
        yardline = 25
        while game_time <= 3600:
            print("What's going on")
            if curr_possession == self.hometeam:
                possession_outcome, self.homestatline = self.runPoss(self.aggregated_team_stats[0], self.homestatline, yardline)
                split = possession_outcome.split("@")
                if split[0] == "Turnover":
                    if int(split[1]) >= 100:
                        yardline = 25
                        game_time += float(split[3])
                    else:
                        yardline = int(split[1])
                        game_time += float(split[3])
                else:
                    score[curr_possession] += int(split[1])
                    yardline = 25
                    game_time += float(split[3])
                curr_possession = self.awayteam
            else:
                possession_outcome, self.awaystatline = self.runPoss(self.aggregated_team_stats[1],self.awaystatline, yardline)
                split = possession_outcome.split("@")
                if split[0] == "Turnover":
                    if int(split[1]) >= 100:
                        yardline = 25
                        game_time += float(split[3])
                    else:
                        yardline = int(split[1])
                        game_time += float(split[3])
                else:
                    score[curr_possession] += int(split[1])
                    yardline = 25
                    game_time += float(split[3])
                curr_possession = self.hometeam
        self.hometeamscore = score[self.hometeam]
        self.awayteamscore = score[self.awayteam]

    def addMatch(self):
        cur = self.conn.cursor(pymysql.cursors.DictCursor)

        history_insertquery = 'INSERT INTO `' + self.historystats + '` ('
        history_values = ' VALUES ('

        for key in self.homestatline.keys():
            history_insertquery += key + ","
            history_values += '%s,'

        for key in self.homestatline.keys():
            if key != "Team_Name" and math.isnan(self.homestatline[key]):
                self.homestatline[key] = 0
            if key != "Team_Name" and math.isnan(self.awaystatline[key]):
                self.awaystatline[key] = 0

        history_insertquery = history_insertquery[:-1] + ") " + history_values[:-1] + ") "
        home_tokens = (self.homestatline['Team_Name'], self.homestatline['Rush_Attempts'], int(self.homestatline['Rush_Yards']), self.homestatline['Rush_TDs'], self.homestatline['Passing_Completions'], self.homestatline['Passing_Attempts'], int(self.homestatline['Pass_Yards']), self.homestatline['Pass_TDs'], self.homestatline['Interceptions'], self.homestatline['Sacks_Allowed'], self.homestatline['Sacked_Yards'], self.homestatline['Fumbles'], self.homestatline['Penalties'], self.homestatline['Penalty_Yards'], int(self.homestatline['Time_Of_Possession']), self.homestatline['matchupid'])

        away_tokens = (self.awaystatline['Team_Name'], self.awaystatline['Rush_Attempts'], int(self.awaystatline['Rush_Yards']), self.awaystatline['Rush_TDs'], self.awaystatline['Passing_Completions'], self.awaystatline['Passing_Attempts'], int(self.awaystatline['Pass_Yards']), self.awaystatline['Pass_TDs'], self.awaystatline['Interceptions'], self.awaystatline['Sacks_Allowed'], self.awaystatline['Sacked_Yards'], self.awaystatline['Fumbles'], self.awaystatline['Penalties'], self.awaystatline['Penalty_Yards'], int(self.awaystatline['Time_Of_Possession']), self.awaystatline['matchupid'])

        print(str(home_tokens))
        print(str(away_tokens))
        cur.execute(history_insertquery, home_tokens)
        cur.execute(history_insertquery, away_tokens)
