from flask import Flask,render_template,redirect,url_for,session,flash,request
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,EmailField,SubmitField,DateField
from wtforms.validators import DataRequired,Email,Length,ValidationError
import bcrypt 
from flask_mysqldb import MySQL
from datetime import datetime 

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '12345'
app.config['MYSQL_DB'] = 'crm'
app.secret_key = 'you_secret_key_here'

mysql = MySQL(app)

class RegisterForm(FlaskForm):
    firstname = StringField("First Name", validators=[DataRequired(), Length(min=1, max=60)])
    lastname = StringField("Last Name", validators=[DataRequired(), Length(min=1, max=50)])
    dob = DateField("Date of Birth", validators=[DataRequired()])
    username = StringField("User Name", validators=[DataRequired(), Length(min=5, max=60)])
    email = EmailField("Email", validators=[DataRequired(),Email(), Length(min=10, max=200)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=5, max=20)])
    phone = StringField("Phone", validators=[DataRequired(), Length(min=10, max=15)]) 
    submit = SubmitField("Register")
    
    def validate_username(self, field):
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT username FROM users WHERE username = %s",(field.data, ))
        user = cursor.fetchone()
        cursor.close()
        if user:
            raise ValidationError("Username Already Taken")
    
class LoginForm(FlaskForm):
    username = StringField("User Name", validators=[DataRequired()])
    password = PasswordField("Password",validators=[DataRequired()])
    submit = SubmitField("Login")
    
class AddLeadForm(FlaskForm):
    firstname = StringField("First Name", validators=[DataRequired(), Length(min=1, max=60)])
    lastname = StringField("Last Name", validators=[DataRequired(), Length(min=1, max=50)])
    email = EmailField("Email", validators=[DataRequired(),Email(), Length(min=10, max=255)])
    mobilephone = StringField("Phone", validators=[DataRequired(), Length(min=10, max=15)]) 
    submit = SubmitField("Add-Lead")

@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/register', methods=["GET", "POST"])
def register(): 
    form = RegisterForm()
    if form.validate_on_submit():
        firstname = form.firstname.data
        lastname = form.lastname.data
        dob = form.dob.data
        username = form.username.data
        email = form.email.data
        password = form.password.data
        phone = form.phone.data
        createddate = datetime.now()
        
        hashed_password = bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())
        print("Hello", hashed_password)
        #store data into database
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO users (firstname,lastname,username,email,password,phone,createddate,dob) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',(firstname,lastname,username,email,hashed_password,phone,createddate,dob))
        mysql.connection.commit()
        cursor.close()
        
        return redirect(url_for('login'))  
    return render_template('register.html',form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        #store data into database
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        if user and bcrypt.checkpw(password.encode('utf-8'), user[5].encode('utf-8')):
            session['id']=user[0]
            return redirect(url_for('dashboard'))
        else:
            flash("Login faild. Please check your username and password","danger")
            return redirect(url_for('login'))    
    return render_template('login.html',form=form)

@app.route('/dashboard')
def dashboard():
    if 'id' in session:
        id = session['id']
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT firstname,lastname,username,email FROM users WHERE id = %s ", (id,))
        user = cursor.fetchone()
        cursor.close()
        
        if user:
            return render_template('dashboard.html', u=user) 
    return redirect(url_for('login'))
        
@app.route('/leads')
def leads():
    if 'id' in session:
        
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM leads")
        leads = cursor.fetchall()
        cursor.close()
        
        return render_template('leads.html', leads=leads)
    return redirect(url_for('login'))

@app.route('/addlead',methods=['GET', 'POST'])
def addlead():
    if 'id' not in session:
        return redirect(url_for('login'))
    form = AddLeadForm()
    if 'id' in session:
        if form.validate_on_submit():

            firstname = form.firstname.data
            lastname = form.lastname.data
            email = form.email.data
            mobilephone = form.mobilephone.data
            createddate = datetime.now()
            
            cursor = mysql.connection.cursor()
            cursor.execute('INSERT INTO leads (firstname, lastname, email, mobilephone, createddate) VALUES (%s, %s, %s, %s, %s)',(firstname, lastname, email, mobilephone, createddate))
            mysql.connection.commit()
            cursor.close()
            
            flash("Lead added successfully!")
            return redirect(url_for('leads'))
        return render_template('addlead.html',form=form)

@app.route('/logout')
def logout():
    session.pop('id', None)
    flash("You have been logged out successfully. ")
    return redirect(url_for('login'))
    
if __name__ == "__main__":
    app.run(debug=True) 