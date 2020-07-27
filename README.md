# cherrypy-site
A simple site with cherrypy and sqlite
## ScreenShots
![login](/screenshots/login.png)
![home](/screenshots/home.png)
![panel](/screenshots/panel.png)
![signin](/screenshots/signin.png)
![404](/screenshots/404.png)
## Run on localhost
First of all,you need to install cherrypy,pymongo and captcha with pip:  
```
pip3 install cherrypy captcha pymongo
```  
Then install mongod server on your os.Change the code if you changed the port.  
Then clone the code with git:  
```
git clone https://github.com/alirezaahani/cherrypy-site.git
```  
And finaly run the main.py:  
```
python main.py
```   
## TODO
- [x] Start making site
- [x] Make the css and html
- [x] Connect site to sqlite database
- [x] Add loginin and signin
- [x] Use hash for saving password
- [x] Add user panel
- [x] Add posting and writing in site
- [x] Show posts and author of post in main page
- [ ] Work on security
- [ ] Find a host for running site
### Importent thing about this site if you want to run it on your host or server
Disable the caching. 
Enable mongodb in your server on default port(or change it in the code)
And have luck !
