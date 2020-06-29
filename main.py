from flask import Flask, render_template, request
import os


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

        #get parameters
        sampleName = request.form.get('sample_name')
        input_folder = request.form.get('input_folder')
        scheme_dir = request.form.get('scheme_folder')
        read_file = request.form.get('read_file')
        primer_scheme = request.form.get('primer_scheme')
        output_folder = request.form.get('output_folder')
        normalise = request.form.get('normalise')
        numThreads = request.form.get('numThreads')

        #these are for gather cmd
        #minLength = request.form['minLength']
        #maxLength = request.form['maxLength']
        #csv_file = request.form['csvFile']
            
        #initialise variables
        gather_cmd = ""
        demul_cmd = ""
        minion_cmd = ""
        overRide = False

        #only doing minion cmd for first sprint
        #below is a sample cmd
        minion_cmd = "artic minion --minimap2 --medaka --normalise 200 --threads 4 --scheme-directory /Users/iggygetout/Documents/binf6111_project/artic-ncov2019/primer_schemes --read-file /Users/iggygetout/Documents/binf6111_project/data/SP1-raw/SP1-mapped.fastq nCoV-2019/V1 sample_name"

        #if nanopolish selected
        if request.form.get('pipeline') == "nanopolish":
            #run nanopolish cmd - to be fixed
            minion_cmd = "blah"
        #if medaka selected
        elif request.form.get('pipeline') == "medaka":
            #run medaka cmd
            minion_cmd = "artic minion --minimap2 --medaka --normalise " + normalise + " --threads " + numThreads + " --scheme-directory " + scheme_dir + " --read-file " + read_file + " " + primer_scheme + " " + sampleName
        #if both nano and medaka are selected
        elif request.form.get('pipeline') == "both":
            #will be nanopolish then medaka cmds separated by ';'
            minion_cmd = "blah"
        
        #if user agrees output can override files with the same name in output folder
        if request.form.get('overRideData'):
            overRide = True

        #run minion cmd - to be moved to progress page
        os.system(minion_cmd)

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
