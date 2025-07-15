'''
The actual implementation of the cv_matcher 
'''
import os #used to access the environment variables (API keys, etc.)
import pandas as pd #used to handle data manipulation
import PyPDF2 #used to read PDF files
import docx #used to read Word documents
from sklearn.feature_extraction.text import TfidfVectorizer #used for text vectorization
from sklearn.metrics.pairwise import cosine_similarity #used to calculate similarity between vectors
import re #used for regular expressions


def extract_text_from_cv(filepath):
    
    #put the text inside a context
    text = ""
    try:
        #handle PDF files
        if filepath.endswith('.pdf'):
            #open the file and read it
            with open(filepath, 'rb') as file:
                reader = PyPDF2.PdfReader(file) #read the pdf
                for page in reader.pages: #iterate through each page
                    text_page = page.extract_text() #extract text from the page
                    if text_page:
                        text += text_page #add the text to the context
        #handle Word documents
        elif filepath.endswith('.docx'):
            doc = docx.Document(filepath) #read the Word document
            for para in doc.paragraphs:
                text += para.text + '\n' #add the text to the context
            
                        
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return ""
    return text

#function to handle the text cleaning
def clean_text(text):
    #remove special characters and extra spaces
    #lower the text
    text = text.lower() #convert text to lowercase
    text = re.sub(r'[^a-z0-9\s]', ' ', text) #handle letters nubers and spaces
    text = re.sub(r'\s+', ' ', text).strip() #remove extra spaces
    return text

def get_job_description(job_id, company_csv):
    try:
        df = pd.read_csv(company_csv) #get the csv
        job_description = df.loc[df['JOBID'] == job_id, 'JOBDESC'].values #fetch the job description
        if job_description.size > 0:
            desc = job_description[0]
            if isinstance(desc, float) and pd.isna(desc):
                return None
            return str(desc)
        else:
            return None
    except Exception as e:
        print(f"Error reading company CSV: {e}")
        return None


def CVMatcher(cv_path,job_id, company_csv):
    
    #extract the text from the cv
    cv_text = extract_text_from_cv(cv_path) #extract text from the CV
    if not cv_text:
        return None, "Failed to extract text from CV" #return None if text extraction fails
    cv_text = clean_text(cv_text) #clean the extracted text
    
    #now get the job description from the company csv
    job_description = get_job_description(job_id, company_csv) #get the job description
    if not job_description:
        return None, "Job ID not found" #return None if job ID is not found
    job_description = clean_text(job_description) #clean the job description
    
    #now dala the text vectorization
    
    #final check 
    if not cv_text or not job_description:
        return None, "CV text or job description is empty" #return None if either text is empty
    
    #attempt vectorization
    try:
        #combine the CV text and job description for vectorization
        documents = [cv_text, job_description] #create a list of documents
        
        TF_IDF = TfidfVectorizer(stop_words='english') #initialize the vectorizer
        
        tfidf_matrix = TF_IDF.fit_transform(documents)
        
        # Calculate the cosine similarity between the two vectors (CV and Job Desc).
        # The result is a 2x2 matrix; the value we need is at [0, 1].
        similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        score = similarity_matrix[0][0]
        
        # Return the score, rounded for cleanliness
        return round(float(score), 4)

    except Exception as e:
        return None, f"Error during vectorization: {e}"