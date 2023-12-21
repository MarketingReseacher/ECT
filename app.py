# Import necessary packages
import numpy as np
import pandas as pd
import streamlit as st
import nltk
nltk.download('vader_lexicon')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')
from nltk import word_tokenize
import contractions
from nltk.sentiment.vader import SentimentIntensityAnalyzer


# Define dictionaries
PastDic = ['past', 'previously', 'previous', 'earlier', 'historically', 'formerly',  'history', 'before', 'prior', 'back', 
             'retroactively', 'priorly', 'hitherto', 'anteriorly', 'yesterday', 'already',  'precedingly', 'afore', 'fore', 'yesteryear', 'antecedently', 
             'was', 'were', 'wasnt', 'werent', 'been', 'hindsight', 'rearview', 'aforetime', 'heretofore', 'yore', 'ago', 'beforehand', 'since', 'then']
  
FutureDic = ['future', 'eventually', 'prospectively', 'henceforth', 'everytime', "everyday", "anytime", 'tomorrow', 'imminently',  'hereafter', 'hereon', 
               'henceforward', 'longrun', 'longterm', 'forthcoming', 'upcoming', 'oncoming', 'incoming', 'impending', 'foreseeable',
                'will', 'shall', 'wont', 'might',  'may', 'forward', 'aftertime', 'thereafter', 'potential', 'potentially', 'intermittently', 'successively', 'supposedly']  

# Define function that calculates temporal features 
def MyTense(t):  
  Textclean = t.lower() 
  def ExpandContractions(text):
    Expanded = contractions.fix(text)
    return Expanded
             
  Textclean = ExpandContractions(Textclean)
  
  def RemoveNonAscii(text):
    return "".join(w for w in text if ord(w) < 128) 
      
  Textclean = RemoveNonAscii(Textclean)
                 
  def POS(text):
    tokens = nltk.word_tokenize(text)
    tagged = nltk.pos_tag(tokens)
                     
    past = []
    future = []
    previous = ""
    beforeprevious = ""

    for item in tagged:
      if (item[0] in PastDic) or (item[1] in ["VBD", "VBN"]) or (item[1] == "VBG" and previous == "been" and beforeprevious == "had") or (item[1] == "VBG" and previous in ["was", "were", "wasnt", "werent"]) or (item[1] == "VBG" and previous == "not" and beforeprevious in ["was", "were", "wasnt", "werent"]):
        past.append(item[0])
      elif (item[0] in FutureDic) or (item[1] in ["VB", "VBZ", "VBP"] and previous in ["will", 'shall', 'wont', 'may', 'might', "would"]) or (item[1] in ["VB", "VBZ", "VBP"] and previous == "not" and beforeprevious in ["will", 'shall', 'wont', 'may', 'might']) or (item[1] in ["VB", "VBZ", "VBP"] and previous == "to" and beforeprevious == "going") or (item[1] == "VBG" and previous == "be" and beforeprevious in ["will", 'shall', 'wont', 'may', 'might', "not"]): 
        future.append(item[0])  
      else:
        pass
                         
      beforeprevious = previous 
      previous = item[0]
    Future = len(future)
    Past = len(past)
    response = {"future" : Future, "past": Past}
                     
    return response
    
  Tenses = POS(Textclean)  
  
  return Tenses

# Define sentiment analyzer function
analyzer = SentimentIntensityAnalyzer()

# Add a selectbox for tab selection
Selected_tab = st.sidebar.selectbox("Select a tab", ["Temporal feature estimator", "Brand Avoidance Predictor based on Future Focus", 
                                                     "Brand Avoidance Predictor based on Future Focus and Covariates"])

# Tab 1
if Selected_tab == "Temporal feature estimator":

  st.write("#### Temporal Feature Estimator")
  st.write("##### User Input")

  # Take text entry as input 
  user_input = st.text_input("Brand failure incident description:")

  # Calculate temporal features using the MyTense function
  Tenses = MyTense(user_input)
  Future = Tenses['future']
  Past = Tenses['past']  
  
  st.write("##### Results")
  Length = len(user_input.split())

  # Display results only after the user inputs non-empty values fot the incident description
  if Length == 0:
      st.write("You have not entered a failure incident description yet.")
  else:
      FuturePR = round(Future/Length * 100, 2)
      PastPR = round(Past/Length * 100, 2) 
      st.write("Percentage of future-focused words in the description:", FuturePR, "%")
      st.write("Percentage of past-focused words in the description:", PastPR, "%")
      Relative = FuturePR - PastPR      
      st.write("Future focus of the description:", Relative)


