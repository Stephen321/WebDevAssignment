import DBcm

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

config = { 'host': '127.0.0.1',
           'database': 'gamesDB',
           'user': 'gamesadmin',
           'password': 'gamesadminpasswd' }
		   
@app.route('/', methods=['GET'])
@app.route('/welcome', methods=['GET'])
def entry() -> 'html':
    """Returns the welcome page to browser."""
    return render_template('welcome.html',
                           the_title='Welcome to the GamesDB Database Editor!',
                           the_table_url='/gettable',
                           the_highscores_url=url_for('showgamehighscores', game='default'),
                           the_playeractivity_url=url_for('showplayeractivity', handle='default'),)

"""Question 2----------------------------------------------------------------------------------"""                 
@app.route('/gettable', methods=['POST'])
def gettable() -> 'url':
    table = request.form['btn']
    return redirect(url_for('showtable', table=table))
    
#display table
@app.route('/table/<path:table>', methods=['GET'])
def showtable(table) -> 'html':
    _ListSQL = ''
    _ScoreGameInfoSQL = ''
    _ScorePlayerInfoSQL = ''
    if table == 'Games':
        _SQL = '''SELECT name,description 
                  FROM games'''
        _ListSQL = '''SELECT id,name
                      FROM games'''
        titles = ('Name', 'Description',)
    elif table == 'Players':
        _SQL = '''SELECT handle, first, last, email, passwd
                  FROM players'''
        _ListSQL = '''SELECT id,handle
                      FROM players'''
        titles = ('Handle', 'First', 'Last', 'Email', 'Passwd',)
    elif table == 'Scores':
        _SQL = '''SELECT games.name, players.handle, scores.score
                  FROM games,players,scores
                  WHERE games.id = scores.game_id and players.id = scores.player_id'''
        _ScorePlayerInfoSQL = '''SELECT id,handle
                      FROM players'''
        _ScoreGameInfoSQL = '''SELECT id,name
                      FROM games'''
        titles = ('Game', 'Player', 'Score',)
    with DBcm.UseDatabase(config) as cursor:
        if _ListSQL != '': #not scores
            cursor.execute(_ListSQL)
            list = cursor.fetchall()
            scoreGames = []
            scorePlayers = []
        else:
            cursor.execute(_ScoreGameInfoSQL)
            scoreGames = cursor.fetchall()
            cursor.execute(_ScorePlayerInfoSQL)
            scorePlayers = cursor.fetchall()
            list = []
        cursor.execute(_SQL)
        data = cursor.fetchall()
    return render_template('table.html',
                           the_title=table + ' Table',
                           the_data=data,
                           home_url='/welcome',
                           the_titles=titles,
                           the_list=list,
                           the_score_games = scoreGames,
                           the_score_players = scorePlayers,
                           the_action_url=url_for('tableaction', table=table))

#check what button was pressed and respond appropriately                           
@app.route('/table/<path:table>/actions', methods=['Post'])
def tableaction(table) -> 'url':
    action = request.form['btn']
    if action == 'Add':
        url = url_for('insertinto', table=table)
    elif action == 'Update':
        url = url_for('update', table=table)
    elif action == 'Delete':
        url = url_for('deletefrom', table=table)
    return redirect(url, code=307)  #code to post
             
#checks if string is an int
def IsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
        
#inserting into table
@app.route('/table/<path:table>/add', methods=['POST'])
def insertinto(table) -> 'url':
    parameters = ()
    if table == 'Games':
        _SQL = '''INSERT INTO games (name, description)
                  VALUES (%s, %s)'''
        if request.form['name'] != '' and request.form['description'] != '':
            parameters = (request.form['name'],request.form['description'])
    elif table == 'Players':
        _SQL = '''INSERT INTO players (handle, first, last, email, passwd)
                  VALUES (%s, %s, %s, %s, %s)'''
        if request.form['handle'] != '' and request.form['first'] != '' and request.form['email'] != '' and request.form['passwd'] != '':
            parameters = (request.form['handle'], request.form['first'], request.form['last'], request.form['email'], request.form['passwd'])
    elif table == 'Scores':
        _SQL = '''INSERT INTO scores (game_id, player_id, score)
                  VALUES (%s, %s, %s)'''
        if request.form['score'] != '' and  IsInt(request.form['score']):
            parameters = (request.form['gameSelect'], request.form['playerSelect'], int(request.form['score']),)
    with DBcm.UseDatabase(config) as cursor:
        if parameters != ():
            cursor.execute(_SQL, parameters)
        #TODO: insert into score
    return redirect(url_for('showtable', table=table))
 
