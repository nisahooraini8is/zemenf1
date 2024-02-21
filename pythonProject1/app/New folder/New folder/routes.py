

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
from flask import Flask, session, render_template, redirect, request, url_for, jsonify,send_file,Response
from passlib.hash import sha256_crypt
from flask_login import login_user
from sqlalchemy import desc, exists, func, case,or_, extract ,and_
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


from app.util import verify_pass


# Set a secret key for session management
app.secret_key = "geoxhr123??"

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

from sqlalchemy import desc


@app.route('/websitejobs')
def websitejobs():
    alljobs = Jobs.query.filter(Jobs.job_status == 'active').order_by(desc(Jobs.created_at)).all()
    formatted_times = [format_posted_time(job.created_at) for job in alljobs]
    for job, formatted_time in zip(alljobs, formatted_times):
        job.formatted_time = formatted_time
    return render_template('websitejobs.html', alljobs=alljobs)


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
                                                file_name=filename, file_content=content, subject_part1='GeoxHR website ')
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

# engine = create_engine('mysql+pymysql://hayat:Hayat_admin123@ec2-15-156-80-22.ca-central-1.compute.amazonaws.com/geoxhrdb')
engine = create_engine('mysql+pymysql://root:@localhost/geoxhr2')
#

# Create a session factory
Session = sessionmaker(bind=engine)
class DotDict(dict):
    def __getattr__(self, attr):
        return self.get(attr)

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

    # print(candidateplace, "candidateplace")

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
        'contractsigned' : contractsigned_data ,
        'contractnotsigned' : contractnotsigned_data ,
        'reopendeals' : reopendeals_data ,
        'candidateplacement' : candidateplacement_data,
        'placementdata_count' : placementdata_count
    })
    return render_template('index.html', data_array=data_array, jobsorder=jobsorder, alldata=alldata)




@app.route('/candidate')
@role_required(allowed_roles=['user', 'admin'])
def candidate():
    page = request.args.get('page', default=1, type=int)
    per_page = 500
    action = 'Interested'
    subject_part1 = 'registered from Geox hr'
    with db.session() as session:
        total_records = session.query(Emails_data).filter(Emails_data.action != action,Emails_data.subject_part1 != subject_part1).count()
        total_pages = ceil(total_records / per_page)
        start_page = max(1, page - 5)
        end_page = min(total_pages, start_page + 10)
        alldata = session.query(Emails_data).filter(Emails_data.action != action,Emails_data.subject_part1 != subject_part1).order_by(
            desc(Emails_data.id)).offset((page - 1) * per_page).limit(per_page).all()
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
    'CAN': '+1',    # Canada
    'CCK': '+61',   # Cocos(Keeling) Islands
    'CH': '+41',    # Switzerland
    'CL': '+56',    # Chile
    'CN': '+86',    # China
    'CM': '+237',   # Cameroon
    'CD': '+243',   # Congo, The Democratic Republic of the
    'CG': '+242',   # Congo
    'CK': '+682',   # Cook Islands
    'CO': '+57',    # Colombia
    'KM': '+269',   # Comoros
    'CV': '+238',   # Cabo Verde(Cape Verde)
    'CR': '+506',   # Costa Rica
    'CU': '+53',    # Cuba
    'CW': '+599',   # Curaçao
    'CX': '+61',    # Christmas Island
    'KY': '+1-345', # Cayman Islands
    'CY': '+357',   # Cyprus
    'CZ': '+420',   # Czechia(Czech Republic)
    'DEU': '+49',   # Germany
    'DJ': '+253',   # Djibouti
    'DM': '+1-767', # Dominica
    'DK': '+45',    # Denmark
    'DO': '+1-809', # Dominican Republic (and +1-829 and +1-849)
    'DZ': '+213',   # Algeria
    'EC': '+593',   # Ecuador
    'EG': '+20',    # Egypt
    'ER': '+291',   # Eritrea
    'EH': '+212',   # Western Sahara
    'ES': '+34',    # Spain
    'EE': '+372',   # Estonia
    'ET': '+251',   # Ethiopia
    'FI': '+358',   # Finland
    'FJ': '+679',   # Fiji
    'FK': '+500',   # Falkland Islands (Malvinas)
    'FR': '+33',    # France
    'FO': '+298',   # Faroe Islands
    'FM': '+691',   # Micronesia, Federated States of
    'GA': '+241',   # Gabon
    'GB': '+44',    # United Kingdom
    'GE': '+995',   # Georgia
    'GG': '+44-1481',  # Guernsey
    'GH': '+233',   # Ghana
    'GI': '+350',   # Gibraltar
    'GN': '+224',   # Guinea
    'GP': '+590',   # Guadeloupe
    'GM': '+220',   # Gambia
    'GW': '+245',   # Guinea-Bissau
    'GQ': '+240',   # Equatorial Guinea
    'GR': '+30',    # Greece
    'GD': '+1-473', # Grenada
    'GL': '+299',   # Greenland
    'GT': '+502',   # Guatemala
    'GF': '+594',   # French Guiana
    'GU': '+1-671', # Guam
    'GY': '+592',   # Guyana
    'HK': '+852',   # Hong Kong
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
    'LT': '+370',# Lithuania
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
    'AW' : '+297',
    'AQ' : '+672',
    'AU' : '+61',
    'BY' : '+375',
    'BV' : '0055',
    'CF' : '+236',
    'CA' : '+1',
    'CC' : '+61',
    'CI' : '+225',
    'DE' : 'Germany',
    'US' : '+1',
    'SG' : '+65'



        # Add more country codes as needed
    }
    all_countries = list(pycountry.countries)
    for country in all_countries:
        alpha2_code = country.alpha_2
        country_name = country.name
        phone_code = phone_codes.get(alpha2_code, 'N/A')  # Get the phone code from the dictionary, default to 'N/A'
        # print(f"Country: {country_name}, Alpha-2 Code: {alpha2_code}, Phone Code: {phone_code}")
    return render_template('candidates.html', alldata=alldata, page=page, total_pages=total_pages,
                           all_countries=all_countries, phone_codes=phone_codes,start_page=start_page, end_page=end_page)

