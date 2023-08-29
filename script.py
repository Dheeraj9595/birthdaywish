from app import app, db, Employee, Event, Template
from datetime import date



with app.app_context():
    # Now you can perform database operations
    
    new_employee = Employee(name="dheeraj pandey", email="dheeraj.959595@gmail.com")
    db.session.add(new_employee)
    db.session.commit()

    today = date.today()
    event_for_employee = Event(employee_id=new_employee.id, event_type="birthday", date=today)
    db.session.add(event_for_employee)
    db.session.commit()

    birthday_template = Template(event_type="birthday", content="Happy Birthday, {name}!")
    db.session.add(birthday_template)
    db.session.commit()

exit()