#!/usr/bin/env python2.7
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import SubmitField, SelectField, RadioField, HiddenField, StringField, IntegerField, FloatField
from wtforms.validators import InputRequired, Length, Regexp, NumberRange
from funcs import *
from create_db import create_schema

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
bootstrap = Bootstrap(app)
app.debug=True

# Use the DB credentials you received by e-mail
DB_USER = "bh2798"
DB_PASSWORD = "2705"
DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"
DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/proj1part2"
engine = create_engine(DATABASEURI, isolation_level="AUTOCOMMIT")

first = False
if first:
    create_schema(engine)




@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/login',methods=['GET','POST'])
def login():
  names={}
  if request.method == 'GET':
    return render_template('login.html')
  else:
    email= request.form.get('email')
    password = request.form.get('password')
    cursor = g.conn.execute(
      """
      SELECT email,	keyword, name FROM users 
      where email=%s
      """, email)
    for result in cursor:
      names['email'],names['keyword'],names['name']=result['email'],result['keyword'],result['name']
    if not names:
      return redirect('/login')
    if email== names['email'] and password == str(names['keyword']):
      session['email'], session['name'] = email, names['name']
      return redirect('/')
    else:
      return redirect('/login')


@app.route('/logout/')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/',methods=['GET','POST'])
def index():
  user_email, user_name = session.get('email'), session.get('name')
  if not user_email:
    return redirect('/login')
  names=[]
  names.append({'email':user_email, 'uname':user_name})
  context = dict(data=names)
  return render_template("index.html", **context)


@app.route('/users/',methods=['GET','POST'])
def users():
  own,other,names = [],[],[]
  user_email, user_name = session.get('email'), session.get('name')
  names.append({'email':user_email, 'uname':user_name})
  cursor=g.conn.execute(
                          """
                          SELECT DISTINCT Users.name,  concat(Users.name, '''s like_list') as Users_likelist, concat(Users.name, '''s Actor_list') as Users_follow  FROM Users, like_list, comment, follow
                          Where Users.email=%s
                          """, session.get('email'))
  cursor_=g.conn.execute(
                          """
                          SELECT DISTINCT Users.name,  concat(Users.name, '''s like_list') as Users_likelist, concat(Users.name, '''s Actor_list') as Users_follow  FROM Users, like_list, comment, follow
                          Where Users.email!=%s
                          """, session.get('email'))

  for result in cursor:
     own.append({'uname': result['name'], 'my_likelist': result['users_likelist'], 'my_follow': result['users_follow']})
  for result in cursor_:
     other.append({'name': result['name'], 'users_likelist': result['users_likelist'],'users_follow': result['users_follow']})
  context = dict(data=names,mydata=own, otherdata=other)
  cursor.close()
  cursor_.close()
  return render_template("users.html", **context)

@app.route('/likelist/<name>/<str>',methods=['GET'])
def likelist(name, str):
  names,likelist=[],[]
  user_email, user_name = session.get('email'), session.get('name')
  names.append({'email':user_email, 'uname':user_name})
  ## we view our own likelist
  if name==session.get('name'):
      cursor = g.conn.execute("""
              SELECT U.name, L.name as like_list_name, L.like_id as id, M.title as Movie_title FROM Users U
              JOIN like_list L on U.email=L.email
              JOIN include i on L.like_id=i.like_id 
              JOIN Movie M on i.idMovie=M.idMovie
              WHERE U.name=%s
              GROUP BY U.name, L.name, L.like_id, M.title
            """, name)
  else:
    ## we view other's likelist
      cursor = g.conn.execute("""
              SELECT U.name, L.name as like_list_name, L.like_id as id, M.title as Movie_title FROM Users U
              JOIN like_list L on U.email=L.email
              JOIN include i on L.like_id=i.like_id 
              JOIN Movie M on i.idMovie=M.idMovie
              WHERE U.name=%s and L.public=1 and L.private=0
              GROUP BY U.name, L.name, L.like_id, M.title
            """, name)
  for result in cursor:
    likelist.append({
                   'User_name':result['name'], 'like_list_name':result['like_list_name'],
                   'id':result['id'], 'users_follow':result['movie_title']})
  cursor.close()
  if likelist:
    user_name = [{'user': likelist[0]['User_name']}]
    context = dict(data=names, likelist=likelist, user=user_name)
    return render_template("users_likelist_public.html", **context)
  else:
    context = dict(data=names)
    return render_template("user_likelist_private.html",**context)


