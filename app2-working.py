#improting libraries
import streamlit as st
from PIL import Image
import pandas as pd
from streamlit_chat import message as st_message
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import SVC
from sklearn.metrics.pairwise import cosine_similarity
from streamlit_chat import message
from streamlit_extras.colored_header import colored_header
from streamlit_extras.add_vertical_space import add_vertical_space
import streamlit_authenticator as stauth
import sqlite3 
# Load the data from CSV file
data = pd.read_csv("BankFAQs.csv")
vectorizer = CountVectorizer()
# Transform the text data into feature vectors
X = vectorizer.fit_transform(data['Question'])
# Define the labels
y = data['Class']
# Train the SVM model
svm_model = SVC(C=10, kernel='rbf', gamma=0.1, decision_function_shape='ovr')
svm_model.fit(X, y)
#setting page configuration
st.set_page_config(page_title="BankMind AI - Your personal NLP based AI for solving your banking queries",
                page_icon=Image.open("icon.png"),
                layout="wide",
                initial_sidebar_state="expanded",
                #menu_items={
                    #  'Get Help':'https://search.google.com/search-console/about ',
                    #   'Report a bug':" https://search.google.com",
                    #'About':"This is this none of that"
                    #     }
                )
#page tile
st.title('BankMind AI')
st.image("image1.jpg",width=200,use_column_width=None,output_format="auto")
#sidebar
with st.sidebar:
    st.title('BankMind AI 🙂')
    st.markdown('''
    ## About
    This app is an LLM-powered chatbot built using:
    - [Streamlit]
    - [Grit] 
    - [Hardwork]   
    💡 Note: No API key required!
    ''')
    add_vertical_space(5)
    st.write('Made with love and brought to you by your beloved bank to solve your queries instantaneously')
def bankmindai():            
    #app layout 
    if 'generated' not in st.session_state:
        st.session_state['generated']=["I'm BankMind AI,How may I help you today?"]
    if 'past' not in st.session_state:
        st.session_state['past']=['Hey!']
    #app layout
    input_container=st.container()
    colored_header(label=' ',description=' ',color_name='blue-30')
    response_container=st.container()
    def generate_answer():
            user_input = st.session_state.input_text        
            # Transform the input question into feature vector
            input_vector = vectorizer.transform([user_input])
            # Predict the class of the input question
            predicted_class = svm_model.predict(input_vector)[0]
            # Find the answer of the predicted class that is most similar to the input question
            class_data = data[data['Class'] == predicted_class]
            class_vectors = vectorizer.transform(class_data['Question'])
            similarities = cosine_similarity(input_vector, class_vectors)
            most_similar_index = similarities.argmax()
            predicted_answer = class_data.iloc[most_similar_index]['Answer']
            st.session_state.past.append(user_input)
            st.session_state.generated.append(predicted_answer)
    #making predictions
    with response_container:
        st.text_input("Talk to the bot", key="input_text", on_change=generate_answer)        
        if st.session_state['generated']:
            for i in range(len(st.session_state['generated'])):
                message(st.session_state['past'][i],is_user=True,key=str(i)+'_user')
                message(st.session_state['generated'][i],key=str(i))
            #for i, chat in enumerate(st.session_state.past):
            #   st_message(**chat, key=str(i))
# setting database management
import hashlib
def make_hashes(password):
	return hashlib.sha256(str.encode(password)).hexdigest()
def check_hashes(password,hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False
conn = sqlite3.connect('data.db')
c = conn.cursor()
# managing database
def create_usertable():
	c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')
def add_userdata(username,password):
	c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
	conn.commit()
def login_user(username,password):
	c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
	data = c.fetchall()
	return data
def view_all_users():
	c.execute('SELECT * FROM userstable')
	data = c.fetchall()
	return data
def main():
    user_login=0
    menu = ["Home","Login","SignUp"]
    choice = st.sidebar.selectbox("Menu",menu)
    if choice == "Home":
        st.subheader("Home")
        st.subheader("Your personal AI assistant to solve all your bank queries")
    elif choice == "Login":
          st.subheader("Please Login to continue")
          username = st.text_input("Enter your username")
          password = st.text_input("Password",type='password')
          if st.checkbox("Login"):
            create_usertable()
            hashed_pswd=make_hashes(password)
            result = login_user(username,check_hashes(password,hashed_pswd))
            if result:
                user_login=1
                st.success("Logged In as {}".format(username))
            else:
                st.warning("Incorrect Username/Password")	
    elif choice == "SignUp":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password",type='password')
        if st.button("Signup"):
            create_usertable()
            add_userdata(new_user,make_hashes(new_password))
            st.success("You have successfully created a valid Account")
            st.info("Go to Login Menu to login")
    if user_login:
	    bankmindai()
if __name__=='__main__':
	main()