# Tab 2
elif Selected_tab == "Brand Avoidance Predictor based on Future Focus":

  
  st.write("#### Brand Avoidance Predictor based on Incident Description's Future Focus")
  st.write("##### User Input")

  
  user_input = st.text_input("Brand failure incident description:")
  
  Tenses = MyTense(user_input)
  Future = Tenses['future']
  Past = Tenses['past'] 
  
  st.write("##### Results")
  
  Length = len(user_input.split())
  
  if Length == 0:
      st.write("You have not entered a failure incident description yet.")
  else:
      FuturePR = round(Future/Length * 100, 2)
      PastPR = round(Past/Length * 100, 2) 
      st.write("Percentage of future-focused words in the description:", FuturePR, "%")
      st.write("Percentage of past-focused words in the description:", PastPR, "%")
      Relative = FuturePR - PastPR      
      st.write("Future focus of the description:", Relative)
      ScaledRel = (Relative + 100)/2
      Answer = (-.11 * Relative) 
      Odds = np.exp(Answer)
      Prob = Odds/(1+Odds)
      Response = round(Prob * 100, 2)
      st.write("The likelihood that this consumer avoids the brand in the future:", Response, "%")


# Tab 3
elif Selected_tab == "Brand Avoidance Predictor based on Future Focus and Covariates":  

  st.write("#### Brand Avoidance Predictor based on Incident Description's Future Focus and Other Covariates")
  st.write("##### User Input")

  user_input = st.text_input("Brand failure incident description:")

  # Take covariate values as input 
  Gender = st.selectbox('Consumer\'s gender:', ["Female", "Male","Unknown", "Unspecified"])
  Relation = st.selectbox('Whether the consumer was the primary victim:', ["Yes", "No"])
  Warmth = st.slider('Brand warmth score', min_value=0, max_value=100, value = 55)
  Excitement = st.slider('Brand excitement score', min_value=0, max_value=100, value = 37)
  Competence = st.slider('Brand competence score', min_value=0, max_value=100, value = 57)
  Sophistication = st.slider('Brand sophistication score', min_value=0, max_value=100, value = 25)
  Ruggedness = st.slider('Brand ruggedness score', min_value=0, max_value=100, value = 49)
  Sales = st.number_input("Brand annual sales, in dollars:")
  Ad = st.number_input("Brand annual advertising spending, in dollars:")
  Marketshare = st.slider('Brand market share', min_value=0, max_value=100, value = 5)

  # Calculate likelihood using values of covariates
  def Resp(Rel, Com, G, R, W, E, C, S, Rug, Sale, A, M):
      if G == "Female":
          GenderCoeff = 1
      elif G == "Male":
          GenderCoeff = .01
      elif G == "Unknown":
          GenderCoeff = .21
      else:
          GenderCoeff = .21     
      if R == "Yes":
          RelationCoeff =  -.08
      else:
          RelationCoeff = 1  
  
      Answer = (-.11 * Rel) + GenderCoeff + RelationCoeff + (.00006 * Com) + (-.01 * W) + (.01 * E) + (-.01 * C) + (-.02 * S) + (.003 * Rug) + (.05 * Sale) + (.01 * M) + (.21 * A) 
      Odds = np.exp(Answer)      
      Prob = Odds/(1+Odds) 
      Response = round(Prob * 100, 2)
             
      return Response

  Tenses = MyTense(user_input)
  Future = Tenses['future']
  Past = Tenses['past'] 
  
  st.write("##### Results")
  
  Length = len(user_input.split())
  
  if Length == 0:
      st.write("You have not entered a failure incident description yet.")
  else:
      FuturePR = round(Future/Length * 100, 2)
      PastPR = round(Past/Length * 100, 2) 
      st.write("Percentage of future-focused words in the description:", FuturePR, "%")
      st.write("Percentage of past-focused words in the description:", PastPR, "%")
      Relative = FuturePR - PastPR      
      st.write("Future focus of the description:", Relative)
      ScaledRel = (Relative + 100)/2
      Comp = round(analyzer.polarity_scores(user_input).get('compound'), 2)
      st.write("Compound sentiment score of the description:", Comp)
      if Sales == 0:
        LnSales = 10.32
      else:
        LnSales = ln(Sales + 1)
      if Ad == 0:
        Advertising = .06
      else: 
        Advertising = Ad 
      Response = Resp(Relative, Comp, Gender, Relation, Warmth, Excitement, Competence, Sophistication, Ruggedness, LnSales, Advertising, Marketshare)
      st.write("The likelihood that this consumer avoids the brand in the future:", Response, "%")




