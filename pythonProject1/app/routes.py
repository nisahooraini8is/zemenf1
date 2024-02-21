
import re
from docx import Document
from dateutil.relativedelta import relativedelta
import PyPDF2
from app.model import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from . import db, app
from werkzeug.utils import secure_filename
import os
import io
from flask import Flask, session, render_template, redirect, request, url_for, jsonify ,send_file ,Response
from passlib.hash import sha256_crypt
from flask_login import login_user
from sqlalchemy import desc, exists, func, case ,or_, extract ,and_, distinct
from functools import wraps
from app.forms import LoginForm, CreateAccountForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json
import pycountry_convert as pc
import pycountry
import csv
from math import ceil
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import bcrypt
import schedule
import time
import multiprocessing
import schedule
import threading
import time
from app.util import verify_pass
import base64
# Set a secret key for session management
app.secret_key = "geoxhr123??"
from base64 import b64encode


def role_required(allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session or 'role' not in session:
                return redirect(url_for('login'))

            user_role = session['role']
            if user_role not in allowed_roles:
                return redirect(url_for('login'))
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def format_job_description(description):
    # Check for numbered list format (e.g., "1. Item 1\n2. Item 2")
    if re.match(r'^\d+\.\s', description, re.MULTILINE):
        formatted_description = re.sub(r'^(\d+\.\s)', r'<li>\1', description, flags=re.MULTILINE)
        formatted_description = f'<ul>{formatted_description}</ul>'
    # Check for bulleted list format (e.g., "• Item 1\n• Item 2")
    elif re.match(r'^•\s', description, re.MULTILINE):
        formatted_description = re.sub(r'^(•\s)', r'<li>\1', description, flags=re.MULTILINE)
        formatted_description = f'<ul>{formatted_description}</ul>'
    # Plain text
    else:
        formatted_description = description

    return formatted_description


def extract_pdf_text(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text_content = ""
    for page in pdf_reader.pages:
        text_content += page.extract_text()
    binary_pdf_content = text_content.encode('utf-8')
    return binary_pdf_content


def extract_pdf_content(pdf_file):
    content = pdf_file.read()
    return content


def extract_docx_content(docx_file):
    doc = Document(docx_file)
    content = docx_file.read()
    return content


def format_posted_time(created_at):
    current_time = datetime.now()
    time_difference = current_time - created_at

    if time_difference.days == 1:
        return "1 day ago"
    elif time_difference.days > 1 and time_difference.days <= 7:
        return f"{time_difference.days} days ago"
    else:
        return created_at.strftime("%Y-%m-%d %H:%M:%S")  # Fallback to original format


@app.route('/websitejobs')
def websitejobs():
    alljobs = Jobs.query.filter(Jobs.job_status == 'active', Jobs.company.in_(['1', '12', '13', '123'])).order_by(
        desc(Jobs.created_at)).all()
    formatted_times = [format_posted_time(job.created_at) for job in alljobs]
    for job, formatted_time in zip(alljobs, formatted_times):
        job.formatted_time = formatted_time
    return render_template('websitejobs.html', alljobs=alljobs)


@app.route('/handshrjobs')
def handshrjobs():
    alljobs = Jobs.query.filter(Jobs.job_status == 'active', Jobs.company.in_(['2', '12', '23', '123'])).order_by(
        desc(Jobs.created_at)).all()
    formatted_times = [format_posted_time(job.created_at) for job in alljobs]
    for job, formatted_time in zip(alljobs, formatted_times):
        job.formatted_time = formatted_time
    return render_template('handshrjobs.html', alljobs=alljobs)


@app.route('/i8isjobs')
def i8isjobs():
    alljobs = Jobs.query.filter(Jobs.job_status == 'active', Jobs.company.in_(['3', '13', '23', '123'])).order_by(
        desc(Jobs.created_at)).all()
    formatted_times = [format_posted_time(job.created_at) for job in alljobs]
    for job, formatted_time in zip(alljobs, formatted_times):
        job.formatted_time = formatted_time
    return render_template('i8isjobs.html', alljobs=alljobs)


@app.route('/i8isjobdetails/<int:id>')
def i8isjobdetails(id):
    jobdetail = Jobs.query.filter(Jobs.id == id).first()
    formatted_time = format_posted_time(jobdetail.created_at)
    jobdetail.formatted_time = formatted_time  # Attach formatted time to the job detail
    job_description = jobdetail.description
    formatted_notes = format_job_description(jobdetail.notes)
    formatted_eligibility = format_job_description(jobdetail.eligibility)
    formatted_responsibility = format_job_description(jobdetail.responsibility)
    formatted_description = format_job_description(job_description)
    jobdetail.formatted_notes = formatted_notes
    jobdetail.formatted_eligibility = formatted_eligibility
    jobdetail.formatted_responsibility = formatted_responsibility
    jobdetail.formatted_description = formatted_description
    # print(formatted_description)
    # print(jobdetail.formatted_time)

    latest_jobs = Jobs.query.order_by(Jobs.created_at.desc()).limit(2).all()
    format_time = [format_posted_time(data.created_at) for data in latest_jobs]
    for job, format_time in zip(latest_jobs, format_time):
        job.format_time = format_time
    return render_template('i8isjobdetails.html', jobdetail=jobdetail, latest_jobs=latest_jobs)


@app.route('/handshrjobdetail/<int:id>')
def handshrjobdetail(id):
    jobdetail = Jobs.query.filter(Jobs.id == id).first()
    formatted_time = format_posted_time(jobdetail.created_at)
    jobdetail.formatted_time = formatted_time  # Attach formatted time to the job detail
    job_description = jobdetail.description
    formatted_notes = format_job_description(jobdetail.notes)
    formatted_eligibility = format_job_description(jobdetail.eligibility)
    formatted_responsibility = format_job_description(jobdetail.responsibility)
    formatted_description = format_job_description(job_description)
    jobdetail.formatted_notes = formatted_notes
    jobdetail.formatted_eligibility = formatted_eligibility
    jobdetail.formatted_responsibility = formatted_responsibility
    jobdetail.formatted_description = formatted_description
    # print(formatted_description)
    # print(jobdetail.formatted_time)

    latest_jobs = Jobs.query.order_by(Jobs.created_at.desc()).limit(2).all()
    format_time = [format_posted_time(data.created_at) for data in latest_jobs]
    for job, format_time in zip(latest_jobs, format_time):
        job.format_time = format_time
    return render_template('handshrjobdetail.html', jobdetail=jobdetail, latest_jobs=latest_jobs)


@app.route('/jobdetail/<int:id>')
def jobdetail(id):
    jobdetail = Jobs.query.filter(Jobs.id == id).first()
    formatted_time = format_posted_time(jobdetail.created_at)
    jobdetail.formatted_time = formatted_time  # Attach formatted time to the job detail
    job_description = jobdetail.description
    formatted_notes = format_job_description(jobdetail.notes)
    formatted_eligibility = format_job_description(jobdetail.eligibility)
    formatted_responsibility = format_job_description(jobdetail.responsibility)
    formatted_description = format_job_description(job_description)
    jobdetail.formatted_notes = formatted_notes
    jobdetail.formatted_eligibility = formatted_eligibility
    jobdetail.formatted_responsibility = formatted_responsibility
    jobdetail.formatted_description = formatted_description
    # print(formatted_description)
    # print(jobdetail.formatted_time)

    latest_jobs = Jobs.query.order_by(Jobs.created_at.desc()).limit(2).all()
    format_time = [format_posted_time(data.created_at) for data in latest_jobs]
    for job, format_time in zip(latest_jobs, format_time):
        job.format_time = format_time
    return render_template('postjobdetail.html', jobdetail=jobdetail, latest_jobs=latest_jobs)


@app.route('/apply', methods=["POST"])
def apply():
    if request.method == 'POST':
        fname = request.form.get('firstName')
        lname = request.form.get('lastName')
        email = request.form.get('email')
        phone = request.form.get('number')
        position = request.form.get('position')
        file = request.files['myFile']
        jobid = request.form.get('jobid')

        filename = file.filename

        if file and '.' in filename:  # Check if the file has a valid extension
            extension = filename.rsplit('.', 1)[1].lower()  # Get the file extension
            if extension in ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp']:  # Add more image formats as needed
                content = file.read()  # Read the content of the file
                current_datee = datetime.now().strftime('%a, %d %b %Y')

                exist = Emails_data.query.filter(
                    and_(Emails_data.email == email, Emails_data.subject_part1 == position)
                ).all()

                current_date = datetime.now()
                one_month_ago = current_date - relativedelta(months=1)
                if exist:
                    for check in exist:
                        formatted_date = datetime.strptime(check.formatted_date, '%a, %d %b %Y')
                        # print(formatted_date, one_month_ago, current_date)
                        if one_month_ago <= formatted_date <= current_date:
                            # print(" already applied")
                            response = jsonify({'message': 'already_applied'})
                            response.status_code = 200
                            return response
                        else:
                            # print("date not set")
                            apply = Emails_data(sender_name=fname + " " + lname, email=email, phone_number=phone,
                                                subject_part2=position, formatted_date=current_datee,
                                                file_name=filename, file_content=content,
                                                subject_part1='GeoxHR website ')
                            db.session.add(apply)
                            db.session.commit()
                            response = jsonify({'message': 'success'})
                            response.status_code = 200
                            return response

                elif not exist:
                    # print("data not exist")
                    apply = Emails_data(sender_name=fname + " " + lname, email=email, phone_number=phone,
                                        subject_part2=position, formatted_date=current_datee, file_name=filename,
                                        file_content=content, subject_part1='GeoxHR website ')
                    db.session.add(apply)
                    db.session.commit()
                    response = jsonify({'message': 'success'})
                    response.status_code = 200
                    return response

            else:
                # print("Unsupported file type")
                return redirect('/websitejobs')

        else:
            # print("File not found or other error")
            return redirect('/websitejobs')


@app.route('/handsapply', methods=["POST"])
def handsapply():
    if request.method == 'POST':
        fname = request.form.get('firstName')
        lname = request.form.get('lastName')
        email = request.form.get('email')
        phone = request.form.get('number')
        position = request.form.get('position')
        file = request.files['myFile']
        jobid = request.form.get('jobid')

        filename = file.filename

        if file and '.' in filename:  # Check if the file has a valid extension
            extension = filename.rsplit('.', 1)[1].lower()  # Get the file extension
            if extension in ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp']:  # Add more image formats as needed
                content = file.read()  # Read the content of the file
                current_datee = datetime.now().strftime('%a, %d %b %Y')

                exist = Emails_data.query.filter(
                    and_(Emails_data.email == email, Emails_data.subject_part1 == position)
                ).all()

                current_date = datetime.now()
                one_month_ago = current_date - relativedelta(months=1)
                if exist:
                    for check in exist:
                        formatted_date = datetime.strptime(check.formatted_date, '%a, %d %b %Y')
                        # print(formatted_date, one_month_ago, current_date)
                        if one_month_ago <= formatted_date <= current_date:
                            # print(" already applied")
                            response = jsonify({'message': 'already_applied'})
                            response.status_code = 200
                            return response
                        else:
                            # print("date not set")
                            apply = Emails_data(sender_name=fname + " " + lname, email=email, phone_number=phone,
                                                subject_part2=position, formatted_date=current_datee,
                                                file_name=filename, file_content=content,
                                                subject_part1='HandsHR website ')
                            db.session.add(apply)
                            db.session.commit()
                            response = jsonify({'message': 'success'})
                            response.status_code = 200
                            return response

                elif not exist:
                    # print("data not exist")
                    apply = Emails_data(sender_name=fname + " " + lname, email=email, phone_number=phone,
                                        subject_part2=position, formatted_date=current_datee, file_name=filename,
                                        file_content=content, subject_part1='HandsHR website ')
                    db.session.add(apply)
                    db.session.commit()
                    response = jsonify({'message': 'success'})
                    response.status_code = 200
                    return response

            else:
                # print("Unsupported file type")
                return redirect('/handshrjobs')

        else:
            # print("File not found or other error")
            return redirect('/handshrjobs')


@app.route('/i8isapply', methods=["POST"])
def i8isapply():
    if request.method == 'POST':
        fname = request.form.get('firstName')
        lname = request.form.get('lastName')
        email = request.form.get('email')
        phone = request.form.get('number')
        position = request.form.get('position')
        file = request.files['myFile']
        jobid = request.form.get('jobid')

        filename = file.filename

        if file and '.' in filename:  # Check if the file has a valid extension
            extension = filename.rsplit('.', 1)[1].lower()  # Get the file extension
            if extension in ['pdf', 'jpg', 'jpeg', 'png', 'gif', 'bmp']:  # Add more image formats as needed
                content = file.read()  # Read the content of the file
                current_datee = datetime.now().strftime('%a, %d %b %Y')

                exist = Emails_data.query.filter(
                    and_(Emails_data.email == email, Emails_data.subject_part1 == position)
                ).all()

                current_date = datetime.now()
                one_month_ago = current_date - relativedelta(months=1)
                if exist:
                    for check in exist:
                        formatted_date = datetime.strptime(check.formatted_date, '%a, %d %b %Y')
                        # print(formatted_date, one_month_ago, current_date)
                        if one_month_ago <= formatted_date <= current_date:
                            # print(" already applied")
                            response = jsonify({'message': 'already_applied'})
                            response.status_code = 200
                            return response
                        else:
                            # print("date not set")
                            apply = Emails_data(sender_name=fname + " " + lname, email=email, phone_number=phone,
                                                subject_part2=position, formatted_date=current_datee,
                                                file_name=filename, file_content=content, subject_part1='i8is website ')
                            db.session.add(apply)
                            db.session.commit()
                            response = jsonify({'message': 'success'})
                            response.status_code = 200
                            return response

                elif not exist:
                    # print("data not exist")
                    apply = Emails_data(sender_name=fname + " " + lname, email=email, phone_number=phone,
                                        subject_part2=position, formatted_date=current_datee, file_name=filename,
                                        file_content=content, subject_part1='i8is website ')
                    db.session.add(apply)
                    db.session.commit()
                    response = jsonify({'message': 'success'})
                    response.status_code = 200
                    return response

            else:
                # print("Unsupported file type")
                return redirect('/i8isjobs')

        else:
            # print("File not found or other error")
            return redirect('/i8isjobs')


@app.route('/')
def route_default():
    if 'user_id' in session:
        user_id = session['user_id']
        role = session['role']
        email = session['email']
        user = session['user']

        return redirect(url_for('index'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Locate user by email
        user = Users.query.filter_by(email=email).first()

        if user and sha256_crypt.verify(password, user.password):
            # Successful login
            login_user(user)
            session['user_id'] = user.id
            session['role'] = user.role
            session['email'] = user.email
            session['user'] = f"{user.fname} {user.lname}"
            return redirect(url_for('index'))

        # Incorrect email or password
        return render_template('login.html', msg='Wrong email or password')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/logoutforcandidate')
def logoutforcandidate():
    session.clear()
    return redirect(url_for('logincandidate'))
#

engine = create_engine('mysql+pymysql://hayat:Hayat_admin123@3.99.155.18/zeemandatabase')
# engine = create_engine('mysql+pymysql://root:@localhost/zeemandatabase')

# Create a session factory
Session = sessionmaker(bind=engine)


class DotDict(dict):
    def __getattr__(self, attr):
        return self.get(attr)

    __setattr__ = dict.__setitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


@app.route('/index')
@role_required(allowed_roles=['user', 'admin'])
def index():
    user_id = session['user_id']
    role = session['role']

    total_users = Users.query.count()
    totalcandidate = Emails_data.query.filter(Emails_data.action == 'Interested').count()
    action = 'Interested'
    alldata = Emails_data.query.filter(Emails_data.action == action).order_by(desc(Emails_data.id)).all()
    task = "default task value"  # Set a default value

    if role == 'user':
        totalforms = allforms_data.query.filter(allforms_data.user_id == user_id).count()
        candidateplace = recruiting_data.query.filter(
            or_(recruiting_data.did_you == 'Candidate Placement',
                recruiting_data.person_starting == 'Candidate Placement'),
            recruiting_data.user_id == user_id
        ).count()
    else:
        totalforms = allforms_data.query.count()
        candidateplace = recruiting_data.query.filter(
            or_(recruiting_data.did_you == 'Candidate Placement',
                recruiting_data.person_starting == 'Candidate Placement')
        ).count()
        # today = datetime.today()
        # print("today", today)
        # days_to_saturday = today.weekday()
        # saturday = today - timedelta(days=days_to_saturday)
        # friday = saturday + timedelta(days=6)
        # weekstart = saturday.strftime("%Y-%m-%d")
        # weekend = friday.strftime("%Y-%m-%d")
        # print("Week start:", weekstart)
        # print("Week end:", weekend)
        #
        # existing_entries = Targets.query.filter(
        #     and_(
        #         Targets.weekstart == weekstart,
        #         Targets.weekend == weekend,
        #         Targets.target != 0
        #     )
        # ).first()
        #
        # if existing_entries:
        #     pass
        # else:
        #     task = "task not set"
        #     print(role, "role", task)

    candidateplacement = (
        Users.query
        .with_entities(
            func.concat(Users.fname, ' ', Users.lname).label('user_name'),
            func.date(recruiting_data.created_at).label('entry_date'),
            func.sum(case(
                (or_(recruiting_data.did_you == 'Candidate Placement',
                     recruiting_data.person_starting == 'Candidate Placement'), 1),
                else_=0)).label('placement_count')
        )
        .outerjoin(recruiting_data, Users.id == recruiting_data.user_id)
        .group_by('user_name', 'entry_date')
        .all()
    )
    resumesent = (
        Users.query
        .with_entities(
            func.concat(Users.fname, ' ', Users.lname).label('user_name'),
            func.date(recruiting_data.created_at).label('entry_date'),
            func.sum(case(
                (or_(recruiting_data.did_you == 'Resume Sent',
                     recruiting_data.person_starting == 'Resume Sent'), 1),
                else_=0)).label('resume_count')
        )
        .outerjoin(recruiting_data, Users.id == recruiting_data.user_id)
        .group_by('user_name', 'entry_date')
        .all()
    )

    interview = (
        Users.query
        .with_entities(
            func.concat(Users.fname, ' ', Users.lname).label('user_name'),
            func.date(recruiting_data.created_at).label('entry_date'),
            func.sum(case(
                (or_(recruiting_data.did_you == 'Interview Scheduled',
                     recruiting_data.person_starting == 'Interview Scheduled'), 1),
                else_=0)).label('interview_count')
        )
        .outerjoin(recruiting_data, Users.id == recruiting_data.user_id)
        .group_by('user_name', 'entry_date')
        .all()
    )

    helpingform = (
        Users.query
        .with_entities(
            func.concat(Users.fname, ' ', Users.lname).label('user_name'),
            func.date(recruiting_data.created_at).label('entry_date'),
            func.sum(case(
                (recruiting_data.did_you == 'Help Another', 1),
                else_=0)).label('helping_count')
        )
        .outerjoin(recruiting_data, Users.id == recruiting_data.user_id)
        .group_by('user_name', 'entry_date')
        .all()
    )
    contractsigned = (
        Users.query
        .with_entities(
            func.concat(Users.fname, ' ', Users.lname).label('user_name'),
            func.date(Marketing.created_at).label('entry_date'),
            func.sum(case(
                (Marketing.status == 'New deal opened and contract signed', 1),
                else_=0)).label('contractsign_count')
        )
        .outerjoin(Marketing, Users.id == Marketing.user_id)
        .group_by('user_name', 'entry_date')
        .all()
    )
    contractnotsigned = (
        Users.query
        .with_entities(
            func.concat(Users.fname, ' ', Users.lname).label('user_name'),
            func.date(Marketing.created_at).label('entry_date'),
            func.sum(case(
                (Marketing.status == 'New deal and contract not signed', 1),
                else_=0)).label('contractnotsign_count')
        )
        .outerjoin(Marketing, Users.id == Marketing.user_id)
        .group_by('user_name', 'entry_date')
        .all()
    )
    reopendeals = (
        Users.query
        .with_entities(
            func.concat(Users.fname, ' ', Users.lname).label('user_name'),
            func.date(Marketing.created_at).label('entry_date'),
            func.sum(case(
                (Marketing.status == 'Reopened deals', 1),
                else_=0)).label('reopen_count')
        )
        .outerjoin(Marketing, Users.id == Marketing.user_id)
        .group_by('user_name', 'entry_date')
        .all()
    )

    interviews_data = []
    helpings_data = []
    resumesents_data = []
    contractsigned_data = []
    contractnotsigned_data = []
    reopendeals_data = []
    candidateplacement_data = []
    placementdata_count = []

    usernames = Users.query.all()
    fullnames = []

    for user in usernames:
        fullnames.append(f"{user.fname} {user.lname}")

    for row in interview:
        entry_date = row.entry_date
        user_name = row.user_name
        if entry_date:
            formatted_date = entry_date.strftime('%Y, %m, %d')
            interview_count = row.interview_count
            interviews_data.append({'date': formatted_date, 'count': interview_count, 'user_name': user_name})
    # print("interviews_data", interviews_data, usernames)

    for row in helpingform:
        entry_date = row.entry_date
        user_name = row.user_name
        if entry_date:
            formatted_date = entry_date.strftime('%Y, %m, %d')
            helping_count = row.helping_count
            helpings_data.append({'date': formatted_date, 'count': helping_count, 'user_name': user_name})
    # print("helpings_data", helpings_data, usernames)

    for row in resumesent:
        entry_date = row.entry_date
        user_name = row.user_name
        if entry_date:
            formatted_date = entry_date.strftime('%Y, %m, %d')
            resume_count = row.resume_count
            resumesents_data.append({'date': formatted_date, 'count': resume_count, 'user_name': user_name})
    # print("resumesents_data", resumesents_data)

    for row in contractsigned:
        entry_date = row.entry_date
        user_name = row.user_name
        if entry_date:
            formatted_date = entry_date.strftime('%Y, %m, %d')
            contractsign_count = row.contractsign_count
            contractsigned_data.append({'date': formatted_date, 'count': contractsign_count, 'user_name': user_name})
    # print("contractsigned_data", contractsigned_data, usernames)

    for row in contractnotsigned:
        entry_date = row.entry_date
        user_name = row.user_name
        if entry_date:
            formatted_date = entry_date.strftime('%Y, %m, %d')
            contractnotsign_count = row.contractnotsign_count
            contractnotsigned_data.append(
                {'date': formatted_date, 'count': contractnotsign_count, 'user_name': user_name})
    # print("contractsigned_data", contractnotsigned_data, usernames)

    for row in reopendeals:
        entry_date = row.entry_date
        user_name = row.user_name
        if entry_date:
            formatted_date = entry_date.strftime('%Y, %m, %d')
            reopen_count = row.reopen_count
            reopendeals_data.append({'date': formatted_date, 'count': reopen_count, 'user_name': user_name})
    # print("reopendeals_data", reopendeals_data, usernames)

    for row in candidateplacement:
        entry_date = row.entry_date
        user_name = row.user_name
        if entry_date:
            formatted_date = entry_date.strftime('%Y, %m, %d')
            placement_count = row.placement_count
            candidateplacement_data.append({'date': formatted_date, 'count': placement_count, 'user_name': user_name})

    # print(candidateplacement_data,usernames)
    jobsorder = db.session.query(Joborder).filter(Joborder.archived == False).order_by(desc(Joborder.id)).all()
    marketing_entries = db.session.query(Marketing).all()

    # Create a dictionary to store company names for faster lookup
    company_name_dict = {entry.id: entry.company for entry in marketing_entries}

    # Update the company names in the jobsorder list
    for job_order in jobsorder:
        company_id = job_order.company_id
        if company_id in company_name_dict:
            job_order.company = company_name_dict[company_id]
    # print(jobsorder, marketing_entries)
    data_array = DotDict({
        'counters': {
            'total_users': total_users,
            'totalcandidate': totalcandidate,
            'totalforms': totalforms,
            'candidateplace': candidateplace,

        },
        'interviews': interviews_data,
        'helpings': helpings_data,
        'resumesents': resumesents_data,
        'usernames': fullnames,
        'contractsigned': contractsigned_data,
        'contractnotsigned': contractnotsigned_data,
        'reopendeals': reopendeals_data,
        'candidateplacement': candidateplacement_data,
        'placementdata_count': placementdata_count
    })
    return render_template('index.html', data_array=data_array, jobsorder=jobsorder, alldata=alldata, msg=task)


country_prefixes = {
    'canada': ['+1', '647', '622', '1', '403', '587', '825', '368', '780', '604', '778', '236', '672', '250', '204',
               '289'],
    'pakistan': ['+92', '03', '92'],
    'india': ['+91', '91'],
    'mexico': ['+52-187', '+52-800', '52-187', '52-800', '52-187', '+52', '52'],
    'philippines': ['+63-999', '+63-001', '63-001', '63-999', '+63', '63']
}

from math import ceil


@app.route('/candidate')
@role_required(allowed_roles=['user', 'admin'])
def candidate():
    selected_year = request.args.get('year_select')
    selected_country = request.args.get('country_select')
    selected_subject = request.args.get('subj_select')
    page = int(request.args.get('page', 1))  # Get page number, default to 1
    per_page = int(request.args.get('per_page', 300))  # Get items per page, default to 5
    # Get items per page, default to 5
    print(selected_year, selected_country, selected_subject, page, per_page)
    action = 'Interested'
    current_year = datetime.now().year  # Get the current year
    subject_part1 = 'registered from Geox hr'

    with db.session() as session:
        # Initialize base query without year filter
        query = session.query(Emails_data).filter(
            Emails_data.action != action,
            Emails_data.subject_part1 != subject_part1
        ).order_by(desc(Emails_data.id))

        # Apply year filter if selected_year is provided, else default to current year
        if selected_year and selected_year != "":
            # Filter by selected year
            query = query.filter(
                or_(
                    extract('year', func.str_to_date(Emails_data.formatted_date, '%a, %d %b %Y')) == int(selected_year),
                    extract('year', func.str_to_date(Emails_data.formatted_date, '%Y-%m-%d')) == int(selected_year)
                )            )
            print(f"Applying year filter: {selected_year}")
        else:
            # Filter by current year
            query = query.filter(
                or_(
                    extract('year', func.str_to_date(Emails_data.formatted_date, '%a, %d %b %Y')) == current_year,
                    extract('year', func.str_to_date(Emails_data.formatted_date, '%Y-%m-%d')) == current_year
                )            )
            print(f"Applying default year filter: {current_year}")

        # Apply subject filter if selected_subject is provided
        if selected_subject and selected_subject != "":
            query = query.filter(
                Emails_data.subject_part2.ilike(f"%{selected_subject}%")
            )
            print(f"Applying subject filter: {selected_subject}")

        # Apply country filter if selected_country is provided
        if selected_country and selected_country.strip().lower() in country_prefixes:
            print(f"Applying country filter for: {selected_country}")
            prefixes = country_prefixes[selected_country.strip().lower()]
            print(f"Prefixes for {selected_country}: {prefixes}")
            # Construct OR condition for country prefixes
            country_prefix_conditions = or_(
                *[func.substr(Emails_data.phone_number, 1, len(prefix)) == prefix for prefix in prefixes]
            )
            print(f"Country prefix conditions: {country_prefix_conditions}")
            query = query.filter(country_prefix_conditions)
            print(f"Applied country filter for: {selected_country}")
        else:
            selected_country = ""

            # Count total number of pages
        total_items = query.count()
        total_pages = ceil(total_items / per_page)

        # Paginate the query results
        paginated_data = query.paginate(page=page, per_page=per_page)
        alldata = paginated_data.items  # Extract the items from the paginated object
        print(total_items, total_pages)
        serialized_alldata = []  # Initialize list to store serialized data

        # Serialize the data
        if alldata:
            print("Data found after filtering:")
            serialized_alldata = [
                {
                    "id": email.id,
                    "email": email.email,
                    "sender_name": email.sender_name,
                    "subject_part1": email.subject_part1,
                    "subject_part2": email.subject_part2,
                    "formatted_date": email.formatted_date,
                    "pdf_content_json": email.subject_part2,
                    "phone_number": email.phone_number,
                    "status": email.status,
                    "action": email.action
                }
                for email in alldata
            ]
        else:
            print("No data found after filtering.")

    phone_codes = {
        'AF': '+93',
        'AO': '+244',
        'AI': '+1-264',
        'AX': '+358',
        'AL': '+355',
        'AD': '+376',
        'AE': '+971',
        'AR': '+54',
        'AM': '+374',
        'AS': '+1-684',
        'TF': '+262',
        'AG': '+1-268',
        'AT': '+43',
        'AZ': '+994',
        'BI': '+257',
        'BE': '+32',
        'BJ': '+229',
        'BQ': '+599',
        'BF': '+226',
        'BD': '+880',
        'BG': '+359',
        'BH': '+973',
        'BS': '+1-242',
        'BA': '+387',
        'BL': '+590',
        'BZ': '+501',
        'BM': '+1-441',
        'BO': '+591',
        'BR': '+55',
        'BB': '+1-246',
        'BN': '+673',
        'BT': '+975',
        'BW': '+267',
        'CFR': '+236',  # Central African Republic
        'CAN': '+1',  # Canada
        'CCK': '+61',  # Cocos(Keeling) Islands
        'CH': '+41',  # Switzerland
        'CL': '+56',  # Chile
        'CN': '+86',  # China
        'CM': '+237',  # Cameroon
        'CD': '+243',  # Congo, The Democratic Republic of the
        'CG': '+242',  # Congo
        'CK': '+682',  # Cook Islands
        'CO': '+57',  # Colombia
        'KM': '+269',  # Comoros
        'CV': '+238',  # Cabo Verde(Cape Verde)
        'CR': '+506',  # Costa Rica
        'CU': '+53',  # Cuba
        'CW': '+599',  # Curaçao
        'CX': '+61',  # Christmas Island
        'KY': '+1-345',  # Cayman Islands
        'CY': '+357',  # Cyprus
        'CZ': '+420',  # Czechia(Czech Republic)
        'DEU': '+49',  # Germany
        'DJ': '+253',  # Djibouti
        'DM': '+1-767',  # Dominica
        'DK': '+45',  # Denmark
        'DO': '+1-809',  # Dominican Republic (and +1-829 and +1-849)
        'DZ': '+213',  # Algeria
        'EC': '+593',  # Ecuador
        'EG': '+20',  # Egypt
        'ER': '+291',  # Eritrea
        'EH': '+212',  # Western Sahara
        'ES': '+34',  # Spain
        'EE': '+372',  # Estonia
        'ET': '+251',  # Ethiopia
        'FI': '+358',  # Finland
        'FJ': '+679',  # Fiji
        'FK': '+500',  # Falkland Islands (Malvinas)
        'FR': '+33',  # France
        'FO': '+298',  # Faroe Islands
        'FM': '+691',  # Micronesia, Federated States of
        'GA': '+241',  # Gabon
        'GB': '+44',  # United Kingdom
        'GE': '+995',  # Georgia
        'GG': '+44-1481',  # Guernsey
        'GH': '+233',  # Ghana
        'GI': '+350',  # Gibraltar
        'GN': '+224',  # Guinea
        'GP': '+590',  # Guadeloupe
        'GM': '+220',  # Gambia
        'GW': '+245',  # Guinea-Bissau
        'GQ': '+240',  # Equatorial Guinea
        'GR': '+30',  # Greece
        'GD': '+1-473',  # Grenada
        'GL': '+299',  # Greenland
        'GT': '+502',  # Guatemala
        'GF': '+594',  # French Guiana
        'GU': '+1-671',  # Guam
        'GY': '+592',  # Guyana
        'HK': '+852',  # Hong Kong
        'HM': '',  # Heard Island and McDonald Islands: No specific dialing code; Australian external territory
        'HN': '+504',  # Honduras
        'HR': '+385',  # Croatia
        'HT': '+509',  # Haiti
        'HU': '+36',  # Hungary
        'ID': '+62',  # Indonesia
        'IM': '+44-1624',  # Isle of Man
        'IN': '+91',  # India
        'IO': '+246',  # British Indian Ocean Territory
        'IE': '+353',  # Ireland
        'IR': '+98',  # Iran, Islamic Republic of
        'IQ': '+964',  # Iraq
        'IS': '+354',  # Iceland
        'IL': '+972',  # Israel
        'IT': '+39',  # Italy
        'JM': '+1-876',  # Jamaica
        'JE': '+44-1534',  # Jersey
        'JO': '+962',  # Jordan
        'JP': '+81',  # Japan
        'KZ': '+7',  # Kazakhstan
        'KE': '+254',  # Kenya
        'KG': '+996',  # Kyrgyzstan
        'KH': '+855',  # Cambodia
        'KI': '+686',  # Kiribati
        'KN': '+1-869',  # Saint Kitts and Nevis
        'KR': '+82',  # Korea, Republic of
        'KW': '+965',  # Kuwait
        'LA': '+856',  # Lao People's Democratic Republic
        'LB': '+961',  # Lebanon
        'LR': '+231',  # Liberia
        'LY': '+218',  # Libya
        'LC': '+1-758',  # Saint Lucia
        'LI': '+423',  # Liechtenstein
        'LK': '+94',  # Sri Lanka
        'LS': '+266',  # Lesotho
        'LT': '+370',  # Lithuania
        'LU': '+352',  # Luxembourg
        'LV': '+371',  # Latvia
        'MO': '+853',  # Macao
        'MF': '+590',  # Saint Martin (French part)
        'MA': '+212',  # Morocco
        'MC': '+377',  # Monaco
        'MD': '+373',  # Moldova, Republic of
        'MG': '+261',  # Madagascar
        'MV': '+960',  # Maldives
        'MX': '+52',  # Mexico
        'MH': '+692',  # Marshall Islands
        'MK': '+389',  # North Macedonia
        'ML': '+223',  # Mali
        'MT': '+356',  # Malta
        'MM': '+95',  # Myanmar
        'ME': '+382',  # Montenegro
        'MN': '+976',  # Mongolia
        'MP': '+1-670',  # Northern Mariana Islands
        'MZ': '+258',  # Mozambique
        'MR': '+222',  # Mauritania
        'MS': '+1-664',  # Montserrat
        'MQ': '+596',  # Martinique
        'MU': '+230',  # Mauritius
        'MW': '+265',  # Malawi
        'MY': '+60',  # Malaysia
        'YT': '+262',  # Mayotte
        'NA': '+264',  # Namibia
        'NC': '+687',  # New Caledonia
        'NE': '+227',  # Niger
        'NF': '+672',  # Norfolk Island
        'NG': '+234',  # Nigeria
        'NI': '+505',  # Nicaragua
        'NU': '+683',  # Niue
        'NL': '+31',  # Netherlands
        'NO': '+47',  # Norway
        'NP': '+977',  # Nepal
        'NR': '+674',  # Nauru
        'NZ': '+64',  # New Zealand
        'OM': '+968',  # Oman
        'PK': '+92',  # Pakistan
        'PA': '+507',  # Panama
        'PN': '+64',  # Pitcairn
        'PE': '+51',  # Peru
        'PH': '+63',  # Philippines
        'PW': '+680',  # Palau
        'PG': '+675',  # Papua New Guinea
        'PL': '+48',  # Poland
        'PR': '+1-787',  # Puerto Rico
        'KP': '+850',  # Korea, Democratic People's Republic of
        'PT': '+351',  # Portugal
        'PY': '+595',  # Paraguay
        'PS': '+970',  # Palestine, State of
        'PF': '+689',  # French Polynesia
        'QA': '+974',  # Qatar
        'RE': '+262',  # Réunion
        'RO': '+40',  # Romania
        'RU': '+7',  # Russian Federation
        'RW': '+250',  # Rwanda
        'SA': '+966',  # Saudi Arabia
        'SD': '+249',  # Sudan
        'SN': '+221',  # Senegal
        'GS': '',  # South Georgia and the South Sandwich Islands
        'SH': '+290',  # Saint Helena, Ascension and Tristan da Cunha
        'SJ': '+47',  # Svalbard and Jan Mayen
        'SB': '+677',  # Solomon Islands
        'SL': '+232',  # Sierra Leone
        'SV': '+503',  # El Salvador
        'SM': '+378',  # San Marino
        'SO': '+252',  # Somalia
        'PM': '+508',  # Saint Pierre and Miquelon
        'RS': '+381',  # Serbia
        'SS': '+211',  # South Sudan
        'ST': '+239',  # Sao Tome and Principe
        'SR': '+597',  # Suriname
        'SK': '+421',  # Slovakia
        'SI': '+386',  # Slovenia
        'SE': '+46',  # Sweden
        'SZ': '+268',  # Eswatini
        'SX': '+1-721',  # Sint Maarten (Dutch part)
        'SC': '+248',  # Seychelles
        'SY': '+963',  # Syrian Arab Republic
        'TC': '+1-649',  # Turks and Caicos Islands
        'TD': '+235',  # Chad
        'TG': '+228',  # Togo
        'TH': '+66',  # Thailand
        'TJ': '+992',  # Tajikistan
        'TK': '+690',  # Tokelau
        'TM': '+993',  # Turkmenistan
        'TL': '+670',  # Timor-Leste
        'TO': '+676',  # Tonga
        'TT': '+1-868',  # Trinidad and Tobago
        'TN': '+216',  # Tunisia
        'TR': '+90',  # Turkey
        'TV': '+688',  # Tuvalu
        'TW': '+886',  # Taiwan, Province of China
        'TZ': '+255',  # Tanzania, United Republic of
        'UG': '+256',  # Uganda
        'UA': '+380',  # Ukraine
        'UM': '',  # United States Minor Outlying Islands
        'UY': '+598',  # Uruguay
        'UZ': '+998',  # Uzbekistan
        'VA': '+39',  # Holy See (Vatican City State)
        'VC': '+1-784',  # Saint Vincent and the Grenadines
        'VE': '+58',  # Venezuela, Bolivarian Republic of
        'VG': '+1-284',  # Virgin Islands, British
        'VI': '+1-340',  # Virgin Islands,U.S.
        'VN': '+84',  # Viet Nam
        'VU': '+678',  # Vanuatu
        'WF': '+681',  # Wallis and Futuna
        'WS': '+685',  # Samoa
        'YE': '+967',  # Yemen
        'ZA': '+27',  # South Africa
        'ZM': '+260',  # Zambia
        'ZW': '+263',  # Zimbabwe
        'AW': '+297',
        'AQ': '+672',
        'AU': '+61',
        'BY': '+375',
        'BV': '0055',
        'CF': '+236',
        'CA': '+1',
        'CC': '+61',
        'CI': '+225',
        'DE': 'Germany',
        'US': '+1',
        'SG': '+65'

        # Add more country codes as needed
    }

    all_countries = list(pycountry.countries)
    for country in all_countries:
        alpha2_code = country.alpha_2
        country_name = country.name
        phone_code = phone_codes.get(alpha2_code, 'N/A')
        # print(f"Country: {country_name}, Alpha-2 Code: {alpha2_code}, Phone Code: {phone_code}")
    unique_subjects = db.session.query(distinct(Emails_data.subject_part2), Emails_data.id,
                                       Emails_data.subject_part1).order_by(
        desc(Emails_data.id)).all()
    unique_lines_set = set()

    for subject_tuple in unique_subjects:
        subject_line = subject_tuple[0]
        subject_part1 = subject_tuple[2]

        if subject_part1.strip() == 'HandsHR website' or subject_part1 == 'GeoxHR website':
            unique_lines_set.add(subject_line)

        if " for " in subject_line and " applied for " in subject_line:
            after_for = subject_line.split(" for ", 1)[1].strip()
            unique_lines_set.add(after_for)

    unique_lines = sorted(list(unique_lines_set))

    # Check if the request is AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # If AJAX request, return JSON response
        filtered_data_html = render_template('candidates.html', alldata=serialized_alldata,
                                             all_countries=all_countries, phone_codes=phone_codes,
                                             unique_lines=unique_lines, selected_year=selected_year,
                                             selected_country=selected_country, selected_subject=selected_subject,
                                             total_pages=total_pages)  # Pass total_pages to the template
        return jsonify({'html': filtered_data_html, 'alldata': serialized_alldata, 'total_pages': total_pages})
    else:
        # If regular request, render the template
        return render_template('candidates.html', alldata=alldata,
                               all_countries=all_countries, phone_codes=phone_codes, unique_lines=unique_lines,
                               total_pages=total_pages)  # Pass total_pages to the template


@app.route('/selecteddata')
@role_required(allowed_roles=['user', 'admin'])
def selecteddata():
    selected_year = request.args.get('year_select')
    selected_country = request.args.get('country_select')
    selected_subject = request.args.get('subj_select')
    page = int(request.args.get('page', 1))  # Get page number, default to 1
    per_page = int(request.args.get('per_page', 300))  # Get items per page, default to 5
    # Get items per page, default to 5
    print(selected_year, selected_country, selected_subject, page, per_page)
    action = 'Interested'
    current_year = datetime.now().year  # Get the current year

    with db.session() as session:
        # Initialize base query without year filter
        query = session.query(Emails_data).filter(
            Emails_data.action == action,
        ).order_by(Emails_data.created_at.desc())

        # Apply year filter if selected_year is provided, else default to current year
        if selected_year and selected_year != "":
            # Filter by selected year
            or_(
                extract('year', func.str_to_date(Emails_data.formatted_date, '%a, %d %b %Y')) == int(selected_year),
                extract('year', func.str_to_date(Emails_data.formatted_date, '%Y-%m-%d')) == int(selected_year)
            )
            print(f"Applying year filter: {selected_year}")
        else:
            # Filter by current year
            query = query.filter(
                or_(
                    extract('year', func.str_to_date(Emails_data.formatted_date, '%a, %d %b %Y')) == current_year,
                    extract('year', func.str_to_date(Emails_data.formatted_date, '%Y-%m-%d')) == current_year
                )            )
            print(f"Applying default year filter: {current_year}")

        # Apply subject filter if selected_subject is provided
        if selected_subject and selected_subject != "":
            query = query.filter(
                Emails_data.subject_part2.ilike(f"%{selected_subject}%")
            )
            print(f"Applying subject filter: {selected_subject}")

        # Apply country filter if selected_country is provided
        # Inside the 'with db.session() as session:' block

        # Apply country filter if selected_country is provided
        if selected_country and selected_country.strip().lower() in country_prefixes:
            print(f"Applying country filter for: {selected_country}")
            prefixes = country_prefixes[selected_country.strip().lower()]
            print(f"Prefixes for {selected_country}: {prefixes}")
            # Construct OR condition for country prefixes
            country_prefix_conditions = or_(
                *[func.substr(Emails_data.phone_number, 1, len(prefix)) == prefix for prefix in prefixes]
            )
            print(f"Country prefix conditions: {country_prefix_conditions}")
            query = query.filter(country_prefix_conditions)
            print(f"Applied country filter for: {selected_country}")
        else:
            selected_country = ""

            # Count total number of pages
        total_items = query.count()
        total_pages = ceil(total_items / per_page)

        # Paginate the query results
        paginated_data = query.paginate(page=page, per_page=per_page)
        alldata = paginated_data.items  # Extract the items from the paginated object
        print(total_items, total_pages)
        serialized_alldata = []  # Initialize list to store serialized data

        # Serialize the data
        if alldata:
            print("Data found after filtering:")
            for data in alldata:
                print(data)  # Assuming 'data' is the object representing each record

            serialized_alldata = [
                {
                    "id": email.id,
                    "email": email.email,
                    "sender_name": email.sender_name,
                    "subject_part1": email.subject_part1,
                    "subject_part2": email.subject_part2,
                    "formatted_date": email.formatted_date,
                    "pdf_content_json": email.subject_part2,
                    "phone_number": email.phone_number,
                    "status": email.status,
                    "action": email.action
                }
                for email in alldata
            ]
        else:
            print("No data found after filtering.")
    phone_codes = {
        'AF': '+93',
        'AO': '+244',
        'AI': '+1-264',
        'AX': '+358',
        'AL': '+355',
        'AD': '+376',
        'AE': '+971',
        'AR': '+54',
        'AM': '+374',
        'AS': '+1-684',
        'TF': '+262',
        'AG': '+1-268',
        'AT': '+43',
        'AZ': '+994',
        'BI': '+257',
        'BE': '+32',
        'BJ': '+229',
        'BQ': '+599',
        'BF': '+226',
        'BD': '+880',
        'BG': '+359',
        'BH': '+973',
        'BS': '+1-242',
        'BA': '+387',
        'BL': '+590',
        'BZ': '+501',
        'BM': '+1-441',
        'BO': '+591',
        'BR': '+55',
        'BB': '+1-246',
        'BN': '+673',
        'BT': '+975',
        'BW': '+267',
        'CFR': '+236',  # Central African Republic
        'CAN': '+1',  # Canada
        'CCK': '+61',  # Cocos(Keeling) Islands
        'CH': '+41',  # Switzerland
        'CL': '+56',  # Chile
        'CN': '+86',  # China
        'CM': '+237',  # Cameroon
        'CD': '+243',  # Congo, The Democratic Republic of the
        'CG': '+242',  # Congo
        'CK': '+682',  # Cook Islands
        'CO': '+57',  # Colombia
        'KM': '+269',  # Comoros
        'CV': '+238',  # Cabo Verde(Cape Verde)
        'CR': '+506',  # Costa Rica
        'CU': '+53',  # Cuba
        'CW': '+599',  # Curaçao
        'CX': '+61',  # Christmas Island
        'KY': '+1-345',  # Cayman Islands
        'CY': '+357',  # Cyprus
        'CZ': '+420',  # Czechia(Czech Republic)
        'DEU': '+49',  # Germany
        'DJ': '+253',  # Djibouti
        'DM': '+1-767',  # Dominica
        'DK': '+45',  # Denmark
        'DO': '+1-809',  # Dominican Republic (and +1-829 and +1-849)
        'DZ': '+213',  # Algeria
        'EC': '+593',  # Ecuador
        'EG': '+20',  # Egypt
        'ER': '+291',  # Eritrea
        'EH': '+212',  # Western Sahara
        'ES': '+34',  # Spain
        'EE': '+372',  # Estonia
        'ET': '+251',  # Ethiopia
        'FI': '+358',  # Finland
        'FJ': '+679',  # Fiji
        'FK': '+500',  # Falkland Islands (Malvinas)
        'FR': '+33',  # France
        'FO': '+298',  # Faroe Islands
        'FM': '+691',  # Micronesia, Federated States of
        'GA': '+241',  # Gabon
        'GB': '+44',  # United Kingdom
        'GE': '+995',  # Georgia
        'GG': '+44-1481',  # Guernsey
        'GH': '+233',  # Ghana
        'GI': '+350',  # Gibraltar
        'GN': '+224',  # Guinea
        'GP': '+590',  # Guadeloupe
        'GM': '+220',  # Gambia
        'GW': '+245',  # Guinea-Bissau
        'GQ': '+240',  # Equatorial Guinea
        'GR': '+30',  # Greece
        'GD': '+1-473',  # Grenada
        'GL': '+299',  # Greenland
        'GT': '+502',  # Guatemala
        'GF': '+594',  # French Guiana
        'GU': '+1-671',  # Guam
        'GY': '+592',  # Guyana
        'HK': '+852',  # Hong Kong
        'HM': '',  # Heard Island and McDonald Islands: No specific dialing code; Australian external territory
        'HN': '+504',  # Honduras
        'HR': '+385',  # Croatia
        'HT': '+509',  # Haiti
        'HU': '+36',  # Hungary
        'ID': '+62',  # Indonesia
        'IM': '+44-1624',  # Isle of Man
        'IN': '+91',  # India
        'IO': '+246',  # British Indian Ocean Territory
        'IE': '+353',  # Ireland
        'IR': '+98',  # Iran, Islamic Republic of
        'IQ': '+964',  # Iraq
        'IS': '+354',  # Iceland
        'IL': '+972',  # Israel
        'IT': '+39',  # Italy
        'JM': '+1-876',  # Jamaica
        'JE': '+44-1534',  # Jersey
        'JO': '+962',  # Jordan
        'JP': '+81',  # Japan
        'KZ': '+7',  # Kazakhstan
        'KE': '+254',  # Kenya
        'KG': '+996',  # Kyrgyzstan
        'KH': '+855',  # Cambodia
        'KI': '+686',  # Kiribati
        'KN': '+1-869',  # Saint Kitts and Nevis
        'KR': '+82',  # Korea, Republic of
        'KW': '+965',  # Kuwait
        'LA': '+856',  # Lao People's Democratic Republic
        'LB': '+961',  # Lebanon
        'LR': '+231',  # Liberia
        'LY': '+218',  # Libya
        'LC': '+1-758',  # Saint Lucia
        'LI': '+423',  # Liechtenstein
        'LK': '+94',  # Sri Lanka
        'LS': '+266',  # Lesotho
        'LT': '+370',  # Lithuania
        'LU': '+352',  # Luxembourg
        'LV': '+371',  # Latvia
        'MO': '+853',  # Macao
        'MF': '+590',  # Saint Martin (French part)
        'MA': '+212',  # Morocco
        'MC': '+377',  # Monaco
        'MD': '+373',  # Moldova, Republic of
        'MG': '+261',  # Madagascar
        'MV': '+960',  # Maldives
        'MX': '+52',  # Mexico
        'MH': '+692',  # Marshall Islands
        'MK': '+389',  # North Macedonia
        'ML': '+223',  # Mali
        'MT': '+356',  # Malta
        'MM': '+95',  # Myanmar
        'ME': '+382',  # Montenegro
        'MN': '+976',  # Mongolia
        'MP': '+1-670',  # Northern Mariana Islands
        'MZ': '+258',  # Mozambique
        'MR': '+222',  # Mauritania
        'MS': '+1-664',  # Montserrat
        'MQ': '+596',  # Martinique
        'MU': '+230',  # Mauritius
        'MW': '+265',  # Malawi
        'MY': '+60',  # Malaysia
        'YT': '+262',  # Mayotte
        'NA': '+264',  # Namibia
        'NC': '+687',  # New Caledonia
        'NE': '+227',  # Niger
        'NF': '+672',  # Norfolk Island
        'NG': '+234',  # Nigeria
        'NI': '+505',  # Nicaragua
        'NU': '+683',  # Niue
        'NL': '+31',  # Netherlands
        'NO': '+47',  # Norway
        'NP': '+977',  # Nepal
        'NR': '+674',  # Nauru
        'NZ': '+64',  # New Zealand
        'OM': '+968',  # Oman
        'PK': '+92',  # Pakistan
        'PA': '+507',  # Panama
        'PN': '+64',  # Pitcairn
        'PE': '+51',  # Peru
        'PH': '+63',  # Philippines
        'PW': '+680',  # Palau
        'PG': '+675',  # Papua New Guinea
        'PL': '+48',  # Poland
        'PR': '+1-787',  # Puerto Rico
        'KP': '+850',  # Korea, Democratic People's Republic of
        'PT': '+351',  # Portugal
        'PY': '+595',  # Paraguay
        'PS': '+970',  # Palestine, State of
        'PF': '+689',  # French Polynesia
        'QA': '+974',  # Qatar
        'RE': '+262',  # Réunion
        'RO': '+40',  # Romania
        'RU': '+7',  # Russian Federation
        'RW': '+250',  # Rwanda
        'SA': '+966',  # Saudi Arabia
        'SD': '+249',  # Sudan
        'SN': '+221',  # Senegal
        'GS': '',  # South Georgia and the South Sandwich Islands
        'SH': '+290',  # Saint Helena, Ascension and Tristan da Cunha
        'SJ': '+47',  # Svalbard and Jan Mayen
        'SB': '+677',  # Solomon Islands
        'SL': '+232',  # Sierra Leone
        'SV': '+503',  # El Salvador
        'SM': '+378',  # San Marino
        'SO': '+252',  # Somalia
        'PM': '+508',  # Saint Pierre and Miquelon
        'RS': '+381',  # Serbia
        'SS': '+211',  # South Sudan
        'ST': '+239',  # Sao Tome and Principe
        'SR': '+597',  # Suriname
        'SK': '+421',  # Slovakia
        'SI': '+386',  # Slovenia
        'SE': '+46',  # Sweden
        'SZ': '+268',  # Eswatini
        'SX': '+1-721',  # Sint Maarten (Dutch part)
        'SC': '+248',  # Seychelles
        'SY': '+963',  # Syrian Arab Republic
        'TC': '+1-649',  # Turks and Caicos Islands
        'TD': '+235',  # Chad
        'TG': '+228',  # Togo
        'TH': '+66',  # Thailand
        'TJ': '+992',  # Tajikistan
        'TK': '+690',  # Tokelau
        'TM': '+993',  # Turkmenistan
        'TL': '+670',  # Timor-Leste
        'TO': '+676',  # Tonga
        'TT': '+1-868',  # Trinidad and Tobago
        'TN': '+216',  # Tunisia
        'TR': '+90',  # Turkey
        'TV': '+688',  # Tuvalu
        'TW': '+886',  # Taiwan, Province of China
        'TZ': '+255',  # Tanzania, United Republic of
        'UG': '+256',  # Uganda
        'UA': '+380',  # Ukraine
        'UM': '',  # United States Minor Outlying Islands
        'UY': '+598',  # Uruguay
        'UZ': '+998',  # Uzbekistan
        'VA': '+39',  # Holy See (Vatican City State)
        'VC': '+1-784',  # Saint Vincent and the Grenadines
        'VE': '+58',  # Venezuela, Bolivarian Republic of
        'VG': '+1-284',  # Virgin Islands, British
        'VI': '+1-340',  # Virgin Islands,U.S.
        'VN': '+84',  # Viet Nam
        'VU': '+678',  # Vanuatu
        'WF': '+681',  # Wallis and Futuna
        'WS': '+685',  # Samoa
        'YE': '+967',  # Yemen
        'ZA': '+27',  # South Africa
        'ZM': '+260',  # Zambia
        'ZW': '+263',  # Zimbabwe
        'AW': '+297',
        'AQ': '+672',
        'AU': '+61',
        'BY': '+375',
        'BV': '0055',
        'CF': '+236',
        'CA': '+1',
        'CC': '+61',
        'CI': '+225',
        'DE': 'Germany',
        'US': '+1',
        'SG': '+65'

        # Add more country codes as needed
    }

    all_countries = list(pycountry.countries)
    for country in all_countries:
        alpha2_code = country.alpha_2
        country_name = country.name
        phone_code = phone_codes.get(alpha2_code, 'N/A')
        # print(f"Country: {country_name}, Alpha-2 Code: {alpha2_code}, Phone Code: {phone_code}")
    unique_subjects = db.session.query(distinct(Emails_data.subject_part2), Emails_data.id,
                                       Emails_data.subject_part1).order_by(
        desc(Emails_data.id)).all()
    unique_lines_set = set()

    for subject_tuple in unique_subjects:
        subject_line = subject_tuple[0]
        subject_part1 = subject_tuple[2]

        # Check if subject_part1 is equal to 'HandsHR website'
        if subject_part1.strip() == 'HandsHR website' or subject_part1 == 'GeoxHR website':
            # Ensure to strip whitespace
            unique_lines_set.add(subject_line)

        # Check for "for" and "applied for" in subject_line
        if " for " in subject_line and " applied for " in subject_line:
            after_for = subject_line.split(" for ", 1)[1].strip()
            unique_lines_set.add(after_for)

    unique_lines = sorted(list(unique_lines_set))
    # print(unique_lines)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # If AJAX request, return JSON response
        filtered_data_html = render_template('candidates.html', alldata=serialized_alldata,
                                             all_countries=all_countries, phone_codes=phone_codes,
                                             unique_lines=unique_lines, selected_year=selected_year,
                                             selected_country=selected_country, selected_subject=selected_subject,
                                             total_pages=total_pages)  # Pass total_pages to the template
        return jsonify({'html': filtered_data_html, 'alldata': serialized_alldata, 'total_pages': total_pages})
    else:
        # If regular request, render the template
        return render_template('candidates.html', alldata=alldata,
                               all_countries=all_countries, phone_codes=phone_codes, unique_lines=unique_lines,
                               total_pages=total_pages)  # Pass total_pages to the template


@app.route('/candidateprofile/<string:email>')
@role_required(allowed_roles=['user', 'admin'])
def candidateprofile(email):
    with db.session() as session:
        alldata = session.query(Emails_data).filter(Emails_data.email == email).order_by(
            desc(Emails_data.created_at)).all()

        sender_name = session.query(Emails_data.sender_name).filter(Emails_data.email == email).first()

        if sender_name:
            sender_name = sender_name[0]
            recruiting = session.query(recruiting_data).filter(recruiting_data.candidate == sender_name,
                                                               recruiting_data.did_you != 'Help Another').all()
        else:
            recruiting = []

    return render_template('profile.html', alldata=alldata, recruiting=recruiting)


@app.route('/registereddata')
@role_required(allowed_roles=['user', 'admin'])
def registereddata():
    subject_part1 = 'registered from Geox hr'
    selected_year = request.args.get('year_select')
    selected_country = request.args.get('country_select')
    selected_subject = request.args.get('subj_select')
    page = int(request.args.get('page', 1))  # Get page number, default to 1
    per_page = int(request.args.get('per_page', 300))  # Get items per page, default to 5
    # Get items per page, default to 5
    print(selected_year, selected_country, selected_subject, page, per_page)
    action = 'Interested'
    current_year = datetime.now().year  # Get the current year

    with db.session() as session:
        # Initialize base query without year filter
        query = session.query(Emails_data).filter(
            Emails_data.action != action,
            Emails_data.subject_part1 == subject_part1
        )

        # Apply year filter if selected_year is provided, else default to current year
        if selected_year and selected_year != "":
            # Filter by selected year
            query = query.filter(
                or_(
                    extract('year', func.str_to_date(Emails_data.formatted_date, '%a, %d %b %Y')) == int(selected_year),
                    extract('year', func.str_to_date(Emails_data.formatted_date, '%Y-%m-%d')) == int(selected_year)
                )            )
            print(f"Applying year filter: {selected_year}")
        else:
            # Filter by current year
            query = query.filter(
                or_(
                    extract('year', func.str_to_date(Emails_data.formatted_date, '%a, %d %b %Y')) == current_year,
                    extract('year', func.str_to_date(Emails_data.formatted_date, '%Y-%m-%d')) == current_year
                )            )
            print(f"Applying default year filter: {current_year}")

        # Apply subject filter if selected_subject is provided
        if selected_subject and selected_subject != "":
            query = query.filter(
                Emails_data.subject_part2.ilike(f"%{selected_subject}%")
            )
            print(f"Applying subject filter: {selected_subject}")

        # Apply country filter if selected_country is provided
        # Inside the 'with db.session() as session:' block

        # Apply country filter if selected_country is provided
        if selected_country and selected_country.strip().lower() in country_prefixes:
            print(f"Applying country filter for: {selected_country}")
            prefixes = country_prefixes[selected_country.strip().lower()]
            print(f"Prefixes for {selected_country}: {prefixes}")
            # Construct OR condition for country prefixes
            country_prefix_conditions = or_(
                *[func.substr(Emails_data.phone_number, 1, len(prefix)) == prefix for prefix in prefixes]
            )
            print(f"Country prefix conditions: {country_prefix_conditions}")
            query = query.filter(country_prefix_conditions)
            print(f"Applied country filter for: {selected_country}")
        else:
            selected_country = ""

            # Count total number of pages
        total_items = query.count()
        total_pages = ceil(total_items / per_page)

        # Paginate the query results
        paginated_data = query.paginate(page=page, per_page=per_page)
        alldata = paginated_data.items  # Extract the items from the paginated object
        print(total_items, total_pages)
        serialized_alldata = []  # Initialize list to store serialized data

        # Serialize the data
        if alldata:
            print("Data found after filtering:")
            for data in alldata:
                print(data)  # Assuming 'data' is the object representing each record

            serialized_alldata = [
                {
                    "id": email.id,
                    "email": email.email,
                    "sender_name": email.sender_name,
                    "subject_part1": email.subject_part1,
                    "subject_part2": email.subject_part2,
                    "formatted_date": email.formatted_date,
                    "pdf_content_json": email.subject_part2,
                    "phone_number": email.phone_number,
                    "status": email.status,
                    "action": email.action
                }
                for email in alldata
            ]
        else:
            print("No data found after filtering.")
    phone_codes = {
        'AF': '+93',
        'AO': '+244',
        'AI': '+1-264',
        'AX': '+358',
        'AL': '+355',
        'AD': '+376',
        'AE': '+971',
        'AR': '+54',
        'AM': '+374',
        'AS': '+1-684',
        'TF': '+262',
        'AG': '+1-268',
        'AT': '+43',
        'AZ': '+994',
        'BI': '+257',
        'BE': '+32',
        'BJ': '+229',
        'BQ': '+599',
        'BF': '+226',
        'BD': '+880',
        'BG': '+359',
        'BH': '+973',
        'BS': '+1-242',
        'BA': '+387',
        'BL': '+590',
        'BZ': '+501',
        'BM': '+1-441',
        'BO': '+591',
        'BR': '+55',
        'BB': '+1-246',
        'BN': '+673',
        'BT': '+975',
        'BW': '+267',
        'CFR': '+236',  # Central African Republic
        'CAN': '+1',  # Canada
        'CCK': '+61',  # Cocos(Keeling) Islands
        'CH': '+41',  # Switzerland
        'CL': '+56',  # Chile
        'CN': '+86',  # China
        'CM': '+237',  # Cameroon
        'CD': '+243',  # Congo, The Democratic Republic of the
        'CG': '+242',  # Congo
        'CK': '+682',  # Cook Islands
        'CO': '+57',  # Colombia
        'KM': '+269',  # Comoros
        'CV': '+238',  # Cabo Verde(Cape Verde)
        'CR': '+506',  # Costa Rica
        'CU': '+53',  # Cuba
        'CW': '+599',  # Curaçao
        'CX': '+61',  # Christmas Island
        'KY': '+1-345',  # Cayman Islands
        'CY': '+357',  # Cyprus
        'CZ': '+420',  # Czechia(Czech Republic)
        'DEU': '+49',  # Germany
        'DJ': '+253',  # Djibouti
        'DM': '+1-767',  # Dominica
        'DK': '+45',  # Denmark
        'DO': '+1-809',  # Dominican Republic (and +1-829 and +1-849)
        'DZ': '+213',  # Algeria
        'EC': '+593',  # Ecuador
        'EG': '+20',  # Egypt
        'ER': '+291',  # Eritrea
        'EH': '+212',  # Western Sahara
        'ES': '+34',  # Spain
        'EE': '+372',  # Estonia
        'ET': '+251',  # Ethiopia
        'FI': '+358',  # Finland
        'FJ': '+679',  # Fiji
        'FK': '+500',  # Falkland Islands (Malvinas)
        'FR': '+33',  # France
        'FO': '+298',  # Faroe Islands
        'FM': '+691',  # Micronesia, Federated States of
        'GA': '+241',  # Gabon
        'GB': '+44',  # United Kingdom
        'GE': '+995',  # Georgia
        'GG': '+44-1481',  # Guernsey
        'GH': '+233',  # Ghana
        'GI': '+350',  # Gibraltar
        'GN': '+224',  # Guinea
        'GP': '+590',  # Guadeloupe
        'GM': '+220',  # Gambia
        'GW': '+245',  # Guinea-Bissau
        'GQ': '+240',  # Equatorial Guinea
        'GR': '+30',  # Greece
        'GD': '+1-473',  # Grenada
        'GL': '+299',  # Greenland
        'GT': '+502',  # Guatemala
        'GF': '+594',  # French Guiana
        'GU': '+1-671',  # Guam
        'GY': '+592',  # Guyana
        'HK': '+852',  # Hong Kong
        'HM': '',  # Heard Island and McDonald Islands: No specific dialing code; Australian external territory
        'HN': '+504',  # Honduras
        'HR': '+385',  # Croatia
        'HT': '+509',  # Haiti
        'HU': '+36',  # Hungary
        'ID': '+62',  # Indonesia
        'IM': '+44-1624',  # Isle of Man
        'IN': '+91',  # India
        'IO': '+246',  # British Indian Ocean Territory
        'IE': '+353',  # Ireland
        'IR': '+98',  # Iran, Islamic Republic of
        'IQ': '+964',  # Iraq
        'IS': '+354',  # Iceland
        'IL': '+972',  # Israel
        'IT': '+39',  # Italy
        'JM': '+1-876',  # Jamaica
        'JE': '+44-1534',  # Jersey
        'JO': '+962',  # Jordan
        'JP': '+81',  # Japan
        'KZ': '+7',  # Kazakhstan
        'KE': '+254',  # Kenya
        'KG': '+996',  # Kyrgyzstan
        'KH': '+855',  # Cambodia
        'KI': '+686',  # Kiribati
        'KN': '+1-869',  # Saint Kitts and Nevis
        'KR': '+82',  # Korea, Republic of
        'KW': '+965',  # Kuwait
        'LA': '+856',  # Lao People's Democratic Republic
        'LB': '+961',  # Lebanon
        'LR': '+231',  # Liberia
        'LY': '+218',  # Libya
        'LC': '+1-758',  # Saint Lucia
        'LI': '+423',  # Liechtenstein
        'LK': '+94',  # Sri Lanka
        'LS': '+266',  # Lesotho
        'LT': '+370',  # Lithuania
        'LU': '+352',  # Luxembourg
        'LV': '+371',  # Latvia
        'MO': '+853',  # Macao
        'MF': '+590',  # Saint Martin (French part)
        'MA': '+212',  # Morocco
        'MC': '+377',  # Monaco
        'MD': '+373',  # Moldova, Republic of
        'MG': '+261',  # Madagascar
        'MV': '+960',  # Maldives
        'MX': '+52',  # Mexico
        'MH': '+692',  # Marshall Islands
        'MK': '+389',  # North Macedonia
        'ML': '+223',  # Mali
        'MT': '+356',  # Malta
        'MM': '+95',  # Myanmar
        'ME': '+382',  # Montenegro
        'MN': '+976',  # Mongolia
        'MP': '+1-670',  # Northern Mariana Islands
        'MZ': '+258',  # Mozambique
        'MR': '+222',  # Mauritania
        'MS': '+1-664',  # Montserrat
        'MQ': '+596',  # Martinique
        'MU': '+230',  # Mauritius
        'MW': '+265',  # Malawi
        'MY': '+60',  # Malaysia
        'YT': '+262',  # Mayotte
        'NA': '+264',  # Namibia
        'NC': '+687',  # New Caledonia
        'NE': '+227',  # Niger
        'NF': '+672',  # Norfolk Island
        'NG': '+234',  # Nigeria
        'NI': '+505',  # Nicaragua
        'NU': '+683',  # Niue
        'NL': '+31',  # Netherlands
        'NO': '+47',  # Norway
        'NP': '+977',  # Nepal
        'NR': '+674',  # Nauru
        'NZ': '+64',  # New Zealand
        'OM': '+968',  # Oman
        'PK': '+92',  # Pakistan
        'PA': '+507',  # Panama
        'PN': '+64',  # Pitcairn
        'PE': '+51',  # Peru
        'PH': '+63',  # Philippines
        'PW': '+680',  # Palau
        'PG': '+675',  # Papua New Guinea
        'PL': '+48',  # Poland
        'PR': '+1-787',  # Puerto Rico
        'KP': '+850',  # Korea, Democratic People's Republic of
        'PT': '+351',  # Portugal
        'PY': '+595',  # Paraguay
        'PS': '+970',  # Palestine, State of
        'PF': '+689',  # French Polynesia
        'QA': '+974',  # Qatar
        'RE': '+262',  # Réunion
        'RO': '+40',  # Romania
        'RU': '+7',  # Russian Federation
        'RW': '+250',  # Rwanda
        'SA': '+966',  # Saudi Arabia
        'SD': '+249',  # Sudan
        'SN': '+221',  # Senegal
        'GS': '',  # South Georgia and the South Sandwich Islands
        'SH': '+290',  # Saint Helena, Ascension and Tristan da Cunha
        'SJ': '+47',  # Svalbard and Jan Mayen
        'SB': '+677',  # Solomon Islands
        'SL': '+232',  # Sierra Leone
        'SV': '+503',  # El Salvador
        'SM': '+378',  # San Marino
        'SO': '+252',  # Somalia
        'PM': '+508',  # Saint Pierre and Miquelon
        'RS': '+381',  # Serbia
        'SS': '+211',  # South Sudan
        'ST': '+239',  # Sao Tome and Principe
        'SR': '+597',  # Suriname
        'SK': '+421',  # Slovakia
        'SI': '+386',  # Slovenia
        'SE': '+46',  # Sweden
        'SZ': '+268',  # Eswatini
        'SX': '+1-721',  # Sint Maarten (Dutch part)
        'SC': '+248',  # Seychelles
        'SY': '+963',  # Syrian Arab Republic
        'TC': '+1-649',  # Turks and Caicos Islands
        'TD': '+235',  # Chad
        'TG': '+228',  # Togo
        'TH': '+66',  # Thailand
        'TJ': '+992',  # Tajikistan
        'TK': '+690',  # Tokelau
        'TM': '+993',  # Turkmenistan
        'TL': '+670',  # Timor-Leste
        'TO': '+676',  # Tonga
        'TT': '+1-868',  # Trinidad and Tobago
        'TN': '+216',  # Tunisia
        'TR': '+90',  # Turkey
        'TV': '+688',  # Tuvalu
        'TW': '+886',  # Taiwan, Province of China
        'TZ': '+255',  # Tanzania, United Republic of
        'UG': '+256',  # Uganda
        'UA': '+380',  # Ukraine
        'UM': '',  # United States Minor Outlying Islands
        'UY': '+598',  # Uruguay
        'UZ': '+998',  # Uzbekistan
        'VA': '+39',  # Holy See (Vatican City State)
        'VC': '+1-784',  # Saint Vincent and the Grenadines
        'VE': '+58',  # Venezuela, Bolivarian Republic of
        'VG': '+1-284',  # Virgin Islands, British
        'VI': '+1-340',  # Virgin Islands,U.S.
        'VN': '+84',  # Viet Nam
        'VU': '+678',  # Vanuatu
        'WF': '+681',  # Wallis and Futuna
        'WS': '+685',  # Samoa
        'YE': '+967',  # Yemen
        'ZA': '+27',  # South Africa
        'ZM': '+260',  # Zambia
        'ZW': '+263',  # Zimbabwe
        'AW': '+297',
        'AQ': '+672',
        'AU': '+61',
        'BY': '+375',
        'BV': '0055',
        'CF': '+236',
        'CA': '+1',
        'CC': '+61',
        'CI': '+225',
        'DE': 'Germany',
        'US': '+1',
        'SG': '+65'

        # Add more country codes as needed
    }

    all_countries = list(pycountry.countries)
    for country in all_countries:
        alpha2_code = country.alpha_2
        country_name = country.name
        phone_code = phone_codes.get(alpha2_code, 'N/A')
        # print(f"Country: {country_name}, Alpha-2 Code: {alpha2_code}, Phone Code: {phone_code}")
    unique_subjects = db.session.query(distinct(Emails_data.subject_part2), Emails_data.id,
                                       Emails_data.subject_part1).order_by(
        desc(Emails_data.id)).all()
    unique_lines_set = set()

    for subject_tuple in unique_subjects:
        subject_line = subject_tuple[0]
        subject_part1 = subject_tuple[2]

        # Check if subject_part1 is equal to 'HandsHR website'
        if subject_part1.strip() == 'HandsHR website' or subject_part1 == 'GeoxHR website':
            # Ensure to strip whitespace
            unique_lines_set.add(subject_line)

        # Check for "for" and "applied for" in subject_line
        if " for " in subject_line and " applied for " in subject_line:
            after_for = subject_line.split(" for ", 1)[1].strip()
            unique_lines_set.add(after_for)

    unique_lines = sorted(list(unique_lines_set))
    # print(unique_lines)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # If AJAX request, return JSON response
        filtered_data_html = render_template('candidates.html', alldata=serialized_alldata,
                                             all_countries=all_countries, phone_codes=phone_codes,
                                             unique_lines=unique_lines, selected_year=selected_year,
                                             selected_country=selected_country, selected_subject=selected_subject,
                                             total_pages=total_pages)  # Pass total_pages to the template
        return jsonify({'html': filtered_data_html, 'alldata': serialized_alldata, 'total_pages': total_pages})
    else:
        # If regular request, render the template
        return render_template('candidates.html', alldata=alldata,
                               all_countries=all_countries, phone_codes=phone_codes, unique_lines=unique_lines,
                               total_pages=total_pages)  # Pass total_pages to the template


@app.route('/export_csv', methods=['POST'])
def export_csv():
    export_route = request.form['export_route']

    action = ''
    subject_part1 = ''
    if export_route == '/candidate':
        action = ''
        subject_part1 != 'registered from Geox hr'
        columns_to_export = ['sender_name', 'email', 'subject_part1', 'subject_part2', 'formatted_date', 'phone_number',
                             'status']
    elif export_route == '/registereddata':
        subject_part1 = 'registered from Geox hr'  # Set subject_part1 to 'registered' for this route
        columns_to_export = ['sender_name', 'email', 'subject_part1', 'subject_part2', 'formatted_date', 'phone_number',
                             'status']
    elif export_route == '/selecteddata':
        action = 'Interested'
        columns_to_export = ['sender_name', 'email', 'subject_part1', 'subject_part2', 'formatted_date', 'phone_number',
                             'status']

    with db.session() as session:
        data = session.query(Emails_data).filter(Emails_data.action == action)
        if subject_part1:
            data = data.filter(Emails_data.subject_part1 == subject_part1)
        data = data.all()

    # Create a CSV file in-memory
    output = io.StringIO()
    csv_writer = csv.writer(output)

    # Write the header row with the selected columns
    csv_writer.writerow(columns_to_export)

    # Write the data rows
    for row in data:
        row_data = [getattr(row, column) for column in columns_to_export]
        csv_writer.writerow(row_data)

    output.seek(0)

    # Send the CSV file as a response
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=data.csv'}
    )


# for pdf view
@app.route('/pdf_content/<int:email_id>')
@role_required(allowed_roles=['user', 'admin'])
def get_pdf_content(email_id):
    email = Emails_data.query.filter_by(id=email_id).first()

    if email and email.file_content:
        file_name = email.file_name
        pdf_content = email.file_content

        # Mark the email as read when the user views the PDF
        if not email.is_read:
            email.is_read = True
            db.session.commit()

        response = send_file(
            io.BytesIO(pdf_content),
            mimetype='application/pdf'
        )

        return response

    return jsonify({'error': 'PDF not found'}), 404


# read/unread
@app.route('/check_is_read/<int:email_id>')
@role_required(allowed_roles=['user', 'admin'])
def check_is_read(email_id):
    email = Emails_data.query.get(email_id)
    if email:
        return jsonify({'is_read': email.is_read})
    return jsonify({'error': 'Email not found'}), 404


@app.route('/filter_emails')
def filter_emails():
    keyword = request.args.get('country_code')
    # print(keyword, "keyword")
    pdf_data = Emails_data.query.order_by(desc(Emails_data.id)).all()
    matching_emails = []
    for email in pdf_data:
        pdf_content_json = email.pdf_content_json
        if pdf_content_json:
            pdf_data_dict = json.loads(pdf_content_json)
            pdf_data_json_lower = json.dumps(pdf_data_dict).lower()
            pdf_words = pdf_data_json_lower.split()
            if keyword in pdf_words:
                matching_emails.append({
                    "id": email.id,
                    "email": email.email,
                    "status": email.status,
                    "action": email.action,
                    "sender_name": email.sender_name,
                    "subject_part1": email.subject_part1,
                    "subject_part2": email.subject_part2,
                    "formatted_date": email.formatted_date,
                    "pdf_content_json": pdf_content_json,
                    "phone_number": email.phone_number
                })

    # Print the search results to the console for debugging
    # print(f"Search results: {matching_emails}")

    return jsonify(matching_emails)


@app.route('/search_pdf')
def search_pdf():
    keyword = request.args.get('keyword')
    current_url = request.args.get('currentUrl')

    keyword_lower = keyword.lower()
    pdf_data = Emails_data.query.order_by(desc(Emails_data.id)).all()
    matching_emails = []

    for email in pdf_data:
        pdf_content_json = email.pdf_content_json
        if pdf_content_json:
            pdf_data_dict = json.loads(pdf_content_json)
            pdf_data_json_lower = json.dumps(pdf_data_dict).lower()
            if (current_url == 'candidate' and email.action != 'Interested') or \
                    (current_url == 'selecteddata' and email.action == 'Interested') or \
                    (
                            current_url == 'registereddata' and email.action != 'Interested' and email.subject_part1 == 'registered from Geox hr') or \
                    current_url not in ['candidate', 'selecteddata', 'registereddata']:
                if keyword_lower in pdf_data_json_lower:
                    matching_emails.append({
                        "id": email.id,
                        "email": email.email,
                        "sender_name": email.sender_name,
                        "subject_part1": email.subject_part1,
                        "subject_part2": email.subject_part2,
                        "formatted_date": email.formatted_date,
                        "pdf_content_json": pdf_content_json,
                        "phone_number": email.phone_number,
                        "status": email.status,
                    })

    return jsonify(matching_emails)


@app.route('/updatemail', methods=['POST'])
@role_required(allowed_roles=['user', 'admin'])
def updatemail():
    try:
        data = request.get_json()
        id = data.get('id')
        user = db.session.query(Emails_data).filter_by(id=id).first()

        selected_option = data.get('selectedOption')

        if selected_option == 'Reverse changes':
            user.status = 'applied'
            user.created_at = datetime.now()  # Set created_at to the current timestamp
        elif selected_option == 'Interested':
            user.action = 'Interested'
            user.created_at = datetime.now()  # Set created_at to the current timestamp
        elif selected_option == 'move to applied':
            user.action = ''
            user.status = 'applied'
            user.created_at = datetime.now()  # Set created_at to the current timestamp

        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'Update successful'}), 200
    except Exception as e:
        return jsonify({'error': 'An error occurred: ' + str(e)}), 500


@app.route('/deletemail', methods=['POST'])
@role_required(allowed_roles=['user', 'admin'])
def deletemail():
    try:
        data = request.get_json()
        id = data.get('id')
        # Query the database to find the Users record by ID
        user = db.session.query(Emails_data).filter_by(id=id).first()
        if user:

            db.session.delete(user)
            db.session.commit()
            return jsonify({'message': 'record deleted successfully'}), 200
        else:
            return jsonify({"Record not found for uid:", id})
    except Exception as e:
        # Handle any other unexpected errors
        return jsonify({'error': 'An error occurred: ' + str(e)}), 500


@app.route('/members')
@role_required(allowed_roles=['user', 'admin'])
def members():
    role = 'user'
    members_data = Users.query.order_by(desc(Users.id)).all()
    # for member in members_data:
    #     print(member.phone)
    print(members_data)
    return render_template('members.html', members_data=members_data)


@app.route('/addmembers')
@role_required(allowed_roles=['user', 'admin'])
def addmembers():
    designation = userdesignation_data.query.all()
    role = Role.query.all()
    return render_template('addmember.html', designations=designation, roles=role)


@app.route('/updatemembers/<int:id>')
@role_required(allowed_roles=['user', 'admin'])
def updatemembers(id):
    if id is not None:
        designation = userdesignation_data.query.all()
        role = Role.query.all()
        user = db.session.query(Users).filter_by(id=id).first()
        return render_template('addmember.html', data=user, designations=designation, roles=role)


@app.route('/savemember', methods=["POST"])
@role_required(allowed_roles=['user', 'admin'])
def savemember():
    if request.method == 'POST':
        id = request.form.get('id')
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        phone = request.form.get('phone')
        address = request.form.get('address')
        email = request.form.get('email')
        role = request.form.get('selected_role')
        designation = request.form.get('selected_designation')
        password = request.form.get('password')
        encpassword = sha256_crypt.encrypt(password)
        print(address,phone,fname)

        try:
            if id is not None:
                entry = db.session.query(Users).filter_by(id=id).first()
                if entry:
                    entry.id = id
                    entry.role = role
                    entry.fname = fname
                    entry.lname = lname
                    entry.phone = phone
                    entry.address = address
                    entry.email = email
                    entry.designation = designation
                    print(password, "entry.password")
                    entry.password = encpassword

                    db.session.commit()  # Update existing user
                    response = jsonify({'message': 'Member updated successfully!'})
                else:
                    response = jsonify({'error': 'Member with specified ID not found'}), 404
            else:
                email_exists = db.session.query(exists().where(Users.email == email)).scalar()
                if not email_exists:
                    entry = Users(fname=fname, lname=lname, email=email, password=encpassword, role=role,phone=phone,address=address,
                                  designation=designation)
                    db.session.add(entry)
                    db.session.commit()
                    response = jsonify({'message': 'Member created successfully!'})
                else:
                    response = jsonify({'error': 'Email already exists'}), 400

        except Exception as e:
            # Handle any errors that occurred during database operations
            db.session.rollback()
            response = jsonify({'error': f'Error saving member: {str(e)}'})
            response.status_code = 500

        return response


@app.route('/deletemembers/<int:id>', methods=['POST'])
@role_required(allowed_roles=['user', 'admin'])
def deletemembers(id):
    if id is not None:
        try:
            db.session.query(Users).filter(Users.id == id).delete()
            db.session.commit()
            return jsonify({'message': 'Member Deleted!'}), 200
        except Exception as e:
            return jsonify({'message': f'Error deleting member: {str(e)}'}), 500


@app.route('/restpassword/<int:id>', methods=['POST'])
@role_required(allowed_roles=['user', 'admin'])
def reset_password(id):
    if id is not None:
        try:
            user = db.session.query(Users).filter(Users.id == id).first()
            print(user, "user")
            if user:
                user.password = ''  # You may want to use a more secure method to reset the password
                db.session.commit()
                return jsonify({'message': 'Password reset successfully!'}), 200
            else:
                return jsonify({'message': 'User not found'}), 404
        except Exception as e:
            return jsonify({'message': f'Error resetting password: {str(e)}'}), 500


@app.route('/user')
@role_required(allowed_roles=['user', 'admin'])
def user():
    return render_template('/user.html')


@app.route('/changepassword', methods=["POST"])
@role_required(allowed_roles=['user', 'admin'])
def chnagepassword():
    if request.method == 'POST':
        user_id = session['user_id']
        oldpassword = request.form.get('oldps')
        newpassword = request.form.get('newps')
        confirmpassword = request.form.get('confirmpswrd')
        check = db.session.query(Users).filter_by(id=user_id).first()
        varify = sha256_crypt.verify(oldpassword, check.password)
        # print(varify)
        if varify:
            # print("varify")
            if newpassword == confirmpassword:
                # print("password confirm")
                password = sha256_crypt.encrypt(confirmpassword)
                check.password = password
                db.session.add(check)
                db.session.commit()
                return render_template('user.html', msg='password changed successfully')
            else:
                return render_template('user.html', msg='confirm password did not match')
        else:
            return render_template('user.html', msg='old password did not match')


# @app.route('/onereporting')
# @role_required(allowed_roles=['user', 'admin'])
# def onereporting():
#     return render_template('/onereporting-form.html')


@app.route('/onereporting_form/<int:candidate_id>/job/<int:jobid>/OrderId/<int:OrderId>')
@app.route('/onereporting_form/<int:id>')
@role_required(allowed_roles=['user', 'admin'])
def onereporting_form(id=None, candidate_id=None, jobid=None, OrderId=None):
    if candidate_id is not None:
        user = db.session.query(Emails_data).filter_by(id=candidate_id).first()
        companydata = db.session.query(Marketing).filter_by(id=jobid, company_status='active').first()
        # companydata = Marketing.query.filter(Marketing.id == jobid, Marketing.company_status == 'active').all()
    elif id is not None:
        user = db.session.query(Emails_data).filter_by(id=id).first()
        companydata = None
    else:
        pass
    # company = Marketing.query.all()
    members = Users.query.filter(Users.designation != 'admin').all()
    company = Marketing.query.filter(Marketing.company_status == 'active').all()
    positions = Joborder.query.filter_by(company_id=companydata.id, id=OrderId,
                                         archived=False).all() if companydata else []
    # print("positions", positions,companydata, company)
    return render_template('recruiting.html', data=user, company=company, companydata=companydata, positions=positions,
                           members=members)


from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'mail.geoxhr.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'geoxhrnotifier@geoxhr.com'
app.config['MAIL_PASSWORD'] = 'Upwork123??'

# Specify the default sender email address
app.config['MAIL_DEFAULT_SENDER'] = 'geoxhrnotifier@geoxhr.com'

mail = Mail(app)


@app.route('/marketing', methods=["POST"])
@role_required(allowed_roles=['user', 'admin'])
def marketing():
    if request.method == 'POST':
        id = request.form.get('id')
        user_id = request.form.get('user_id')
        name = request.form.get('name')
        company = request.form.get('company')
        cperson = request.form.get('cperson')
        phone = request.form.get('phone')
        location = request.form.get('location')
        markup = request.form.get('markup')
        jobid = request.form.get('jobid')
        active = 'active'
        job_titles = request.form.getlist('job_title')
        pay_rates = request.form.getlist('pay_rate')
        pay_rate_types = request.form.getlist('pay_rate_type')
        shifts_start = request.form.getlist('shift_start')
        shifts_end = request.form.getlist('shift_end')
        total_vacancies = request.form.getlist('total_vacancies')
        Status = request.form.get('Status')
        other_report = request.form.get('otherreport')
        notes = request.form.get('notes')
        # print(Status, "status")
        formtype = 'New Deals Contract Signed'
        if id is not None:
            entry = db.session.query(Marketing).filter_by(id=id).first()
            entry.company = company
            entry.status = Status
            entry.cperson = cperson
            entry.cphone = phone
            entry.Markup = markup
            entry.location = location
            entry.otherReport = other_report
            entry.Notes = notes
            db.session.add(entry)
            db.session.commit()
            forms = db.session.query(allforms_data).filter_by(form_id=id, form_type=formtype).first()
            forms.belongsto = cperson
            forms.status = Status
            db.session.add(forms)
            db.session.commit()

            for i in range(len(job_titles)):
                if i == 0:
                    # print(i, "length of jobs")
                    updatejob = db.session.query(Joborder).filter(Joborder.company_id == id,
                                                                  Joborder.id == jobid).first()
                    updatejob.job_title = job_titles[i]
                    updatejob.pay_rate = pay_rates[i]
                    updatejob.pay_rate_type = pay_rate_types[i]
                    updatejob.shift_start = shifts_start[i]
                    updatejob.shift_end = shifts_end[i]
                    updatejob.total_vacancy = total_vacancies[i]
                    updatejob.jobstatus = active
                    selected_days = request.form.getlist(f'days-{i + 1}[]')  # Use the unique field name
                    selected_days_str = ', '.join(selected_days)  # or any default value
                    # print("selected_days_strwith0", selected_days_str)

                    # Rest of the code for processing the form data
                    db.session.add(forms)
                    db.session.commit()

                if i >= 1:
                    # print("yess new")
                    job_title = job_titles[i]
                    pay_rate = pay_rates[i]
                    pay_rate_type = pay_rate_types[i]
                    shift_start = shifts_start[i]
                    shift_end = shifts_end[i]
                    total_vacancy = total_vacancies[i]
                    selected_days = request.form.getlist(f'days-{i + 1}[]')  # Use the unique field name
                    selected_days_str = ', '.join(selected_days)
                    # print("selected_days_strwith1", selected_days_str)

                    order = Joborder(user_id=user_id, company_id=id, payrate=pay_rate, salarytype=pay_rate_type,
                                     jobstatus=active,
                                     title=job_title, starttime=shift_start, endtime=shift_end,
                                     vacancy=total_vacancy, days=selected_days_str)
                    db.session.add(order)
                    db.session.commit()


        else:
            # Now, insert the list data
            entry = Marketing(user_id=user_id, name=name, company=company, status=Status, cperson=cperson,
                              company_status=active,
                              cphone=phone, location=location, Markup=markup, otherReport=other_report, Notes=notes)

            db.session.add(entry)
            db.session.commit()

            submitted_id = entry.id
            forms = allforms_data(user_id=user_id, form_id=submitted_id, filledby=name, belongsto=cperson,
                                  form_type=formtype, status=Status)
            db.session.add(forms)
            db.session.commit()

            from datetime import datetime, timedelta

            try:
                today = datetime.today()
                print("today", today)
                days_to_saturday = today.weekday()
                saturday = today - timedelta(days=days_to_saturday)
                friday = saturday + timedelta(days=6)
                weekstart = saturday.strftime("%Y-%m-%d")
                weekend = friday.strftime("%Y-%m-%d")
                print("Week start:", weekstart)
                print("Week end:", weekend)

                target_entry = Targets.query.filter(Targets.user_id == user_id, Targets.weekstart == weekstart,
                                                    Targets.weekend == weekend).all()
                print("Target entry:", target_entry)

                if not target_entry:
                    users = Users.query.filter(Users.designation != 'admin').all()
                    for user in users:
                        target_data = Targets(
                            user_id=user.id,
                            name=f"{user.fname} {user.lname}",
                            new=0,
                            notsigned=0,
                            reopen=0,
                            resume=0,
                            interview=0,
                            placement=0,
                            helping=0,
                            target=0,
                            score=0,
                            weekstart=weekstart,
                            weekend=weekend
                        )
                        db.session.add(target_data)

                    db.session.commit()

                    target_entry = Targets.query.filter(Targets.user_id == user_id, Targets.weekstart == weekstart,
                                                        Targets.weekend == weekend).all()
                    print("Target entry:", target_entry)

                for entry in target_entry:
                    if Status == 'New deal opened and contract signed':
                        entry.new_achieve += 1
                        entry.target_achieve += 1
                        entry.score_achieve += 3
                    elif Status == 'New deal and contract not signed':
                        entry.notsigned_achieve += 1
                        entry.target_achieve += 1
                        entry.score_achieve += 2
                    elif Status == 'Reopened deals':
                        entry.reopen_achieve += 1
                        entry.target_achieve += 1
                        entry.score_achieve += 1

                    print(" entry.achieve_percentage ", entry.achieve_percentage, entry.score, entry.score_achieve)
                    if entry.score_achieve != 0:
                        entry.achieve_percentage = entry.score_achieve / entry.score * 100
                        print(" entry.achieve_percentage1 ", entry.achieve_percentage)
                    else:
                        entry.achieve_percentage = 0  # Avoid division by zero
                        print(" entry.achieve_percentage2 ", entry.achieve_percentage)

                db.session.commit()
                print("Targets updated successfully")

            except Exception as e:
                print(f"Error updating/inserting Targets: {e}")

            for i in range(len(job_titles)):
                job_title = job_titles[i]
                pay_rate = pay_rates[i]
                pay_rate_type = pay_rate_types[i]
                shift_start = shifts_start[i]
                shift_end = shifts_end[i]
                selected_days = request.form.getlist(f'days-{i + 1}[]')
                selected_days_str = ', '.join(selected_days)
                selected_days = request.form.getlist(f'days-{i + 1}[]')  # Use the unique field name
                selected_days_str = ', '.join(selected_days)
                # print(f"Selected days for job {i + 1}: {selected_days_str}")
                total_vacancy = total_vacancies[i]

                order = Joborder(user_id=user_id, company_id=submitted_id, payrate=pay_rate, salarytype=pay_rate_type,
                                 jobstatus=active, title=job_title, starttime=shift_start, endtime=shift_end,
                                 vacancy=total_vacancy, days=selected_days_str)
                # jobstatus = jobstatuss,
                db.session.add(order)
                db.session.commit()

        recipients = ['notify@geoxhr.com ', 'nhoorain161@gmail.com']

        if Status == 'New deal opened and contract signed':
            email_subject = f'''ClickHr:- A new contract signed with {company} filled by {name} '''
            email_body = f'''
                  <!DOCTYPE html>
                  <html>
                  <head>
                       <style>
                          body {{
                              font-family: Arial, sans-serif;
                          }}
                          .container {{
                              background-color: #f2f2f2;
                              padding: 20px;
                              border-radius: 10px;
                          }}
                          .details {{
                              margin-top: 10px;
                          }}
                          .details p {{
                              margin: 0;
                          }}
                          .bold {{
                              font-weight: bold;
                          }}
                          .signature {{
                              margin-top: 20px;
                              font-style: italic;
                              font-size:15px
                          }}
                          .signature p {{
                              margin: 0px;
                              font-style: italic;
                          }}
                          .geoxhr {{
                                 width: 100px;
                                margin-top: 10px;
                          }}
                      </style>
                  </head>
                  <body>
                      <div class="container">
                          <p>Dear Kamran,</p>
                          <p>We're excited to share some progress with you!<br>A fresh agreement has been inked, marking a significant milestone. Dive into the details below:</p>

                          <div class="details">
                              <p><span class="bold">Company Name:</span> {company}</p>
                              <p><span class="bold">FilledBy:</span> {name}</p>
                              <p><span class="bold">Markup:</span> {markup}%</p>
                          </div>

                          {"" if len(job_titles) == 0 else '<p class="bold">Job Titles and Total Vacancies:</p>'}

                          <div class="details">
                              {"" if len(job_titles) == 0 else '<ul>'}
                              {"".join([f'<li> Job Titles: <span class="bold">{job_title}</span>, Total Vacancies: <span class="bold">{vacancy}</span></li>' for i, (job_title, vacancy) in enumerate(zip(job_titles, total_vacancies))])}
                              {"" if len(job_titles) == 0 else '</ul>'}
                          </div>

                          <div class="signature">
                              <p>Best regards,</p>
                              <p>{name}</p>
                              <p>Team GeoxHR</p>
                              <p><img class="geoxhr" src="https://geoxhr.com/wp-content/uploads/2021/10/DragonOurClientLogos1Green-1.png" alt="GeoxHR Logo"></p>
                          </div>
                      </div>
                  </body>
                  </html>
                  '''
        elif Status == 'New deal and contract not signed':
            email_subject = f'''ClickHr:- Heads Up: Form in, contract not signed with {company} filled by {name} '''
            email_body = f'''
                  <!DOCTYPE html>
                  <html>
                  <head>
                       <style>
                          body {{
                              font-family: Arial, sans-serif;
                          }}
                          .container {{
                              background-color: #f2f2f2;
                              padding: 20px;
                              border-radius: 10px;
                          }}
                          .details {{
                              margin-top: 10px;
                          }}
                          .details p {{
                              margin: 0;
                          }}
                          .bold {{
                              font-weight: bold;
                          }}
                          .signature {{
                              margin-top: 20px;
                              font-style: italic;
                              font-size:15px
                          }}
                          .signature p {{
                              margin: 0px;
                              font-style: italic;
                          }}
                          .geoxhr {{
                                 width: 100px;
                                margin-top: 10px;
                          }}
                      </style>
                  </head>
                  <body>
                      <div class="container">
                          <p>Dear Kamran,</p>
                          <p>We're excited to share some progress with you! A fresh agreement has been inked, marking a significant milestone. Dive into the details below:</p>

                          <div class="details">
                              <p><span class="bold">Company Name:</span> {company}</p>
                              <p><span class="bold">FilledBy:</span> {name}</p>
                              <p><span class="bold">Markup:</span> {markup}%</p>
                          </div>

                          {"" if len(job_titles) == 0 else '<p class="bold">Job Titles and Total Vacancies:</p>'}

                          <div class="details">
                              {"" if len(job_titles) == 0 else '<ul>'}
                              {"".join([f'<li> Job Titles: <span class="bold">{job_title}</span>, Total Vacancies: <span class="bold">{vacancy}</span></li>' for i, (job_title, vacancy) in enumerate(zip(job_titles, total_vacancies))])}
                              {"" if len(job_titles) == 0 else '</ul>'}
                          </div>

                          <div class="signature">
                              <p>Best regards,</p>
                              <p>{name}</p>
                              <p>Team GeoxHR</p>
                              <p><img class="geoxhr" src="https://geoxhr.com/wp-content/uploads/2021/10/DragonOurClientLogos1Green-1.png" alt="GeoxHR Logo"></p>
                          </div>
                      </div>
                  </body>
                  </html>
                  '''
        elif Status == 'Reopened deals':
            email_subject = f'''ClickHr:- We have successfully reopened the deal with {company} filled by {name} '''
            email_body = f'''
                  <!DOCTYPE html>
                  <html>
                  <head>
                      <style>
                          body {{
                              font-family: Arial, sans-serif;
                          }}
                          .container {{
                              background-color: #f2f2f2;
                              padding: 20px;
                              border-radius: 10px;
                          }}
                          .details {{
                              margin-top: 10px;
                          }}
                          .details p {{
                              margin: 0;
                          }}
                          .bold {{
                              font-weight: bold;
                          }}
                          .signature {{
                              margin-top: 20px;
                              font-style: italic;
                              font-size:15px
                          }}
                          .signature p {{
                              margin: 0px;
                              font-style: italic;
                          }}
                          .geoxhr {{
                                 width: 100px;
                                margin-top: 10px;
                          }}
                      </style>
                  </head>
                  <body>
                      <div class="container">
                          <p>Dear Kamran,</p>
                          <p>I'm thrilled to announce that after much collaboration and effort, we have successfully reopened the deal with <span class="bold">{company}</span>. This is a testament to our commitment and the hard work of everyone involved. Dive into the details below:</p>

                          <div class="details">
                              <p><span class="bold">Company Name:</span> {company}</p>
                              <p><span class="bold">FilledBy:</span> {name}</p>
                              <p><span class="bold">Markup:</span> {markup}%</p>
                          </div>

                          {"" if len(job_titles) == 0 else '<p class="bold">Job Titles and Total Vacancies:</p>'}

                          <div class="details">
                              {"" if len(job_titles) == 0 else '<ul>'}
                              {"".join([f'<li> Job Titles: <span class="bold">{job_title}</span>, Total Vacancies: <span class="bold">{vacancy}</span></li>' for i, (job_title, vacancy) in enumerate(zip(job_titles, total_vacancies))])}
                              {"" if len(job_titles) == 0 else '</ul>'}
                          </div>

                          <div class="signature">
                              <p>Best regards,</p>
                              <p>{name}</p>
                              <p>Team GeoxHR</p>
                              <p><img class="geoxhr" src="https://geoxhr.com/wp-content/uploads/2021/10/DragonOurClientLogos1Green-1.png" alt="GeoxHR Logo"></p>
                          </div>
                      </div>
                  </body>
                  </html>
                  '''
        else:
            email_subject = 'New Form Submission'

        msg = Message(subject=email_subject, recipients=recipients, html=email_body)
        mail.send(msg)

        response = jsonify({'message': 'success'})
        response.status_code = 200
        return response
    else:
        return "Unsupported method"


@app.route('/hrforms', methods=["POST"])
@role_required(allowed_roles=['user', 'admin'])
def hrforms():
    if request.method == 'POST':
        id = request.form.get('id')
        user_id = request.form.get('user_id')
        name = request.form.get('name')
        candidate = request.form.get('cname')
        late = request.form.get('Late/absent')
        Informed = request.form.get('Informed/uninformed')
        reasonvacation = request.form.get('reasonvacation')
        notes = request.form.get('notes')
        formtype = 'HR Forms'
        status = late + " " + Informed
        if late != 'request for leave':
            reasonvacation = ""
        if id is not None:
            entry = db.session.query(Hrforms).filter_by(id=id).first()
            entry.candidate_name = candidate
            entry.late = late
            entry.informed = Informed
            entry.reason_vacation = reasonvacation
            entry.notes = notes
            db.session.add(entry)
            db.session.commit()
            forms = db.session.query(allforms_data).filter_by(form_id=id, form_type=formtype).first()
            forms.belongsto = candidate
            forms.status = status
        else:
            entry = Hrforms(user_id=user_id, name=name, candidate_name=candidate, late=late, informed=Informed,
                            reason_vacation=reasonvacation, notes=notes)
            db.session.add(entry)
            db.session.commit()
            submitted_id = entry.id

            forms = allforms_data(user_id=user_id, form_id=submitted_id, filledby=name, belongsto=candidate,
                                  form_type=formtype, status=status)
        db.session.add(forms)
        db.session.commit()
        response = jsonify({'message': 'success'})
        response.status_code = 200
        return response
    else:
        return "Unsupported method"


@app.route('/resumesent', methods=["POST"])
@role_required(allowed_roles=['user', 'admin'])
def resumesent():
    if request.method == 'POST':
        formid = request.form.get('formid')
        id = request.form.get('id')
        user_id = request.form.get('user_id')
        name = request.form.get('name')
        candidate = request.form.get('cname')
        phone = request.form.get('cphone')
        position = request.form.get('selected_position')
        did_you = request.form.get('Didyou')
        companydate = request.form.get('companydate')
        relative_file_path = ''
        status = ''
        selected_value = request.form.get('selected_company')
        company_id, company_name = selected_value.split('|')
        interviewdate = request.form.get('interviewdate')
        other_report = request.form.get('Otherreport')
        if did_you == 'Help Another':
            help = request.form.get('help')
            person_starting = request.form.get('person_starting')
            status = did_you
            belongsto_value = help

        elif did_you != 'Help Another':
            help = ''
            person_starting = ''
            status = did_you
            belongsto_value = candidate  # Use 'belongsto_value' instead of 'candidate'

        if did_you == 'Candidate Placement':
            ecname = request.form.get('ecname')
            ecnumber = request.form.get('ecnumber')
            location = request.form.get('Location')
            locationcgoing = request.form.get('clocation')
            starttime = request.form.get('starttime')
            needmember = request.form.get('needteam')
            file = request.files['myFile']
            if file.filename:
                filename = secure_filename(file.filename)
                base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
                image_path = os.path.join(base_dir, 'app', 'static', 'jobimgs')
                os.makedirs(image_path, exist_ok=True)
                relative_file_path = os.path.join('static', 'jobimgs', filename)
                file_path = os.path.join(base_dir, 'app', relative_file_path)
                file.save(file_path)
        elif did_you != 'Candidate Placement':
            file = ""
            ecname = ''
            ecnumber = ''
            location = ''
            locationcgoing = ''
            starttime = ''
            needmember = ''
        notes = request.form.get('notes')
        formtype = 'Person Placement'
        if formid is not None:
            entry = db.session.query(recruiting_data).filter_by(id=formid).first()
            entry.candidate = candidate
            entry.phone = phone
            entry.company = company_name
            entry.did_you = did_you
            entry.ecname = ecname
            entry.ecnumber = ecnumber
            entry.location = location
            entry.locationcgoing = locationcgoing
            entry.starttime = starttime
            entry.needmember = needmember
            entry.interviewdate = interviewdate
            entry.companydate = companydate
            entry.help = help
            entry.person_starting = status
            entry.other_report = other_report
            entry.position = position
            entry.notes = notes
            if file:
                entry.photo = relative_file_path
            db.session.add(entry)
            db.session.commit()

            forms = db.session.query(allforms_data).filter_by(form_id=formid, form_type=formtype).first()
            forms.belongsto = candidate
            forms.status = status
            db.session.add(forms)
            db.session.commit()
            if status == "Candidate Placement":
                with Session() as session:
                    companyy = session.query(Marketing).filter(
                        Marketing.id == company_id
                    ).first()
                    updatevacancy = session.query(Joborder).filter(Joborder.company_id == companyy.id,
                                                                   Joborder.title == position,
                                                                   Joborder.jobstatus == 'active').first()
                    if updatevacancy is not None and updatevacancy.vacancy == 1:
                        updatevacancy.vacancy -= 1
                        updatevacancy.jobstatus = 'inactive'
                        session.add(updatevacancy)
                        session.commit()
                        checkjobs = Joborder.query.filter(Joborder.company_id == companyy.id,
                                                          Joborder.jobstatus == 'active').all()
                        all_vacancies_zero = all(data.vacancy == 0 for data in checkjobs)
                        if all_vacancies_zero:
                            companyinactive = session.query(Marketing).filter(Marketing.id == company_id).first()
                            companyinactive.company_status = 'inactive'
                            session.add(companyinactive)
                            session.commit()
                    else:
                        updatevacancy.vacancy -= 1
                        session.add(updatevacancy)
                        session.commit()
            else:
                hello = "No matching record found for updating vacancy"
            db.session.commit()
            response = jsonify({'message': 'success'})
            response.status_code = 200
            return response
        else:
            entry = recruiting_data(user_id=user_id, name=name, candidate=candidate, phone=phone, company=company_name,
                                    did_you=did_you,
                                    ecname=ecname, ecnumber=ecnumber, location=location, locationcgoing=locationcgoing,
                                    starttime=starttime,
                                    needmember=needmember, photo=relative_file_path, interviewdate=interviewdate,
                                    companydate=companydate, help=help, person_starting=status,
                                    other_report=other_report, position=position, notes=notes)
            db.session.add(entry)
            db.session.commit()
            submitted_id = entry.id
            forms = allforms_data(user_id=user_id, form_id=submitted_id, filledby=name, belongsto=belongsto_value,
                                  form_type=formtype, status=status)
            db.session.add(forms)
            db.session.commit()
            try:
                today = datetime.today()
                print("today", today)
                days_to_saturday = today.weekday()
                saturday = today - timedelta(days=days_to_saturday)
                friday = saturday + timedelta(days=6)
                weekstart = saturday.strftime("%Y-%m-%d")
                weekend = friday.strftime("%Y-%m-%d")
                print("Week start:", weekstart)
                print("Week end:", weekend)

                target_entry = Targets.query.filter(Targets.user_id == user_id, Targets.weekstart == weekstart,
                                                    Targets.weekend == weekend).all()
                print("Target entry:", target_entry)
                if not target_entry:
                    users = Users.query.filter(Users.designation != 'admin').all()
                    for user in users:
                        target_data = Targets(
                            user_id=user.id,
                            name=f"{user.fname} {user.lname}",
                            new=0,
                            notsigned=0,
                            reopen=0,
                            resume=0,
                            interview=0,
                            placement=0,
                            helping=0,
                            target=0,
                            score=0,
                            weekstart=weekstart,
                            weekend=weekend
                        )
                        db.session.add(target_data)

                    db.session.commit()

                    target_entry = Targets.query.filter(Targets.user_id == user_id, Targets.weekstart == weekstart,
                                                        Targets.weekend == weekend).all()
                    print("Target entry:", target_entry)
                for entry in target_entry:
                    if did_you == 'Resume Sent':
                        entry.resume_achieve += 1
                        entry.target_achieve += 1
                        entry.score_achieve += 2
                    elif did_you == 'Interview Scheduled':
                        entry.interview_achieve += 1
                        entry.target_achieve += 1
                        entry.score_achieve += 2
                    elif did_you == 'Candidate Placement':
                        entry.placement_achieve += 1
                        entry.target_achieve += 1
                        entry.score_achieve += 3
                    elif did_you == 'Help Another':
                        entry.helping_achieve += 1
                        entry.target_achieve += 1
                        entry.score_achieve += 1
                    print(" entry.achieve_percentage ", entry.achieve_percentage, entry.score,
                          entry.score_achieve)
                    if entry.score_achieve != 0:
                        entry.achieve_percentage = entry.score_achieve / entry.score * 100
                        print(" entry.achieve_percentage1 ", entry.achieve_percentage)

                    else:
                        entry.achieve_percentage = 0  # Avoid division by zero
                        print(" entry.achieve_percentage2 ", entry.achieve_percentage)

                db.session.commit()
                print("Targets updated successfully")
            except Exception as e:
                print(f"Error updating Targets: {e}")
                pass
            user = db.session.query(Emails_data).filter_by(id=id).first()
            user.status = status
            db.session.add(user)
            db.session.commit()
            if status == "Candidate Placement":
                with Session() as session:  # Start a transaction
                    companyy = session.query(Marketing).filter(
                        Marketing.id == company_id
                    ).first()
                    updatevacancy = session.query(Joborder).filter(Joborder.company_id == companyy.id,
                                                                   Joborder.title == position,
                                                                   Joborder.jobstatus == 'active').first()
                    # updatevacancy = Joborder.query.filter(Joborder.company_id == companyy.id, Joborder.title == position, Joborder.jobstatus == 'active').first()
                    if updatevacancy is not None and updatevacancy.vacancy == 1:
                        updatevacancy.vacancy -= 1
                        updatevacancy.jobstatus = 'inactive'
                        session.add(updatevacancy)

                        session.commit()
                        checkjobs = Joborder.query.filter(Joborder.company_id == companyy.id,
                                                          Joborder.jobstatus == 'active').all()

                        all_vacancies_zero = all(data.vacancy == 0 for data in checkjobs)

                        if all_vacancies_zero:
                            # Perform your action when all vacancy counts are zero
                            companyinactive = session.query(Marketing).filter(Marketing.id == company_id).first()
                            companyinactive.company_status = 'inactive'
                            session.add(companyinactive)
                            session.commit()

                    else:
                        updatevacancy.vacancy -= 1
                        session.add(updatevacancy)

                        session.commit()

                email_subject = f'''ClickHr:- A new Candidate({candidate}) is Placed at company({company_name}) filled by {name} '''
                email_body = f'''
                                 <!DOCTYPE html>
                                 <html>
                                 <head>
                                      <style>
                                         body {{
                                             font-family: Arial, sans-serif;
                                         }}
                                         .container {{
                                             background-color: #f2f2f2;
                                             padding: 20px;
                                             border-radius: 10px;
                                         }}
                                         .details {{
                                             margin-top: 10px;
                                         }}
                                         .details p {{
                                             margin: 0;
                                         }}
                                         .bold {{
                                             font-weight: bold;
                                         }}
                                         .signature {{
                                             margin-top: 20px;
                                             font-style: italic;
                                             font-size:15px
                                         }}
                                         .signature p {{
                                             margin: 0px;
                                             font-style: italic;
                                         }}
                                         .geoxhr {{
                                                width: 100px;
                                               margin-top: 10px;
                                         }}
                                     </style>
                                 </head>
                                 <body>
                                     <div class="container">
                                         <p>Dear Kamran,</p>
                                         <p>We're excited to share some progress with you!<br>A fresh agreement has been inked, marking a significant milestone. Dive into the details below:</p>

                                         <div class="details">
                                            <p><span class="bold">company Name:</span> {company_name}</p>
                                             <p><span class="bold">candidate Name:</span> {candidate}</p>
                                             <p><span class="bold">position:</span> {position}</p>
                                             <p><span class="bold">FilledBy:</span> {name}</p>

                                         </div>

                                         <div class="signature">
                                             <p>Best regards,</p>
                                             <p>{name}</p>
                                             <p>Team GeoxHR</p>
                                             <p><img class="geoxhr" src="https://geoxhr.com/wp-content/uploads/2021/10/DragonOurClientLogos1Green-1.png" alt="GeoxHR Logo"></p>
                                         </div>
                                     </div>
                                 </body>
                                 </html>
                                 '''
                recipients = ['notify@geoxhr.com ', 'nhoorain161@gmail.com']
                msg = Message(subject=email_subject, recipients=recipients, html=email_body)
                mail.send(msg)
            else:
                hello2 = "No matching record found for updating vacancy."
            db.session.commit()
            response = jsonify({'message': 'success'})
            response.status_code = 200
            return response
    else:
        # Handle other HTTP methods, if needed
        return "Unsupported method"


@app.route('/jobs')
@role_required(allowed_roles=['user', 'admin'])
def jobs():
    alljobs = (
        Jobs.query
        .order_by(desc(Jobs.id))
        .all()
    )
    return render_template('jobs.html', alljobs=alljobs)


@app.route('/deletejobs/<int:id>')
@role_required(allowed_roles=['user', 'admin'])
def deletejob(id):
    if id is not None:
        try:
            db.session.query(Jobs).filter(Jobs.id == id).delete()
            db.session.commit()
            # print(f'Successfully deleted job with ID {id}')
            return jsonify({'message': 'Job Deleted!'}), 200
        except Exception as e:
            # print(f'Error deleting job with ID {id}: {str(e)}')
            return jsonify({'message': f'Error job delete: {str(e)}'}), 500


def convert_unix_to_local(timestamp):
    # Convert Unix timestamp to local datetime
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp)


