# Personality-resume-analysis-using-NLP
The applcation help to determined the personality of a resume with the giving of some features

# Pre-requirement
Python Version 3 

# Cloning the projet 
git clone https://github.com/koatiromeo/Personality-resume-analysis-using-NLP.git <br />
cd Personality-resume-analysis-using-NLP <br />

# Installing Dependencies packages
python -m pip install -r requirements.txt <br />
python -m pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-2.3.1/en_core_web_sm-2.3.1.tar.gz <br />
python <br />
import nltk <br />
nltk.download('stopwords') <br />
nltk.download('punkt') <br />

# Run the Application 
python -m streamlit run App.py
## Result after the running command
!['Result after running'](running.png)

## Execution In the browser :
!['In the browser'](mainscreen.png)

## After Loading of a resume:
!['Apres ajout d'un cv'](afterloadresume.png)