from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
	return render_template("about.html")

#not sure if this should be a get method
@app.route("/output", methods = ["GET", "POST"])
def output():
    job_name = request.args.get('job_name')
    output_folder = request.args.get('output_folder')
#@app.route("/output", methods = ["POST"])
#def outputFormHandler():
    if request.method == "POST":
        plots = []
        if request.form.get('barplot') == "yes":
            plots.append("barplot")
        if request.form.get('boxplot') == "yes":
            plots.append("boxplot")
        if not plots:
            plots = "Nothing selected."
        if request.form['submit_button'] == 'Preview':
            return render_template("output.html", job_name=job_name, output_folder=output_folder, preview_plots=plots)
        if request.form['submit_button'] == 'Download':
            return render_template("output.html", job_name=job_name, output_folder=output_folder, download_plots=plots)
    return render_template("output.html", job_name=job_name, output_folder=output_folder)

@app.route("/progress")
def progress():
	return render_template("progress.html")

@app.route("/parameters")
def parameters():
	return render_template("parameters.html")

if __name__ == "__main__":
    app.run(debug=True)