@app.route('/follow/<names>/<str1>',methods=['GET'])
def follow(names, str1):
  name,follow=[],[]
  user_email, user_name = session.get('email'), session.get('name')
  name.append({'email':user_email, 'uname':user_name})
  cursor=g.conn.execute("""
              Select U.name, A.name as actor FROM 
              Users U JOIN follow F on U.email=F.email
              JOIN actor A on F.actor_id=A.actor_id
              WHERE U.name=%s
                       """, names)
  for result in cursor:
     follow.append({'User_name':result['name'], 'actor':result['actor']})
  cursor.close()
  if follow:
    user_name = [{'user': follow[0]['User_name']}]
    context = dict(data=name, follow=follow, user=user_name)
    return render_template("users_follow.html", **context)
  else:
    context = dict(data=name)
    return render_template("follow_no.html", **context)

@app.route('/movie')
def movie():
  names,movie=[],[]
  user_email, user_name = session.get('email'), session.get('name')
  names.append({'email':user_email, 'uname':user_name})
  cursor=g.conn.execute("""
                SELECT title,	overview,	release_date FROM movie
                        """)

  for result in cursor:
     movie.append({'title':result['title'], 'overview':result['overview'],
                   'release_date':result['release_date']})
  context = dict(data=names, movie=movie)
  cursor.close()
  return render_template("movies.html", **context)


@app.route('/profiles/<name>')
def profiles(name):
  names, titles, aname=[],[],[]
  user_email, user_name = session.get('email'), session.get('name')
  names.append({'email':user_email, 'uname':user_name})
  cursor=g.conn.execute("""
        SELECT M.title as title FROM movie M
        WHERE M.title=%s
          """, name)
  cursor_=g.conn.execute("""
                        SELECT M.title, C.rating, U.name as user, C.content as comment FROM movie M
                        JOIN comment C ON M.idmovie=C.idMovie 
                        JOIN Users U on U.email=C.email
                        WHERE M.title=%s
                        """, name
  )
  for result in cursor:
     titles.append({'title':result['title']})
  for result in cursor_:
     aname.append({'title':result['title'], 'rating':result['rating'],
                   'user':result['user'], 'comment':result['comment']})
  context = dict(data=names, aname=aname, name=name, title=titles)
  cursor.close()
  return render_template("Movie_profiles.html",**context)


@app.route('/Languages/<name>')
def Languages(name):
  names,lang=[],[]
  user_email, user_name = session.get('email'), session.get('name')
  names.append({'email':user_email, 'uname':user_name})
  cursor=g.conn.execute("""
                SELECT L.name as languages  FROM Languages L
              JOIN speak S ON L.language_id=S.language_id
              JOIN Movie M on S.idmovie=M.idmovie
              WHERE M.title=%s
                        """, name)
  for result in cursor:
     lang.append({'languages':result['languages']})
  context = dict(data=names, lang=lang, name=name)
  cursor.close()
  return render_template("Languages.html", **context)

@app.route('/Crew/<name>')
def Crew(name):
  names,crew=[],[]
  user_email, user_name = session.get('email'), session.get('name')
  names.append({'email':user_email, 'uname':user_name})
  cursor = g.conn.execute("""
                      SELECT W.job as job, C.name as name  FROM crew C 
                      JOIN work W ON C.crew_id=W.crew_id
                      JOIN Movie M ON W.idmovie=M.idmovie
                      WHERE M.title=%s
                        """, name)
  for result in cursor:
    crew.append({'job': result['job'], 'name': result['name']})
  context = dict(data=names, crew=crew, name=name )
  cursor.close()
  return render_template("Crew.html", **context)