@app.route('/postnewjobs')
@role_required(allowed_roles=['user', 'admin'])
def postnewjobs():
    return render_template('/postnewjobs.html')


@app.route('/selectjob/<int:id>', methods=['POST', 'GET'])
@role_required(allowed_roles=['user', 'admin'])
def selectjob(id):
    if request.method == 'POST':
        jobid = request.form.get('jobid')
        # print(jobid)
        user = db.session.query(Emails_data).filter_by(id=id).first()
        jobdata = db.session.query(Jobs).filter_by(id=jobid).first()
        return render_template('recruiting.html', data=user, jobdata=jobdata)
    else:
        alljobs = Jobs.query.all()
        return render_template('jobs.html', alljobs=alljobs, id=id)


@app.route('/editjob/<int:id>')
@role_required(allowed_roles=['user', 'admin'])
def editjob(id):
    job = db.session.query(Jobs).filter(Jobs.id == id).first()
    return render_template('postnewjobs.html', job=job)

@app.route('/newposition')
@role_required(allowed_roles=['user', 'admin'])
def newposition():
    return render_template('newposition.html')

@app.route('/digital-onboarding', methods=["GET", "POST"])
def digitalonboarding():
    return render_template('digital-onboarding.html')

@app.route('/holderdetails/<int:id>')
def holderdetails(id):
    data = db.session.query(accounts).filter(accounts.id == id).first()

    # Encode blob data to Base64 for rendering in HTML
    id_front_image = b64encode(data.id_front_blob).decode("utf-8") if data.id_front_blob else None
    id_back_image = b64encode(data.id_back_blob).decode("utf-8") if data.id_back_blob else None
    selfie_image = b64encode(data.selfie_blob).decode("utf-8") if data.selfie_blob else None

    return render_template('holderdetails.html', data=data, id_front_image=id_front_image,
                           id_back_image=id_back_image, selfie_image=selfie_image)

