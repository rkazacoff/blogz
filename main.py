from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG']=True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text(255))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16))
    password = db.Column(db.String(16))
    blogs = db.relationship('Blog', backref = 'owner')
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        
@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route("/newpost", methods=['POST', 'GET'])
def newpost():
    
    blog_title_error = ''
    blog_body_error = ''
    
    if request.method == 'POST':
        blog_title = request.form.get('blog')
        owner = request.form.get('owner_id')
        if len(blog_title) < 1:
            blog_title_error = ('Your title must contain at least 1 character')
            
        blog_body = request.form.get('blog-body')
        if len(blog_body) < 1:
            blog_body_error = ('Your blog body must contain at least 1 character')
        
        if any([blog_title_error, blog_body_error]):
            return render_template('newpost.html', blog_title_error=blog_title_error, 
            blog_body_error=blog_body_error, blog_title=blog_title, blog_body=blog_body)
        else:
            new_blog = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog)
            db.session.commit()
            new_blog_id = new_blog.id
            blog = Blog.query.get(new_blog_id)
            return render_template('/blog.html', blog=blog)

    return render_template('newpost.html', title="Add New Blog Post")

def blog_checkoff():

    blog_id = int(request.form['blog-id'])
    blog = Blog.query.get(blog_id)
    db.session.add(blog)
    db.session.commit()
    return redirect('/newpost')

@app.route('/blog', methods=['GET'])
def blog():
    
    blog_id = int(request.args.get('id'))
    blog = Blog.query.get(blog_id)
    
    return render_template('blog.html', blog=blog)
    

@app.route('/', methods=['GET','POST'])
def index():   
    
    
    posted_blogs = Blog.query.all()
    return render_template('index.html',posted_blogs=posted_blogs)

@app.route('/signup', methods=['GET','POST'])
def signup():

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"

    return render_template('register.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            # flash("Logged in")
            return redirect('/newpost')
        else:
            #flash('User password incorrect, or user does not exist', 'error')
            return '<h1>Error!</h1>'

    return render_template('login.html')

# @app.route('/index', methods=['GET','POST'])


# if __name__ == '__main__':
#     app.run()