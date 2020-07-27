import cherrypy
import os.path
import hashlib
import string
import time
import random
from pymongo import MongoClient
from captcha.image import ImageCaptcha

captcha_output = ""
#Making a strong hash using sha512(It's little bit slow it think)
def hasher(password):
    password = str(password)
    h = hashlib.sha512(password.encode())
    return h.hexdigest()

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

#404 page
def page404(status, message, traceback, version):
    return theme("صفحه مورد نظر یافت نشد","404")

def SearchDupUser(username):
    output = users.find_one({'username':username})
    if output is None:
        return True
    else:
        return False

def SearchUser(username,password):
    output = users.find_one({'username':username,'password':password})
    if output is None:
        return False
    else:
        return True

def InsertUser(username,password):
    data = {'username':username,'password':password}
    if SearchDupUser(username):
        users.insert_one(data)
        return True
    else:
        return False

def InsetPost(content,username):
    data = {'content':content,'username':username,'date':time.ctime()}
    posts.insert_one(data)    

def ShowAllPosts():
    text = ""
    posts_in_list = list(posts.find())
    posts_in_list.reverse()
    for post in posts_in_list:
        text += "توسط " + post['username'] + "در : " + post['date'] +":" + post['content'] + "<hr>"
    return text

class Site(object):
    @cherrypy.expose
    def index(self):
        html = theme(
        """<div style="text-align:center;">برای <a href="/login">ورود</a> کلیک کنید</div><div style="text-align:center;">برای <a href="/signin">ثبت نام</a> کلیک کنید<br></div>{}""".format(ShowAllPosts())
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
                if InsertUser(username,hasher(password)):
                    return theme("ثبت نام با موفقیت انجام شد ! <script>function Redirect() {window.location = \"/login\";}setTimeout('Redirect()', 1000);</script>","ثبت نام")
                else:
                    return theme("نام کاربری تکراریست <script>function Redirect() {window.location = \"/signin\";}setTimeout('Redirect()', 1000);</script>","ثبت نام")
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
            if SearchUser(username,hasher(password)):
                cherrypy.session['islogin'] = True
                return theme("ورود با موفقیت انجام شد ، در حال انتقال به پنل <script>function Redirect() {window.location = \"/panel\";}setTimeout('Redirect()', 1000);</script>","ورود")
        else:
            return theme("لطفا کپچا را صحیح وارد کنید<script>function Redirect() {window.location = \"/login\";}setTimeout('Redirect()', 1000);</script>","ورود")
    
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
                #Redirect to root
                InsetPost(contect,username)
                raise cherrypy.HTTPRedirect("/panel")
            else:
                #Redirect to root
                raise cherrypy.HTTPRedirect("/")
        except:
            #Redirect to root
            raise cherrypy.HTTPRedirect("/")

#Main function
if __name__ == "__main__":
    #Connecting to the mongod server
    client = MongoClient()
    #Making a database
    db = client['site']
    #Making collections
    users = db['users']
    posts = db['posts']
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