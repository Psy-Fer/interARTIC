from flask import Flask, render_template, request, redirect, url_for, json, jsonify
#from src.job import Job
import src.queue as q
import os
import base64
from celery import Celery
import subprocess
from src.system import System
from celery.utils.log import get_task_logger
import requests
import random
import time
import fnmatch
import subprocess
from subprocess import Popen, PIPE, CalledProcessError
import sys
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret!'
# Celery configuration
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

logger = get_task_logger(__name__)


@celery.task(bind=True)
def longTask(self):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        time.sleep(1)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}

@celery.task(bind=True)
def executeJob(self, gather_cmd, demult_cmd, min_cmd):
    logger.info("In tasks.py, executing job...")
    print(gather_cmd, demult_cmd, min_cmd)

    #command = "echo running; for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do sleep 1; echo i; done ; echo FINISHING JOB"
    commands = [gather_cmd, demult_cmd, min_cmd]
    for i, cmd in enumerate(commands):
        po = subprocess.Popen(cmd, shell=True,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
        stdout, stderr = po.communicate()
        #self.update_state(state='PROGRESS')
        po.wait()

        if i == 0:
            status = "Successfully ran gather"
            n = 50
        else:
            status = "Successfully ran minion"
            n = 100

        self.update_state(state='PROGRESS', meta={'current': n, 'status': status, 'command': cmd})
        returnCode = po.returncode
        if returnCode != 0:
            raise Exception("Command {} got return code {}.\nSTDOUT: {}\nSTDERR: {}".format(cmd, returnCode, stdout, stderr))
        print("JOB CMD {} RETURNED: {}".format(cmd, returnCode))

    return {'current': 100, 'total': 100, 'status': 'Task completed!', 'result': returnCode}


@app.route('/task/<job_name>', methods = ['POST'])
def task(job_name):
    job = qSys.getJobByName(job_name)
    task = executeJob.apply_async(args=[job.gather_cmd, job.demult_cmd, job.min_cmd])
    #task = longTask.apply_async()
    return jsonify({}), 202, {'Location': url_for('task_status', task_id = task.id)}

@app.route('/status/<task_id>')
def task_status(task_id):
    task = executeJob.AsyncResult(task_id)
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'current': 0,
            'total': 100,
            'status': 'Pending...'
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'current': task.info.get('current', 0),
            'total': 100,
            'status': task.info.get('status', '')
        }
        if 'result' in task.info:
            response['result'] = task.info['result']
    else:
        # something went wrong in the background job
        response = {
            'state': task.state,
            'current': 1,
            'total': 100,
            'status': str(task.info),  # this is the exception raised
        }
    return json.htmlsafe_dumps(response)


max_queue_size = 10
qSys = System(10)

#initialise variables
gather_cmd = ""
demul_cmd = ""
minion_cmd = "test"
override_data = False

@app.route("/home")
def home():
    #Update displayed queue on home page
    queueList = []
    if qSys.queue.empty():
        return render_template("home.html", queue = None)

    for item in qSys.queue.getItems():
        queueList.append({item._job_name : url_for('progress', job_name=item._job_name, task_id = item._task_id)})

    # for item in jobQueue.getItems():
    #     queueList.append({item._job_name : url_for('progress', job_name=item._job_name)})

    queueDict = {'jobs': queueList}
    for key, value in queueDict.items():
        print(key, value)

    displayQueue = json.htmlsafe_dumps(queueDict)
    return render_template("home.html", queue = displayQueue)

@app.route("/about")
def about():
	return render_template("about.html")

@app.route("/parameters", methods = ["POST","GET"])
def parameters():
    if request.method == "POST":
        #get parameters
        job_name = request.form.get('job_name')
        input_folder = request.form.get('input_folder')
        read_file = request.form.get('read_file')
        primer_scheme = request.form.get('primer_scheme')
        output_folder = request.form.get('output_folder')
        normalise = request.form.get('normalise')
        num_threads = request.form.get('num_threads')
        pipeline = request.form.get('pipeline')
        num_samples = request.form.get('num_samples')
        min_length = request.form.get('min_length')
        max_length = request.form.get('max_length')
        bwa = request.form.get('bwa')
        skip_nanopolish = request.form.get('skip_nanopolish')
        dry_run = request.form.get('dry_run')
        num_samples = request.form.get('num_samples')

        #if user agrees output can override files with the same name in output folder
        if request.form.get('override_data'):
            override_data = True
        else:
            override_data = False

        errors = {}
        if not os.path.isdir(input_folder):
            errors['input_folder'] = "Invalid path."
        elif len(os.listdir(input_folder)) == 0:
            errors['input_folder'] = "Directory is empty."

        #if read file is specified by user
        if read_file:
            if not os.path.isfile(read_file):
                errors['read_file'] = "Invalid path/file."
        else:
            #to be filled later
            read_file = ""

        #if no output folder entered, creates one inside of input folder
        if not output_folder:
            output_folder = input_folder + "/output"

        #if the output folder does not exist, it is created
        #maybe need to put in checks for this?
        if not os.path.exists(output_folder):
            make_dir = 'mkdir "' + output_folder + '"'
            os.system(make_dir)
        # Make empty log file for initial progress rendering
        make_log = 'touch ' + '"' + output_folder + '"' +'/all_cmds_log.txt'
        os.system(make_log)

        #check length parameters are valid

        if min_length.isdigit() == False:
            errors['invalid_length'] = "Invalid minimum length."
            if max_length.isdigit() == False:
                errors['invalid_length'] = "Invalid maximum and minimum length."
        elif max_length.isdigit() == False:
            errors['invalid_length'] = "Invalid maximum length."
        elif int(max_length) < int(min_length):
            errors['invalid_length'] = "Invalid parameters: Maximum length smaller than minimum length."

        if qSys.queue.full():
        # if jobQueue.full():
            errors['full_queue'] = "Job queue is full."

        print("Errors: ", errors)

        if len(errors) != 0:
            return render_template('parameters.html', errors=errors, name=job_name, input_folder=input_folder,read_file=read_file,primer_scheme=primer_scheme,output_folder=output_folder)

        #no spaces in the job name - messes up commands
        job_name = job_name.replace(" ", "_")

        #Create a new instance of the Job class
        new_job = qSys.newJob(job_name, input_folder, read_file, primer_scheme, output_folder, normalise, num_threads, pipeline, min_length, max_length, bwa, skip_nanopolish, dry_run, override_data, num_samples)
        print("HEHE")

        #Add job to queue
        qSys.addJob(new_job)

        return redirect(url_for('progress', job_name=job_name))

    #Update displayed queue on home page
    queueList = []
    if qSys.queue.empty():
        return render_template("parameters.html", queue = None)

    for item in qSys.queue.getItems():
        queueList.append({item._job_name : url_for('progress', job_name=item._job_name, task_id = item._task_id)})

    # for item in jobQueue.getItems():
    #     queueList.append({item._job_name : url_for('progress', job_name=item._job_name)})

    queueDict = {'jobs': queueList}
    displayQueue = json.htmlsafe_dumps(queueDict)
    return render_template("parameters.html", queue = displayQueue)

