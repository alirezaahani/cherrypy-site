import cherrypy
import os.path
import hashlib
import string
import random
import sqlite3 as db
from captcha.image import ImageCaptcha

captcha_output = ""
#Making a strong hash using sha512(It's little bit slow it think)
def hasher(password):
    password = str(password)
    h = hashlib.sha512(password.encode())
    return h.hexdigest()
#These three function are really easy to understand.
def create_database():
    connection = db.connect("database.db")
    connection.close()

def create_table(table_name):
    connection = db.connect("database.db")
    cur = connection.cursor()
    cur.execute("create table if not exists {}(id integer primary key autoincrement,username text,password text)".format(table_name))
    connection.close()

def create_table_posts(table_name):
    connection = db.connect("database.db")
    cur = connection.cursor()
    cur.execute("create table if not exists {}(id integer primary key autoincrement,username text,post text)".format(table_name))
    connection.close()

def search_database(filters,value,search):
    #Making a connetion
    connection = db.connect("database.db")
    cur = connection.cursor()
    #Searching in database
    cur.execute("select {0} from login where {1}=\"{2}\"".format(filters,value,search))
    contect = cur.fetchall()
    connection.close()
    if len(contect) > 0:
        return contect
    else:
        return False

def insert_data(username,password):
    #Searching for dup username
    if search_database("username","username",username):
        return False
    #Checking for strong password
    elif len(password) <= 6:
        return -1
    else:
        #Making a connetion
        connection = db.connect("database.db")
        #Getting a cursor
        cur = connection.cursor()
        #Inserting the data
        cur.execute("insert into login(username,password) values('{0}','{1}')".format(username,hasher(password)))
        #Commitng the data
        connection.commit()
        connection.close()
        return True

def insert_post(contect,username):
    #Checking for empty input
    if len(contect) <= 0:
        return False
    else:
        #Making a connection
        connection = db.connect("database.db")
        #Getting a cursor
        cur = connection.cursor()
        #Inserting values(name and post)
        cur.execute("insert into posts(username,post) values('{0}','{1}')".format(username,contect))
        #Commiting the inserted data
        connection.commit()
        connection.close()
        return True

#This fucntion is for theme
def theme(text,title):
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

def show_posts():
    #A lot of value
    post = result_post = result_name = total_post = total_name = post_content = name = ""
    count = 0
    #Connecting to database
    connection = db.connect("database.db")
    #Getting a cursor
    cur = connection.cursor()
    #Getting all the posts
    cur.execute("select post from posts")
    post = cur.fetchall()
    post.reverse()
    #Getting all the username
    cur.execute("select username from posts")
    name = cur.fetchall()
    name.reverse()
    #This loop is for showing all posts and username in a good looking way
    for result_post,result_name in zip(post,name):
        for total_post,total_name in zip(result_post,result_name):
            if count == 0:
                post_content += "<hr>"
            post_content += str(total_name)
            post_content += ": "
            post_content += str(total_post)
            post_content += "<hr>"
            count += 1
    #Closing the db
    connection.close()
    #Returning the final result
    return post_content

#404 page
def page404(status, message, traceback, version):
    return theme("صفحه مورد نظر یافت نشد","404")

