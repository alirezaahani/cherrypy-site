import cherrypy
import os.path
import sqlite3 as db
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
    return theme("<div style=\"text-align:center;\">برای <a href=\"/login\">ورود</a> کلیک کنید</div><div style=\"text-align:center;\">برای <a href=\"/signin\">ثبت نام</a> کلیک کنید<br></div>","صفحه اصلی")
  @cherrypy.expose
  def signin(self):
    return theme("""
    <center>
      <form method="post" action="signinprocess" />
        <input type="text" value="نام کاربری شما" name="username" />
        <input type="password" value="password" name="password" />
        <button type="submit">ثبت نام</button>
      </form>
    </center>
    ""","صفحه اصلی")

  @cherrypy.expose
  def signinprocess(self,password,username):
    try:
      if username == "" or password == "":
        return theme("لطفا تمامی فرم هارا پرکنید<script>function Redirect() {window.location = \"/\";}document.write(\"<br> و شما تا چندثانیه دیگر به صفحه اصلی منتقل خواهید شد\");setTimeout('Redirect()', 3000);</script>","ثبت نام")
      else:
        if insert_data(username,password):
          return theme("کاربر مورد نظر ساخته شد <script>function Redirect() {window.location = \"/\";}document.write(\"<br> و شما تا چندثانیه دیگر به صفحه اصلی منتقل خواهید شد\");setTimeout('Redirect()', 3000);</script>","ثبت نام")
        else:
          return theme("نام کاربری تکرایست و کاربر مورد نظر ساخته نشد<script>function Redirect() {window.location = \"/\";}document.write(\"<br> و شما تا چندثانیه دیگر به صفحه اصلی منتقل خواهید شد\");setTimeout('Redirect()', 3000);</script>","ثبت نام")
    except:
      return theme("متاسفانه به علت اشکالات در دیتابیس کاربر موردنظر ساخته نشد<script>function Redirect() {window.location = \"/\";}document.write(\"<br> و شما تا چندثانیه دیگر به صفحه اصلی منتقل خواهید شد\");setTimeout('Redirect()', 3000);</script>","ثبت نام")
  
  @cherrypy.expose
  def login(self):
    return theme("""
    <center>
      <form method="post" action="loginprocess" />
        <input type="text" value="نام کاربری شما" name="username" />
        <input type="password" value="password" name="password" />
        <button type="submit">ورود</button>
      </form>
    </center>
    """)
  
  @cherrypy.expose
  def loginprocess(self,username,password):
    if search_database("username","username",username) & search_database("password","password",password):
      cherrypy.session['islogin'] = "yes"
      return theme("شما با موفقیت وارد سایت شدید<script>function Redirect() {window.location = \"/panel\";}document.write(\"<br> و شما تا چندثانیه دیگر به مرکزمدیریت منتقل خواهید شد\");setTimeout('Redirect()', 1000);</script>","ورود")
    else:
      return theme("نام کاربری یا رمز عبور شما اشتباه است<script>function Redirect() {window.location = \"/login\";}document.write(\"<br> و شما تا چندثانیه دیگر به صفحه ورود منتقل خواهید شد\");setTimeout('Redirect()', 1000);</script>","ورود")
  
  @cherrypy.expose
  def panel(self):
    try:
      if cherrypy.session['islogin'] == "yes":
        #Admin panel here
        pass
    except:
      return theme("لطفا وارد سایت شوید<script>function Redirect() {window.location = \"/login\";}setTimeout('Redirect()', 1000);</script>","ورود")
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