@app.route("/progress/<job_name>", methods = ["GET", "POST"])
def progress(job_name):
    #print(jobQueue.getJob)
    job = qSys.getJobByName(job_name)
    job_name = job._job_name

    path = job.output_folder
    path +="/all_cmds_log.txt"

    print(path)
    with open(path, "r") as f:
        gatherOutput = f.read().replace("\n","<br/>")

    #pattern = "^ERROR"
    #error = {}
    #with open(path, "r") as f:
    #    for line in f:
    #        result = re.match(pattern, line)
    #        if (result):
    #            error['error_pipeline'] = "Error found"

    # num_in_queue = jobQueue.getJobNumber(job_name)
    # queue_length = jobQueue.getNumberInQueue()
    num_in_queue = qSys.queue.getJobNumber(job_name)
    queue_length = qSys.queue.getNumberInQueue()

    return render_template("progress.html", gatherOutput=gatherOutput, num_in_queue=num_in_queue, queue_length=queue_length, job_name=job_name)

#
# Extra stuff:
# @app.route("/progress", methods = ["GET", "POST"])
# def progress():
#     #job = jobQueue.getJobByName(job_name)
#     #print(job)

#     #gather_cmd = job.gather_cmd
#     #output_folder = job.output_folder
#     #min_cmd = job.min_cmd
#    # print(gather_cmd, output_folder, min_cmd)
#     #decode
#     #gather_cmd = base64.b64decode(gather_cmd).decode()
#     #output_folder = base64.b64decode(output_folder).decode()
#     #min_cmd = base64.b64decode(min_cmd).decode()
#     #run minion cmd
# #    os.system(gather_cmd)
# #    os.system(min_cmd)
#     #move output files into output folder
#     #os.system('mv ' + job_name + '* ' + output_folder)
#     return render_template("progress.html", gatherOutput=gatherOutput, error=error)


#not sure if this should be a get method
@app.route("/output/<job_name>", methods = ["GET", "POST"])
def output(job_name): #need to update to take in job name as parameter
    #job_name = request.args.get('job_name')
    #output_folder = request.args.get('output_folder')
    job = qSys.getJobByName(job_name)
    output_folder = job._output_folder
    output_files = []
    barplot = ''
    boxplot = ''

    if output_folder:
        if os.path.exists(output_folder):
            for (dirpath, dirnames, filenames) in os.walk(output_folder):
                for name in filenames:
                    if fnmatch.fnmatch(name, '*barplot.png'):
                        barplot = name
                    if fnmatch.fnmatch(name, '*boxplot.png'):
                        boxplot = name
                output_files.extend(filenames)

        if request.method == "POST":
            plots = {}
            if request.form.get('barplot') == "yes":
                if barplot:
                    #plots['barplot'] = '../'+output_folder[2:]+'/'+barplot
                    plots['barplot'] = '../static/'+barplot
            if request.form.get('boxplot') == "yes":
                if boxplot:
                    #plots['boxplot'] = '../'+output_folder[2:]+'/'+boxplot
                    plots['boxplot'] = '../static/'+boxplot

            if request.form['submit_button'] == 'Preview':
                return render_template("output.html", job_name=job_name, output_folder=output_folder, output_files=output_files, preview_plots=plots)
            if request.form['submit_button'] == 'Download':
                return render_template("output.html", job_name=job_name, output_folder=output_folder, output_files=output_files, download_plots=plots)

    return render_template("output.html", job_name=job_name, output_folder=output_folder, output_files=output_files)


if __name__ == "__main__":
    app.run(debug=True)
