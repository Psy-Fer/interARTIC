from flask import Flask, render_template  
from markupsafe import escape

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/newJob")
def newJob():
	#return render_template("newJob.html")
    return "Create new job"

@app.route("/progress/<string:job_id>")
def progress(job_id):
	return render_template("progress.html", job_id=job_id)

if __name__ == "__main__":
    app.run(debug=True)