@app.route('/candidateprofile/<string:email>')
@role_required(allowed_roles=['user', 'admin'])
def candidateprofile(email):
    with db.session() as session:
        alldata = session.query(Emails_data).filter(Emails_data.email == email).order_by(
            desc(Emails_data.created_at)).all()

        sender_name = session.query(Emails_data.sender_name).filter(Emails_data.email == email).first()

        if sender_name:
            sender_name = sender_name[0]
            recruiting = session.query(recruiting_data).filter(recruiting_data.candidate == sender_name).all()
        else:
            recruiting = []

    return render_template('profile.html', alldata=alldata, recruiting=recruiting)


@app.route('/selecteddata')
@role_required(allowed_roles=['user', 'admin'])
def selecteddata():
    page = request.args.get('page', default=1, type=int)
    per_page = 500
    action = 'Interested'
    with db.session() as session:
        total_records = session.query(Emails_data).filter(Emails_data.action == action).count()
        total_pages = ceil(total_records / per_page)
        start_page = max(1, page - 5)
        end_page = min(total_pages, start_page + 10)
        alldata = session.query(Emails_data).filter(Emails_data.action == action).order_by(
            desc(Emails_data.created_at)).offset((page - 1) * per_page).limit(per_page).all()
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
        phone_code = phone_codes.get(alpha2_code, 'N/A')  # Get the phone code from the dictionary, default to 'N/A'
        # print(f"Country: {country_name}, Alpha-2 Code: {alpha2_code}, Phone Code: {phone_code}")
    return render_template('candidates.html', alldata=alldata, page=page, total_pages=total_pages,
                           all_countries=all_countries, phone_codes=phone_codes, start_page=start_page,
                           end_page=end_page)

