from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from functools import wraps

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)
app.secret_key = "medtrack_secret"

# ---------------- MYSQL CONNECTION ----------------
def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",         # adjust if you use MySQL password
        database="medtrack"
    )
    return conn

# ---------------- LOGIN REQUIRED DECORATOR ----------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("index.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        role = request.form["role"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        table = "doctors" if role == "doctor" else "patients"

        # Check if email already exists
        cursor.execute(f"SELECT * FROM {table} WHERE email=%s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return "Email already registered!"

        # Insert new user
        cursor.execute(f"INSERT INTO {table} (name,email,password) VALUES (%s,%s,%s)", (name,email,password))
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("login"))

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # check doctor
        cursor.execute("SELECT * FROM doctors WHERE email=%s AND password=%s",(email,password))
        doctor = cursor.fetchone()
        if doctor:
            session["user"] = email
            session["role"] = "doctor"
            cursor.close()
            conn.close()
            return redirect(url_for("doctor_dashboard"))

        # check patient
        cursor.execute("SELECT * FROM patients WHERE email=%s AND password=%s",(email,password))
        patient = cursor.fetchone()
        cursor.close()
        conn.close()
        if patient:
            session["user"] = email
            session["role"] = "patient"
            return redirect(url_for("patient_dashboard"))

        return "Invalid credentials"

    return render_template("login.html")

# ---------------- DASHBOARDS ----------------
@app.route("/patient_dashboard")
@login_required
def patient_dashboard():
    return render_template("patient_dashboard.html")

@app.route("/doctor_dashboard")
@login_required
def doctor_dashboard():
    return render_template("doctor_dashboard.html")

# ---------------- BOOK APPOINTMENT ----------------
@app.route("/book_appointment", methods=["GET","POST"])
@login_required
def book_appointment():
    if session.get("role") != "patient":
        return "Only patients can book appointments."

    if request.method=="POST":
        doctor_email = request.form["doctor_email"]
        date = request.form["date"]
        time = request.form["time"]
        patient_email = session["user"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO appointments (doctor, patient_email, date, time, status) VALUES (%s,%s,%s,%s,%s)",
            (doctor_email, patient_email, date, time, "Pending")
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("view_appointments"))

    return render_template("book_appointment.html")

# ---------------- VIEW APPOINTMENTS ----------------
@app.route("/view_appointments")
@login_required
def view_appointments():
    user_email = session["user"]
    role = session.get("role")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if role == "doctor":
        cursor.execute("SELECT * FROM appointments WHERE doctor=%s ORDER BY date,time", (user_email,))
        appointments = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("view_appointment_doctor.html", appointments=appointments)

    else:  # patient
        cursor.execute("SELECT * FROM appointments WHERE patient_email=%s ORDER BY date,time", (user_email,))
        appointments = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template("view_appointment_patient.html", appointments=appointments)

# ---------------- ACCEPT / REJECT ----------------
@app.route("/accept/<int:id>")
@login_required
def accept_appointment(id):
    if session.get("role") != "doctor":
        return "Only doctors can accept appointments."

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE appointments SET status='Accepted' WHERE id=%s",(id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("view_appointments"))

@app.route("/reject/<int:id>")
@login_required
def reject_appointment(id):
    if session.get("role") != "doctor":
        return "Only doctors can reject appointments."

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE appointments SET status='Rejected' WHERE id=%s",(id,))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for("view_appointments"))

# ---------------- SUBMIT DIAGNOSIS ----------------
@app.route("/submit_diagnosis", methods=["GET", "POST"])
@login_required
def submit_diagnosis():
    if session.get("role") != "doctor":
        return "Only doctors can submit diagnosis."

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        appointment_id = request.form["appointment_id"]
        diagnosis = request.form["diagnosis"]

        cursor.execute(
            "UPDATE appointments SET diagnosis=%s WHERE id=%s",
            (diagnosis, appointment_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for("view_appointments"))

    # GET request: show appointments for this doctor
    cursor.execute("SELECT * FROM appointments WHERE doctor=%s ORDER BY date,time", (session["user"],))
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template("submit_diagnosis.html", appointments=appointments)

# ---------------- LOGOUT ----------------
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("home"))

# ---------------- RUN APP ----------------
if __name__=="__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)