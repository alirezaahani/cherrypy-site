import cherrypy
import sqlite3
import hashlib
import chevron
import random
import string
import io
import base64
import os
import os.path
import html
import time
from markdown import markdown
from captcha.image import ImageCaptcha

DB_NAME = './private/database.sqlite3'

def hasher(text):
    return hashlib.sha512(text.encode()).hexdigest()

def gen_captcha():
    captcha_output = ''.join(random.sample(string.hexdigits, 4)).lower()
    image = ImageCaptcha()
    file = io.BytesIO()
    image.write(captcha_output,file)
    byte = file.getvalue()
    base = base64.b64encode(byte)
    return (captcha_output,base.decode("utf-8"))




def RenderMenus():
    menus = []
    with sqlite3.connect(DB_NAME) as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM menu')
        for row in cur.fetchall():
            menus.append({'text':row[1],'link':row[2]})
        return menus

def RenderPosts(limit = -1,post_id = -1):
    posts = []
    with sqlite3.connect(DB_NAME) as con:
        cur = con.cursor()
        if (limit > 0.1) and (post_id > 0):
            try:
                cur.execute('SELECT * FROM posts WHERE id = ? LIMIT ?',(post_id,limit,))
            except:
                return False
        
        elif (limit == 0.1) and (post_id > 0):
            try:
                cur.execute('SELECT * FROM posts WHERE id = ?',(post_id,))
            except:
                return False
        
        elif limit == 0.1:
            cur.execute('SELECT * FROM posts')
        
        elif limit > 0:
            cur.execute('SELECT * FROM posts LIMIT ?',(limit,))
        
        else:
            cur.execute('SELECT * FROM posts')
        
        for row in cur.fetchall():
            posts.append({'user':row[1],'title':row[3],'content':row[2],'date':row[4],'post_id':row[0]})
    
    posts.reverse()
    return posts

def RenderAllows(limit = -1):
    users = []
    with sqlite3.connect(DB_NAME) as con:
        cur = con.cursor()
        if limit > 0:
            cur.execute('SELECT * FROM allow LIMIT ?',(limit,))
        else:
            cur.execute('SELECT * FROM allow')
        for row in cur.fetchall():
            users.append({'username':row[1]})
    return users




def CheckUser(password,username):
    with sqlite3.connect(DB_NAME) as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM users WHERE password = ? AND username = ?',(password,username,))
        data = cur.fetchall()
        if data:
            return data[0][3]
        else:
            return False

def IsAllowed(username):
    with sqlite3.connect(DB_NAME) as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM allow WHERE username = ?',(username,))
        if cur.fetchall():
            return True
        else:
            return False




def InsertPost(title,nickname,content):
    with sqlite3.connect(DB_NAME) as con:
        content = html.escape(content)
        content = markdown(content)
        date = time.ctime()
        cur = con.cursor()
        cur.execute('INSERT INTO posts(title,nickname,text,date) VALUES (?,?,?,?)',(title,nickname,content,date,))
        con.commit()
        return True

def InsertUser(username,password,nickname):
    with sqlite3.connect(DB_NAME) as con:
        cur = con.cursor()
        try:
            cur.execute('INSERT INTO users(username,password,nickname) VALUES (?,?,?)',(username,password,nickname))
            return True
        except sqlite3.IntegrityError:
            return False

def AllowUser(username):
    with sqlite3.connect(DB_NAME) as con:
        cur = con.cursor()
        try:
            cur.execute('INSERT INTO allow(username) VALUES(?)', (username,) )
            return True
        except sqlite3.IntegrityError:
            return False



@cherrypy.tools.register('before_handler')
def auth():
    if cherrypy.session.get("islogin"):
        return True
    else:
        raise cherrypy.HTTPRedirect("/login")