@app.route('/registereddata')
@role_required(allowed_roles=['user', 'admin'])
def registereddata():
    page = request.args.get('page', default=1, type=int)
    per_page = 500
    action = 'Interested'
    subject_part1= 'registered from Geox hr'
    with db.session() as session:
        total_records = session.query(Emails_data).filter(Emails_data.action != action,Emails_data.subject_part1 == subject_part1).count()
        total_pages = ceil(total_records / per_page)
        start_page = max(1, page - 5)
        end_page = min(total_pages, start_page + 10)
        alldata = session.query(Emails_data).filter(Emails_data.action != action,Emails_data.subject_part1 == subject_part1).order_by(
            desc(Emails_data.created_at)).offset((page - 1) * per_page).limit(per_page).all()
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
        phone_code = phone_codes.get(alpha2_code, 'N/A')  # Get the phone code from the dictionary, default to 'N/A'
        # print(f"Country: {country_name}, Alpha-2 Code: {alpha2_code}, Phone Code: {phone_code}")
    # print(total_records)

    return render_template('candidates.html', registereddata=alldata, page=page, total_pages=total_pages,
                           all_countries=all_countries, phone_codes=phone_codes, start_page=start_page,
                           end_page=end_page)

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
                    "email" :  email.email,
                    "status" : email.status,
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
    keyword_lower = keyword.lower()
    # Print the keyword to the console for debugging
    # print(f"Searching for keyword: {keyword}")
    pdf_data = Emails_data.query.order_by(desc(Emails_data.id)).all()
    matching_emails = []
    for email in pdf_data:
        pdf_content_json = email.pdf_content_json
        if pdf_content_json:
            pdf_data_dict = json.loads(pdf_content_json)
            pdf_data_json_lower = json.dumps(pdf_data_dict).lower()
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
                    "status" : email.status,
                })
    # Print the search results to the console for debugging
    # print(f"Search results: {matching_emails}")

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
        email = request.form.get('email')
        role = request.form.get('selected_role')
        designation = request.form.get('selected_designation')
        password = request.form.get('password')
        encpassword = sha256_crypt.encrypt(password)

        try:
            if id is not None:
                entry = db.session.query(Users).filter_by(id=id).first()
                if entry:
                    entry.id = id
                    entry.role = role
                    entry.fname = fname
                    entry.lname = lname
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
                    entry = Users(fname=fname, lname=lname, email=email, password=encpassword, role=role,
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
            print(user,"user")
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
        user_id=session['user_id']
        oldpassword = request.form.get('oldps')
        newpassword = request.form.get('newps')
        confirmpassword = request.form.get('confirmpswrd')
        check = db.session.query(Users).filter_by(id=user_id).first()
        varify = sha256_crypt.verify(oldpassword, check.password)
        # print(varify)
        if varify:
            # print("varify")
            if newpassword==confirmpassword:
                # print("password confirm")
                password = sha256_crypt.encrypt(confirmpassword)
                check.password=password
                db.session.add(check)
                db.session.commit()
                return render_template('user.html', msg='password changed successfully')
            else:
                return render_template('user.html', msg='confirm password did not match')
        else:
            return render_template('user.html', msg='old password did not match')


@app.route('/onereporting')
@role_required(allowed_roles=['user', 'admin'])
def onereporting():
    return render_template('/onereporting-form.html')


@app.route('/onereporting_form/<int:candidate_id>/job/<int:jobid>/OrderId/<int:OrderId>')
@app.route('/onereporting_form/<int:id>')
@role_required(allowed_roles=['user', 'admin'])
def onereporting_form(id=None, candidate_id=None, jobid=None, OrderId= None):
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
    company = Marketing.query.filter(Marketing.company_status == 'active').all()
    positions = Joborder.query.filter_by(company_id=companydata.id, id=OrderId,archived = False).all() if companydata else []
    # print("positions", positions,companydata, company)
    return render_template('recruiting.html', data=user, company=company, companydata=companydata, positions=positions)


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

                    order = Joborder(user_id=user_id, company_id=id, payrate=pay_rate, salarytype=pay_rate_type,jobstatus = active,
                                      title=job_title, starttime=shift_start, endtime=shift_end,
                                     vacancy=total_vacancy,days = selected_days_str)
                    db.session.add(order)
                    db.session.commit()


        else:
            # Now, insert the list data
            entry = Marketing(user_id=user_id, name=name, company=company, status=Status, cperson=cperson, company_status = active,
                              cphone=phone, location=location, Markup=markup, otherReport=other_report, Notes=notes)

            db.session.add(entry)
            db.session.commit()
            submitted_id = entry.id

            forms = allforms_data(user_id=user_id, form_id=submitted_id, filledby=name, belongsto=cperson,
                                  form_type=formtype, status=Status)
            db.session.add(forms)
            db.session.commit()
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
                                  jobstatus = active, title=job_title, starttime=shift_start, endtime=shift_end,
                                 vacancy=total_vacancy,days = selected_days_str)
                # jobstatus = jobstatuss,
                db.session.add(order)
                db.session.commit()

        recipients = ['notify@geoxhr.com ','nhoorain161@gmail.com']

        if Status == 'New deal opened and contract signed':
            email_subject = "Good news! A new contract signed"
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
            email_subject = "Heads Up: Form in, contract not signed"
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
            email_subject = "Exciting news! We have successfully reopened the deal"
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
            status = person_starting
        elif did_you != 'Help Another':
            help = ''
            person_starting = ''
            status = did_you
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
                hello  = "No matching record found for updating vacancy"
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
            forms = allforms_data(user_id=user_id, form_id=submitted_id, filledby=name, belongsto=candidate,
                                  form_type=formtype, status=status)
            db.session.add(forms)
            db.session.commit()
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

                email_subject = "Good news! A new Candidate is Placed"
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
                recipients = ['notify@geoxhr.com ','nhoorain161@gmail.com']
                msg = Message(subject=email_subject, recipients=recipients, html=email_body)
                mail.send(msg)
            else:
                hello2  = "No matching record found for updating vacancy."
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
    job=db.session.query(Jobs).filter(Jobs.id==id).first()
    return render_template('postnewjobs.html', job=job)

