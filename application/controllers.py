from flask import Flask, render_template, redirect, request
from flask import current_app  as app
from .models import *

@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        this_user = User.query.filter_by(username=username).first()
        if not this_user:
            return render_template('login.html', error="This User doesn't exist kindly register!")
        if this_user.type == 'doctor':
            doctor = Doctor.query.filter_by(user_id=this_user.id).first()
            if doctor and doctor.blacklisted:
                return render_template('login.html', error="You have been blacklisted by the hospital. You can't login!")
        if this_user.type == 'general':
            patient = Patient.query.filter_by(user_id=this_user.id).first()
            if patient and patient.blacklisted:
                return render_template('login.html', error="You have been blacklisted by the hospital. You can't login!")   
        if this_user:
            if this_user.password == password:
                if this_user.type == 'admin':   
                    return redirect('/admin')
                elif this_user.type == 'doctor':
                    doctor = Doctor.query.filter_by(user_id=this_user.id).first()
                    return redirect(f'/doctor/{doctor.Doctor_id}')
                else:
                    patient = Patient.query.filter_by(user_id=this_user.id).first()
                    return redirect(f'/patient/{patient.Patient_id}')
            else:
                return render_template('login.html', error="Password entered is incorrect!")
        else:
            return render_template('login.html', error="User doesn't exist!")
           
    return render_template('login.html')

@app.route('/register', methods=["GET","POST"])
def register():
    this_user = User.query.filter_by(type='general').first()
    if request.method == "POST":
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        patient_name = request.form['patient_name']
        name_exists = User.query.filter_by(username=username).first()
        email_exists = User.query.filter_by(email=email).first()
        if name_exists or email_exists:
            return render_template('register.html', error="This User already exist. Kindly login!")
        else:
            user = User(username=username, email=email, password=password, type='general')
            db.session.add(user)
            db.session.commit()
            patient = Patient(Patient_name=patient_name, user_id=user.id)
            db.session.add(patient)
            db.session.commit()
            return redirect('/login')
    return render_template('register.html')

@app.route("/create", methods=["GET","POST"])
def create():
    this_user = User.query.filter_by(type="admin").first()
    if request.method == "POST":
        return render_template('create.html')
    
@app.route("/create-doctor", methods=["GET","POST"])
def create_dr():
    this_user = User.query.filter_by(type="admin").first()
    if request.method == "POST":
        name = request.form['name']
        department = request.form['department']
        experience = request.form['experience']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        email_exists = User.query.filter_by(email=email).first()
        if email_exists:
            return render_template('create.html', error='This email already exists. Kindly use different email!')
        else:
            user = User(username=username, email=email, password=password, type='doctor')
            db.session.add(user)
            db.session.commit()
            new_doctor = Doctor(Doctor_name=name, Department_name=department, Experience=experience, 
                                user_id=user.id)
            db.session.add(new_doctor)
            db.session.commit()
        return redirect("/admin")
    return render_template('create.html')
    
@app.route("/view-details-c/<int:patient_id>", methods=["GET","POST"])
def vdc(patient_id):
    doctors = Doctor.query.filter_by(Department_name='Cardiology', blacklisted=False).all()
    return render_template('view_details_cardiology.html', doctors=doctors, patient_id=patient_id)
    
@app.route("/view-details-o/<int:patient_id>", methods=["GET","POST"])
def vdo(patient_id):
    doctors = Doctor.query.filter_by(Department_name='Oncology', blacklisted=False).all()
    return render_template('view_details_oncology.html', doctors=doctors, patient_id=patient_id)  
    
@app.route("/view-details-g/<int:patient_id>", methods=["GET","POST"])
def vdg(patient_id):
    doctors = Doctor.query.filter_by(Department_name='General', blacklisted=False).all()
    return render_template('view_details_general.html', doctors=doctors, patient_id=patient_id)
      
@app.route('/view-details/<department>/<int:doctor_id>')
def vdd(department, doctor_id):
    doctors = Doctor.query.filter_by(Department_name=department).all()
    return render_template('view_details_doctor.html', doctors=doctors, department=department, doctor_id=doctor_id)