@app.route('/applyaccount')
def applyaccount():
    return render_template('apply.html')





@app.route('/applyforaccount', methods=["GET", "POST"])
def applyforaccount():
    if request.method == 'POST':
        # Retrieve form data
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        sphone = request.form.get('sphone')
        birth_day = request.form.get('birthDay')
        birth_month = request.form.get('birthMonth')
        birth_year = request.form.get('birthYear')
        birth_date = f"{birth_day} - {birth_month} - {birth_year}"
        province = request.form.get('province')
        tin = request.form.get('tin')
        street = request.form.get('streetAddress')
        city = request.form.get('city')
        postalCode = request.form.get('postalCode')
        residential = request.form.get('residential')
        gross = request.form.get('gross')
        sourceOfIncome = request.form.get('sourceOfIncome')
        empStatus = request.form.get('employmentStatus')
        jobOccupation = request.form.get('jobOccupation')
        appointtime = request.form.get('appointtime')
        appointdate = request.form.get('appointdate')
        Locations = request.form.get('Locations')
        id_front = request.files['upload1']
        id_back = request.files['upload2']
        selfie = request.files['selfie']

        # Convert files to blob data
        id_front_blob = id_front.read()
        id_back_blob = id_back.read()
        selfie_blob = selfie.read()

        # Print form data
        print("First Name:", fname)
        print("Last Name:", lname)
        print("Email:", email)
        print("Birth Date:", birth_date)
        print("Primary Phone:", phone)
        print("Secondary Phone:", sphone)
        print("Position:", province)
        print("TIN:", tin)
        print("Street Address:", street)
        print("City:", city)
        print("Postal Code:", postalCode)
        print("Residential Status:", residential)
        print("Gross Annual Income:", gross)
        print("Source of Income:", sourceOfIncome)
        print("Employment Status:", empStatus)
        print("Occupation:", jobOccupation)
        print("Appointment Time:", appointtime)
        print("Appointment Date:", appointdate)
        print("Location:", Locations)

        # Check if the entry exists
        entry = db.session.query(accounts).filter_by(email=email).first()

        if entry:
            # Update existing entry
            entry.fname = fname
            entry.lname = lname
            entry.birth_date = birth_date
            entry.phone = phone
            entry.sphone = sphone
            entry.province = province
            entry.tin = tin
            entry.street = street
            entry.city = city
            entry.pc = postalCode
            entry.res = residential
            entry.gross = gross
            entry.sInc= sourceOfIncome
            entry.empstatus = empStatus
            entry.occ = jobOccupation
            entry.aptime = appointtime
            entry.apdate = appointdate
            entry.branch = Locations
            entry.id_front_blob = id_front_blob
            entry.id_back_blob = id_back_blob
            entry.selfie_blob = selfie_blob
        else:
            # Create new entry
            entry = accounts(fname=fname, lname=lname, email=email, birth_date=birth_date, phone=phone,
                             sphone=sphone, province=province, tin=tin, street=street, city=city, pc=postalCode,
                             res=residential, gross=gross, sInc=sourceOfIncome, empstatus=empStatus, occ=jobOccupation,
                             aptime=appointtime, apdate=appointdate, branch=Locations,id_front_blob=id_front_blob, id_back_blob=id_back_blob, selfie_blob=selfie_blob)

        db.session.add(entry)
        db.session.commit()
        response = jsonify({'message': 'success'})
        response.status_code = 200
        return response
    else:

     return redirect('/digital-onboarding')


