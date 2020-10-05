from app import db
from sqlalchemy import Column, DateTime
import datetime


class LiveUserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    text = db.Column(db.String(1000))
    intent = db.Column(db.String(100))
    chatbot_ans = db.Column(db.String(1000))
    date_time = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, user_id, text, intent, chatbot_ans):
        self.user_id = user_id
        self.text = text
        self.intent = intent
        self.chatbot_ans = chatbot_ans


def CreateLiveUserData(user_id,text,intent, chatbot_ans):

    LiveUserDataObj = LiveUserData(user_id,text,intent, chatbot_ans)
    db.session.add(LiveUserDataObj)
    db.session.commit()

    return LiveUserDataObj


class DoctorVisit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    doctor_name = db.Column(db.String(100))
    visit_type = db.Column(db.String(20))
    complaint = db.Column(db.String(100))
    date = Column(DateTime)
    time = Column(DateTime)
    treatment_type = db.Column(db.String(20))
    test_suggested = db.Column(db.Boolean)
    fees = db.Column(db.Integer)
    images = db.Column(db.String(1000))
    test_done = db.Column(db.Boolean)
    test_suggested_name = db.Column(db.String(100))
    test_report_images = db.Column(db.String(1000))
    hospital_name = db.Column(db.String(100))

    def __init__(self,user_id, doctor_name, visit_type, complaint, date, time, treatment_type, test_suggested, fees,
                 images, test_done, test_suggested_name, test_report_images, hospital_name):
        self.user_id = user_id
        self.doctor_name = doctor_name
        self.visit_type = visit_type
        self.complaint = complaint
        self.date = date
        self.time = time
        self.treatment_type = treatment_type
        self.test_suggested = test_suggested
        self.fees = fees
        self.images = images
        self.test_done = test_done
        self.test_suggested_name = test_suggested_name
        self.test_report_images = test_report_images
        self.date = date
        self.time = time
        self.treatment_type = treatment_type
        self.test_suggested = test_suggested
        self.fees = fees
        self.hospital_name = hospital_name


def CreateDoctorVisit(user_id, doctor_name, visit_type, complaint, date, time, treatment_type, test_suggested, fees,
                      images, test_done, test_suggested_name, test_report_images, hospital_name):

    DoctorVisitObj = DoctorVisit(user_id, doctor_name, visit_type, complaint, date, time, treatment_type, test_suggested, fees,
                      images, test_done, test_suggested_name, test_report_images, hospital_name)
    db.session.add(DoctorVisitObj)
    db.session.commit()

    return DoctorVisitObj


class BloodPressure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    systolic_pressure = db.Column(db.Integer)
    diastolic_pressure = db.Column(db.Integer)
    pulse = db.Column(db.Integer)
    date = Column(DateTime,default=datetime.datetime.utcnow)
    time = Column(DateTime,default=datetime.datetime.utcnow)

    def __init__(self, user_id,systolic_pressure, diastolic_pressure, pulse):
        self.user_id = user_id
        self.systolic_pressure = systolic_pressure
        self.diastolic_pressure = diastolic_pressure
        self.pulse = pulse
        # self.date = date
        # self.time = time


def CreateBloodPressure(user_id,systolic_pressure, diastolic_pressure,pulse):

    BloodPressureObj = BloodPressure(user_id,systolic_pressure, diastolic_pressure,pulse)
    db.session.add(BloodPressureObj)
    db.session.commit()

    return BloodPressureObj


class BloodSugar(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    type_of_test = db.Column(db.String(20))
    results = db.Column(db.String(1000))
    date = Column(DateTime, default=datetime.datetime.utcnow)
    time = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, user_id,type_of_test, results):
        self.user_id = user_id
        self.type_of_test = type_of_test
        self.results = results
        # self.date = date
        # self.time = time


def CreateBloodSugar(user_id,type_of_test, results):

    BloodSugarObj = BloodSugar(user_id,type_of_test, results)
    db.session.add(BloodSugarObj)
    db.session.commit()

    return BloodSugarObj


