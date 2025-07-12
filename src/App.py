'''
Our main application file for the Flask app.
This file initializes the Flask app and sets up the routes.
'''
import os # this is used to access environment variables (API keys, etc.)
import pandas as pd # this is used for data manipulation
from flask import Flask, render_template, request, jsonify # this is used to create the Flask app and handle requests
from datetime import datetime # this is used to handle date and time
from werkzeug.utils import secure_filename # this is used to securely handle file uploads

from cv_matcher import CVMatcher # this is our custom module for CV matching

app = Flask(__name__) # create a Flask app instance

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
    
    except Exception as e:
         return jsonify({'error': str(e)}), 500


#return the updated job data
@app.route('/company.csv', methods=['GET'])
def get_company_data():
    try:
        df = pd.read_csv(Company_csv)
        return df.to_json(orient='records'), 200
    except FileNotFoundError:
        return jsonify([]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#route to handle job applications
@app.route('/application', methods=['POST'])
def applu_for_job():
    
    #first receive the cv file and job id from the request
    if 'cv_file' not in request.files or 'job_id' not in request.form:
        return jsonify({'error': 'No CV file or job ID provided'}), 400
    
    #get the CV file and job ID
    file = request.files['cv']
    user_id = request.form['user_id']
    job_id = request.form['job_id']
    
    try: 
        job_id = int(job_id) #convert job_id to integer
        
        #Save the cv to the upload folder
        filename = secure_filename(f"user_{user_id}_job_{job_id}_date_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        cv_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(cv_path) #save the CV file to the upload folder
        
        #calculate the score
        similarity_score = CVMatcher(cv_path, job_id).calculate_similarity() #use the CVMatcher to calculate the similarity score
        
        df = pd.read_csv(applicant_csv) #read the existing applicant data from CSV
        
        #create a csv entry for the application
        application_data = {
            'APPLICATION_ID' : (df['APPLICATION_ID'].max() + 1) if not df.empty else 1, #generate a new APPLICATION_ID
            'JOB_ID': job_id,
            'USER_ID': user_id,
            'CV_PATH': cv_path,
            'SIMILARITY_SCORE': similarity_score,
            'APPLIED_AT': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        #write the application data to the CSV file
        new_df = pd.DataFrame([application_data]) #create a DataFrame for the new application
        df = pd.concat([df, new_df], ignore_index=True) #append the new
        df.to_csv(applicant_csv, index=False) #save the updated DataFrame to CSV
        
        return jsonify({'message': 'Application submitted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
#done now call the main function to run the app
if __name__ == '__main__':
    initialize_system()
    # Use 0.0.0.0 to make it accessible on your network
    app.run(host='0.0.0.0', port=5000, debug=True)