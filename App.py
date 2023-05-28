import streamlit as st
import pandas as pd
import base64,random
import time,datetime
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import io,random
from streamlit_tags import st_tags
from PIL import Image
import pymysql
from Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos
import pafy
import plotly.express as px
import pickle
from sklearn.feature_extraction.text import CountVectorizer
import plotly.express as px
import pandas as pd
import re
from datetime import date
import nltk
from guess_indian_gender import IndianGenderPredictor
import joblib


cEXT = pickle.load( open( "data/models/cEXT.p", "rb"))
cNEU = pickle.load( open( "data/models/cNEU.p", "rb"))
cAGR = pickle.load( open( "data/models/cAGR.p", "rb"))
cCON = pickle.load( open( "data/models/cCON.p", "rb"))
cOPN = pickle.load( open( "data/models/cOPN.p", "rb"))
vectorizer_31 = pickle.load( open( "data/models/vectorizer_31.p", "rb"))
vectorizer_30 = pickle.load( open( "data/models/vectorizer_30.p", "rb"))
pipeline = joblib.load('multiclass.joblib')

def create_test_data(gender,age,openness,neuroticism,conscientiousness,agreeableness,extraversion):
    
    d = {'Gender' : [gender],
        'Age' : [age],
        'openness' : [openness],
        'neuroticism' : [neuroticism],
        'conscientiousness' : [conscientiousness],
        'agreeableness' : [agreeableness],
        'extraversion' : [extraversion]}

    df = pd.DataFrame.from_dict(d)
    
    return df

def calculate_age(year,month,day):
    today = date.today()
    return today.year - year - ((today.month, today.day) < (month, day))
    
def predict_personality(text):
    scentences = re.split("(?<=[.!?]) +", text)
    text_vector_31 = vectorizer_31.transform(scentences)
    text_vector_30 = vectorizer_30.transform(scentences)
    EXT = cEXT.predict(text_vector_31)
    NEU = cNEU.predict(text_vector_30)
    AGR = cAGR.predict(text_vector_31)
    CON = cCON.predict(text_vector_31)
    OPN = cOPN.predict(text_vector_31)
    return [EXT[0], NEU[0], AGR[0], CON[0], OPN[0]]
    


def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()
    return text

def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