@app.route('/onboradingdetails')
@role_required(allowed_roles=['user', 'admin'])
def onboradingdetails():
    return render_template('onboradingdetails.html')

@app.route('/subdetails')
@role_required(allowed_roles=['user', 'admin'])
def subdetails():
    accuser_data = accounts.query.order_by(desc(accounts.id)).all()
    print(accuser_data)
    return render_template('subdetails.html',accuser_data=accuser_data)


@app.route('/postjob', methods=['POST'])
@role_required(allowed_roles=['user', 'admin'])
def postjob():
    if request.method == 'POST':

        id = request.form.get('id')
        title = request.form.get('title')
        name = request.form.get('name')
        selected_companies = request.form.getlist('company_name')
        user_id = request.form.get('user_id')
        location = request.form.get('location')
        experience = request.form.get('experience')
        JobType = request.form.get('Job-Type')
        duration = request.form.get('duration')
        onsite = request.form.get('onsite')
        salarytypes = request.form.get('salarytypes')
        Salary = request.form.get('Salary')
        date = request.form.get('date')
        job_status = request.form.get('active')
        description = request.form.get('description')
        responsibility = request.form.get('responsibility')
        eligibility = request.form.get('eligibility')
        notes = request.form.get('notes')
        print(selected_companies, "company")

        if "Geox hr" in selected_companies and "Hands hr" in selected_companies and "i8is" in selected_companies:
            company_code = "123"
        elif "Geox hr" in selected_companies and "Hands hr" in selected_companies:
            company_code = "12"
        elif "i8is" in selected_companies and "Hands hr" in selected_companies:
            company_code = "23"
        elif "i8is" in selected_companies and "Geox hr" in selected_companies:
            company_code = "13"
        elif "Geox hr" in selected_companies:
            company_code = "1"
        elif "Hands hr" in selected_companies:
            company_code = "2"
        elif "i8is" in selected_companies:
            company_code = "3"
        else:
            company_code = ""

        print(company_code)
        file = request.files['myFile']
        if file.filename:
            filename = secure_filename(file.filename)

            # Get the base directory of the app
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

            # Create the directory 'static/jobimgs' if it doesn't exist
            image_path = os.path.join(base_dir, 'app', 'static', 'jobimgs')
            os.makedirs(image_path, exist_ok=True)

            # Append the desired filename to the image_path
            relative_file_path = os.path.join('static', 'jobimgs', filename)

            # Save the file with the specified name in the 'static/jobimgs' folder
            file_path = os.path.join(base_dir, 'app', relative_file_path)
            file.save(file_path)
        else:
            relative_file_path = ''

        if id is not None:
            entry = db.session.query(Jobs).filter_by(id=id).first()
            entry.title = title
            entry.company = company_code
            entry.experience = experience
            entry.location = location
            entry.job_type = JobType
            entry.duration = duration
            entry.onsite = onsite
            entry.salary_type = salarytypes
            entry.salary = Salary
            entry.job_date = date
            entry.job_status = job_status
            entry.description = description
            entry.responsibility = responsibility
            entry.eligibility = eligibility
            entry.notes = notes
            if file.filename:
                entry.image = relative_file_path
        else:
            entry = Jobs(user_id=user_id, name=name, title=title, image=relative_file_path, company=company_code,
                         location=location,
                         job_type=JobType, duration=duration, onsite=onsite, salary_type=salarytypes, salary=Salary,
                         job_date=date, job_status=job_status, description=description, responsibility=responsibility,
                         eligibility=eligibility, experience=experience,
                         notes=notes)
        db.session.add(entry)
        db.session.add(entry)
        db.session.commit()
        response = jsonify({'message': 'success'})
        response.status_code = 200
        return response
    else:
        return "Unsupported method"


