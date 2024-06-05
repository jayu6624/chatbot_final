from flask import Flask, render_template, jsonify, request, url_for, redirect, session
from flask_pymongo import PyMongo
import google.generativeai as genai
import os
import re
from bson.objectid import ObjectId
import datetime

app = Flask(__name__)

# Configure the Gemini API key
genai.configure(api_key="AIzaSyDTbuHg-3Z8MQxvQzhtu0chkvv-2-hMav4")

# Generate a random secret key for session management
app.secret_key = os.urandom(24)

# Define the generation config and safety settings
generation_config = {
    "temperature": 1.0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain"
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
]

# Set up MongoDB connection
app.config["MONGO_URI"] = "mongodb://localhost:27017/chatgpt"
mongo = PyMongo(app)

@app.route("/")
def first():
    return render_template('main.html')

@app.route("/chat")
def chat():
    if 'username' in session:
        # Retrieve the logged-in user's chat history
        user = mongo.db.users.find_one({'username': session['username']})
        chats = mongo.db.chats.find({'user_id': user['_id']})
        myChats = [chat for chat in chats]
        return render_template("index.html", myChats=myChats)
    else:
        return redirect(url_for('login'))

@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username1 = request.form['username']
        password1 = request.form['password']
        user = mongo.db.users.find_one({'username': username1})

        if user and password1 == user['password']:
            session['username'] = username1
            session['_id'] = str(user['_id'])
            return redirect(url_for('first'))
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route("/logout")
def logout():
    session.pop('username', None)
    session.pop('_id', None)
    return redirect(url_for('first'))

@app.route("/history")
def history():
    if 'username' in session:
        # Retrieve the logged-in user's chat history
        user = mongo.db.users.find_one({'username': session['username']})
        chats = mongo.db.chats.find({'_id': user['_id']})
        myChat = [chat for chat in chats]
        return render_template('history.html', myChats=myChat)
    else:
        return redirect(url_for('login'))

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        mongo.db.users.insert_one({"email": email, "username": username, "password": password})

        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route("/api", methods=["POST"])
def qa():
    if request.method == "POST":
        if 'username' not in session:
            return jsonify({"result": "Error: User not logged in"}), 403

        question = request.json.get("question")
        user_id = ObjectId(session['_id'])

        chat = mongo.db.chats.find_one({"question": question, "user_id": user_id})
        if chat:
            data = {"result": chat['answer']}
        else:
            try:
                model = genai.GenerativeModel(
                    model_name="gemini-1.5-flash-latest",
                    safety_settings=safety_settings,
                    generation_config=generation_config
                )
                chat_session = model.start_chat()
                response = chat_session.send_message(question)
                
                answer = response.text.strip()
                answer = re.sub(r'[^a-zA-Z0-9\s]', '', answer)
                
                try:
                    result = int(answer)
                    answer = str(result)
                except ValueError:
                    pass
                
                final = re.sub(r'[^a-zA-Z0-9\s]', '', answer)
                mongo.db.chats.insert_one({
                    "question": question, 
                    "answer": final, 
                    "user_id": user_id, 
                    "timestamp": datetime.datetime.utcnow()
                })
                data = {"result": final}
            except Exception as e:
                data = {"result": f"Error: {str(e)}"}

        return jsonify(data)

if __name__ == "__main__":
    app.run(debug=True, port=5002)








# from flask import Flask, render_template, jsonify, request, url_for, redirect, session
# from flask_pymongo import PyMongo
# import google.generativeai as genai
# import os
# import re

# app = Flask(__name__)

# # Configure the Gemini API key
# genai.configure(api_key="AIzaSyDTbuHg-3Z8MQxvQzhtu0chkvv-2-hMav4")

# # Generate a random secret key for session management
# app.secret_key = os.urandom(24)

# # Define the generation config and safety settings
# generation_config = {
#     "temperature": 1.0,
#     "top_p": 0.95,
#     "top_k": 64,
#     "max_output_tokens": 8192,
#     "response_mime_type": "text/plain"
# }

# safety_settings = [
#     {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
#     {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
#     {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
#     {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
# ]

# # Set up MongoDB connection
# app.config["MONGO_URI"] = "mongodb://localhost:27017/chatgpt"
# mongo = PyMongo(app)

# @app.route("/")
# def first():
#     return render_template('main.html')

# @app.route("/chat")
# def chat():
#     if 'username' in session:
#         # Retrieve all chats from MongoDB
#         chats = mongo.db.chats.find({})
#         myChats = [chat for chat in chats]
#         return render_template("index.html", myChats=myChats)
#     else:
#         return redirect(url_for('login'))

