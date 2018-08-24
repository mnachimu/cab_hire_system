from flask import Flask, render_template, redirect, url_for, request, session, flash
from random import random
import sqlite3 as db
import requests
from functools import wraps
from werkzeug.utils import secure_filename
import os

from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = "heythere"
app.config['UPLOAD_FOLDER'] = 'static/pics'
#app.config['MAIL_SERVER']='smtp.gmail.com'
#app.config['MAIL_PORT'] = 465
#app.config['MAIL_USERNAME'] = 'suvanika@gmail.com'
#app.config['MAIL_PASSWORD'] = 'starfire27'
#app.config['MAIL_USE_TLS'] = False
#app.config['MAIL_USE_SSL'] = True
#mail = Mail(app)

conn = db.connect('database/taxico.sqlite')
c = conn.cursor()

KEY = 'GIkrwTQkD0Cx45e6FniRpg'

def sendOTP(otp, to, fake=False):
    if not fake:
        URL = 'https://www.smsgatewayhub.com/api/mt/SendSMS?APIKey={}&senderid=TESTIN&channel=2&DCS=0&flashsms=0&number=91{}&text={}&route=13'.format(KEY, to, "Taxi Co, happy riding! OTP : " + str(otp))
        requests.get(URL)


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            
            if session['logged_in']:
                
                return f(*args, **kwargs)
        else:
            return redirect(url_for('login'))
    return wrap


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return render_template("home.html")


@app.route('/')
def home():
    return render_template("home.html")


@app.route("/dashboard")
@login_required
def dashboard():
    user_email = session["user"]
    #session["user"] = user_email
    c.execute("select name from user where email = '{}'".format(user_email))
    name = c.fetchone()[0]
    fname = name.split()[0]
    return render_template("dashboard.html", user=fname)


@app.route('/otp', methods=["GET", "POST"])
def verifylogin():
    if request.method == "GET":
        server_otp = 1111
        session["server_otp"] = server_otp
        # print "boooo", session["temp_email"]
        c.execute("select ph_no from user where email = '{}'".format(session["temp_email"]))
        user_ph = c.fetchone()[0]
        print(user_ph)
        sendOTP(to=user_ph, otp=server_otp, fake=True)
        return render_template("loginverify.html", mob=user_ph)
    else:
        client_otp = int(request.form["otp"])
        if client_otp == session["server_otp"]:
            session["logged_in"] = True
            session["user"] = session["temp_email"]
            session["temp_email"] = None
            return redirect(url_for("dashboard"))
        else:
            return render_template("loginverify.html", msg="Invalid OTP Try again")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template('login.html')
    else:
        okay = False
        email = request.form['email']
        # print email
        password = request.form['pass']
        c.execute("select email from login where email = '{}'".format(email))
        emails_db = c.fetchall()
        # print emails_db
        emails_db = [email_db[0] for email_db in emails_db]
        if email in emails_db:
            c.execute("select password from login where email = '{}';".format(email))
            db_pass = c.fetchone()[0]
            if password == db_pass:
                okay = True
            else:
                msg = "Invalid Credentials!"
        else:
            # print email
            # print emails_db
            okay = False
            msg = "No such user exists, sign up."
        if okay:
            session["temp_email"] = email
            print(session["temp_email"])
            
            print("hi")
            return redirect(url_for("verifylogin"))
            
        else:
            print(":(")
            return render_template('login.html', msg=msg)
            


@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "GET":
        server_otp = int(random() * 10000)
        session["server_otp"] = server_otp
        user_ph = session['temp'][1]
        sendOTP(to=user_ph, otp=server_otp)
        return render_template("verify.html", mob=session["temp"][1])
    else:
        client_otp = int(request.form["otp"])
        if client_otp == session["server_otp"]:
            c.execute("insert into user values (?, ?, ?, ?, ?, ?, ?)",
                      (session["temp"][0], session["temp"][2], "None", "-1", session["temp"][1], "None", "None"))
            c.execute("insert into login values (?, ?)", (session["temp"][2], session["temp"][3]))
            conn.commit()
            session["logged_in"] = True
            session["user"] = session["temp"][2]
            session['temp'] = None
           # msg = Message('Registration succcessful!', sender = 'suvanika@gmail.com', recipients = session["user"])
            #msg.body = "Hey there! Thanks for registering with us. Hope you have a heavenly journey :D!"
            #mail.send(msg)
            return redirect(url_for("dashboard"))
        else:
            return render_template("verify.html", msg="Invalid OTP", mob=session["temp"][1])