#####jobs end


from flask import request


@app.route('/jobOders')
@role_required(allowed_roles=['user', 'admin'])
def jobOders():
    page = request.args.get('page', default=1, type=int)
    per_page = 10
    show_archived = request.args.get('show_archived', type=int)
    if show_archived:
        jobs_orders = db.session.query(Joborder).filter(Joborder.archived == True).order_by(desc(Joborder.id)).paginate(page=page, per_page=per_page)
    else:
        jobs_orders = db.session.query(Joborder).filter(Joborder.archived == False).order_by(desc(Joborder.id)).paginate(page=page, per_page=per_page)

    total_pages = jobs_orders.pages
    start_page = max(1, page - 5)
    end_page = min(total_pages, start_page + 10)

    marketing_entries = db.session.query(Marketing).all()
    company_name_dict = {entry.id: entry.company for entry in marketing_entries}
    for job_order in jobs_orders.items:
        company_id = job_order.company_id
        if company_id in company_name_dict:
            job_order.company = company_name_dict[company_id]

    action = 'Interested'
    alldata = Emails_data.query.filter(Emails_data.action == action).order_by(desc(Emails_data.id)).all()

    return render_template('jobsorder.html', jobsorder=jobs_orders, alldata=alldata, page=page, total_pages=total_pages,
                           start_page=start_page, end_page=end_page)