class App(object):
    @cherrypy.expose
    def index(self):
        args = {
            'menu' : RenderMenus(),
            'posts' : RenderPosts(10)
        }
        with open('pages/index.html') as f:
            return chevron.render(f,args)
    
    @cherrypy.expose
    def archive(self,post_id=-1):
        post_id = int(post_id)
        args = {
            'menu' : RenderMenus()
        }
        response = RenderPosts(0.1,post_id)
        if response:
            args['posts'] = response
        else:
            args['show_message'] = True
            args['message'] = 'No posts found :('
        
        with open('pages/archive.html') as f:
            return chevron.render(f,args)

    @cherrypy.expose
    def login(self,password = "",username = "",captcha = ""):
        if cherrypy.session.get("islogin"):
            raise cherrypy.HTTPRedirect('/panel')

        args = {
                'menu' : RenderMenus(),
                'message' : '',
                'show_message' : False,
                'form' : True,
                'base64' : ''
        }

        if password and username and captcha:
            args['show_message'] = True
            if cherrypy.session.get('captcha') == captcha:
                if CheckUser(hasher(password),username):
                    cherrypy.session['islogin'] = True
                    cherrypy.session['nickname'] = CheckUser(hasher(password),username)
                    raise cherrypy.HTTPRedirect('/panel')
                else:
                    args['message'] = 'Please check your password or username'
                    system_captcha = gen_captcha()
                    cherrypy.session['captcha'] = system_captcha[0]
                    args['base64'] = system_captcha[1]
            else:
                args['message'] = 'Please enter the captcha correctly'
                system_captcha = gen_captcha()
                cherrypy.session['captcha'] = system_captcha[0]
                args['base64'] = system_captcha[1]
        else:
            system_captcha = gen_captcha()
            cherrypy.session['captcha'] = system_captcha[0]
            args['base64'] = system_captcha[1]

        with open('pages/login.html') as f:
                return chevron.render(f,args)

    @cherrypy.expose
    def signin(self,password = "",username = "",nickname = "",captcha = ""):

        if cherrypy.session.get("islogin"):
            raise cherrypy.HTTPRedirect('/panel')

        args = {
                'menu' : RenderMenus(),
                'message' : '',
                'show_message' : False,
                'form' : True,
                'base64' : ''
        }

        if password and username and captcha:
            args['show_message'] = True
            if cherrypy.session.get('captcha') == captcha:
                if IsAllowed(username):
                    if InsertUser(username,hasher(password),nickname):
                        args['message'] = 'SignIn successfully!'
                        system_captcha = gen_captcha()
                        cherrypy.session['captcha'] = system_captcha[0]
                        args['base64'] = system_captcha[1]
                    else:
                        args['message'] = 'A user with same username exists, Please Try again!'
                        system_captcha = gen_captcha()
                        cherrypy.session['captcha'] = system_captcha[0]
                        args['base64'] = system_captcha[1]
                else:
                    args['message'] = 'You are not allowed!'
                    system_captcha = gen_captcha()
                    cherrypy.session['captcha'] = system_captcha[0]
                    args['base64'] = system_captcha[1]
            else:
                args['message'] = 'Please enter the captcha correctly'
                system_captcha = gen_captcha()
                cherrypy.session['captcha'] = system_captcha[0]
                args['base64'] = system_captcha[1]
        else:
            system_captcha = gen_captcha()
            cherrypy.session['captcha'] = system_captcha[0]
            args['base64'] = system_captcha[1]

        with open('pages/signin.html') as f:
                return chevron.render(f,args)

    @cherrypy.expose
    @cherrypy.tools.auth()
    def panel(self,title = "",content = ""):
        args = {
            'menu' : RenderMenus(),
            'show_message' : False,
            'message': ''
        }
        args['menu'].append({'link':'/logout','text':'Logout'})
        args['menu'].append({'link':'/allow','text':'Allow users'})
        if title and content:
            args['show_message'] = True
            if InsertPost(title,cherrypy.session.get("nickname"),content):
                args['message'] = 'Post submited !'
        else:
            args['show_message'] = False
        
        with open('pages/panel.html') as f:
            return chevron.render(f,args)
    
    @cherrypy.expose
    @cherrypy.tools.auth()
    def allow(self,username=""):
        args = {
            'menu' : RenderMenus(),
            'show_message' : False,
            'message': '',
            'allowes' : RenderAllows()
        }
        args['menu'].append({'link':'/logout','text':'Logout'})
        args['menu'].append({'link':'/allow','text':'Allow users'})
        if username:
            args['show_message'] = True
            if AllowUser(username):
                args['message'] = 'User allowed to signin now !'
            else:
                args['message'] = 'User is allready allowed to signin !'
        
        with open('pages/allow.html') as f:
            return chevron.render(f,args)

    @cherrypy.expose
    @cherrypy.tools.auth()
    def logout(self):
        cherrypy.session['islogin'] = False
        cherrypy.session['nickname'] = ""
        raise cherrypy.HTTPRedirect('/login')


def main():
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static'
        }
    }
    cherrypy.quickstart(App(),'/',conf)

if __name__ == "__main__":
    main()
