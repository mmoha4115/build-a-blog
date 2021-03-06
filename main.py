from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:asdqwe@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'

class Posts(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title,body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))

    post = db.relationship('Posts', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

#functions to validate length, spaces, empty field, and '@' and '.' in email
def length(field):
    if len(field) > 8 and len(field) < 120:
        return True
    return False

def spaces(field):
    space = ' '
    if space in field:
        return False
    return True

def empty(field):
    emp = ''
    if field == emp:
        return False
    return True

def atdot_check(email):
    at = '@'
    dot = '.'
    if at in email and dot in email:
        return True
    return False

def use_pass(field):
    error = empty(field)
    if error == False:
        return False
    error = length(field)
    if error == False:
        return False
    error = spaces(field)
    if error == False:
        return False
    return True

def eml(field):
    error = length(field)
    if error == False:
        return False
    error = spaces(field)
    if error == False:
        return False
    error = atdot_check(field)
    if error == False:
        return False
    return True

@app.route('/')
def blogpage():
    return redirect('/blog')

@app.before_request
def require_login():
    allowed_routes = ['login', 'register']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash('Logged In', 'error')
            return redirect('/')
        else:
            # TODO - explain why login failed
            flash('User password is invalid or the user does not exist', 'error')

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        
        main_msg = "That's not a valid {0}"
        verify_msg = "Passwords don't match"
        password_error = ''
        verify_error = ''
        email_error = ''
        succes_condition = 0    #counter if no error =0 - return succes.html
        #validate email
        if eml(email) == False:
            email = ''
            email_error = main_msg.format('email')
            succes_condition +=1
        #validate password
        if use_pass(password) == False:
            password_error = main_msg.format('password')
            succes_condition+=1
        #validate verify-password
        if verify != password :
            verify_error = verify_msg 
            succes_condition+=1
        #if any error= render user-signup.html with errors else render succes.html
        if succes_condition > 0:
            return render_template('register.html', email=email, email_error=email_error,
            password='', password_error=password_error, 
            verify='', verify_error=verify_error)
        # TODO - validate user's data

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

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')

@app.route('/blog')
def blog():
    posts = Posts.query.all()
    return render_template('blog.html', posts=posts)
    
@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        title_error = ''
        body_error = ''
        bad_field = 0
        if empty(body) == False:
            body_error =  'Please fill in the body.'
            bad_field += 1
        if empty(title) == False:
            title_error = 'Please fiil in the title.' 
            bad_field += 1
        if bad_field > 0:
            return render_template('newpost.html', title=title, body=body,title_error=title_error,body_error=body_error)
        owner = User.query.filter_by(email=session['email']).first()
        new_post = Posts(title,body,owner)
        db.session.add(new_post)
        db.session.commit()
        return render_template('viewpost.html',post_title=title,post_body=body)
    return render_template('newpost.html')
    
@app.route('/viewpost')
def viewpost():
    post_id = request.args.get('post_id')
    post_id = int(post_id)
    post = Posts.query.filter_by(id = post_id).first()
    post_title = post.title
    post_body = post.body
    return render_template('viewpost.html',post_title=post_title,post_body=post_body)

if __name__ == '__main__':
    app.run()