@app.route('/Companies')
@role_required(allowed_roles=['user', 'admin'])
def Companies():
    page = request.args.get('page', default=1, type=int)
    per_page = 50
    companies = Marketing.query.all()
    total_records = len(companies)
    total_pages = ceil(total_records / per_page)
    start_page = max(1, page - 5)
    end_page = min(total_pages, start_page + 10)
    return render_template('/jobsorder.html',companies=companies,page=page, total_pages=total_pages,
                           start_page=start_page, end_page=end_page)


@app.route('/archive_jobs', methods=['POST'])
def archive_jobs():
    selected_job_ids = [int(job_id) for job_id in request.form.getlist('selected_jobs[]')]
    print("Selected Job IDs:", selected_job_ids)  # Print the list of selected job IDs for debugging purposes

    for job_id in selected_job_ids:
        job = Joborder.query.get(job_id)
        if job:
            print(job)
            if job.archived:  # If job is archived, unarchive it
                job.archived = False
            else:  # If job is not archived, archive it
                job.archived = True
            db.session.commit()  # Commit the changes to the database

    return redirect(url_for('jobOders'))

@app.route('/archive_companies', methods=['POST'])
def archive_companies():
    selected_company_ids = [int(company_id) for company_id in request.form.getlist('selected_company[]')]
    print("Selected Job IDs:", selected_company_ids)  # Print the list of selected job IDs for debugging purposes

    for company_id in selected_company_ids:
        company = Marketing.query.get(company_id)
        if company:
            print(company)
            if company.company_status == "active":  # If job is archived, unarchive it
                company.company_status = "inactive"
            else:  # If job is not archived, archive it
                company.company_status = "active"
            db.session.commit()  # Commit the changes to the database

    return redirect(url_for('Companies'))


