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
        test = request.form.get('test')

        #parameters
        sampleName = request.form.get('sample_name')
        numThreads = request.form.get('numThreads')
        minLength = request.form.get('minLength')
        maxLength = request.form.get('maxLength')
        normaliseNano = request.form.get('normaliseNanopolish')
        normaliseMendaka = request.form.get('normaliseMendaka')
        #print(request.form.get('val'))

        output_folder = request.form.get('outputFolder')
            
        gather_cmd = ""
        demul_cmd = ""
        #only doing minion cmd for first sprint
        minion_cmd = "artic minion --minimap2 --medaka --normalise 200 --threads 4 --scheme-directory /Users/iggygetout/Documents/binf6111_project/artic-ncov2019/primer_schemes --read-file /Users/iggygetout/Documents/binf6111_project/data/SP1-raw/SP1-mapped.fastq nCoV-2019/V1 sample_name"
        if request.form.get('nanopolish') == "yes":
            #run nanopolish cmd
            minion_cmd = "blah"
        elif request.form.get('mendaka') == "yes":
            #run mendaka cmd
            minion_cmd = "artic minion --minimap2 --medaka --normalise " + normaliseMendaka + " --threads " + numThreads + " --scheme-directory /Users/iggygetout/Documents/binf6111_project/artic-ncov2019/primer_schemes --read-file /Users/iggygetout/Documents/binf6111_project/data/SP1-raw/SP1-mapped.fastq nCoV-2019/V1 sample_name"
        elif request.form.get('both') == "yes":
            minion_cmd = "blah"
        
        if request.form.get('overRideData') == "yes":
            overRide = True
        return render_template("progress.html", min_cmd = minion_cmd)
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

@app.route("/progress", methods = ["GET", "POST"])
def progress():
	return render_template("progress.html")

if __name__ == "__main__":
    app.run(debug=True)
