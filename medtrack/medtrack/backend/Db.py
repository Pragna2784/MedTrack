import boto3
import uuid

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

patients_table = dynamodb.Table('Patients')
doctors_table = dynamodb.Table('Doctors')
appointments_table = dynamodb.Table('Appointments')
diagnosis_table = dynamodb.Table('Diagnosis')


def register_patient(name,email,password):

    patient_id=str(uuid.uuid4())

    patients_table.put_item(
        Item={
            "PatientID":patient_id,
            "Name":name,
            "Email":email,
            "Password":password
        }
    )

    return patient_id


def patient_login(email,password):

    response=patients_table.scan()

    for user in response['Items']:
        if user['Email']==email and user['Password']==password:
            return user

    return None


def doctor_login(email,password):

    response=doctors_table.scan()

    for doc in response['Items']:
        if doc['Email']==email and doc['Password']==password:
            return doc

    return None


def create_appointment(patient_id,doctor_id,date):

    appointment_id=str(uuid.uuid4())

    appointments_table.put_item(
        Item={
            "AppointmentID":appointment_id,
            "PatientID":patient_id,
            "DoctorID":doctor_id,
            "Date":date,
            "Status":"Booked"
        }
    )

    return appointment_id


def add_diagnosis(patient_id,doctor_id,report):

    diagnosis_id=str(uuid.uuid4())

    diagnosis_table.put_item(
        Item={
            "DiagnosisID":diagnosis_id,
            "PatientID":patient_id,
            "DoctorID":doctor_id,
            "Report":report
        }
    )

    return diagnosis_id


def get_history(patient_id):

    response=diagnosis_table.scan()

    history=[]

    for item in response['Items']:
        if item['PatientID']==patient_id:
            history.append(item)

    return history