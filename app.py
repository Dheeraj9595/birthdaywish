from flask import Flask, jsonify, Response
from flask_restx import Api, Resource
from email.mime.text import MIMEText
import smtplib
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:1234@localhost/birthdayapp'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database Models


class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))
    event_type = db.Column(db.String(50))
    date = db.Column(db.Date)


class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    events = db.relationship('Event', backref='employee')


class Template(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50))
    content = db.Column(db.Text)


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    message = db.Column(db.String, nullable=False)

def send_email(email, content):
    try:
        # In a real-world scenario, use an email sending library/service here
        print(f"Sent email to {email}: {content}")
        return True
    except Exception as e:
        db.session.add(Log(message=str(e)))
        db.session.commit()
        return False


@app.route("/send-test-email")
def send_test_email_route():
    if send_email('dheeraj.959595@gmail.com', 'Test', '<h1>This is a test email.</h1>'):
        return "Email sent successfully!"
    else:
        return "Failed to send email."


api = Api(app, version='1.0', title='Event API',
          description='A simple Event API')


ns_logs = api.namespace('logs', description='Log operations')


@ns_logs.route('/')
class LogList(Resource):
    def get(self):
        logs = Log.query.all()
        return [{"id": log.id, "timestamp": log.timestamp, "message": log.message} for log in logs]


@app.route("/process-events") #to process the birthday wishes 
def process_events():
    today = datetime.today().date()
    events = Event.query.filter_by(date=today).all()

    if not events:
        db.session.add(Log(message="No events today"))
        db.session.commit()
        return jsonify(message="No events today")

    for event in events:
        template = Template.query.filter_by(
            event_type=event.event_type).first()
        if template:
            content = template.content.replace("{name}", event.employee.name)
            if send_email(event.employee.email, content):
                db.session.add(
                    Log(message=f"Email sent to {event.employee.email} for {event.event_type}"))
            else:
                db.session.add(Log(
                    message=f"Failed to send email to {event.employee.email} for {event.event_type}"))
        else:
            db.session.add(Log(message=f"No template for {event.event_type}"))

        db.session.commit()

    return jsonify(message="Processing completed")

@app.route("/logs") #for logs of email sent
def view_logs():
    logs = Log.query.all()
    return jsonify([{"id": log.id, "timestamp": log.timestamp, "message": log.message} for log in logs])



if __name__ == "__main__":
    app.run(debug=True)
