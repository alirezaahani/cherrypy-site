# cherrypy-site
A simple site with cherrypy and sqlite
## Run on localhost
First of all,you need to install cherrypy with pip:  
```
pip3 install cherrypy
```  
Then clone the code with git:  
```
git clone https://github.com/alirezaahani/cherrypy-site.git
```  
And finaly run the main.py:  
```
python main.py
```  
## Run on PythonAnyWhere  
First you need make an account on PythonAnyWhere.  
Then in the panel , select "web" form the menu.  
If you don't have any apps , create one with Manually config.  
Open the file browser and create a folder named "public" and in it create another folder and name it css.  
In css folder put "style.css" file and save.  
Edit you wsgi file which is in /var/www  
Put main-pythonanywhere.py in it and save.  
Now your site should be running.  
Demo : http://alirezaahani.pythonanywhere.com  
Be careful because main-pythonanywhere.py dosen't update like main code.  
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
- [x] Find a host for running site