@app.route('/admin')    
def admin():
    this_user = User.query.filter_by(type="admin").first()
    all_doc = Doctor.query.all()
    all_pat = Patient.query.all()
    count = total()
    search = request.args.get('Search','').lower()
    appointments = Appointments.query.filter_by(Status='Booked').all()
    past_appointments = Appointments.query.filter((Appointments.Status=='Completed') | (Appointments.Status=='Cancelled')).all()
    upcoming_count = len(appointments)
    past_count = len(past_appointments)
    if search:
        all_doc = [doc for doc in all_doc if search in doc.Doctor_name.lower()]
        all_pat = [pat for pat in all_pat if search in pat.Patient_name.lower()] 
         

    return render_template("admin_dashboard.html", this_user=this_user, all_doc=all_doc, all_pat=all_pat, count=count, 
                           past_appointments=past_appointments,appointments=appointments, upcoming_count=upcoming_count, 
                           past_count=past_count)

def total():
    return{
    'total_doc' : Doctor.query.count(),
    'total_pat' : Patient.query.count()
    }

@app.route("/admin/edit-doctor/<int:doctor_id>", methods=["GET","POST"])
def edit_d(doctor_id):
    doctor = Doctor.query.filter_by(Doctor_id=doctor_id).first()
    if not doctor:
        return render_template("edit_doctor.html", error="This Doctor doesn't exist!")
    if request.method == "POST":
        doctor.Doctor_name = request.form.get('Doctor_name')   
        doctor.Department_name = request.form.get('Department_name')
        doctor.Experience = request.form.get('Experience')
        db.session.commit()
        return redirect('/admin')
    return render_template("edit_doctor.html", doctor=doctor)

@app.route("/admin/edit-patient/<int:patient_id>", methods=["GET","POST"])
def edit_p(patient_id):
    patient = Patient.query.filter_by(Patient_id=patient_id).first()
    if not patient:
        return redirect('/admin')
    if request.method == "POST":
        patient.Patient_name=request.form.get('pname')
        patient.Doctor_name=request.form.get('dname')
        patient.Department_name=request.form.get('department')
        db.session.commit()
        return redirect('/admin')
    return render_template('edit_patient_admin.html', patient=patient)


@app.route('/edit-patient', methods=["GET", "POST"])
def edit_ap():
    return render_template('edit_patient_admin.html')


@app.route('/admin/delete-patient/<int:patient_id>', methods=["GET","POST"])
def delete_patient(patient_id):
    if request.method == "POST":
        patient = Patient.query.get(patient_id)
        if patient:
            user = User.query.get(patient.user_id)
            if user:
                db.session.delete(user)
            db.session.delete(patient)
            db.session.commit()
    return redirect('/admin')        


@app.route('/edit-doctor', methods=["GET","POST"])
def edit():
        return render_template('edit_doctor.html')
    
@app.route('/admin/delete-doctor/<int:doctor_id>', methods=["POST"])
def delete(doctor_id):
    if request.method == "POST":
        doctor = Doctor.query.get(doctor_id)
        if doctor:
            user = User.query.get(doctor.user_id)
            if user:
                db.session.delete(user)
            db.session.delete(doctor)
            db.session.commit()
    return redirect('/admin')     