@app.route('/Genres/<name>')
def Genres(name):
  names,genres=[],[]
  user_email, user_name = session.get('email'), session.get('name')
  names.append({'email':user_email, 'uname':user_name})
  cursor = g.conn.execute("""
                        SELECT G.name as genre FROM describe_genre D
                        JOIN genre G on D.genre_id=G.genre_id 
                        JOIN movie M on D.idmovie=M.idmovie
                        WHERE M.title=%s
                        """, name)
  for result in cursor:
     genres.append({'genre': result['genre']})
  context = dict(data=names,genres=genres, name=name)
  cursor.close()
  return render_template("Genres.html", **context)

@app.route('/Characters/<name>')
def Characters(name):
  names,char=[],[]
  user_email, user_name = session.get('email'), session.get('name')
  names.append({'email':user_email, 'uname':user_name})
  cursor = g.conn.execute("""
                        SELECT A.name as actor, C.name as character FROM Characters C
                        JOIN Movie M on C.idmovie=M.idMovie
                        JOIN Actor A on C.actor_id=A.actor_id
                        WHERE M.title=%s
                         """, name)
  for result in cursor:
     char.append({'actor': result['actor'], 'character':result['character']})
  context = dict(data=names, char=char, name=name)
  cursor.close()
  return render_template("Characters.html", **context)


@app.route('/Company/<name>')
def Company(name):
  names,comp=[],[]
  user_email, user_name = session.get('email'), session.get('name')
  names.append({'email':user_email, 'uname':user_name})
  cursor = g.conn.execute("""
                      SELECT C.name as company FROM Movie M 
                      JOIN produce P on M.idmovie=P.idmovie
                      JOIN Company C on C.company_id=P.company_id 
                      WHERE M.title=%s
                         """, name)
  for result in cursor:
    comp.append({'company': result['company']})
  context = dict(data=names, comp=comp, name=name)
  cursor.close()
  return render_template("Company.html", **context)

@app.route('/Actor')
def allActor():
    names = []
    user_email, user_name = session.get('email'), session.get('name')
    names.append({'email':user_email, 'uname':user_name})
    actors = []
    cursor = g.conn.execute(
        '''
        SELECT name FROM Actor
        ''')
    for result in cursor:
        actors.append({'actor': result['name']})
    
    context = dict(data=names, actors = actors)
    cursor.close()
    return render_template('Actor.html', **context)

@app.route('/Actor/<name>')
def Actor(name):
  names,actor=[],[]
  user_email, user_name = session.get('email'), session.get('name')
  names.append({'email':user_email, 'uname':user_name})
  cursor = g.conn.execute("""
                          SELECT A.name as actor, A.gender FROM Characters C
                          JOIN Movie M on C.idmovie=M.idMovie
                          JOIN Actor A on C.actor_id=A.actor_id
                          WHERE A.name=%s
                         """, name)
  for result in cursor:
     actor.append({'actor': result['actor'], 'gender':result['gender']})
  context = dict(data=names, actor=actor, name=name)
  cursor.close()
  return render_template("Actors.html", **context)


@app.route('/followlist/<name>')
def followlist(name):
  names,flist=[],[]
  user_email, user_name = session.get('email'), session.get('name')
  names.append({'email':user_email, 'uname':user_name})
  cursor = g.conn.execute("""
                          SELECT U.name as follower FROM follow F
                          JOIN Users U on F.email=U.email
                          JOIN Actor A on F.actor_id=A.actor_id
                          Where A.name=%s
                         """, name)
  for result in cursor:
    flist.append({'follower':result['follower']})
  context = dict(data=names, flist=flist, name=name)
  cursor.close()
  return render_template("followlist.html", **context)

