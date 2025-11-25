from flask import Flask
from application.database import db
app = None

def create_app():
    app = Flask(__name__)
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///hospital.sqlite3"
    db.init_app(app)
    app.app_context().push()
    return app

app = create_app()
from application.controllers import *

if __name__ == '__main__':
    # db.create_all()
    # user1 = User(username = 'admin123', email = 'user@admin.com', password = 'admin@1234', type = 'admin')
    # db.session.add(user1)
    # db.session.commit()
    # db.create_all()
    # department1 = Department(Department_name='Cardiology', Description='Department for Heart and Cardiovascular diseases')
    # department2 = Department(Department_name='Oncology', Description='Department for Cancer treatment')
    # department3 = Department(Department_name='General', Description='Department for General body-checkups')
    # db.session.add(department1)
    # db.session.add(department2)
    # db.session.add(department3)
    # db.session.commit()
    # db.create_all()
    app.run()