@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template('signup.html')
    else:
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        password = request.form["pass"]
        repeat_password = request.form["repeat-pass"]
        okay = True
        if password != repeat_password:
            okay = False
            msg = "Passwords do not match!"
        c.execute("select email from user")
        emails_db = c.fetchall()
        emails_db = [email_db[0] for email_db in emails_db]
        if email in emails_db:
            okay = False
            msg = "Email already exists! Try logging in instead"
        c.execute("select ph_no from user")
        phone_db = c.fetchall()
        phone_db = [int(ph_db[0]) for ph_db in phone_db]
        if int(phone) in phone_db:
            okay = False
            msg = "Phone number is already registered!"
        if okay:
            session["temp"] = [name, phone, email, password]
            return redirect(url_for("verify"))
        else:
            return render_template("signup.html", msg=msg)


"""@app.route('/profile', methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "GET":
        User = session["user"]
        print (User)
        c.execute("select * from user where email = '{}'".format(session["user"]))
        name, email, address, dob, ph_no, state, country,balance = c.fetchone()
        if dob == "-1":
            dob = None
        if state == "None":
            state = None
        if country == "None":
            country = None
        if address == "None":
            address = None
        return render_template("profile.html", name=name, email=email, phone=ph_no, dob=dob, address=address, country=country, state=state)
    else:
        return redirect(url_for("editprofile"))

@app.route('/editprofile', methods=["GET", "POST"])
@login_required
def editprofile():
    if request.method == "GET":
        
        User = session["user"]
        print (User)
        c.execute("select * from user where email = '{}'".format(User))
        name, email, address, dob, ph_no, state, country, balance = c.fetchone()
        if dob == "-1":
            dob = ""
        if state == "None":
            state = ""
        if country == "None":
            country = ""
        if address == "None":
            address = ""
        return render_template("editprofile1.html",   name=name, email=email, phonenumber=ph_no, dob=dob, address=str(address), country=country, state=state)
    else:

        if request.method == 'POST':
            
            User = session["user"]
            name = request.form["name"]
            phone = request.form["phonenumber"]
            address = request.form["address"]
            dob = request.form["dob"]
            country = request.form["country"]
            state = request.form["state"]
        
        c.execute("UPDATE user SET name = ? ,ph_no = ?,address= ?,dob = ? ,state= ?,country= ? WHERE email= ? ",
                  (name, phone, address, dob, state, country, User))
        conn.commit()
        return redirect(url_for("profile"))"""


@app.route('/forgetpass', methods=["GET","POST"])
def forget():
    if request.method == "GET":
       return render_template('forgetpass.html')
    else:
        okay = True
        email = request.form["email"]
        phone = request.form["phno"]
        password = request.form["pass"]
        repeat_password = request.form["repass"]
        if password != repeat_password:
            okay = False
            msg = "Passwords do not match!"
        if okay:
            c.execute("""UPDATE login SET password = ? WHERE email= ? """,
                      (password,email))
            session["temp"] = [email, phone, password, repeat_password]
            return redirect(url_for("passverify"))
        else:
            return render_template("forgetpass.html", msg=msg)

@app.route("/promo")
@login_required
def promo():
    return render_template("promo.html")

@app.route("/passverify", methods=["GET", "POST"])
def passverify():
    if request.method == "GET":
        server_otp = int(random() * 10000)
        session["server_otp"] = server_otp
        user_ph = session['temp'][1]
        sendOTP(to=user_ph, otp=server_otp)
        return render_template("passverify.html", mob=session["temp"][1])
    else:
        client_otp = int(request.form["otp"])
        if client_otp == session["server_otp"]:
            c.execute("insert into user values (?, ?, ?, ?, ?, ?, ?, ?)",
                      (session["temp"][0], session["temp"][2], "None", "-1", session["temp"][1], "None", "None","0"))
            c.execute("insert into login values (?, ?)", (session["temp"][2], session["temp"][3]))
            conn.commit()
            session["logged_in"] = True
            session["user"] = session["temp"][2]
            session['temp'] = None
           # msg = Message('Registration succcessful!', sender = 'suvanika@gmail.com', recipients = session["user"])
            #msg.body = "Hey there! Thanks for registering with us. Hope you have a heavenly journey :D!"
            #mail.send(msg)
            return redirect(url_for("login"))
        else:
            return render_template("passverify.html", msg="Invalid OTP", mob=session["temp"][1])


   