@app.route('/postjob', methods=['POST'])
@role_required(allowed_roles=['user', 'admin'])
def postjob():
    if request.method == 'POST':
        id = request.form.get('id')
        title = request.form.get('title')
        name = request.form.get('name')
        company = request.form.get('company')
        user_id = request.form.get('user_id')
        location = request.form.get('location')
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
            relative_file_path=''

        if id is not None:
            entry = db.session.query(Jobs).filter_by(id=id).first()
            entry.title=title
            entry.company=company
            entry.location=location
            entry.job_type=JobType
            entry.duration= duration
            entry.onsite= onsite
            entry.salary_type=salarytypes
            entry.salary=Salary
            entry.job_date=date
            entry.job_status=job_status
            entry.description=description
            entry.responsibility=responsibility
            entry.eligibility=eligibility
            entry.notes=notes
            if file.filename:
                entry.image =relative_file_path
        else:
            entry = Jobs(user_id=user_id, name=name, title=title, image=relative_file_path, company=company, location=location,
                            job_type=JobType, duration= duration, onsite= onsite, salary_type=salarytypes, salary=Salary,
                            job_date=date, job_status=job_status, description=description, responsibility=responsibility, eligibility=eligibility,
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





@app.route('/jobOders')
@role_required(allowed_roles=['user', 'admin'])
def jobOders():
    page = request.args.get('page', default=1, type=int)
    per_page = 200
    total_records = db.session.query(Joborder).order_by(desc(Joborder.id)).count()
    total_pages = ceil(total_records / per_page)
    start_page = max(1, page - 5)
    end_page = min(total_pages, start_page + 10)
    # jobsorder = db.session.query(Joborder).order_by(desc(Joborder.id)).offset((page - 1) * per_page).limit(per_page).all()
    # marketing_entries = db.session.query(Marketing).all()
    jobsorder = db.session.query(Joborder).order_by(desc(Joborder.id)).all()
    marketing_entries = db.session.query(Marketing).all()
    company_name_dict = {entry.id: entry.company for entry in marketing_entries}
    for job_order in jobsorder:
        company_id = job_order.company_id
        if company_id in company_name_dict:
            job_order.company = company_name_dict[company_id]
    action = 'Interested'
    alldata = Emails_data.query.filter(Emails_data.action == action).order_by(desc(Emails_data.id)).all()
    # print(jobsorder, marketing_entries)
    return render_template('jobsorder.html',jobsorder=jobsorder, alldata=alldata,page=page, total_pages=total_pages,start_page=start_page, end_page=end_page)


@app.route('/archive_job/<int:job_id>', methods=['POST'])
@role_required(allowed_roles=['user', 'admin'])
def archive_job(job_id):
    job = Joborder.query.get(job_id)
    if job:
        job.archived = True
        db.session.commit()
        response = jsonify({'message': 'success'})
        response.status_code = 200
        return response
    else:
        return "Unsupported method"
    return redirect(url_for('jobOders'))

@app.route('/unarchive_job/<int:job_id>', methods=['POST'])
@role_required(allowed_roles=['user', 'admin'])
def unarchive_job(job_id):
    job = Joborder.query.get(job_id)
    if job:
        job.archived = False
        db.session.commit()
        response = jsonify({'message': 'success'})
        response.status_code = 200
        return response
    else:
        return "Unsupported method"
    return redirect(url_for('jobOders'))


@app.route('/position', methods=['POST'])
@role_required(allowed_roles=['user', 'admin'])
def position():
    data = request.get_json()
    selectedOption = data.get('companyId')
    # print(selectedOption)
    positions = Joborder.query.filter(and_(Joborder.company_id == selectedOption, Joborder.jobstatus=='active',Joborder.archived == False)).all()
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
    per_page =100

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


@app.route('/OneReportingForm')
@role_required(allowed_roles=['user', 'admin'])
def OneReportingForm():
    return render_template('onereporting-form.html')

@app.route('/getregistered')
def getregistered(data=None):
    return render_template('getregistered.html',data=data)

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
    return render_template('addnewemployee.html',data=data)

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
    type='view'
    if form_type=='New Deals Contract Signed':
        formdata = Marketing.query.filter(Marketing.id==form_id).first()
        jobsdata = Joborder.query.filter(Joborder.company_id==form_id).all()
        # print(*jobsdata)
        return render_template('marketing.html', type=type, formdata=formdata, jobsdata=jobsdata)
    elif form_type=='Person Placement':
         formdata = recruiting_data.query.filter(recruiting_data.id==form_id).first()
         company = Marketing.query.all()
         return render_template('recruiting.html', type=type, formdata=formdata, company=company)
    elif form_type=='HR Forms':
         formdata = Hrforms.query.filter(Hrforms.id==form_id).first()
         return render_template('hrforms.html', type=type, formdata=formdata)
    elif form_type=='Other Final':
         formdata = Otherfinal.query.filter(Otherfinal.id==form_id).first()
         return render_template('otherreport.html', type=type, formdata=formdata)


@app.route('/editforms/<int:form_id>/<string:form_type>')
@role_required(allowed_roles=['user', 'admin'])
def editforms(form_id, form_type):
    type='edit'
    if form_type=='New Deals Contract Signed':
        formdata = Marketing.query.filter(Marketing.id==form_id).first()
        jobsdata = Joborder.query.filter(Joborder.company_id == form_id).all()
        return render_template('marketing.html', type=type, formdata=formdata, jobsdata=jobsdata)
    elif form_type=='Person Placement':
         formdata = recruiting_data.query.filter(recruiting_data.id==form_id).first()
         company = Marketing.query.all()
         return render_template('recruiting.html', type=type, formdata=formdata, company=company)
    elif form_type=='HR Forms':
         formdata = Hrforms.query.filter(Hrforms.id==form_id).first()
         return render_template('hrforms.html', type=type, formdata=formdata)
    elif form_type=='Other Final':
         formdata = Otherfinal.query.filter(Otherfinal.id==form_id).first()
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

def convert_unix_to_local(timestamp):
    # Convert Unix timestamp to local datetime
    if timestamp is None:
        return None
    return datetime.fromtimestamp(timestamp)


USER_ACCESS_TOKEN = '3bb93391790030e714cf2fbce97f603b'