class MedicalId(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    user_medical_id = db.Column(db.String(20))
    user_password = db.Column(db.String(100))
    date = Column(DateTime, default=datetime.datetime.utcnow)
    time = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, user_id,user_medical_id, user_password):
        self.user_id = user_id
        self.user_medical_id = user_medical_id
        self.user_password = user_password


def CreateMedicalId(user_id,user_medical_id, user_password):

    MedicalIdObj = MedicalId(user_id,user_medical_id, user_password)
    db.session.add(MedicalIdObj)
    db.session.commit()

    return MedicalIdObj


class UserProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    age = db.Column(db.Integer)
    address = db.Column(db.String(100))
    weight = db.Column(db.String(20))
    height = db.Column(db.String(20))
    occupation = db.Column(db.String(100))
    marital_status = db.Column(db.String(20))
    blood_group = db.Column(db.String(20))
    user_phone_number = db.Column(db.String(20))
    apk_version = db.Column(db.String(20))
    user_city = db.Column(db.String(20))
    user_gender = db.Column(db.String(20))
    token = db.Column(db.String(100))
    date_time = Column(DateTime, default=datetime.datetime.utcnow())

    def __init__(self, name, age, address, weight, height, occupation,marital_status,blood_group,user_phone_number,
                 apk_version,user_city,token, user_gender):
        self.name = name
        self.age = age
        self.address = address
        self.weight = weight
        self.height = height
        self.occupation = occupation
        self.marital_status = marital_status
        self.age = age
        self.blood_group = blood_group
        self.user_phone_number = user_phone_number
        self.apk_version = apk_version
        self.user_city = user_city
        self.token = token
        self.user_gender = user_gender


def CreateUserProfile(name, age, address, weight, height, occupation,marital_status,blood_group,user_phone_number,
                      apk_version,user_city,token, user_gender):

    UserProfileObj = UserProfile(name, age, address, weight, height, occupation,marital_status,blood_group,user_phone_number,
                                 apk_version,user_city,token, user_gender)
    db.session.add(UserProfileObj)
    db.session.commit()

    return UserProfileObj


class UserMedicalHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    diabetes = db.Column(db.Boolean)
    blood_pressure = db.Column(db.String(20))
    asthma = db.Column(db.Boolean)
    heat_disease = db.Column(db.Boolean)
    hiv = db.Column(db.Boolean)
    tb = db.Column(db.Boolean)
    any_allergy = db.Column(db.Boolean)

    def __init__(self, user_id, diabetes, blood_pressure, asthma, heat_disease, hiv, tb, any_allergy):
        self.user_id = user_id
        self.diabetes = diabetes
        self.blood_pressure = blood_pressure
        self.asthma = asthma
        self.heat_disease = heat_disease
        self.hiv = hiv
        self.tb = tb
        self.any_allergy = any_allergy
        self.heat_disease = heat_disease


def CreateUserMedicalHistory(user_id,diabetes, blood_pressure, asthma,heat_disease,hiv,tb,any_allergy):

    UserMedicalHistoryObj = UserMedicalHistory(user_id,diabetes, blood_pressure, asthma,heat_disease,hiv,tb,any_allergy)

    db.session.add(UserMedicalHistoryObj)
    db.session.commit()
    return UserMedicalHistoryObj


class ApkVersion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.Integer)
    url = db.Column(db.String(100))

    def __init__(self, version, url):
        self.version = version
        self.url = url


def CreateApkVersion(version, url):

    ApkVersionObj = ApkVersion(version, url)

    db.session.add(ApkVersionObj)
    db.session.commit()
    return ApkVersionObj


if __name__ == "__main__":

    db.create_all()

"""
GRANT ALL PRIVILEGES ON *.* TO 'db_user'@'localhost' IDENTIFIED BY 'P@s$w0rd123!';
mysql -u db_user -p

CREATE DATABASE db_name;

GRANT ALL PRIVILEGES ON *.* TO 'omdappdbuser'@'localhost';
| GRANT ALL PRIVILEGES ON `omdaoodb`.* TO 'omdappdbuser'@'localhost'          |
| GRANT ALL PRIVILEGES ON `omdappdb`.`omdappdb` TO 'omdappdbuser'@'localhost' 
SHOW GRANTS FOR 'omdappdbuser'@'localhost';


"""
