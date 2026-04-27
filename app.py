from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = 'skportal2024'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skportal.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ── MODELS ──────────────────────────────────

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'sk_council' or 'captain'

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='Planned')
    budget = db.Column(db.Float, default=0.0)
    start_date = db.Column(db.String(20))
    end_date = db.Column(db.String(20))

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer)
    address = db.Column(db.String(200))
    contact = db.Column(db.String(20))
    status = db.Column(db.String(20), default='Active')

class FinancialReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    amount = db.Column(db.Float, default=0.0)
    report_type = db.Column(db.String(20))  # 'Income' or 'Expense'
    date = db.Column(db.String(20))
    description = db.Column(db.Text)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    doc_type = db.Column(db.String(50))
    filename = db.Column(db.String(200))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

# ── ROUTES ───────────────────────────────────

@app.route('/')
def public():
    projects = Project.query.all()
    return render_template('public.html', projects=projects)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user'] = user.username
            session['role'] = user.role
            if user.role == 'sk_council':
                return redirect(url_for('sk_dashboard'))
            elif user.role == 'captain':
                return redirect(url_for('captain_dashboard'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ── SK COUNCIL ───────────────────────────────

@app.route('/sk')
def sk_dashboard():
    if session.get('role') != 'sk_council':
        return redirect(url_for('login'))
    projects = Project.query.all()
    members = Member.query.all()
    reports = FinancialReport.query.all()
    documents = Document.query.all()
    return render_template('sk_dashboard.html',
                           projects=projects,
                           members=members,
                           reports=reports,
                           documents=documents)

@app.route('/sk/add-project', methods=['GET', 'POST'])
def add_project():
    if session.get('role') != 'sk_council':
        return redirect(url_for('login'))
    if request.method == 'POST':
        project = Project(
            name=request.form['name'],
            description=request.form['description'],
            status=request.form['status'],
            budget=float(request.form['budget']),
            start_date=request.form['start_date'],
            end_date=request.form['end_date']
        )
        db.session.add(project)
        db.session.commit()
        return redirect(url_for('sk_dashboard'))
    return render_template('add_project.html')

@app.route('/sk/add-member', methods=['GET', 'POST'])
def add_member():
    if session.get('role') != 'sk_council':
        return redirect(url_for('login'))
    if request.method == 'POST':
        member = Member(
            name=request.form['name'],
            age=int(request.form['age']),
            address=request.form['address'],
            contact=request.form['contact'],
            status=request.form['status']
        )
        db.session.add(member)
        db.session.commit()
        return redirect(url_for('sk_dashboard'))
    return render_template('add_member.html')

@app.route('/sk/add-report', methods=['GET', 'POST'])
def add_report():
    if session.get('role') != 'sk_council':
        return redirect(url_for('login'))
    if request.method == 'POST':
        report = FinancialReport(
            title=request.form['title'],
            amount=float(request.form['amount']),
            report_type=request.form['report_type'],
            date=request.form['date'],
            description=request.form['description']
        )
        db.session.add(report)
        db.session.commit()
        return redirect(url_for('sk_dashboard'))
    return render_template('add_report.html')

# ── BARANGAY CAPTAIN ─────────────────────────

@app.route('/captain')
def captain_dashboard():
    if session.get('role') != 'captain':
        return redirect(url_for('login'))
    projects = Project.query.all()
    members = Member.query.all()
    reports = FinancialReport.query.all()
    return render_template('captain_dashboard.html',
                           projects=projects,
                           members=members,
                           reports=reports)

# ── CREATE TABLES + DEFAULT USERS ────────────

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='sk_council').first():
        db.session.add(User(username='sk_council', password='sk2023', role='sk_council'))
    if not User.query.filter_by(username='captain').first():
        db.session.add(User(username='captain', password='captain2023', role='captain'))
    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)