@app.route('/position', methods=['POST'])
@role_required(allowed_roles=['user', 'admin'])
def position():
    data = request.get_json()
    selectedOption = data.get('companyId')
    # print(selectedOption)
    positions = Joborder.query.filter(
        and_(Joborder.company_id == selectedOption, Joborder.jobstatus == 'active', Joborder.archived == False)).all()
    positions_list = [{'position_name': position.title} for position in positions]

    return jsonify({'positions': positions_list})


@app.route('/otherfinal', methods=["POST"])
@role_required(allowed_roles=['user', 'admin'])
def otherfinal():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        name = request.form.get('name')
        otherreport = request.form.get('otherreport')
        notes = request.form.get('notes')
        formtype = 'Other Final'
        status = "Other Report"
        candidate = "-"
        id = request.form.get('id')
        if id is not None:
            entry = db.session.query(Otherfinal).filter_by(id=id).first()
            entry.other_report = otherreport
            entry.notes = notes
            db.session.add(entry)
            db.session.commit()
        else:

            entry = Otherfinal(user_id=user_id, name=name, other_report=otherreport, notes=notes)

            db.session.add(entry)
            db.session.commit()
            submitted_id = entry.id

            forms = allforms_data(user_id=user_id, form_id=submitted_id, filledby=name, belongsto=candidate,
                                  form_type=formtype, status=status)
            db.session.add(forms)
            db.session.commit()
        response = jsonify({'message': 'success'})
        response.status_code = 200
        return response
    else:
        # Handle other HTTP methods, if needed
        return "Unsupported method"


@app.route('/forms')
@role_required(allowed_roles=['user', 'admin'])
def forms():
    page = request.args.get('page', default=1, type=int)
    per_page = 100

    if session['role'] == 'admin':
        total_records = db.session.query(allforms_data).count()
    elif session['role'] == 'user':
        user_id = session['user_id']
        total_records = db.session.query(allforms_data).filter(allforms_data.user_id == user_id).count()

    total_pages = ceil(total_records / per_page)
    start_page = max(1, page - 5)
    end_page = min(total_pages, start_page + 10)

    if session['role'] == 'admin':
        alldata = (
            allforms_data.query
            .order_by(desc(allforms_data.id))
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )
    elif session['role'] == 'user':
        user_id = session['user_id']
        alldata = (
            allforms_data.query
            .filter(allforms_data.user_id == user_id)
            .order_by(desc(allforms_data.id))
            .offset((page - 1) * per_page)
            .limit(per_page)
            .all()
        )

    alldata_with_marketing_or_recruiting = []
    for data in alldata:
        marketing = (
            Marketing.query
            .filter(Marketing.id == data.form_id, Marketing.name == data.filledby)
            .first()
        )
        if marketing:
            alldata_with_marketing_or_recruiting.append((data, marketing))
        else:
            recruiting = (
                recruiting_data.query
                .filter(recruiting_data.id == data.form_id, recruiting_data.name == data.filledby)
                .first()
            )
            if recruiting:
                alldata_with_marketing_or_recruiting.append((data, recruiting))
            else:
                otherfinal = (
                    Otherfinal.query
                    .filter(Otherfinal.id == data.form_id, Otherfinal.name == data.filledby)
                    .first()
                )
                if otherfinal:
                    alldata_with_marketing_or_recruiting.append((data, otherfinal))
                else:
                    hrforms = (
                        Hrforms.query
                        .filter(Hrforms.id == data.form_id, Hrforms.name == data.filledby)
                        .first()
                    )
                    if hrforms:
                        alldata_with_marketing_or_recruiting.append((data, hrforms))

    return render_template(
        'forms.html',
        alldata_with_marketing_or_recruiting=alldata_with_marketing_or_recruiting,
        page=page,
        total_pages=total_pages,
        start_page=start_page,
        end_page=end_page
    )





@app.route('/onereporting')
@app.route('/OneReportingForm')
@role_required(allowed_roles=['user', 'admin'])
def OneReportingForm():
    companies = Marketing.query.filter(Marketing.company_status == 'active').all()

    # Convert each Marketing object to a dictionary representation
    company_data = []
    for company in companies:
        company_dict = {
            'id': company.id,
            'company_name': company.company,
            'contact_person': company.cperson,
            'contact_person_name': company.cphone,
            # Add more attributes as needed
        }
        company_data.append(company_dict)

    return render_template('/onereporting-form.html', company=company_data,companies=companies)


@app.route('/getregistered')
def getregistered(data=None):
    return render_template('getregistered.html', data=data)


UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/addnewemployeetodata', methods=['POST'])
def addnewemployeetodata():
    if request.method == 'POST':
        sender_name = request.form.get('candidate_name')
        email = request.form.get('email')
        current_date = request.form.get('date')
        phone = request.form.get('phone_number')
        description = request.form.get('description')
        uploaded_file = request.files['myFile']
        new_password = request.form.get('newps')
        confirm_password = request.form.get('confirmpswrd')
        # print(confirm_password,"asdfsd")
        if new_password == confirm_password:
            if new_password is not None:
                existing_login = candidateLogin.query.filter_by(email=email).first()
                if existing_login:
                    response = jsonify({'message': 'Email already exists'})
                    response.status_code = 400
                    return response
                else:
                    new_login = candidateLogin(email=email, password=confirm_password)
                    db.session.add(new_login)
                    db.session.commit()
                    email_subject = "Registration Successful on Geox HR!"
                    email_body = f'''
                                                             <!DOCTYPE html>
                                                             <html>
                                                             <head>
                                                                  <style>
                                                                     body {{
                                                                         font-family: Arial, sans-serif;
                                                                     }}
                                                                     .container {{
                                                                         background-color: #f2f2f2;
                                                                         padding: 20px;
                                                                         border-radius: 10px;
                                                                     }}
                                                                     .details {{
                                                                         margin-top: 10px;
                                                                     }}
                                                                     .details p {{
                                                                         margin: 0;
                                                                     }}
                                                                     .bold {{
                                                                         font-weight: bold;
                                                                     }}
                                                                     .signature {{
                                                                         margin-top: 20px;
                                                                         font-style: italic;
                                                                         font-size:15px
                                                                     }}
                                                                     .signature p {{
                                                                         margin: 0px;
                                                                         font-style: italic;
                                                                     }}
                                                                     .geoxhr {{
                                                                            width: 100px;
                                                                           margin-top: 10px;
                                                                     }}
                                                                 </style>
                                                             </head>
                                                             <body>
                                                                 <div class="container">
                                                                     <p>Hello {sender_name},</p>
                                                                     <p>Congratulations! Your registration on <span class="bold">GeoxHR</span> has been successfully completed. We're thrilled to have you onboard.</p>

                                                                     <p> Access Your Account:
                                                                          To sign in and manage your profile, simply click on the link below:
                                                                           <a href="http://15.156.80.22:8000/candidate_login">Sign In to Your Account </a></p>

                                                                     <p> Track Your Application Status:
                                                                          Stay in the loop! Log in anytime to check the status of your application and stay updated on the progress.We've made it easy for you to track each step from application submission to placement.
                                                                         </p>
                                                                     <p>We're committed to connecting you with the best opportunities that align with your skills and aspirations. If you have any questions or require assistance, please don't hesitate to reach out.</p>   
                                                                     <p>Wishing you success in your career journey!</p>

                                                                     <div class="signature">
                                                                         <p>Warm Regards,,</p>
                                                                         <p>The GeoxHR Team</p>
                                                                         <p>Email:geoxhrnotifier@geoxhr.com</p>
                                                                         <p><img class="geoxhr" src="https://geoxhr.com/wp-content/uploads/2021/10/DragonOurClientLogos1Green-1.png" alt="GeoxHR Logo"></p>
                                                                     </div>
                                                                 </div>
                                                             </body>
                                                             </html>
                                                             '''
                    recipients = [email, 'nhoorain161@gmail.com']
                    msg = Message(subject=email_subject, recipients=recipients, html=email_body)
                    mail.send(msg)
        else:
            response = jsonify({'message': 'Passwords do not match'})
            response.status_code = 400
            return response
        if uploaded_file:
            if '.' in uploaded_file.filename and uploaded_file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                filename = secure_filename(uploaded_file.filename)
                file_content = uploaded_file.read()  # Read the PDF file content
            else:
                response = jsonify({'message': 'Invalid file extension'})
                response.status_code = 400  # Bad Request
                return response
        else:
            filename = "manually"
            file_content = None

        apply = Emails_data(
            sender_name=sender_name,
            email=email,
            phone_number=phone,
            subject_part2=description,
            formatted_date=current_date,
            file_name=filename,
            file_content=file_content,
            pdf_content_json=None,
            subject_part1='registered from Geox hr',
            action=""

        )

        db.session.add(apply)
        db.session.commit()

        response = jsonify({'message': 'success'})
        response.status_code = 200
        return response
    else:
        return redirect('/getregistered')


@app.route('/addmanualemployee')
@role_required(allowed_roles=['user', 'admin'])
def addmanualemployee(data=None):
    return render_template('addnewemployee.html', data=data)


@app.route('/addmanualemployeetodata', methods=['POST'])
@role_required(allowed_roles=['user', 'admin'])
def addmanualemployeetodata():
    if request.method == 'POST':
        sender_name = request.form.get('candidate_name')
        email = request.form.get('email')
        current_date = request.form.get('date')
        phone = request.form.get('phone_number')
        description = request.form.get('description')
        uploaded_file = request.files['myFile']
        if uploaded_file:
            if '.' in uploaded_file.filename and uploaded_file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
                filename = secure_filename(uploaded_file.filename)
                file_content = uploaded_file.read()  # Read the PDF file content
            else:
                response = jsonify({'message': 'Invalid file extension'})
                response.status_code = 400  # Bad Request
                return response
        else:
            filename = "manually"
            file_content = None

        apply = Emails_data(
            sender_name=sender_name,
            email=email,
            phone_number=phone,
            subject_part2=description,
            formatted_date=current_date,
            file_name=filename,
            file_content=file_content,  # Store the file content as BLOB
            pdf_content_json=None,  # You can handle PDF content as needed
            subject_part1='manually',
            action="Interested"
        )

        db.session.add(apply)
        db.session.commit()

        response = jsonify({'message': 'success'})
        response.status_code = 200
        return response
    else:
        return redirect('/addmanualemployee')


