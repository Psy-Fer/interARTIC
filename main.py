from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/output")
def output():
	return render_template("output.html", job_name='Job 1', output_folder='/my_ouput_folder')

@app.route("/output", methods = ["POST"])
def outputFormHandler():
    plots = []
    if request.form.get('barplot') == "yes":
        plots.append("barplot")
    if request.form.get('boxplot') == "yes":
        plots.append("boxplot")
    if request.form['submit_button'] == 'Preview':
        return render_template("output.html", job_name='Job 1', output_folder='/my_ouput_folder', preview_plots=plots)
    if request.form['submit_button'] == 'Download':
        return render_template("output.html", job_name='Job 1', output_folder='/my_ouput_folder', download_plots=plots)

if __name__ == "__main__":
    app.run(debug=True)