st.set_page_config(
   page_title="KOATI (21P646) GROUPE6 RH HELP",
   page_icon='./Logo/SRA_Logo.ico',
)
def run():
    st.title("KOATI GROUPE6 RH HELPER")
    link = '[©Developed by koatiromeo](https://github.com/koatiromeo/Personality-resume-analysis-using-NLP)'
    st.markdown(link, unsafe_allow_html=True)
    img = Image.open('./Logo/SRA_Logo.jpg')
    img = img.resize((250,250))
    st.image(img)


    pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
    if pdf_file is not None:
            save_image_path = './Uploaded_Resumes/'+pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                ## Get the whole resume data
                resume_text = pdf_reader(save_image_path)
                st.header("**Resume Analysis**")
                st.success("THE RESUME IS FOR: "+ resume_data['name'])
                st.subheader("**The Basic info**")
                try:
                    st.text('Name: '+resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Resume pages: '+str(resume_data['no_of_pages']))
                except:
                    pass
                    
                st.subheader("**Possible sexe and age**")
                try:
                    ages = []
                    pattern = "\d{2}[/-]\d{2}[/-]\d{4}"
                    dates = re.findall(pattern, resume_text)
                    for date in dates:
                       if "-" in date:
                          day, month, year = map(int, date.split("-"))
                       else:
                          day, month, year = map(int, date.split("/"))
                       if 1 <= day <= 31 and 1 <= month <= 12:
                          ages.append(calculate_age(year,month,day))
                    
                    if ages:
                       st.text('Age: '+ str(max(ages)))
                    i = IndianGenderPredictor()
                    thesexe = i.predict(name=resume_data['name'])
                    if thesexe == "male":
                     thesexe = "Male"
                     st.text('Sexe: Male')
                    else:
                     thesexe = "Female"
                     st.text('Sexe: Female')
                except:
                    pass

                st.subheader("**INFORMATION LINK TO PERSONALITY💡**")
                ## Get all sentences
                sentences = nltk.sent_tokenize(resume_text)
                clear_sentences = [
                    item.replace('\r', '').replace('\n', '')
                    for item in sentences
                ]
                print("Arrive IC")
                print("\n\n Les sentences  \n", clear_sentences)
                
                ##Find trait 
                datastrait = {
                    'openness':[],
                    'neuroticism':[],
                    'conscientiousness':[],
                    'agreeableness' : [],
                    'extraversion': []
                }
                
                for sentence in clear_sentences:
                    predictions = predict_personality(sentence)
                    if predictions[0] == 1:
                        datastrait['extraversion'].append(sentence)
                    if predictions[1] == 1 :
                        datastrait['neuroticism'].append(sentence)
                    if predictions[2] == 1 :
                        datastrait['agreeableness'].append(sentence)
                    if predictions[3] == 1 :
                        datastrait['conscientiousness'].append(sentence)
                    if predictions[4] == 1 :
                        datastrait['openness'].append(sentence)
                        
                ## Skill shows
                keywords = st_tags(label='### Openness sentences in the resume',value=datastrait['openness'],key = '1')
                keywords = st_tags(label='### Neuroticism sentences in the resume',value=datastrait['neuroticism'],key = '2')
                keywords = st_tags(label='### Conscientiousness sentences in the resume',value=datastrait['conscientiousness'],key = '3')
                keywords = st_tags(label='### Agreeableness sentences in the resume',value=datastrait['agreeableness'],key = '4')
                keywords = st_tags(label='### Extraversion sentences in the resume',value=datastrait['extraversion'],key = '5')
                
                ##  recommendation
                st.subheader("**EVALUATION TRAITS OF PERSONALIT ⚙️**")
                if ages:
                  theage = st.number_input("AGE", min_value=18, max_value=65, value=max(ages))
                else:
                  theage = st.number_input("AGE", min_value=18, max_value=65)
                
                if thesexe == "Male":
                     thesexe = st.selectbox('SEXE',('Male', 'Female'))
                else:
                     thesexe = st.selectbox('SEXE',('Female', 'Male'))
                
                theopenness = st.number_input("OPENNESS", min_value=1, max_value=10)
                theneuroticism = st.number_input("NEUROTICISM", min_value=1, max_value=10)
                theconscientiousness = st.number_input("CONSCIENTIOUSNESS", min_value=1, max_value=10)
                theagreeableness = st.number_input("AGREEABLENESS", min_value=1, max_value=10)
                theextraversion = st.number_input("EXTRAVERSION", min_value=1, max_value=10)
                
                if st.button('GIVE PERSONALITY'):
                  if thesexe == "Male":
                     thepersonality =  pipeline.predict(create_test_data(0,theage,theopenness,theneuroticism,theconscientiousness,theagreeableness,theextraversion))
                  else:
                     thepersonality =  pipeline.predict(create_test_data(1,theage,theopenness,theneuroticism,theconscientiousness,theagreeableness,theextraversion))
                  if thepersonality == 0:
                    st.markdown('''<h4 style='text-align: left; color: green;'>The personality is dependable!''',unsafe_allow_html=True)
                  elif thepersonality == 1:
                    st.markdown('''<h4 style='text-align: left; color: green;'>The personality is extraverted!''',unsafe_allow_html=True)
                  elif thepersonality == 2:
                    st.markdown('''<h4 style='text-align: left; color: green;'>The personality is lively!''',unsafe_allow_html=True)
                  elif thepersonality == 3:
                    st.markdown('''<h4 style='text-align: left; color: green;'>The personality is responsible!''',unsafe_allow_html=True)
                  else:
                    st.markdown('''<h4 style='text-align: left; color: green;'>The personality is serious!''',unsafe_allow_html=True)

                  st.balloons()
                   


run()