class Site(object):

    @cherrypy.expose
    def index(self):
        html = theme(
        """<div style="text-align:center;">برای <a href="/login">ورود</a> کلیک کنید</div><div style="text-align:center;">برای <a href="/signin">ثبت نام</a> کلیک کنید<br></div>{}""".format(show_posts())
        ,"صفحه اصلی")
        return html

    @cherrypy.expose
    def signin(self):
        #Making captcha and putting it in public/out.png
        global captcha_output
        captcha_output = ''.join(random.sample(string.hexdigits, 4)).lower()
        image = ImageCaptcha()
        image.write(captcha_output,"./public/out.png")
        return theme("""
        <center>
            <p>پسورد باید حداقل ۶ حرف باشد</p>
            <p>جهت جلوگیری از مشکلات در ورود لطفا از حروف انگلیسی برای نام کاربری خود استفاده کنید</p>
            <form method="post" action="signinprocess" />
                نام کاربری:<input type="text" value="" name="username" /><br>
                رمز ورود:<input type="password" value="" name="password" /><br>
                کپجا : <input type="text" name="captcha"><br>
                <button type="submit">ثبت نام</button><br>
    		    <img src="static/out.png">
            </form>
        </center>""","ثبت نام")

    @cherrypy.expose
    def signinprocess(self,password,username,captcha):
        #Checking for empty input
        if len(username) < 0 or len(password) < 0 or len(captcha) < 0:
            return theme("لطفا تمامی فرم هارا پرکنید<script>function Redirect() {window.location = \"/signin\";}setTimeout('Redirect()', 1000);</script>","ثبت نام")
        else:
            #Checking the captcha
            if captcha.lower() == captcha_output:
                #Inserting the user
                if insert_data(username,password):
                    return theme("کاربر مورد نظر ساخته شد <script>function Redirect() {window.location = \"/login\";}setTimeout('Redirect()', 1000);</script>","ثبت نام")
                elif insert_data(username,password) == -1:
                    return theme("رمز عبور کوتاه است !<script>function Redirect() {window.location = \"/signin\";}setTimeout('Redirect()', 1000);</script>","ثبت نام")
                else:
                    return theme("نام کاربری تکراریست<script>function Redirect() {window.location = \"/signin\";}setTimeout('Redirect()', 1000);</script>","ثبت نام")
            else:
                return theme("لطفا کپچا را صحیح وارد کنید<script>function Redirect() {window.location = \"/signin\";}setTimeout('Redirect()', 1000);</script>","ثبت نام")
    
    @cherrypy.expose
    def login(self):
        #Making a captcha and saving it in public/out.png
        global captcha_output
        captcha_output = ''.join(random.sample(string.hexdigits, 4)).lower()
        image = ImageCaptcha()
        image.write(captcha_output,"./public/out.png")
        return theme("""
        <center>
            <p>جهت ورود لطفا اطالاعات زیر را کامل کرده و بر روی دکمه ورود کلیک کنید</p>
            <form method="post" action="loginprocess" />
                نام کاربری:<input type="text" value="" name="username" /><br>
                رمز ورود:<input type="password" value="" name="password" /><br>
                کپجا : <input type="text" name="captcha"><br>
                <button type="submit">ورود</button><br>
    	        <img src="static/out.png">
            </form>
        </center>
        ""","ورود")

    @cherrypy.expose
    def loginprocess(self,username,password,captcha):
        #Checking the captcha
        if captcha.lower() == captcha_output:
            #Checking the database
            if search_database("username","username",username) and search_database("password","password",hasher(password)):
                cherrypy.session['islogin'] = True
                return theme("شما با موفقیت وارد سایت شدید<script>function Redirect() {window.location = \"/panel\";}setTimeout('Redirect()', 1000);</script>","ورود")
            else:
                return theme("نام کاربری یا رمز عبور شما اشتباه است<script>function Redirect() {window.location = \"/login\";}setTimeout('Redirect()', 1000);</script>","ورود")
        else:
            return theme("لطفا کپچا را صحیح وارد کنید<script>function Redirect() {window.location = \"/login\";}setTimeout('Redirect()', 1000);</script>","ثبت نام")
    
    @cherrypy.expose
    def panel(self):
        #I use try cuz of the sessions not definding, tell me if there is a better way
        try:
            if cherrypy.session['islogin']:
                output = """
                    <center>
                        <a href="/logout">خروج</a></center>
                        <form method="post" action="/post_insert">
                            اسم نویسنده :<input type="text" name="username"><br>
                            <textarea name="contect"></textarea><br>
                            <button type="submit">ثبت</button>
                        </form>
                    </center>"""
                #Showing a form for inseting posts
                return theme(output,"مرکز مدیریت")
        except:
            return theme("لطفا وارد سایت شوید<script>function Redirect() {window.location = \"/login\";}setTimeout('Redirect()', 1000);</script>","ورود")

    @cherrypy.expose
    def logout(self):
        #I use try cuz of the sessions not definding, tell me if there is a better way
        try:
            #Checking if user is logined or not
            if cherrypy.session['islogin']:
                #Loging the user out
                cherrypy.session['islogin'] = False
                #Redirect to root
                raise cherrypy.HTTPRedirect("/")
            else:
                #Redirect to root
                raise cherrypy.HTTPRedirect("/")
        except:
            #Redirect to root
            raise cherrypy.HTTPRedirect("/")

    @cherrypy.expose
    def post_insert(self,contect,username):
        #I use try cuz of the sessions not definding, tell me if there is a better way
        try:
            #Checking if your is logined
            if cherrypy.session['islogin']:
                #Just for disabling the javascript and css
                contect = contect.replace("\n","<br>")
                contect = contect.replace("<script>","lol")
                contect = contect.replace("<style>","lol")
                username = username.replace("\n","<br>")
                username = username.replace("<script>","lol")
                username = username.replace("<style>","lol")
                insert_post(contect,username)
                #Redirect to root
                raise cherrypy.HTTPRedirect("/panel")
            else:
                #Redirect to root
                raise cherrypy.HTTPRedirect("/")
        except:
            #Redirect to root
            raise cherrypy.HTTPRedirect("/")

#Main function
if __name__ == "__main__":
    #Creating the database
    create_database()
    #Creating a table for logins
    create_table("login")
    #Creating a table for posts
    create_table_posts("posts")
    #Config for the app
    conf = {
        #Config for root of the site
        '/' : {
            #Enabling the sessions
            'tools.sessions.on': True,
            #Setting the 404 page
            'error_page.404': page404,
            #Getting the dir for file saving a stuff
            'tools.staticdir.root': os.path.abspath(os.getcwd()),
            #Making the sessions secure
            'tools.sessions.secure': True,
        },
        #Config for the static folder of the site(It's for pictures and styles)
        '/static': {
            #Enabling it
            'tools.staticdir.on': True,
            #Setting the dir of static
            'tools.staticdir.dir': './public'
        }
    }
    #Starting the app
    cherrypy.quickstart(Site(),'/',conf)