@app.route('/movielist/<name>')
def movielist(name):
  names,mlist=[],[]
  user_email, user_name = session.get('email'), session.get('name')
  names.append({'email':user_email, 'uname':user_name})
  cursor = g.conn.execute("""
                          SELECT A.name as actor, M.title as movie  FROM Characters C
                          JOIN Movie M on C.idmovie=M.idMovie
                          JOIN Actor A on C.actor_id=A.actor_id
                          WHERE A.name=%s
                         """, name)
  for result in cursor:
    mlist.append({'actor': result['actor'], 'movie':result['movie']})
  context = dict(data=names, mlist=mlist, name=name)
  cursor.close()
  return render_template("movielist.html", **context)

# Example of adding new data to the database
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
  form = addUser()
  if form.validate_on_submit():
    email = request.form['email']
    name = request.form['name']
    gender = request.form['gender']
    password = request.form['password']
    g.conn.execute('''
                          INSERT INTO Users VALUES
                          (%s, %s, %s, %s)
                          ''',
                   (email, name, gender, password)
                   )
    message = f'New User {name} has been created! '
    return render_template('add_user.html', message=message)
  else:
    for field, errors in form.errors.items():
      for error in errors:
        flash('Error in {}: {}'.format(
          getattr(form, field).label.text,
          error), 'error')
    return render_template('add_user.html', form=form)


@app.route('/add_likelist/<name>',methods=['GET', 'POST'])
def add_likelist(name):
  user_email = session.get('email')
  form=addlikelist()
  if form.validate_on_submit():
    lname = request.form['name']
    share = request.form['share_value']
    if share==1:
      public, private=1, 0
    else:
      public, private=0, 1
    cursor = g.conn.execute('''
                            SELECT like_list.name From like_list, movie
                            WHERE like_list.email=%s
                            ''',user_email)
    cur_llist=[]
    for result in cursor:
       cur_llist.append(result[0])
    #likelist name should be different
    if lname not in cur_llist:
      g.conn.execute('''
                            INSERT INTO like_list(name, email, public, private) VALUES
                            (%s, %s, %s, %s)
                            ''',
                     (lname, user_email, public, private)
                     )
      message = f'New likelist has been created! '
      return render_template('add_likelist.html', message=message)
    else:
      return redirect('/users')
  else:
    for field, errors in form.errors.items():
      for error in errors:
        flash('Error in {}: {}'.format(
          getattr(form, field).label.text,
          error), 'error')
    return render_template('add_likelist.html', form=form)

@app.route('/add_movie/<name>', methods=['GET', 'POST'])
def add_movie(name):
  names=[]
  user_email, user_name = session.get('email'), session.get('name')
  names.append({'email':user_email, 'uname':user_name})
  user_email = session.get('email')
  cursor = g.conn.execute('''
                          SELECT DISTINCT like_list.name From like_list
                          WHERE like_list.email=%s
                          ''', user_email)
  cur_llist = []
  for result in cursor:
     cur_llist.append({'name':result['name']})
  print(cur_llist)
  context=dict(data=names, likelist=cur_llist, movie=name)
  print(context)
  return render_template('add_movie.html', **context)