# @app.route("/about")
# def about():
#     return render_template('about.html')

# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == 'POST':
#         username1 = request.form['username']
#         password1 = request.form['password']
#         user = mongo.db.users.find_one({'username': username1})

#         if user and password1 == user['password']:
#             session['username'] = username1
#             return redirect(url_for('chat'))
#         else:
#             error = 'Invalid username or password'
#             return render_template('login.html', error=error)
#     return render_template('login.html')

# @app.route("/logout")
# def logout():
#     session.pop('username', None)
#     return redirect(url_for('login'))

# @app.route("/history")
# def history():
#     if 'username' in session:
#         chats = mongo.db.chats.find({})
#         myChat = [chat for chat in chats]
#         return render_template('history.html', myChats=myChat)
#     else:
#         return redirect(url_for('login'))

# @app.route("/signup", methods=["POST", "GET"])
# def signup():
#     if request.method == 'POST':
#         email = request.form['email']
#         username = request.form['username']
#         password = request.form['password']

#         mongo.db.users.insert_one({"email": email, "username": username, "password": password})

#         return redirect(url_for('login'))
#     return render_template('signup.html')

# @app.route("/api", methods=["POST"])
# def qa():
#     if request.method == "POST":
#         question = request.json.get("question")

#         chat = mongo.db.chats.find_one({"question": question})
#         if chat:
#             data = {"result": chat['answer']}
#         else:
#             try:
#                 model = genai.GenerativeModel(
#                     model_name="gemini-1.5-flash-latest",
#                     safety_settings=safety_settings,
#                     generation_config=generation_config
#                 )
#                 chat_session = model.start_chat()
#                 response = chat_session.send_message(question)
                
#                 answer = response.text.strip()
#                 answer = re.sub(r'[^a-zA-Z0-9\s]', '', answer)
                
#                 try:
#                     result = int(answer)
#                     answer = str(result)
#                 except ValueError:
#                     pass
                
#                 final = re.sub(r'[^a-zA-Z0-9\s]', '', answer)
#                 mongo.db.chats.insert_one({"question": question, "answer": final})
#                 data = {"result": final}
#             except Exception as e:
#                 data = {"result": f"Error: {str(e)}"}

#         return jsonify(data)

# if __name__ == "__main__":
#     app.run(debug=True, port=5002)


# from flask import Flask, render_template, jsonify, request, url_for, redirect, session
# from flask_pymongo import PyMongo
# import google.generativeai as genai
# from pymongo import MongoClient
# import os

# sk = os.urandom(24)

# app = Flask(__name__)
# app.secret_key = sk  # Set a secret key for session management

# # Configure the Gemini API key
# genai.configure(api_key="AIzaSyDTbuHg-3Z8MQxvQzhtu0chkvv-2-hMav4")

# # Define the generation config and safety settings
# generation_config = {
#     "temperature": 1.0,
#     "top_p": 0.95,
#     "top_k": 64,
#     "max_output_tokens": 8192,
#     "response_mime_type": "text/plain"
# }

# safety_settings = [
#     {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
#     {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
#     {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
#     {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
# ]

# # Set up MongoDB connection
# app.config["MONGO_URI"] = "mongodb://localhost:27017/chatgpt"
# mongo = PyMongo(app)

# @app.route("/")
# def first():
#     return render_template('main.html')

# @app.route("/index", methods=['GET'])
# def chat():
#     if 'username' in session:
#         # Retrieve all chats from MongoDB
#         chats = mongo.db.chats.find({})
#         myChats = [chat for chat in chats]
#         return render_template("index.html", myChats=myChats)
#     else:
#         return redirect(url_for('login'))

# @app.route("/about")
# def about():
#     return render_template('about.html')

# @app.route("/login", methods=["GET", "POST"])
# def login():
#     if request.method == 'POST':
#         print("Entered in login part-----------------")
#         username1 = request.form['username']
#         password1 = request.form['password']
#         user = mongo.db.users.find_one({'username': username1})

#         # Debugging statements
#         print("Attempting login for username:", username1)
#         print("User found in database:", user)

#         if user and password1 == user['password']:
#             session['username'] = username1
#             print("Login successful for username:", username1)
#             return redirect(url_for('chat'))
#         else:
#             print("Invalid username or password")
#             error = 'Invalid username or password'
#             return render_template('login.html', error=error)
#     return render_template('login.html')
# @app.route("/history")
# def history():
#     if 'username' in session:
#         chats = mongo.db.chats.find({})
#         myChats = [chat for chat in chats]
#         return render_template('history.html', myChats=myChats)
#     else:
#         return redirect(url_for('login'))

