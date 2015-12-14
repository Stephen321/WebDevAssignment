import DBcm

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

config = { 'host': '127.0.0.1',
           'database': 'gamesDB',
           'user': 'gamesadmin',
           'password': 'gamesadminpasswd' }
		   
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
    
@app.route('/table/<path:table>', methods=['GET'])
def showtable(table) -> 'html':
    with DBcm.UseDatabase(config) as cursor:
        if table == 'Games':
            _SQL = '''SELECT name,description 
                      FROM games'''
            titles = ('Name', 'Description',)
        elif table == 'Players':
            _SQL = '''SELECT handle, first, last, email, passwd
                      FROM players'''
            titles = ('Handle', 'First', 'Last', 'Email', 'Passwd',)
        elif table == 'Scores':
            _SQL = '''SELECT games.name, players.handle, scores.score
                      FROM games,players,scores
                      WHERE games.id = scores.game_id and players.id = scores.player_id'''
            titles = ('Game Name', 'Player', 'Score',)
        cursor.execute(_SQL)
        data = cursor.fetchall()
    return render_template(table.lower() + 'table.html',
                           the_title=table + ' Table',
                           the_data=data,
                           home_url='/welcome',
                           the_titles=titles,
                           the_add_url=url_for('insertinto', table=table))

'''inserting into table'''
@app.route('/table/<path:table>/add', methods=['POST'])
def insertinto(table) -> 'url':
    with DBcm.UseDatabase(config) as cursor:
        canExecute = False
        if table == 'Games':
            _SQL = '''INSERT INTO games (name, description)
                      VALUES (%s, %s)'''
            if request.form['name'] != '' and request.form['description'] != '':
                canExecute = True
        if canExecute:
            cursor.execute(_SQL, (request.form['name'],request.form['description']))
    return redirect(url_for('showtable', table=table))
        
"""Question 3----------------------------------------------------------------------------------"""                 
@app.route('/getgame', methods=['POST'])
def gethighscores() -> 'url':
    game = request.form['btn']
    return redirect(url_for('showgamehighscores', game=game))
    
@app.route('/highscores/<path:game>', methods=['GET'])
def showgamehighscores(game) -> 'html':
    with DBcm.UseDatabase(config) as cursor:
        _GamesSQL = '''SELECT name
                       FROM games'''
        cursor.execute(_GamesSQL)
        games = cursor.fetchall()
        games = [''.join(x) for x in games]
        print(games)
        _HighscoresSQL = '''SELECT players.handle, scores.score
                            FROM players,scores
                            WHERE scores.game_id=(SELECT id
                                            FROM games
                                            WHERE games.name=%s)
                            AND players.id = scores.player_id
                            ORDER BY scores.score DESC'''
        cursor.execute(_HighscoresSQL, (game,))
        data = cursor.fetchall()
        '''data = data[:10]'''
        titles = ('Player', 'Score',)
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
    handle = request.form['btn']
    return redirect(url_for('showplayeractivity', handle=handle))
    
@app.route('/activity/<path:handle>', methods=['GET'])
def showplayeractivity(handle) -> 'html':
    with DBcm.UseDatabase(config) as cursor:
        _PlayersSQL = '''SELECT handle
                         FROM players'''
        cursor.execute(_PlayersSQL)
        players = cursor.fetchall()
        players = [''.join(x) for x in players]
        _ActivitySQL = '''SELECT games.name,scores.score
                          FROM games,scores
                          WHERE scores.player_id=(SELECT id
                                                  FROM players
                                                  WHERE players.handle=%s)
                          AND games.id=scores.game_id'''        
        cursor.execute(_ActivitySQL, (handle,))
        data = cursor.fetchall()
        titles = ('Game', 'Score',)
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

