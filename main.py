from flask import Flask, render_template, request, redirect, url_for
import os
import base64


app = Flask(__name__)

#initialise variables
gather_cmd = ""
demul_cmd = ""
minion_cmd = "test"
overRide = False

@app.route("/home")
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
        pipeline = request.form.get('pipeline')
        minLength = request.form.get('minLength')
        maxLength = request.form.get('maxLength')
        bwa = request.form.get('bwa')
        skipNanopolish = request.form.get('skipNanopolish')
        dryRun = request.form.get('dryrun')

        errors = {}
        print(errors)
        if not os.path.isdir(input_folder):
            errors['input_folder'] = "Invalid path."
        elif len(os.listdir(input_folder)) == 0:
            errors['input_folder'] = "Directory is empty."

        if not os.path.isdir(scheme_dir):
            errors['scheme_dir'] = "Invalid path."
        elif len(os.listdir(scheme_dir)) == 0:
            errors['scheme_dir'] = "Directory is empty."

        if not os.path.isfile(read_file):
            errors['read_file'] = "Invalid path/file."

        #if no output folder entered, creates one inside of input folder
        if not output_folder:
            output_folder = input_folder + "/output"

        #if the output folder does not exist, it is created
        #maybe need to put in checks for this? 
        if not os.path.exists(output_folder):
            make_dir = 'mkdir "' + output_folder + '"'
            os.system(make_dir)

        #check length parameters are valid

        if minLength.isdigit() == False:
            errors['invalid_length'] = "Invalid minimum length."
            if maxLength.isdigit() == False:
                errors['invalid_length'] = "Invalid maximum and minimum length."
        elif maxLength.isdigit() == False:
            errors['invalid_length'] = "Invalid maximum length."
        elif int(maxLength) < int(minLength):
            errors['invalid_length'] = "Invalid parameters: Maximum length smaller than minimum length."

        if len(errors) != 0:
            return render_template('parameters.html', errors=errors, name=sampleName, input_folder=input_folder,scheme_dir=scheme_dir,read_file=read_file,primer_scheme=primer_scheme,output_folder=output_folder)

        #no spaces in the sample name - messes up commands
        sampleName = sampleName.replace(" ", "_")

        #these are for gather cmd
        minLength = request.form.get('minLength')
        maxLength = request.form.get('maxLength')
        #csv_file = request.form['csvFile']

        gather_cmd = ""
        dem_cmd = ""
        minion_cmd = ""

        #if nanopolish selected
        if request.form.get('pipeline') == "nanopolish":
            #construct cmds
            minion_cmd = "echo 'no command for nanopolish yet'"
        #if medaka selected
        elif request.form.get('pipeline') == "medaka":
            #construct cmds
            gather_cmd = "artic gather --min-length " + minLength + " --max-length " + maxLength + " --prefix " + sampleName + " --directory " + input_folder +" --no-fast5s"
            minion_cmd = "artic minion --minimap2 --medaka --normalise " + normalise + " --threads " + numThreads + " --scheme-directory " + scheme_dir + " --read-file " + read_file + " " + primer_scheme + " \"" + sampleName + "\""
        #if both nano and medaka are selected
        elif request.form.get('pipeline') == "both":
            #construct commands joined together
            minion_cmd = "echo 'no command for nanopolish yet'"

        #if user agrees output can override files with the same name in output folder
        if request.form.get('overRideData'):
            overRide = True

        #need to encode - '/' in file path screws with url
        gather_cmd = base64.b64encode(gather_cmd.encode())
        output_folder = base64.b64encode(output_folder.encode())
        minion_cmd = base64.b64encode(minion_cmd.encode())

        #return render_template("progress.html", min_cmd = minion_cmd)
        return redirect(url_for('progress', gather_cmd = gather_cmd, min_cmd = minion_cmd, sample_name = sampleName, output_folder = output_folder))
    return render_template("parameters.html")

@app.route("/progress/<gather_cmd>/<min_cmd>/<sample_name>/<output_folder>", methods = ["GET", "POST"])
def progress(gather_cmd, min_cmd, sample_name, output_folder):
    #decode
    gather_cmd = base64.b64decode(gather_cmd).decode()
    output_folder = base64.b64decode(output_folder).decode()
    min_cmd = base64.b64decode(min_cmd).decode()
    #run minion cmd
    os.system(gather_cmd)
    os.system(min_cmd)
    #move output files into output folder
    os.system('mv ' + sample_name + '* ' + output_folder)
    return render_template("progress.html")

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


if __name__ == "__main__":
    app.run(debug=True)
