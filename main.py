from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/parameters", methods = ["POST","GET"])
def parameters():
    if request.method == "POST":
        input_folder = request.form.get('inputFolder')
        csv_file = request.form.get('csvFile')
            
        pipeline = []
        if request.form.get('nanopolish') == "yes":
            pipeline.append("nanopolish")
        if request.form.get('mendaka') == "yes":
            pipeline.append("mendaka")
        if request.form.get('both') == "yes":
            pipeline.append("nanopolish")
            pipeline.append("mendaka")
        
        numThreads = request.form.get('numThreads')
        minLength = request.form.get('minLength')
        maxLength = request.form.get('maxLength')
        normaliseNano = request.form.get('normaliseNanopolish')
        normaliseMendaka = request.form.get('normaliseMendaka')
        
        output_folder = request.form.get('outputFolder')
        
        if request.form.get('overRideDate') == "yes":
            overRide = True
        return render_template("progress.html")
    return render_template("parameters.html")

#not sure if this should be a get method
@app.route("/output", methods = ["GET", "POST"])
def output():
    job_name = request.args.get('job_name')
    output_folder = request.args.get('output_folder')
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

if __name__ == "__main__":
    app.run(debug=True)
