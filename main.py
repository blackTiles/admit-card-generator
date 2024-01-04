from flask import Flask, render_template, redirect, request, session, flash
import mysql.connector
from datetime import timedelta
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.permanent_session_lifetime = timedelta(days=2)


try:
    db = mysql.connector.connect(database="pythonprojects", host="db4free.net", user="user123", password="123456")
    cursor = db.cursor()
except mysql.connector.Error as e:
    print(f"Error connecting to MySQL: {e}")
    cursor = None

@app.route("/")
def index():
    if 'user_id' in session:
        return redirect("/download")
    else:
        return render_template("index.html")

@app.route("/submit", methods=["POST", "GET"])
def submit():
    if request.method == "POST":
        try:
            hall_ticket_number = request.form["ticket"]
            date_of_birth = request.form["dob"]
            
            if hall_ticket_number != "" and date_of_birth != "":
                cursor.execute("""SELECT * FROM employees WHERE ROLLNO='{}' AND DOB='{}' """.format(hall_ticket_number, date_of_birth))
                user = cursor.fetchall()
                
                if len(user) > 0:
                    session.permanent = True
                    session['user_id'] = user[0][3]
                    return redirect("/download")
                else:
                    flash("The given Roll Number and Date Of Birth doesn't match.")
                    return redirect("/")
            else:
                flash("The form shouldn't be empty")
                return redirect("/")
        except mysql.connector.Error as e:
            print(f"MySQL Error: {e}")
            return render_template("error.html", error_message="An error occurred while processing your request.")
    else:
        return redirect("/")


@app.route("/download")
def download():
    if 'user_id' in session:
        try:
            rollno = session['user_id']
            cursor.execute("""SELECT * FROM employees WHERE ROLLNO='{}' """.format(rollno))
            user = cursor.fetchall()
            
            return render_template("download.html", data={'sno': user[0][0], 'dateofexam': user[0][1], 'appearingpost': user[0][2], 'rollno': user[0][3], 'name': user[0][4], 'fathername': user[0][5], 'dob': user[0][6], 'venue': user[0][7], 'address': user[0][8], 'imageurl': user[0][9]})
        except mysql.connector.Error as e:
            print(f"MySQL Error: {e}")
            return render_template("error.html", error_message="An error occurred while processing your request.")
    else:
        return redirect("/")

@app.route("/logout")
def logout():
    if 'user_id' in session:
        session.pop('user_id', None)
        return redirect("/")
    else:
        return redirect("/")

if __name__ == "__main__":
    app.run(debug=False)
