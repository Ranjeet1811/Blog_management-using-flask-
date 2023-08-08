from flask import Flask,request,render_template,Request,session,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json 
from flask_mail import Mail
import os
from werkzeug.utils import secure_filename
import math


with open('config.json','r') as c:
    params=json.load(c)["params"]


localserver = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['upload_folder'] = params['location']



if localserver:
    app.config['SQLALCHEMY_DATABASE_URI'] =params["localurl"]        #  'mysql://root:ranjeet@localhost/python'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] =params["prod_url"] 


db=SQLAlchemy(app)


class Contact(db.Model):
   
    ''' sno,name,email,phone_num,msg,date'''

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String)
    phone_num = db.Column(db.String,nullable=False)
    msg = db.Column(db.String,nullable=False)
    date = db.Column(db.String,nullable=True)



class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    subtitle = db.Column(db.String,nullable = False)
    content = db.Column(db.String,nullable=False)
    slug = db.Column(db.String,nullable=False)
    img_url = db.Column(db.String,nullable=False)
    date = db.Column(db.String,nullable=True)



@app.route('/')
def home():
    flash("Welcome to Ranjeet IT Services ","success")
    # flash("computer work","danger")

    post = Posts.query.filter_by().all()
    last = math.ceil(len(post))/int(params["no_of_posts"])
    page = request.args.get('page')
    if(not str(page).isnumeric()):
        page = 1
    page = int(page)
    post = post[(page-1)*int(params["no_of_posts"]): (page-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]
    if(page ==1):
        prev = "#"
        next ="/?page="+str(page+1)
    elif(page==last):
        prev="/?page="+str(page-1)
        next = "#"
    else:
        prev = "/?page="+str(page-1)
        next = "/?page="+str(page+1)

    return render_template('index.html',params = params,posts = post,prev=prev,next=next)


@app.route('/post/<string:post_slug>',methods = ['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug = post_slug).first()
    return render_template('post.html',params = params,post = post)


@app.route('/about')
def about():
    return render_template('about.html',params = params)


@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route('/uploader',methods = ['GET','POST'])
def uploader():
    if ("user" in session and session['user']==params['admin_user']):

        if request.method == "POST":
            f= request.files['file1']
            f.save(os.path.join(app.config['upload_folder'],secure_filename(f.filename)))
            return "Uploaded successfully"
        

@app.route('/delete/<string:sno>',methods = ['GET','POST'])
def delete(sno):
    if ("user" in session and session['user']==params['admin_user']):
        post = Posts.query.filter_by(sno= sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/dashboard')



@app.route('/edit/<string:sno>',methods = ['GET','POST'])
def edit(sno):
    # check user already login 
    if ("user" in session and session['user']==params['admin_user']):
        if request.method=='POST':
            title = request.form.get('title')
            subtitle = request.form.get('subtitle')
            slug = request.form.get('slug')
            content =request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()
# ADDING POST 
            if sno=='0' or sno == 0:
                print("Hello")
                post = Posts(title = title,subtitle=subtitle,slug = slug,content=content,img_url=img_file,date= date)
                print(post)
                db.session.add(post)
                db.session.commit()
                flash("Your post submited succesfully","success")

                # edit post 
            else:
                post = Posts.query.filter_by(sno=sno).first()
                print("hello",post)
                post.title = title
                post.slug = slug
                post.content = content
                post.subtitle = subtitle
                post.img_url = img_file
                post.date = datetime.now()
                db.session.add(post)
                db.session.commit()
                flash("Your post edited succesfully","success")
                return redirect("/edit/"+sno)

        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html',params= params,post = post,sno =sno)
   

@app.route('/contact',methods = ['GET','POST'])
def contact():
    if (request.method == 'POST'):
        '''add entry to the database '''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        print(name,email,message)
        entry = Contact(name=name,email = email,phone_num= phone,msg = message,date = datetime.now())
        db.session.add(entry)
        db.session.commit()
        flash("thanks for submitting you details","success")
    return render_template('contact.html',params = params)




@app.route('/dashboard',methods =['GET','POST'])
def dashboard():
  
    # if user already log in 
    if "user" in session and session['user']==params['admin_user']:
        posts = Posts.query.filter_by().all()
        return render_template('dashboard.html',params=params,posts=posts)
    
    if request.method=='POST':
        username= request.form.get('user')
        userpass = request.form.get('pass')
        if username==params['admin_user'] and userpass==params['admin_pass']:
            #add user to log in 
            session['user']=username
            posts = Posts.query.filter_by().all()
            return render_template("dashboard.html", params=params,posts=posts)
        else:
            return redirect("/dashboard")
    else:

        return render_template('login.html',params = params)



if __name__ == '__main__':
    app.run(debug=True,port = 1726)


