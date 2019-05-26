from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG']=True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = '1q2w3e4r'

class Blog(db.Model):

    blog_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text(255))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), unique = True)
    password = db.Column(db.String(16))
    blogs = db.relationship('Blog', backref='owner')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        
@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route("/newpost", methods=['POST', 'GET'])
def newpost():
    
    blog_title_error = ''
    blog_body_error = ''
    
    if request.method == 'POST':
        blog_title = request.form.get('blog-title')
        blog_body = request.form.get('blog-body')
        owner = User.query.filter_by(username=session['username']).first()
        if len(blog_title) < 1:
            blog_title_error = ('Your title must contain at least 1 character')
                    
        if len(blog_body) < 1:
            blog_body_error = ('Your blog body must contain at least 1 character')
        
        if any([blog_title_error, blog_body_error]):
            return render_template('newpost.html', blog_title_error=blog_title_error, 
            blog_body_error=blog_body_error, blog_title=blog_title, blog_body=blog_body)
        else:
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            # new_blog.id = new_blog.id
            # blog = Blog.query.get(new_blog_id)
            return render_template('/blog.html', blog=new_blog)

    return render_template('newpost.html', title="Add New Blog Post")

@app.route('/blog', methods=['GET'])
def blog():
    
    if request.args.get("user_id"):
        user_ref = request.args.get('user_id')
        blogs = Blog.query.filter_by(owner_id = user_ref).all()
        return render_template('blog.html', blogs=blogs)
    
    # blog_ref = request.args.get('blog_id')
    
    else:
        blogs = Blog.query.get('blog_id')
        return render_template('blog.html', blogs=blogs)
    
@app.route('/', methods=['GET','POST'])
def index():   
    users = User.query.all()
    #posted_blogs = Blog.query.all()    
    #posted_blogs = Blog.query.filter_by(owner_id=owner_id).all()
    return render_template('index.html',users=users)

@app.route('/signup', methods=['GET','POST'])
def signup():
    name_error=''
    pass_error=''
    exist_error=''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user :
            exist_error = 'Username already exists!'
        if username =='' :
            name_error = "Please specify a valid username."
        if len(username) < 3 :
            name_error = "Username should be 3 or more characters."
        if password =='':
            pass_error = "Password required."
        if len(password) <= 3 :
            pass_error = "Password should be more than 3 characters."
        if password != verify :
            pass_error = "Passwords must match."
        if exist_error!='':
            return render_template('signup.html', exist_error=exist_error, username=username)
        if name_error !='' or pass_error !='':
            return render_template('signup.html', username=username, name_error=name_error, pass_error=pass_error)
        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = username
        flash("You have successfully signed up")
        
        return redirect('/login')
     
    return render_template('signup.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            # flash("Logged in")
            return redirect('/newpost')
        else:
            login_error = 'Wrong username/password, try again.'
            return render_template('login.html', login_error=login_error)

    return render_template('login.html')

#@app.route('/index', methods=['GET','POST'])

@app.route('/logout', methods=['GET'])
def logout():
    del session['username'] 
    return redirect ('/')


if __name__ == '__main__':
    app.run()