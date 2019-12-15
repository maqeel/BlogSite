from flask import Flask, flash, redirect, url_for, render_template, request
import hashlib # included in Python library, no need to install
import psycopg2 # for database connection
#from backend.forms import RegistrationForm
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import login_user, current_user, logout_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

u_authenticated = False
u_id="0"
u_name=""

posts = [
    {
        'author': 'Corey Schafer',
        'title': 'Blog Post 1',
        'content': 'First post content',
        'date_posted': 'April 20, 2018'
    },
    {
        'author': 'Jane Doe',
        'title': 'Blog Post 2',
        'content': 'Second post content',
        'date_posted': 'April 21, 2018'
    }
]

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

#    def validate_username(self, username):
#        user = Users.query.filter_by(username=username.data).first()
#        if user:
#            raise ValidationError('That username is taken. Please choose a different one.')

#    def validate_email(self, email):
#        user = Users.query.filter_by(email=email.data).first()
#        if user:
#            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

@app.route("/")
@app.route("/home")
def home():
    # show our html form to the user
    t_message = "Python and Postgres Registration Application"
    return render_template("home.html", u_authenticated=u_authenticated, u_name=u_name, message = t_message, posts=posts)

#@app.route("/")
@app.route("/register", methods=["POST","GET"])
def register():

    form = RegistrationForm()
    # get user input from the html form
    username=str(form.username.data)
    t_email=str(form.email.data)
    #t_hashed=hashlib.sha256(form.password.data.encode(utf8))
    t_password=str(form.password.data)
    #t_email = request.form.get("t_email", "")
    #t_password = request.form.get("t_password", "")

    # check for blanks
    if username == "":
        t_message = "Please fill in your email address"
        return render_template("register.html", message = t_message, form=form)

    # check for blanks
    if t_email == "":
        t_message = "Please fill in your email address"
        return render_template("register.html", message = t_message, form=form)

    if t_password == "":
        t_message = "Please fill in your password"
        return render_template("register.html", message = t_message, form=form)

    # hash the password they entered
    t_hashed = hashlib.sha256(t_password.encode())
    t_password = t_hashed.hexdigest()

    # database insert
    t_host = "blogdb_postgres"
    t_port = "5432"
    t_dbname = "blogdb"
    t_user = "docker"
    db_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=t_user)
    db_cursor = db_conn.cursor()

    # We take the time to build our SQL query string so that
    #   (a) we can easily & quickly read it
    #   (b) we can easily & quickly edit or add/remote lines
    #   The more complex the query, the greater the benefits
    s = "INSERT INTO users "
    s += "("
    s += " username"
    s += ", email"
    s += ", password"
    s += ") VALUES ("
    s += " '" + username + "'"
    s += ",'" + t_email + "'"
    s += ",'" + t_password + "'"
    s += ")"

    # Warning: this format allows for a user to try to insert
    #   potentially damaging code, commonly known as "SQL injection".
    #   In a later article we will show some methods for
    #   preventing this.

    # Here we are catching and displaying any errors that occur
    #   while TRYing to commit the execute our SQL script.
    if form.validate_on_submit():
        db_cursor.execute(s)
        try:
            db_conn.commit()
            flash('Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))
        except psycopg2.Error as e:
            t_message = "Database error: " + e + "/n SQL: " + s
            return render_template("register.html", message = t_message, form=form)

    t_message = "Your user account has been added."
    return render_template("register.html", message = t_message, form=form)

@app.route("/login", methods=["POST","GET"])
def login():

    form = LoginForm()

    t_email=str(form.email.data)
    t_password=str(form.password.data)

    # hash the password they entered
    t_hashed = hashlib.sha256(t_password.encode())
    t_password = t_hashed.hexdigest()

    t_host = "blogdb_postgres"
    t_port = "5432"
    t_dbname = "blogdb"
    t_user = "docker"
    db_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=t_user)
    db_cursor = db_conn.cursor()

    postgreSQL_select_Query = "select id, username from users where email='" + t_email +"' and password='" + t_password + "'"

    user=None

    if form.validate_on_submit():
        try:
            db_cursor.execute(postgreSQL_select_Query)
            
            global u_id
            global u_name
            global u_authenticated
            rs = db_cursor.fetchone()
            u_id=str(rs[0])
            u_name=str(rs[1])