@app.route('/include_likelist/<lname>/<mname>', methods=['GET', 'POST'])
def include_likelist(lname, mname):
  user_email, user_name = session.get('email'), session.get('name')
  form=includelikelist()
  if form.validate_on_submit():
      cursor = g.conn.execute('''
                            SELECT M.title as Movie_title FROM Users U
                            JOIN like_list L on U.email=L.email
                            JOIN include i on L.like_id=i.like_id 
                            JOIN Movie M on i.idMovie=M.idMovie
                            WHERE U.name=%s and L.name=%s
                            GROUP BY U.name, L.name, L.like_id, M.title
                            ''',user_name, lname)
      mlist,include=[],[]
      for result in cursor:
         mlist.append(result[0])
      if mname not in mlist:
        cursor = g.conn.execute('''
                              SELECT movie.idmovie, like_list.like_id FROM like_list, movie
                              WHERE like_list.name=%s and movie.title=%s
                              ''', lname, mname)
        for result in cursor:
           idmovie, likeid=result['idmovie'],result['like_id']
        g.conn.execute('''
                              INSERT INTO include(idmovie, like_id) VALUES
                              (%s, %s)
                              ''', (idmovie, likeid) )
        message = f'Movie has been inserted into likelist'
        return render_template('include_likelist.html', message=message)
      else:
        return redirect('/movie')

  else:
    for field, errors in form.errors.items():
      for error in errors:
        flash('Error in {}: {}'.format(
          getattr(form, field).label.text,
          error), 'error')
    return render_template('include_likelist.html', form=form)

  return render_template('include_likelist.html')
"""
        cursor=g.conn.execute('''
                          SELECT movie.idmovie, like_list.like_id From like_list, movie
                          WHERE like_list.name=%s and like_list.email=%s and movie.title=%s
                          ''',lname, user_email, name)
    for result in cursor:
      include['idmovie'],include['like_id'] =result['idmovie'], result['like_id']
    g.conn.execute('''
                          INSERT INTO include(idmovie, like_id) VALUES
                          (%s, %s)
                          ''',
                   (include['idmovie'],include['like_id'])
                   )

"""


@app.route('/add_comment/<name>', methods=['GET', 'POST'])
def add_comment(name):
    form = Comment()
    user_email = session.get('email')
    cursor = g.conn.execute('''
                            SELECT idMovie
                            FROM movie
                            WHERE title = %s
                            ''', name)
    mid = int([result for result in cursor][0][0])
    cursor.close()
    date = stringdate()
    cursor_ = g.conn.execute('''
                             SELECT COUNT(*) AS c
                             FROM comment
                             ''')
    comment_count = []
    for result in cursor_:
        comment_count.append(int(result['c']))
    
    cursor_.close()
    if form.validate_on_submit():
        rate = request.form['rate']
        comment = request.form['comment']
        g.conn.execute('''
                       INSERT INTO Comment VALUES
                       (%s, %s, %s, %s, %s, %s)
                       ''',
                       (comment_count[0]+1, comment, date, rate, user_email, mid)
                       )
        message = f'You have successfully made a comment on {name} !'
        return render_template('add_comment.html', message=message)
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash('Error in {}: {}'.format(
                    getattr(form, field).label.text,
                    error), 'error')
        return render_template('add_comment.html', form=form)
        

@app.route('/Actor/<name>', methods=['GET', 'POST'])
def follow_actor(name):
    user_email = session.get('email')
    followers = {}
    if request.method=='POST':
        if request.form.get('Action1') == 'Follow':
            acid_cursor = g.conn.execute(
                '''
                SELECT actor_id
                FROM Actor
                WHERE name = %s
                ''', name)
            for result in acid_cursor:
                acid = result['actor_id']
            acid_cursor.close()
            cursor = g.conn.execute(
                '''
                SELECT *
                FROM follow
                WHERE email = %s AND actor_id = %s
                ''',
                (user_email, acid))
            for result in cursor:
                followers['email'], followers['id'] = result['email'], result['id']
            if not followers:
                g.conn.execute(
                    '''
                    INSERT INTO follow VALUES
                    (%s, %s)
                    ''',
                    (user_email, acid))
                flash('Succesful follow!')
                return redirect('/Actor')
            else:
                flash('You have followed this actor before!')
                return redirect('/Actor')
            
            
if __name__ == "__main__":
  import click
  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='127.0.0.1')
  @click.argument('PORT', default=5000, type=int)
  def run(debug, threaded, host, port):
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)
  run()
