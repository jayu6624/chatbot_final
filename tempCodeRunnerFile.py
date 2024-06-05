from flask import Flask,rander_templetes

app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_templetes('index.html')

app.run(debug=True)