#            for row in rs:
#                u_id=row["id"]

        except (Exception, psycopg2.Error) as error :
            print ("Error while fetching data from PostgreSQL", error)

        finally:
            #closing database connection.
            if(db_conn):
                db_cursor.close()
                db_conn.close()
                print("PostgreSQL connection is closed")
        
        if rs:
            u_authenticated = True
            form = PostForm()
            next_page = request.args.get('next')
            #return render_template("post.html", title='New Post', u_authenticated=u_authenticated, u_id=u_id,
            #               form=form, legend='New Post')
            return render_template("home.html", title='Home', u_authenticated=u_authenticated, u_name=u_name, u_id=u_id, posts=posts)
            #return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/post", methods=["POST","GET"])
def post():
    form = PostForm()
    u_authenticated=True

    t_title=str(form.title.data)
    t_content=str(form.content.data)

    # database insert
    t_host = "blogdb_postgres"
    t_port = "5432"
    t_dbname = "blogdb"
    t_user = "docker"
    db_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=t_user)
    db_cursor = db_conn.cursor()

    global u_id
    global u_name

    s = "INSERT INTO Post "
    s += "(" 
    s += " title"
    s += ", content"
    s += ", user_id"
    s += ") VALUES ("
    s += " '" + t_title + "'"
    s += ",'" + t_content + "'"
    s += "," + u_id + ")"

    if form.validate_on_submit():
        db_cursor.execute(s)
        try:
            db_conn.commit()
            flash('Your post has been created!', 'success')
            return redirect(url_for('post'))
        except psycopg2.Error as e:
            print ("Error while inserting data in PostgreSQL", error)

    t_message = "Your post has been added."
    return render_template('post.html', title='New Post',u_name=u_name, u_authenticated=u_authenticated,
                           form=form, legend='New Post')

@app.route("/logout")
def logout():
    global u_authenticated
    u_authenticated = False
    #return redirect(url_for('home'))
    t_message = "Python and Postgres Registration Application"
    return render_template("home.html", u_authenticated=u_authenticated, message = t_message, posts=posts)

@app.route("/account")
def account():
    global u_name
    return render_template('account.html', title='Account', u_name=u_name, u_authenticated=u_authenticated)

@app.route("/user/<string:u_name>")
def user_posts(u_name):
    page = request.args.get('page', 1, type=int)
#    user = User.query.filter_by(username=username).first_or_404()

    t_host = "blogdb_postgres"
    t_port = "5432"
    t_dbname = "blogdb"
    t_user = "docker"
    db_conn = psycopg2.connect(host=t_host, port=t_port, dbname=t_dbname, user=t_user)
    db_cursor = db_conn.cursor()

    #global u_name
    global u_id
    global u_authenticated
    postgreSQL_select_Query = "select * from post where user_id=" + u_id

    try:
        db_cursor.execute(postgreSQL_select_Query)
        posts = db_cursor.fetchall()
#        u_id=str(rs[0])
#        u_name=str(rs[1])
#       for row in rs:
#       u_id=row["id"]

    except (Exception, psycopg2.Error) as error :
        print ("Error while fetching data from PostgreSQL", error)

    finally:
        #closing database connection.
        if(db_conn):
            db_cursor.close()
            db_conn.close()
            print("PostgreSQL connection is closed")

    #posts = Post.query.filter_by(author=user)\
     #   .order_by(Post.date_posted.desc())\
      #  .paginate(page=page, per_page=5)
    return render_template('user_posts.html', u_authenticated=u_authenticated, posts=posts, u_name=u_name)

# this is for command line testing
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
