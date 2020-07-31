import cherrypy
import os.path
import hashlib
import string
import time
import random
import re
from pymongo import MongoClient
from captcha.image import ImageCaptcha

captcha_output = ""

#Making a strong hash using sha512(It's little bit slow it think)
def Hasher(password):
    password = str(password)
    h = hashlib.sha512(password.encode())
    return h.hexdigest()

@cherrypy.tools.register('before_handler')
def auth():
    sess = cherrypy.session
    if sess.get("islogin"):
        return True # It should just return, not important what it returns
    else:
        raise cherrypy.HTTPRedirect("/login")

def Redirect(url):
    output = "<script>function Redirect() {window.location = \"" + url + "\";}setTimeout('Redirect()', 1000);</script>"
    return output

#This fucntion is for theme
def Theme(text,title):
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
def Page404(status, message, traceback, version):
    return Theme("صفحه مورد نظر یافت نشد","404")

def ShowPostsByAuthor(author):
    output = ""
    counter = 0
    posts_in_list = list(posts.find())
    posts_in_list.reverse()
    for post in posts_in_list:
        if re.search(author,post['username']):
            if counter == 0:
                output += str(len(posts_in_list)) + " پست از طریق عبارت باقاعده  : " + author + " پیدا شد " + "<hr>"
            output += "توسط " + post['username'] + " در "  + post['date'] +": <br>" + post['content'] + "<hr>"
            counter += 1
        else:
            output = "هیچ پستی توسط عبارت با قاعده : " + author + "پیدا نشد ."
    return output

def SearchDupUser(username):
    output = users.find_one({'username':username})
    if output is None:
        return True
    else:
        return True

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
    output = ""
    posts_in_list = list(posts.find())
    posts_in_list.reverse()
    for post in posts_in_list:
        output += "توسط " + post['username'] + " در "  + post['date'] +": <br>" + post['content'] + "<hr>"
    return output

class Site(object):
    @cherrypy.expose
    def index(self):
        html = Theme(
        """<center>برای <a href="/login">ورود</a> کلیک کنید<br>برای <a href="/signin">ثبت نام</a> کلیک کنید<br></center>
        <br>
        <center>
            <form method="get" action="searchprocess">
                نام نویسنده : <input name="author" />
                <button>جست و جو</button>
                <p>جست و جو از طریق عبارات باقاعده و در نویسنده ها جست و جو انجام میشود</p>
            </form>
        </center>
        {}
        """.format(ShowAllPosts())
        ,"صفحه اصلی")
        return html

    @cherrypy.expose
    def signin(self, username="", password="",captcha=""):
        if not(username and password):
            #Making captcha and putting it in public/out.png
            global captcha_output
            captcha_output = ''.join(random.sample(string.hexdigits, 4)).lower()
            image = ImageCaptcha()
            image.write(captcha_output,"./public/out.png")
            return Theme("""
            <center>
                <p>پسورد باید حداقل ۶ حرف باشد</p>
                <p>جهت جلوگیری از مشکلات در ورود لطفا از حروف انگلیسی برای نام کاربری خود استفاده کنید</p>
                <form method="post" action="/signin" />
                    نام کاربری:<input type="text" value="" name="username" /><br>
                    رمز ورود:<input type="password" value="" name="password" /><br>
                    کپجا : <input type="text" name="captcha"><br>
                    <button type="submit">ثبت نام</button><br>
                    <img src="static/out.png">
                </form>
            </center>""","ثبت نام")
        if captcha.lower() == captcha_output:
            #Inserting the user
            if InsertUser(username,Hasher(password)):
                return Theme("ثبت نام با موفقیت انجام شد !{}".format(Redirect("/login")),"ورود")
            else:
                return Theme("نام کاربری تکراریست.{}".format(Redirect("/signin")),"ورود")
        else:
            return Theme("لطفا کپچا را درست وارد کنید.{}".format(Redirect("/signin")),"ورود")

    @cherrypy.expose
    def login(self, username="", password="",captcha=""):
        if not(username and password):
            #Making a captcha and saving it in public/out.png
            global captcha_output
            captcha_output = ''.join(random.sample(string.hexdigits, 4)).lower()
            image = ImageCaptcha()
            image.write(captcha_output,"./public/out.png")
            return Theme("""
            <center>
                <p>جهت ورود لطفا اطالاعات زیر را کامل کرده و بر روی دکمه ورود کلیک کنید</p>
                <form method="post" action="/login" />
                    نام کاربری:<input type="text" value="" name="username" /><br>
                    رمز ورود:<input type="password" value="" name="password" /><br>
                    کپجا : <input type="text" name="captcha"><br>
                    <button type="submit">ورود</button><br>
                    <img src="static/out.png">
                </form>
            </center>
            ""","ورود")
        if captcha.lower() == captcha_output:
            #Checking the database
            if SearchUser(username,Hasher(password)):
                cherrypy.session['islogin'] = True
                return Theme("ورود با موفقیت انجام شد ! در حال انتقال شما به پنل.{}".format(Redirect("/panel")),"ورود")
            else:
                return Theme("نام کاربری یا رمز عبور اشتباه است{}".format(Redirect("/login")),"ورود")
        else:
            return Theme("لطفا کپچا را صحیح وارد کنید{}".format(Redirect("/login")),"ورود")
    
    @cherrypy.expose
    @cherrypy.tools.auth()
    def panel(self,contect="",username=""):
        if not (contect and username):
            output = """
            <center>
                <a href="/logout">خروج</a></center>
                <form method="post" action="/panel">
                    اسم نویسنده :<input type="text" name="username"><br>
                    <textarea name="contect"></textarea><br>
                    <button type="submit">ثبت</button>
                </form>
            </center>"""
            #Showing a form for inseting posts
            return Theme(output,"مرکز مدیریت")
        else:
            contect = contect.replace("\n","<br>")
            contect = contect.replace("<script>","lol")
            contect = contect.replace("<style>","lol")
            username = username.replace("<script>","lol")
            username = username.replace("<style>","lol")
            InsetPost(contect,username)
            return Theme("مطلب شما با موفقیت ارسال شد ! در حال انتقال به پنل {}".format(Redirect("/panel")),"پنل")
    
    @cherrypy.expose
    @cherrypy.tools.auth()
    def logout(self):
        cherrypy.session['islogin'] = False
        #Redirect to root
        raise cherrypy.HTTPRedirect("/")
    
    @cherrypy.expose
    def searchprocess(self,author):
        author = author.replace("<script>","lol")
        author = author.replace("<style>","lol")
        return Theme(ShowPostsByAuthor(author),"جست و جو")

#Main function
if __name__ == "__main__":
    #Connecting to the mongod server
    client = MongoClient()
    #Making a database
    db = client['cherrypy']
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
            'error_page.404': Page404,
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