@app.route('/wall',methods=["GET", "POST"])
@login_required
def wall():
    if request.method == "GET":
        User = session["user"]
        print (User)
        c.execute("select balance from user where email = '{}'".format(User))
        balance = c.fetchone()
        b=balance[0]
        return render_template("wall.html", bal=b)

@app.route('/pay',methods=["GET","POST"])
@login_required
def pay():
    if request.method == "GET":
        User = session["user"]
        print (User)
        return render_template("pay.html")
    else:
        print "yeah"
        User = session["user"]
        print "one"
        b = request.form["amt"]
        print b
        num = request.form["num"]
        cvv = request.form["cvv"]
        print num
        print cvv
        cvv1=int(cvv)
        c.execute("select cvv from card where number = '{}'".format(num))
        car = c.fetchone()
        carcvv = car[0]
        print carcvv
        if carcvv == cvv1:
            print 1
            c.execute("select balance from user where email = '{}' ".format(User))
            print "yy"
            b1 = c.fetchone()
            b2 = int(b)
            b2 = b2 + b1[0]
            print b2
            c.execute("UPDATE user SET balance = ?  WHERE email= ? ", (b2, User))
            print "ggg"
            conn.commit()
            print "yeah agaon"
            return render_template("wall.html", bal=b2)
        else:
            return render_template("dashboard.html")


@app.route('/profile', methods=["GET", "POST"])
@login_required
def profile():
    if request.method == "GET":
        c.execute("select * from user where email = '{}'".format(session["user"]))
        name, email, address, dob, ph_no, state, country,balance = c.fetchone()
        if dob == "-1":
            dob = None
        if state == "None":
            state = None
        if country == "None":
            country = None
        if address == "None":
            address = None
        filename = secure_filename(session["user"][:-4] + ".jpg")
        imgpath1 = '../static/pics/' + filename
        if os.path.exists(imgpath1):
            imgpath = imgpath1
        else:
            imgpath = '../static/images/profile.png'

        return render_template("profile.html", name=name, email=email, phone=ph_no, dob=dob, address=address,
                               country=country, state=state, imgpath=imgpath)
    else:
        return redirect(url_for("editprofile"))


@app.route('/editprofile', methods=["GET", "POST"])
@login_required
def editprofile():
    if request.method == "GET":

        User = session["user"]
        print (User)
        c.execute("select * from user where email = '{}'".format(User))
        name, email, address, dob, ph_no, state, country,balance = c.fetchone()
        if dob == "-1":
            dob = ""
        if state == "None":
            state = ""
        if country == "None":
            country = ""
        if address == "None":
            address = ""
        return render_template("editprofile1.html", name=name, email=email, phonenumber=ph_no, dob=dob,
                               address=str(address), country=country, state=state)
    else:

        if request.method == 'POST':
            if 'file' not in request.files:
                flash('Nopicture attached')

            file = request.files['file']
            if file:
                user = session["user"][:-4] + ".jpg"
                filename = secure_filename(session["user"][:-4] + ".jpg")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                filename = secure_filename(session["user"][:-4] + ".jpg")
                imgpath = '../static/pics/' + filename
            file = request.files['aadhar']
            if file:
                user = session["user"][:-4] + "a.jpg"
                filename = secure_filename(session["user"][:-4] + "a.jpg")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                filename = secure_filename(session["user"][:-4] + "a.jpg")
                imgpath = '../static/pics/' + filename
            if 'file' not in request.files:
                flash('No Aadhar picture attached')

            User = session["user"]
            name = request.form["name"]
            phone = request.form["phonenumber"]
            address = request.form["address"]
            dob = request.form["dob"]
            country = request.form["country"]
            state = request.form["state"]

        c.execute("""UPDATE user SET name = ? ,ph_no = ?,address= ?,dob = ? ,state= ?,country= ? WHERE email= ? """,
                  (name, phone, address, dob, state, country, User))
        conn.commit()
        return render_template('profile.html',name=name, email=User, phone=phone, dob=dob, address=address,
                               country=country, state=state, imgpath=imgpath)


app.run()
