'''
Our main application file for the Flask app.
This file initializes the Flask app and sets up the routes.
'''
import os # this is used to access environment variables (API keys, etc.)
import pandas as pd # this is used for data manipulation
from flask import Flask, render_template, request, jsonify # this is used to create the Flask app and handle requests
from datetime import datetime # this is used to handle date and time
from werkzeug.utils import secure_filename # this is used to securely handle file uploads
from flask_cors import CORS
import yagmail

from cv_matcher import CVMatcher # this is our custom module for CV matching


app = Flask(__name__)
CORS(app)

#fetch basic constants 
UPLOAD_FOLDER = './data/cv_uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # set the upload folder for CVs

    
Company_csv = './data/company.csv'
applicant_csv = './data/applicant.csv'

# Ensure necessary directories and files exist when the app starts
def initialize_system():
   
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True) #create the upload folder if it doesn't exist
    
    if not os.path.exists(Company_csv):
        pd.DataFrame(columns=[
            'JOBID', 'JOBNAME', 'JOB_DESCRIPTION', 'OPEN_DATE', 'CLOSE_DATE'
        ]).to_csv(Company_csv, index=False) #create the company CSV file if it doesn't exist
        
    if not os.path.exists(applicant_csv):
        pd.DataFrame(columns=[
            'APPLICATION_ID', 'JOB_ID', 'USER_ID', 'UPLOADED_CV_PATH', 
            'TIME_UPLOADED', 'SIMILARITY_SCORE'
        ]).to_csv(applicant_csv, index=False) #create the applicant CSV file if it doesn't exist

#save the job to the csv file
@app.route('/company', methods=['POST'])
def add_jobs():
    job_data = request.get_json() #receive the job data from the request
    
    #validate the job data
    if not all(key in job_data for key in ['JOBNAME', 'JOBDESC']):
        return jsonify({'error': 'Invalid job data'}), 400
    
    try:
     #read the existing company data
        df = pd.read_csv(Company_csv) #read the company data from CSV
        
    #create or append the new job data
        new_job = {
        'JOBID': (df['JOBID'].max() + 1) if not df.empty else 1, #generate a new JOBID
        'JOBNAME': job_data['JOBNAME'],
        'JOBDESC': job_data['JOBDESC'],
        'CREATED_AT': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'CLOSE_DATE': job_data['CLOSE_DATE'] 
    }
        new_df = pd.DataFrame([new_job]) #create a DataFrame for the new job
        df = pd.concat([df, new_df], ignore_index=True) #append the new
        df.to_csv(Company_csv, index=False) #save the updated DataFrame to CSV
    
        return jsonify({'message': 'Job added successfully'}), 200

    except Exception as e:
         return jsonify({'error': str(e)}), 500

#The function to handle logins
@app.route('/login', methods=['POST'])
def login():
    
    data = request.json
    
    #For the sake of simplicity lets just use for demo we use stored simple userdata   
    username = data.get('username')
    password = data.get('password')
    
    if username == "user@TeamA.com" and password == "thebest123":
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "unauthorized"}), 401

#return the updated job data
@app.route('/Home', methods=['GET'])
def get_company_data():
    try:
        df = pd.read_csv(Company_csv)
        return df.to_json(orient='records'), 200
    except FileNotFoundError:
        return jsonify([]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#route to handle job applications
import yagmail  # Ensure this is imported at the top

@app.route('/application', methods=['POST'])
def applu_for_job():
    
    if 'cv_file' not in request.files or 'job_id' not in request.form:
        return jsonify({'error': 'No CV file or job ID provided'}), 400

    file = request.files['cv_file']
    user_id = request.form['user_id']
    job_id = request.form['job_id']
    email = request.form.get('email')  

    print("The job_id is:", job_id)

    try:
        job_id = int(job_id)

        # Save the CV
        filename = secure_filename(f"user_{user_id}_job_{job_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
        cv_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(cv_path)

        # Match score
        similarity_score = CVMatcher(cv_path, job_id, Company_csv)

        # Save to CSV
        df = pd.read_csv(applicant_csv)
        application_data = {
            'APPLICATION_ID': (df['APPLICATION_ID'].max() + 1) if not df.empty else 1,
            'JOB_ID': job_id,
            'CV_PATH': cv_path,
            'SIMILARITY_SCORE': similarity_score,
            'APPLIED_AT': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        new_df = pd.DataFrame([application_data])
        df = pd.concat([df, new_df], ignore_index=True)
        df.to_csv(applicant_csv, index=False)

        # ✉️ Send conditional email
        try:
            yag = yagmail.SMTP("therealcineema@gmail.com", "ogbozhfyhlzucrxm")

            if similarity_score < 0.5:
                yag.send(
                    to=email,
                    subject="Application Update – IntelliBuild",
                    contents=f"""
                    Dear {user_id},

                    Thank you for applying to Job #{job_id}. After reviewing your application, 
                    we regret to inform you that your profile did not meet the initial matching criteria.

                    We encourage you to apply for future roles with us.

                    Regards,
                    IntelliBuild Team
                    """
                )
            else:
                yag.send(
                    to=email,
                    subject="You're Shortlisted – IntelliBuild",
                    contents=f"""
                    Dear {user_id},

                    Thank you for your application to Job #{job_id}.
                    We're happy to inform you that your application has passed the initial screening phase 
                    with a match score of {similarity_score:.2f}.

                    Our team will be in touch with the next steps.

                    Regards,
                    IntelliBuild Team
                    """
                )
        except Exception as e:
            print("Email sending failed:", e)

        return jsonify({'message': 'Application submitted successfully.'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

#done now call the main function to run the app
if __name__ == '__main__':
    initialize_system()
    
    app.run(host='0.0.0.0', port=5000, debug=True) #run the app 