@app.route('/admin/blacklist-doctor/<int:doctor_id>', methods=["GET","POST"])
def blacklist1(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if doctor:
        doctor.blacklisted = True
        db.session.commit()
    return redirect('/admin')

@app.route('/admin/blacklist-patient/<int:patient_id>', methods=["GET","POST"])
def blacklist2(patient_id):
    patient = Patient.query.get(patient_id)
    if patient:
        patient.blacklisted = True
        db.session.commit() 
    return redirect('/admin') 

@app.route('/patient/<int:patient_id>', methods=["GET", "POST"])
def patient_dash(patient_id):
    patient = Patient.query.get(patient_id)
    this_user = User.query.filter_by(id=patient.user_id).first()
    if not patient:
        return render_template('patient_dashboard.html', error="This patient doesn't exist!")
    departments = Department.query.all()
    appointments = Appointments.query.filter_by(Patient_id=patient.Patient_id, Status = 'Booked').all()
    return render_template('patient_dashboard.html', patient=patient, departments=departments, appointments=appointments, this_user=this_user)

@app.route('/patient/<int:patient_id>/edit-profile', methods=["GET", "POST"])
def edit_profile(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return render_template('edit_profile_patient.html', error='Patient not found!')
    patient_id = patient.Patient_id
    if request.method == "POST":
        patient.Patient_name = request.form.get('patient_name')
        db.session.commit()
        return redirect(f'/patient/{patient_id}')
    return render_template('edit_profile_patient.html', patient=patient)   
            

@app.route('/patient/edit_profile_patient', methods=["GET","POST"]) 
def edit_profile1():
    this_user = User.query.filter_by(type='general').first()
    if request.method == "POST":
        return render_template('edit_profile_patient.html', this_user=this_user)
    
@app.route('/patient/<int:patient_id>/my-appointments')
def my_appointments(patient_id):
    patient = Patient.query.get(patient_id) 
    if not patient:
        return render_template('patient_dashboard.html', error='Patient not found!')
    appointments = Appointments.query.filter_by(Patient_id=patient.Patient_id).order_by(Appointments.Date.desc()).all()
    return render_template('patient_dashboard.html', patient=patient, appointments=appointments)

    
@app.route('/patient/<int:patient_id>/appointment/<int:doctor_id>', methods=["GET","POST"])
def appointment_book(patient_id,doctor_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return render_template('check_availability_pd.html', error='Patient not found!')
    doctor = Doctor.query.get(doctor_id)
    availabilities = DoctorAvailability.query.filter_by(Doctor_id=doctor_id, Is_available=True).order_by(DoctorAvailability.Date.asc()).all()
    if request.method == "POST":
        date = request.form.get('Date')
        time = request.form.get('Time')

        appointment_exist = Appointments.query.filter_by(Doctor_id=doctor_id, Date=date, Time=time, Status='Booked').first()
        if appointment_exist:
            return render_template('check_availability_pd.html', doctor=doctor, availabilities=availabilities, error='Slot Already Booked', patient=patient)
        available_slot = DoctorAvailability.query.filter_by(Doctor_id=doctor_id, Date=date, Start_time=time, Is_available=True).first()
        if available_slot:
            available_slot.Is_available = False
        patient.Doctor_name = doctor.Doctor_name
        patient.Department_name = doctor.Department_name
        appointment = Appointments(Patient_id=patient.Patient_id, Doctor_id=doctor_id, Date=date, Time=time, Status='Booked')
        db.session.add(appointment)
        db.session.commit()
        return redirect(f'/patient/{patient_id}')
    return render_template('check_availability_pd.html', doctor=doctor, availabilities=availabilities, patient=patient) 

@app.route('/patient/<int:patient_id>/history')
def p_history(patient_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return render_template('History.html', error='Patient not found!')
    complete_appointments = Appointments.query.filter_by(Patient_id=patient.Patient_id, Status='Completed').all()
    treatments = []
    for appointment in complete_appointments:
        treatment = Treatment.query.filter_by(Appointment_id=appointment.Appointment_id).first()
        if treatment:
            treatments.append(treatment)
    return render_template('History.html', patient=patient, all_pat=[patient], alltreatment=treatments)        

@app.route('/patient/<int:patient_id>/cancel-appointment/<int:appointment_id>', methods=["POST"])
def cancel_appointment(patient_id, appointment_id):
    patient = Patient.query.get(patient_id)
    if not patient:
        return "Patient not found!"
    appointment = Appointments.query.get(appointment_id)
    if appointment and appointment.Patient_id == patient.Patient_id:
        appointment.Status = 'Cancelled'
        db.session.commit()
    return redirect(f'/patient/{patient_id}')    

@app.route('/doctor/<int:doctor_id>')
def doctor(doctor_id):
    doctor = Doctor.query.get(doctor_id) 
    if not doctor:
        return "Doctor not found!"
    this_user = User.query.filter_by(id=doctor.user_id).first()
    appointments = Appointments.query.filter_by(Doctor_id=doctor.Doctor_id).all()  

    return render_template('doctor_dashboard.html', this_user=this_user, doctor=doctor,
                            appointments=appointments)

@app.route('/doctor/update', methods=["GET","POST"])
def patient_update():
    if request.method == "GET":
        appointment_id = request.args.get('appointment_id')
        doctor_id = request.args.get('doctor_id')
        appointment = Appointments.query.get(appointment_id)
        doctor = Doctor.query.get(doctor_id)
        if not appointment:
            return "Appointment not found!"
        return render_template('update.html', appointment=appointment, doctor=doctor)    
    if request.method == "POST":
        appointment_id = request.form.get('appointment_id')
        doctor_id = request.form.get('doctor_id')
        tests_done = request.form.get('Test')
        diagnosis = request.form.get('Diagnosis')
        prescription = request.form.get('Prescription')
        medicines = request.form.get('Medicines')

        appointment = Appointments.query.filter_by(Appointment_id=appointment_id).first()
        if not appointment:
            return redirect(f'/doctor/{doctor_id}')
        
        treatment = Treatment.query.filter_by(Appointment_id=appointment_id).first()
        if treatment:
            treatment.Tests_Done = tests_done
            treatment.Diagnosis = diagnosis
            treatment.Prescription = prescription
            treatment.Medicines = medicines 
        else:
            treatment = Treatment(Appointment_id=appointment_id, Tests_Done=tests_done, Diagnosis=diagnosis, 
                                  Prescription=prescription, Medicines=medicines)
            db.session.add(treatment)
        appointment.Status = 'Completed'
        db.session.commit()
        return redirect(f'/doctor/{doctor_id}')
    return render_template('update.html')

@app.route('/doctor/<int:doctor_id>/provide-a', methods=["GET","POST"])
def provide(doctor_id):
    doctor = Doctor.query.get(doctor_id)
    if not doctor:
        return "Doctor not found!"
    if request.method == "POST":
        date = request.form.get('Date')
        start_time = request.form.get('Start_time')
        end_time = request.form.get('End_time')

        doctor_available = DoctorAvailability.query.filter_by(Doctor_id=doctor.Doctor_id, Date=date).first()

        if doctor_available:
            doctor_available.Start_time = start_time
            doctor_available.End_time = end_time
            doctor_available.Is_available = True 
        else:
            new_availability = DoctorAvailability(Doctor_id=doctor.Doctor_id, Date=date, Start_time=start_time, 
                                                  End_time=end_time, Is_available=True)
            db.session.add(new_availability)
            db.session.commit()
        return redirect(f'/doctor/{doctor_id}/provide-a')
        
    availabilities = DoctorAvailability.query.filter_by(Doctor_id=doctor.Doctor_id).all()           
    return render_template('check_availability_dd.html', availabilities=availabilities, doctor=doctor)
    
@app.route('/doctor/mark-as-complete/<int:appointment_id>', methods=["POST"])
def complete(appointment_id):
    appointment = Appointments.query.get(appointment_id)
    doctor_id = appointment.Doctor_id
    if appointment and appointment.Status == "Booked":
        appointment.Status = "Completed"
        db.session.commit()
    return redirect(f'/doctor/{doctor_id}')    
    
@app.route('/doctor/cancel/<int:appointment_id>', methods=["POST"])
def cancel(appointment_id):
    appointment = Appointments.query.get(appointment_id)
    doctor_id = appointment.Doctor_id
    if appointment and appointment.Status == "Booked":
        appointment.Status = "Cancelled"
        db.session.commit()
    return redirect(f'/doctor/{doctor_id}') 







    




    
        










