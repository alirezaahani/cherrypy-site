import cherrypy
import os.path
import sqlite3 as db
from time import sleep

def create_database():
  connection = db.connect("database.db")
  connection.close()

def create_table(table_name):
  connection = db.connect("database.db")
  cur = connection.cursor()
  cur.execute("create table {}(id integer primary key,username text,password text)".format(table_name))
  connection.close()

def search_database(filters,value,search):
  connection = db.connect("database.db")
  cur = connection.cursor()
  cur.execute("select {0} from login where {1}=\"{2}\"".format(filters,value,search))
  contect = cur.fetchall()
  connection.close()
  if not contect == []:
    return True
  else:
    return False

def insert_data(username,password):
  if search_database("username","username",username):
    return False
  else:
    connection = db.connect("database.db")
    cur = connection.cursor()
    cur.execute("insert into login(username,password) values('{0}','{1}')".format(username,password))
    connection.commit()
    connection.close()
    return True

def show_data():
  connection = db.connect("database.db")
  cur = connection.cursor()
  cur.execute("select * from login")
  contect = cur.fetchall()
  connection.close()
  return contect

def theme(text = "",title = ""):
  return """
    <html>
      <head>
        <title>{1}</title>
        <link href="/static/css/style.css" rel="stylesheet"/>
        <link type="text/css" rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/sahel-font@v3.4.0/dist/font-face.css"/>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
      </head>
      <body>
        <div id="warp">
          {0}
        </div>  
      </body>
    </html>
    """.format(text,title)

class Site(object):
  @cherrypy.expose
  def index(self):
    return theme("""
    <center>
      <form method="post" action="signin" />
        <input type="text" value="نام کاربری شما" name="username" />
        <input type="password" value="password" name="password" />
        <button type="submit">ثبت نام</button>
      </form>
    </center>
    ""","صفحه اصلی")

  @cherrypy.expose
  def signin(self,password,username):
    try:
      if insert_data(username,password):
        return theme("کاربر مورد نظر ساخته شد <script>function Redirect() {window.location = \"/\";}document.write(\"<br> و شما تا چندثانیه دیگر به صفحه اصلی منتقل خواهید شد\");setTimeout('Redirect()', 3000);</script>")
      else:
        return theme("نام کاربری تکرایست و کاربر مورد نظر ساخته نشد<script>function Redirect() {window.location = \"/\";}document.write(\"<br> و شما تا چندثانیه دیگر به صفحه اصلی منتقل خواهید شد\");setTimeout('Redirect()', 3000);</script>")
    except:
      return theme("متاسفانه به علت اشکالات در دیتابیس کاربر موردنظر ساخته نشد<script>function Redirect() {window.location = \"/\";}document.write(\"<br> و شما تا چندثانیه دیگر به صفحه اصلی منتقل خواهید شد\");setTimeout('Redirect()', 3000);</script>")
if __name__ == "__main__":

  create_database()
  try :
    create_table("login")
  except :
    pass

  conf = {
    '/' : {
      'tools.sessions.on': True,
      'tools.staticdir.root': os.path.abspath(os.getcwd())
    },
    '/static' : {
      'tools.staticdir.on' : True,
      'tools.staticdir.dir' : './public'
    }
  }

  cherrypy.quickstart(Site(),'/',conf)
