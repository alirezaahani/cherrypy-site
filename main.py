import cherrypy
import os.path
import sqlite3 as db
import hashlib
def hasher(password):
  password = str(password)
  h = hashlib.md5(password.encode())
  return h.hexdigest()

def create_database():
  connection = db.connect("database.db")
  connection.close()

def create_table(table_name):
  connection = db.connect("database.db")
  cur = connection.cursor()
  cur.execute("create table if not exists {}(id integer primary key autoincrement,username text,password text)".format(table_name))
  connection.close()

def search_database(filters,value,search):
  connection = db.connect("database.db")
  cur = connection.cursor()
  cur.execute("select {0} from login where {1}=\"{2}\"".format(filters,value,search))
  contect = cur.fetchall()
  connection.close()
  if not contect == []:
    return contect
  else:
    return False

def insert_data(username,password):
  if search_database("username","username",username):
    return False
  elif len(password) <= 6:
    return False
  else:
    connection = db.connect("database.db")
    cur = connection.cursor()
    cur.execute("insert into login(username,password) values('{0}','{1}')".format(username,hasher(password)))
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

def page404(status, message, traceback, version):
  return theme("صفحه مورد نظر یافت نشد","404")
class Site(object):
  @cherrypy.expose
  def index(self):
    return theme("<div style=\"text-align:center;\">برای <a href=\"/login\">ورود</a> کلیک کنید</div><div style=\"text-align:center;\">برای <a href=\"/signin\">ثبت نام</a> کلیک کنید<br></div>","صفحه اصلی")
  @cherrypy.expose
  def signin(self):
    return theme("""
    <center>
      <p>پسورد باید حداقل ۶ حرف باشد</p>
      <p>جهت جلوگیری از مشکلات در ورود لطفا از حروف انگلیسی برای نام کاربری خود استفاده کنید</p>
      <form method="post" action="signinprocess" />
        نام کاربری:<input type="text" value="" name="username" /><br>
        رمز ورود:<input type="password" value="" name="password" /><br>
        <button type="submit">ثبت نام</button>
      </form>
    </center>
    ""","ثبت نام")

  @cherrypy.expose
  def signinprocess(self,password,username):
    try:
      if username == "" or password == "":
        return theme("لطفا تمامی فرم هارا پرکنید<script>function Redirect() {window.location = \"/\";}setTimeout('Redirect()', 3000);</script>","ثبت نام")
      else:
        if insert_data(username,password):
          return theme("کاربر مورد نظر ساخته شد <script>function Redirect() {window.location = \"/\";}setTimeout('Redirect()', 3000);</script>","ثبت نام")
        else:
          return theme("نام کاربری تکراریست یا رمز عبور شما کوتاه است<script>function Redirect() {window.location = \"/\";}setTimeout('Redirect()', 3000);</script>","ثبت نام")
    except:
      return theme("متاسفانه به علت اشکالات در دیتابیس کاربر موردنظر ساخته نشد<script>function Redirect() {window.location = \"/\";}setTimeout('Redirect()', 3000);</script>","ثبت نام")
  
  @cherrypy.expose
  def login(self):
    return theme("""
    <center>
      <p>جهت ورود لطفا اطالاعات زیر را کامل کرده و بر روی دکمه ورود کلیک کنید</p>
      <form method="post" action="loginprocess" />
        نام کاربری:<input type="text" value="" name="username" /><br>
        رمز ورود:<input type="password" value="" name="password" /><br>
        <button type="submit">ورود</button>
      </form>
    </center>
    ""","ورود")
  
  @cherrypy.expose
  def loginprocess(self,username,password):
    if search_database("username","username",username) and search_database("password","password",hasher(password)):
      cherrypy.session['islogin'] = True
      return theme("شما با موفقیت وارد سایت شدید<script>function Redirect() {window.location = \"/panel\";}setTimeout('Redirect()', 1000);</script>","ورود")
    else:
      return theme("نام کاربری یا رمز عبور شما اشتباه است<script>function Redirect() {window.location = \"/login\";}setTimeout('Redirect()', 1000);</script>","ورود")
  @cherrypy.expose
  def panel(self):
    try:
      if cherrypy.session['islogin'] == True:
        output = """
        <center><a href="/logout">خروج</a></center>
        """
        return theme(output,"مرکز مدیریت")
    except:
      return theme("لطفا وارد سایت شوید<script>function Redirect() {window.location = \"/login\";}setTimeout('Redirect()', 1000);</script>","ورود")
  @cherrypy.expose
  def logout(self):
    if cherrypy.session['islogin']:
      cherrypy.session['islogin'] == False
      raise cherrypy.HTTPRedirect("/")
if __name__ == "__main__":

  create_database()

  create_table("login")

  conf = {
    '/' : {
      'tools.sessions.on': True,
      'error_page.404': page404,  
      'tools.staticdir.root': os.path.abspath(os.getcwd()),
    },
    '/static' : {
      'tools.staticdir.on' : True,
      'tools.staticdir.dir' : './public'
    }
  }
  cherrypy.quickstart(Site(),'/',conf)