@app.route('/view/<int:form_id>/<string:form_type>')
@role_required(allowed_roles=['user', 'admin'])
def view(form_id, form_type):
    type = 'view'
    if form_type == 'New Deals Contract Signed':
        formdata = Marketing.query.filter(Marketing.id == form_id).first()
        jobsdata = Joborder.query.filter(Joborder.company_id == form_id).all()
        # print(*jobsdata)
        return render_template('marketing.html', type=type, formdata=formdata, jobsdata=jobsdata)
    elif form_type == 'Person Placement':
        formdata = recruiting_data.query.filter(recruiting_data.id == form_id).first()
        company = Marketing.query.all()
        return render_template('recruiting.html', type=type, formdata=formdata, company=company)
    elif form_type == 'HR Forms':
        formdata = Hrforms.query.filter(Hrforms.id == form_id).first()
        return render_template('hrforms.html', type=type, formdata=formdata)
    elif form_type == 'Other Final':
        formdata = Otherfinal.query.filter(Otherfinal.id == form_id).first()
        return render_template('otherreport.html', type=type, formdata=formdata)


@app.route('/editforms/<int:form_id>/<string:form_type>')
@role_required(allowed_roles=['user', 'admin'])
def editforms(form_id, form_type):
    type = 'edit'
    if form_type == 'New Deals Contract Signed':
        formdata = Marketing.query.filter(Marketing.id == form_id).first()
        jobsdata = Joborder.query.filter(Joborder.company_id == form_id).all()
        return render_template('marketing.html', type=type, formdata=formdata, jobsdata=jobsdata)
    elif form_type == 'Person Placement':
        formdata = recruiting_data.query.filter(recruiting_data.id == form_id).first()
        company = Marketing.query.all()
        return render_template('recruiting.html', type=type, formdata=formdata, company=company)
    elif form_type == 'HR Forms':
        formdata = Hrforms.query.filter(Hrforms.id == form_id).first()
        return render_template('hrforms.html', type=type, formdata=formdata)
    elif form_type == 'Other Final':
        formdata = Otherfinal.query.filter(Otherfinal.id == form_id).first()
        return render_template('otherreport.html', type=type, formdata=formdata)


@app.route('/candidate_login')
def candidate_login():
    return render_template("candidate_login.html")


@app.route('/logincandidate', methods=['GET', 'POST'])
def logincandidate():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = candidateLogin.query.filter_by(email=email).first()
        if user and user.password == password:
            return redirect(url_for('viewhistory', email=email))
        else:
            return render_template('candidate_login.html', msg="Invalid credentials")

    return render_template('candidate_login.html')


@app.route('/viewhistory/<string:email>')
def viewhistory(email):
    with db.session() as session:
        alldata = session.query(Emails_data).filter(Emails_data.email == email).order_by(
            desc(Emails_data.created_at)).all()
        sender_name = session.query(Emails_data.sender_name).filter(Emails_data.email == email).first()
        if sender_name:
            sender_name = sender_name[0]
            recruiting = session.query(recruiting_data).filter(recruiting_data.candidate == sender_name).all()
        else:
            recruiting = []
    # return render_template('forcandidate_view.html', alldata=alldata, recruiting=recruiting)
    return render_template('viewhistory.html', alldata=alldata, recruiting=recruiting)


@app.route('/deleteform/<int:form_id>/<string:form_type>', methods=['POST'])
@role_required(allowed_roles=['user', 'admin'])
def deleteform(form_id, form_type):
    try:
        db.session.query(allforms_data).filter(allforms_data.form_id == form_id,
                                               allforms_data.form_type == form_type).delete()
        db.session.commit()

        if form_type == 'New Deals Contract Signed':
            db.session.query(Marketing).filter(Marketing.id == form_id).delete()
        elif form_type == 'Person Placement':
            db.session.query(recruiting_data).filter(recruiting_data.id == form_id).delete()
        elif form_type == 'HR Forms':
            db.session.query(Hrforms).filter(Hrforms.id == form_id).delete()
        elif form_type == 'Other Final':
            db.session.query(Otherfinal).filter(Otherfinal.id == form_id).delete()

        db.session.commit()
        return jsonify({'message': 'Form Deleted!'}), 200
    except Exception as e:
        return jsonify({'message': f'Error deleting form: {str(e)}'}), 500


@app.route('/target')
@role_required(allowed_roles=['user', 'admin'])
def target():
    user_id = session['user_id']
    role = session['role']

    if role == 'user':
        members_data = Targets.query.filter(Targets.user_id == user_id).order_by(desc(Targets.id)).all()
    else:
        members_data = Targets.query.order_by(desc(Targets.id)).all()

    # Iterate over each item in members_data
    for member in members_data:
        print(member.new_achieve, "members_data")

    return render_template('/target.html', members_data=members_data)


@app.route('/addtarget')
@role_required(allowed_roles=['user', 'admin'])
def addtarget():
    members_data = Users.query.filter(Users.designation != 'admin').order_by(desc(Users.id)).all()
    score_data = score_board.query.all()
    return render_template('/addtarget.html', members_data=members_data, score_data=score_data)


@app.route('/edit_target')
def edit_target():
    selected_week = request.args.get('selectedWeek')
    selected_week_data = Targets.query.filter(Targets.weekstart == selected_week).order_by(desc(Targets.id)).all()
    print("Selected Week:", selected_week, selected_week_data)

    return render_template('/addtarget.html', selected_week_data=selected_week_data)


@app.route('/resettarget', methods=['POST'])
def resettarget():
    if request.method == 'POST':
        ids = request.form.getlist('id')
        weekstart = request.form.getlist('weekstart')
        weekend = request.form.getlist('weekend')
        user_ids = request.form.getlist('user_id')
        names = request.form.getlist('name')
        news = request.form.getlist('new')
        notsigneds = request.form.getlist('notsigned')
        reopens = request.form.getlist('reopen')
        resumes = request.form.getlist('resume')
        interviews = request.form.getlist('interview')
        placements = request.form.getlist('placement')
        helpings = request.form.getlist('helping')
        targets = request.form.getlist('target')
        scores = request.form.getlist('score')
        blue = 3
        green = 2
        yellow = 1
        print("Lengths:", len(user_ids), len(names), len(news), len(notsigneds), len(reopens), len(resumes),
              len(interviews), len(placements), len(helpings), len(targets), len(scores))
        print("User IDs:", user_ids)
        print("Names:", names)

        print("Week start:", ids, weekstart, weekend, user_ids, names, news)
        print(weekstart, weekend)
        for i in range(len(user_ids)):
            id = int(ids[i])  # Convert id to integer
            user_id = user_ids[i]
            name = names[i]
            new = int(news[i]) if news[i] else 0
            notsigned = int(notsigneds[i]) if notsigneds[i] else 0
            reopen = int(reopens[i]) if reopens[i] else 0
            resume = int(resumes[i]) if resumes[i] else 0
            interview = int(interviews[i]) if interviews[i] else 0
            placement = int(placements[i]) if placements[i] else 0
            helping = int(helpings[i]) if helpings[i] else 0
            target = new + notsigned + reopen + resume + interview + placement + helping
            score = new * blue + notsigned * green + reopen * yellow + resume * green + interview * green + placement * blue + helping * yellow
            print(type(new), "type")

            # Use update method
            weekstart_date = datetime.strptime(weekstart[i], '%Y-%m-%d %H:%M:%S').date()
            weekend_date = datetime.strptime(weekend[i], '%Y-%m-%d %H:%M:%S').date()

            # Use update method
            Targets.query.filter(
                and_(
                    Targets.id == id,
                    Targets.user_id == user_id,
                    Targets.weekstart == weekstart_date,
                    Targets.weekend == weekend_date
                )
            ).update(
                {
                    "new": new,
                    "notsigned": notsigned,
                    "reopen": reopen,
                    "resume": resume,
                    "interview": interview,
                    "placement": placement,
                    "helping": helping,
                    "target": target,
                    "score": score
                }
            )

        db.session.commit()
        response = jsonify({'message': 'success'})
        response.status_code = 200
        return response
    else:
        return redirect('/target')


@app.route('/savetarget', methods=['POST'])
def savetarget():
    if request.method == 'POST':
        user_ids = request.form.getlist('user_id')
        names = request.form.getlist('name')
        news = request.form.getlist('new')
        notsigneds = request.form.getlist('notsigned')
        reopens = request.form.getlist('reopen')
        resumes = request.form.getlist('resume')
        interviews = request.form.getlist('interview')
        placements = request.form.getlist('placement')
        helpings = request.form.getlist('helping')
        targets = request.form.getlist('target')
        scores = request.form.getlist('score')
        blue = 3
        green = 2
        yellow = 1
        print("Lengths:", len(user_ids), len(names), len(news), len(notsigneds), len(reopens), len(resumes),
              len(interviews), len(placements), len(helpings), len(targets), len(scores))
        print("User IDs:", user_ids)
        print("Names:", names)

        today = datetime.today()
        print("today", today)
        days_to_saturday = today.weekday()
        saturday = today - timedelta(days=days_to_saturday)
        friday = saturday + timedelta(days=6)
        weekstart = saturday.strftime("%Y-%m-%d")
        weekend = friday.strftime("%Y-%m-%d")
        print("Week start:", weekstart)
        print("Week end:", weekend)

        print(weekstart, weekend)
        for i in range(len(user_ids)):
            user_id = user_ids[i]
            name = names[i]
            new = int(news[i]) if news[i] else 0
            notsigned = int(notsigneds[i]) if notsigneds[i] else 0
            reopen = int(reopens[i]) if reopens[i] else 0
            resume = int(resumes[i]) if resumes[i] else 0
            interview = int(interviews[i]) if interviews[i] else 0
            placement = int(placements[i]) if placements[i] else 0
            helping = int(helpings[i]) if helpings[i] else 0
            target = new + notsigned + reopen + resume + interview + placement + helping
            score = new * blue + notsigned * green + reopen * yellow + resume * green + interview * green + placement * blue + helping * yellow
            print(type(new), "type")
            existing_entry = Targets.query.filter_by(
                user_id=user_id,
                weekstart=weekstart,
                weekend=weekend
            ).first()

            if existing_entry:
                # Update existing entry
                existing_entry.new = new
                existing_entry.notsigned = notsigned
                existing_entry.reopen = reopen
                existing_entry.resume = resume
                existing_entry.interview = interview
                existing_entry.placement = placement
                existing_entry.helping = helping
                existing_entry.target = target
                existing_entry.score = score
            else:
                # Add new entry
                target_data = Targets(
                    user_id=user_id,
                    name=name,
                    new=new,
                    notsigned=notsigned,
                    reopen=reopen,
                    resume=resume,
                    interview=interview,
                    placement=placement,
                    helping=helping,
                    target=target,
                    score=score,
                    weekstart=weekstart,
                    weekend=weekend
                )
                db.session.add(target_data)

        db.session.commit()
        # Now, retrieve emails based on the user_ids
        user_emails = Users.query.filter(Users.id.in_(user_ids), Users.designation != 'admin').with_entities(
            Users.email).all()

        # Extract the emails from the query result
        emails = [email[0] for email in user_emails]
        print(emails)
        recipients = ['nhoorain161@gmail.com', 'notify@geoxhr.com']
        recipients2 = emails
        user_name = session['user']
        user_email = session['email']

        try:
            user_name = session['user']
            user_email = session['email']
            email_subject = f'''ClickHr:- A new Weekly Target is set filled by {user_name} '''
            email_body = f'''
                               <!DOCTYPE html>
                               <html>
                               <head>
                                   <style>
            body {{
                font-family: 'Arial', sans-serif;
                background-color: #f0f0f0;
                margin: 0;
                padding: 0; 
            }}
            .container {{
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                overflow: hidden;
                margin: 15px 0px;
                padding: 20px;
                max-width: 800px;
            }}
            .header {{
                background-color: #007bff;
                color: #ffffff;
                padding: 10px;
                text-align: center;
                border-radius: 10px 10px 0 0;
            }}
            h2 {{
                margin: 0;
            }}
            p {{
                margin: 10px 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
            }}
            th, td {{
                border: 1px solid #dddddd;
                text-align:center;
                padding:3px;
            }}
            th {{
                background-color: #f2f2f2;
            }}
            .signature {{
                margin-top: 20px;
                font-style: italic;
                font-size: 15px;
            }}
            .geoxhr {{
                width: 100px;
                margin-top: 10px;
            }}
        </style>
                               </head>
                               <body>
                                   <div class="container">
                                       <p>Dear Kamran,</p>
                                       <p>I hope this email finds you well. I wanted to inform you that weekly tasks have been assigned to our users for the current week. This includes a breakdown of tasks for each user to ensure clarity and accountability.Dive into the details below:</p>

                                       <table id="targetTable">
                                           <tr>
                                               <th>Name</th>
                                               <th>New Contrat</th>
                                               <th>Not signed</th>
                                               <th>ReopenDeals</th>
                                               <th>ResumeSents</th>
                                               <th>Interviews</th>
                                               <th>Placements</th>
                                               <th>Helpings</th>
                                               <th>Total</th>
                                           </tr>
                               '''
            for i in range(len(user_ids)):
                new_target = int(news[i]) if news[i] else 0
                notsigned_target = int(notsigneds[i]) if notsigneds[i] else 0
                reopen_target = int(reopens[i]) if reopens[i] else 0
                resume_target = int(resumes[i]) if resumes[i] else 0
                interview_target = int(interviews[i]) if interviews[i] else 0
                placement_target = int(placements[i]) if placements[i] else 0
                helping_target = int(helpings[i]) if helpings[i] else 0

                target = new_target + notsigned_target + reopen_target + resume_target + interview_target + placement_target + helping_target
                score = (
                        new_target * blue +
                        notsigned_target * green +
                        reopen_target * yellow +
                        resume_target * green +
                        interview_target * green +
                        placement_target * blue +
                        helping_target * yellow
                )

                email_body += f'''
                    <tr>
                        <td>{names[i]}</td>
                        <td>{new_target}</td>
                        <td>{notsigned_target}</td>
                        <td>{reopen_target}</td>
                        <td>{resume_target}</td>
                        <td>{interview_target}</td>
                        <td>{placement_target}</td>
                        <td>{helping_target}</td>
                        <td>Target: {target}<br>Score: {score}</td>
                    </tr>
                '''
            email_body += f'''
                                       </table>

                                       <div class="signature">
                                           <p>Best regards,</p>
                                           <p>{user_name}</p>
                                           <p>{user_email}</p>
                                           <p><img class="geoxhr" src="https://geoxhr.com/wp-content/uploads/2021/10/DragonOurClientLogos1Green-1.png" alt="GeoxHR Logo"></p>
                                       </div>
                                   </div>
                               </body>
                               </html>
                           '''
        except:
            pass
        msg = Message(subject=email_subject, recipients=recipients, html=email_body)
        mail.send(msg)
        try:
            user_email_subject = "Weekly Tasks Assigned"
            user_email_body = f'''
                    <p>Dear User,</p>
                    <p>We hope this email finds you well. We wanted to inform you that your weekly tasks have been assigned by {user_name} </p>
                    <p>Best regards,</p>
                    <p>Your Company Name</p>
                '''
            user_msg = Message(subject=user_email_subject, recipients=emails, html=user_email_body)
            mail.send(user_msg)
        except Exception as e:
            pass
            print(f"Error sending user email to {user_email}: {str(e)}")

        response = jsonify({'message': 'success'})
        response.status_code = 200
        return response
    else:
        return redirect('/target')


# def send_email():
#     with app.app_context():
#         today = datetime.today()
#         print("today", today)
#         days_to_saturday = today.weekday()
#         saturday = today - timedelta(days=days_to_saturday)
#         friday = saturday + timedelta(days=6)
#         weekstart = saturday.strftime("%Y-%m-%d")
#         weekend = friday.strftime("%Y-%m-%d")
#         print("Week start:", weekstart)
#         print("Week end:", weekend)
#         members_data = Targets.query.filter(Targets.weekstart == weekstart,
#                                                     Targets.weekend == weekend).order_by(desc(Targets.id)).all()
#
#
#         subj = f"weekly target report ({weekstart}-{weekend})"
#         recipients = ['nhoorain161@gmail.com','notify@geoxhr.com']
#         user_email_subject = subj
#         email_body = f'''
#             <!DOCTYPE html>
#             <html>
#             <head>
#                 <style>
#                     body {{
#                         font-family: 'Arial', sans-serif;
#                         background-color: #f0f0f0;
#                         margin: 0;
#                         padding: 0;
#                     }}
#                     .container {{
#                         background-color: #ffffff;
#                         border-radius: 10px;
#                         box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
#                         overflow: hidden;
#                         margin: 15px 0px;
#                         padding: 20px;
#                         max-width: 800px;
#                     }}
#                     .header {{
#                         background-color: #007bff;
#                         color: #ffffff;
#                         padding: 10px;
#                         text-align: center;
#                         border-radius: 10px 10px 0 0;
#                     }}
#                     h2 {{
#                         margin: 0;
#                     }}
#                     p {{
#                         margin: 10px 0;
#                     }}
#                     table {{
#                         width: 100%;
#                         border-collapse: collapse;
#                         margin-top: 20px;
#                     }}
#                     th, td {{
#                         border: 1px solid #dddddd;
#                         text-align:center;
#                         padding:3px;
#                     }}
#                     th {{
#                         background-color: #f2f2f2;
#                     }}
#                     .signature {{
#                         margin-top: 20px;
#                         font-style: italic;
#                         font-size: 15px;
#                     }}
#                     .geoxhr {{
#                         width: 100px;
#                         margin-top: 10px;
#                     }}
#                 </style>
#             </head>
#             <body>
#                 <div class="container">
#                     <p>Dear Kamran,</p>
#                     <p>I hope this email finds you well. Here is the comprehensive weekly target report showcasing the remarkable achievements and progress of our dedicated team. Your insights and feedback are highly appreciated.</p>
#
#                     <table id="targetTable">
#                         <tr>
#                             <th>Name</th>
#                             <th>Target</th>
#                             <th>Score</th>
#                             <th>Score Percentage</th>
#                         </tr>
#         '''
#
#         for users in members_data:
#             name = users.name
#             total_target = users.target
#             achieved_target = users.target_achieve
#             total_score = users.score
#             achieved_score = users.score_achieve
#             achieved_percentage = users.achieve_percentage
#             print(name, total_target, achieved_target, total_score, achieved_score, achieved_percentage)
#
#             email_body += f'''
#                         <tr>
#                             <td>{name}</td>
#                             <td>{achieved_target}/{total_target}</td>
#                             <td>{achieved_score}/{total_score}</td>
#                             <td>{achieved_percentage}%</td>
#                         </tr>
#         '''
#
#         user_msg = Message(subject=user_email_subject, recipients=recipients, html=email_body)
#         mail.send(user_msg)
#         print("Email sent")
#
#
# def start_scheduler():
#     schedule.every().friday.at("11:00").do(send_email)
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

# Create a thread for the scheduler
# scheduler_thread = threading.Thread(target=start_scheduler)

# Start the scheduler thread
# scheduler_thread.start()
# Keep the script running to execute scheduled tasks


@app.route('/update_score', methods=['POST'])
def update_score():
    if request.method == 'POST':
        blue = request.form.get('blue')
        green = request.form.get('green')
        yellow = request.form.get('yellow')
        print(blue, green, yellow)

        score_data = score_board(
            blue=blue,
            green=green,
            yellow=yellow,
        )

        db.session.add(score_data)

        # Commit changes to the database after the loop
    db.session.commit()

    return render_template('target.html')


def convert_unix_to_local(timestamp):
    # Convert Unix timestamp to local datetime
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp)


USER_ACCESS_TOKEN = '3bb93391790030e714cf2fbce97f603b'
