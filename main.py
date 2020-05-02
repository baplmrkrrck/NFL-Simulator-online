from flask import Flask
from flask import render_template
from flask import request,session, redirect, url_for, escape,send_from_directory,make_response
from users import usersList
from players import playersList
from teams import teamsList
from matchHistory import matchHistory
from simulator import simulatorRunner
from stats import matchstats
import pymysql,json,time

from flask_session import Session  #serverside sessions

#https://github.com/baplmrkrrck/NFL-Simulator-online

app = Flask(__name__,static_url_path='')

SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)

@app.route('/set')
def set():
    session['time'] = time.time()
    return 'set'

@app.route('/get')
def get():
    return str(session['time'])

@app.route('/login',methods = ['GET','POST'])
def login():
    '''
    -check login
    -set session
    -redirect to menu
    -check session on login pages
    '''
    print('-------------------------')
    if request.form.get('username') is not None and request.form.get('password') is not None:
        c = usersList()
        if c.tryLogin(request.form.get('username'),request.form.get('password')):
            print('login ok')
            session['user'] = c.data[0]
            session['active'] = time.time()

            return redirect('main')
        else:
            print('login failed')
            return render_template('login.html', title='Login', msg='Incorrect login.')
    else:
        if 'msg' not in session.keys() or session['msg'] is None:
            m = 'Type your email and password to continue.'
        else:
            m = session['msg']
            session['msg'] = None
        return render_template('login.html', title='Login', msg=m)

@app.route('/logout',methods = ['GET','POST'])
def logout():
    del session['user']
    del session['active']
    return render_template('login.html', title='Login', msg='Logged out.')

@app.route('/main')
def main():
    if checkSession() == False:
        return redirect('login')
    c = usersList()
    c.getById(session['user']['userid'])

    return render_template('main.html', title='main',  user=c.data[0])

@app.route('/')
def home():
    return redirect('login')

@app.route('/user')
def user():
    if checkSession() == False:
        return redirect('login')
    c = usersList()
    if request.args.get(c.pk) is None:
        return render_template('error.html', msg='No user id given.')

    c.getById(request.args.get(c.pk))
    if len(c.data) <= 0:
        return render_template('error.html', msg='user not found.')

    print(c.data)
    return render_template('user.html', title='user ',  user=c.data[0])

@app.route('/newuser',methods = ['GET', 'POST'])
def newuser():
    if checkSession() == False:
        return redirect('login')
    if request.form.get('fname') is None:
        c = usersList()
        c.set('username','')
        c.set('fname','')
        c.set('lname','')
        c.set('email','')
        c.set('password','')
        c.set('subscribed','')
        c.add()
        return render_template('newuser.html', title='New user',  user=c.data[0])
    else:
        c = usersList()
        c.set('username',request.form.get('username'))
        print(request.form.get('username'))
        c.set('fname',request.form.get('fname'))
        c.set('lname',request.form.get('lname'))
        c.set('email',request.form.get('email'))
        c.set('password',request.form.get('password'))
        c.add()
        if c.verifyNew():
            c.insert()
            print(c.data)
            return render_template('saveduser.html', title='user Saved',  user=c.data[0])
        else:
            return render_template('newuser.html', title='user Not Saved',  user=c.data[0],msg=c.errorList)

@app.route('/saveuser',methods = ['GET', 'POST'])
def saveuser():
    if checkSession() == False:
        return redirect('login')
    c = usersList()
    c.set('id',request.form.get('id'))
    c.set('username',request.form.get('username'))
    c.set('fname',request.form.get('fname'))
    c.set('lname',request.form.get('lname'))
    c.set('email',request.form.get('email'))
    c.set('password',request.form.get('password'))
    c.add()
    if c.verifyChange():
        c.update()
        #print(c.data)
        #return ''
        return render_template('saveduser.html', title='user Saved',  user=c.data[0])
    else:
        return render_template('user.html', title='user Not Saved',  user=c.data[0],msg=c.errorList)

@app.route('/simulator', methods = ['GET', 'POST'])
def simulator():
    if checkSession() == False:
        return redirect('login')
    teams = teamsList()
    teams.getAll()
    data = []
    for team in teams.data:
        temp = {"Team_Name": team["Team_Name"].replace(" ", "_"), "Record": team["Record"]}
        data.append(temp)
    return render_template('simulator/simulator.html', title='Simulator',  teams=data)

@app.route('/runsim', methods = ['GET', 'POST'])
def runsim():
    if checkSession() == False:
        return redirect('login')
    h = request.args.get("hometeam").replace("_", " ")
    a = request.args.get("awayteam").replace("_", " ")

    match = matchHistory()
    match.set("muteamone", h)
    match.set("muteamtwo", a)
    match.set("muteamonescore", 0)
    match.set("muteamtwoscore", 0)
    match.set("userid", session['user']['userid'])
    match.add()
    match.insert()

    match.getAll()
    s = simulatorRunner(h,a,match.data[len(match.data) - 1][match.pk])
    s.runSim()
    s.addMatch()

    print(str(s.muid))
    match.data[s.muid - 1]["muteamonescore"] = s.hometeamscore
    match.data[s.muid - 1]["muteamtwoscore"] = s.awayteamscore
    match.update(s.muid - 1)

    return render_template('simulator/runsim.html', title='Running sim',  simulation=s)


@app.route('/players')
def players():
    if checkSession() == False:
        return redirect('login')
    p = playersList()
    p.getAll()
    return render_template('player/players.html', title='Players',  players=p.data)

@app.route('/player')
def player():
    if checkSession() == False:
        return redirect('login')
    pid = request.args.get("playerid")
    print("We here boys" + pid)
    p = playersList()
    p.getById(pid)
    return render_template('player/player.html', title='' + p.data[0]["playername"],  player=p.data[0])

@app.route('/history')
def history():
    if checkSession() == False:
        return redirect('login')
    match = matchHistory()
    match.getByField("userid", session['user']['userid'])

    return render_template('matches/matches.html', title='Match ups created by user',  matches=match.data)

@app.route('/stats')
def stats():
    if checkSession() == False:
        return redirect('login')
    muid = request.args.get("matchid")

    match = matchHistory()
    match.getById(muid)

    print(str(match.data))
    ms = matchstats()
    ms.getByField("matchupid", muid)
    return render_template('matches/stats.html', title='Stats for match up', homescore=match.data[0]["muteamonescore"], awayscore=match.data[0]["muteamtwoscore"],  stats=ms.data)

def checkSession():
    if 'active' in session.keys():
        timeSinceAct = time.time() - session['active']
        print(timeSinceAct)
        if timeSinceAct > 500:
            session['msg'] = 'Your session has timed out.'
            return False
        else:
            session['active'] = time.time()
            return True
    else:
        return False


@app.route('/static/<path:path>')
def send_static(path):
    return send_from_directory('static', path)


if __name__ == '__main__':
   app.secret_key = '1234'
   app.run(host='127.0.0.1',debug=True)