#updating table
@app.route('/table/<path:table>/update', methods=['POST'])
def update(table) -> 'url':
    parameters = ()
    if table == 'Games':
        _SQL = '''UPDATE games
                  SET name = %s, description = %s
                  WHERE id = %s'''
        if request.form['name'] != '' and request.form['description'] != '':
            parameters = (request.form['name'],request.form['description'],)
    elif table == 'Players':
        _SQL = '''UPDATE players
                  SET handle = %s, first = %s, last = %s, email = %s, passwd = %s
                  WHERE id = %s'''
        if request.form['handle'] != '' and request.form['first'] != '' and request.form['last'] != '' and request.form['email'] != '' and request.form['passwd'] != '':
            parameters = (request.form['handle'], request.form['first'], request.form['last'], request.form['email'], request.form['passwd'],)
    #don't update scores
    with DBcm.UseDatabase(config) as cursor:
        if parameters != ():
            cursor.execute(_SQL, parameters + (request.form['select'],))
    return redirect(url_for('showtable', table=table))
    
#deleting from table
@app.route('/table/<path:table>/delete', methods=['POST'])
def deletefrom(table) -> 'url':
    if table == 'Games':
        _SQL = '''DELETE FROM games
                  WHERE id = %s'''
    elif table == 'Players':
        _SQL = '''DELETE FROM players
                  WHERE id = %s'''
        #don't delete from scores
    with DBcm.UseDatabase(config) as cursor:
        cursor.execute(_SQL, (request.form['select'],))                 
    return redirect(url_for('showtable', table=table))
        
"""Question 3----------------------------------------------------------------------------------"""                 
@app.route('/getgame', methods=['POST'])
def gethighscores() -> 'url':
    game = request.form['nameSelect']
    return redirect(url_for('showgamehighscores', game=game))
    
@app.route('/highscores/<path:game>', methods=['GET'])
def showgamehighscores(game) -> 'html':
    _GamesSQL = '''SELECT name
                   FROM games'''
    _HighscoresSQL = '''SELECT players.handle, scores.score
                        FROM players,scores
                        WHERE scores.game_id=(SELECT id
                                        FROM games
                                        WHERE games.name=%s)
                        AND players.id = scores.player_id
                        ORDER BY scores.score DESC
                        LIMIT 10'''
    titles = ('Player', 'Score',)
    with DBcm.UseDatabase(config) as cursor:
        cursor.execute(_GamesSQL)
        games = cursor.fetchall()
        games = [''.join(x) for x in games]
        cursor.execute(_HighscoresSQL, (game,))
        data = cursor.fetchall()
    return render_template('selectiontable.html',
                           the_title='Game High-Scores',
                           home_url='/welcome',
                           the_list=games,
                           the_showactivity_url='/getgame',
                           the_data=data,
                           the_titles=titles,
                           the_name=game,
                           the_text='The highscores of ',
                           the_selecting_text='Select a game to its high-score table.')
                           
"""Question 4----------------------------------------------------------------------------------"""                  
@app.route('/gethandle', methods=['POST'])
def getactivity() -> 'url':
    handle = request.form['nameSelect']
    return redirect(url_for('showplayeractivity', handle=handle))
    
@app.route('/activity/<path:handle>', methods=['GET'])
def showplayeractivity(handle) -> 'html':
    _PlayersSQL = '''SELECT handle
                     FROM players'''
    _ActivitySQL = '''SELECT games.name,scores.score,scores.ts
                      FROM games,scores
                      WHERE scores.player_id=(SELECT id
                                              FROM players
                                              WHERE players.handle=%s)
                      AND games.id=scores.game_id''' 
    titles = ('Game', 'Score', 'Time',)
    with DBcm.UseDatabase(config) as cursor:
        cursor.execute(_PlayersSQL)
        players = cursor.fetchall()
        players = [''.join(x) for x in players]       
        cursor.execute(_ActivitySQL, (handle,))
        data = cursor.fetchall()
    return render_template('selectiontable.html',
                           the_title='Player Activity',
                           home_url='/welcome',
                           the_list=players,
                           the_showactivity_url='/gethandle',
                           the_data=data,
                           the_titles=titles,
                           the_name=handle,
                           the_text='The activity of ',
                           the_selecting_text='Select a player to see their activity.')
						   
if __name__ == '__main__':
    app.run(debug=True)