# @app.route("/signup", methods= ["GET","POST"])
# def signup():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         username = request.form.get('username')
#         password = request.form.get('password')
       
#         # Store the password as plain text (not recommended in production)
#         mongo.db.users.insert_one({"email": email, "username": username, "password": password})
        
#         # Debugging statement
#         print("User signed up with email:", email, "and username:", username)
        
#         return redirect(url_for('login'))
#     return render_template('signup.html')

# @app.route("/logout")
# def logout():
#     session.pop("username", None)
#     return redirect(url_for("main"))

# @app.route("/api", methods=["POST"])
# def qa():
#     if request.method == "POST":
#         question = request.json.get("question")
#         chat = mongo.db.chats.find_one({"question": question})
#         if chat:
#             data = {"result": chat['answer']}
#             return jsonify(data)
#         else:
#             try:
#                 model = genai.GenerativeModel(
#                     model_name="gemini-1.5-flash-latest",
#                     safety_settings=safety_settings,
#                     generation_config=generation_config
#                 )
#                 chat_session = model.start_chat()
#                 response = chat_session.send_message(question)
#                 print(response)

#                 answer = response.text.strip()

#                 # Store the question and answer in MongoDB
#                 mongo.db.chats.insert_one({"question": question, "answer": answer})

#                 data = {"result": answer}
#             except Exception as e:
#                 data = {"result": f"Error: {str(e)}"}

#         return jsonify(data)
# if __name__ == "__main__":
#     app.run(debug=True, port=5007)



# from flask import Flask, render_template, jsonify, request
# from flask_pymongo import PyMongo
# import google.generativeai as genai

# app = Flask(__name__)

# # Configure the Gemini API key
# genai.configure(api_key="AIzaSyAKF0zHomwUReNo1SQXFZ-_XFBWh_fF7S0")

# # Define the generation config and safety settings
# generation_config = {
#     "temperature": 1.0,
#     "top_p": 0.95,
#     "top_k": 64,
#     "max_output_tokens": 8192,
#     "response_mime_type": "text/plain"
# }

# safety_settings = [
#     {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
#     {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
#     {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
#     {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}
# ]

# # Set up MongoDB connection
# app.config["MONGO_URI"] = "mongodb://localhost:27017/chatgpt"
# mongo = PyMongo(app)

# @app.route("/")
# def hello():
#     # Retrieve all chats from MongoDB
#     chats = mongo.db.chats.find({})
#     myChats = [chat for chat in chats]
#     return render_template("index.html", myChats=myChats)

# @app.route("/api", methods=["POST"])
# def qa():
#     if request.method == "POST":
#         question = request.json.get("question")

#         # Check if the question is already in the database
#         chat = mongo.db.chats.find_one({"question": question})
#         if chat:
#             # If the question is in the database, return the stored answer
#             data = {"result": chat['answer']}
#             return jsonify(data)
#         else:
#             try:
#                 # Initialize the Gemini generative model
#                 model = genai.GenerativeModel(
#                     model_name="gemini-1.5-flash-latest",
#                     safety_settings=safety_settings,
#                     generation_config=generation_config
#                 )

#                 # Start a chat session and generate a response
#                 chat_session = model.start_chat()
#                 response = chat_session.send_message(question)
                
#                 # Print the response for debugging
#                 print(response)
                
#                 if response and hasattr(response, 'choices') and response.choices:
#                     # Extract the generated text from the response
#                     generated_text = response.candidates[0].content[0].text.strip()
#                     answer = generated_text
#                 else:
#                     answer = "Sorry, I couldn't generate a response."
#             except Exception as e:
#                 # Handle any exceptions raised during model usage
#                 answer = f"Error: {str(e)}"
            
#             # Debugging information for the answer and question
#             print(f"Question: {question}, Answer: {answer}")

#             # Store the question and answer in MongoDB
#             try:
#                 mongo.db.chats.insert_one({"question": question, "answer": answer})
#                 print("Successfully inserted into the database.")
#             except Exception as e:
#                 print(f"Database insertion error: {str(e)}")

#             # Prepare the response data
#             data = {"result": answer}
#             print(response.candidates[0].content[0].parts[0].text.strip())

#         return jsonify(data)

# if __name__ == "__main__":
#     app.run(debug=True, port=5002)
