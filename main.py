from flask import Flask, render_template, request, redirect, url_for, json, jsonify, flash
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
app.secret_key = "shhhh"

# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

logger = get_task_logger(__name__)

def check_override(output_folder, override_data):
    dir_files = os.listdir(output_folder)
    if len(dir_files) > 0:
        return True
    return False

def removeFiles(output_folder, override_data, job_name):
    dir_files = os.listdir(output_folder)
    filematch = 0
    if "all_cmds_log.txt" in dir_files and len(dir_files) == 1:
        remove = "rm -r " + output_folder + "/*"
        os.system(remove)

    if override_data is False and len(dir_files) > 0:
        for f in dir_files:
            if fnmatch.fnmatch(f, job_name+'*'):
                filematch += 1
        if filematch > 0:
            remove = 'rm -r \"' + output_folder + '\"/'+job_name+'*'
            os.system(remove)
            remove = 'rm -r \"' + output_folder + '\"/all_cmds_log.txt'
            os.system(remove)
        else:
            remove = 'rm -r \"' + output_folder + '\"/all_cmds_log.txt'
            os.system(remove)
    elif override_data is True:
        remove = "rm -r " + output_folder + "/*"
        os.system(remove)


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
    job.task_id = task.id
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

@app.route("/")
def route():
    return redirect(url_for('home'))

@app.route("/home")
def home():
    #Update displayed queue on home page
    queueList = []
    if qSys.queue.empty():
        return render_template("home.html", queue = None)

    for item in qSys.queue.getItems():
        queueList.append({item._job_name : url_for('progress', job_name=item._job_name, task_id = item._task_id)})

    queueDict = {'jobs': queueList}
    for key, value in queueDict.items():
        print(key, value)

    displayQueue = json.htmlsafe_dumps(queueDict)
    return render_template("home.html", queue = displayQueue)

@app.route("/about")
def about():
	return render_template("about.html")

def checkInputs(input_folder, output_folder, primer_scheme_dir, read_file, pipeline, override_data, min_length, max_length):

    errors = {}
    
    if input_folder[-1] == "/":
        input_folder = input_folder[:-1]

    if output_folder[-1] == "/":
        output_folder = output_folder[:-1]

    if primer_scheme_dir[-1] == "/":
        primer_scheme_dir = primer_scheme_dir[:-1]
    
    #give error if input folder path is invalid or empty
    if not os.path.isdir(input_folder):
        errors['input_folder'] = "Invalid path."
    elif len(os.listdir(input_folder)) == 0:
        errors['input_folder'] = "Directory is empty."

    #if no output folder entered, creates one inside of input folder
    if not output_folder:
        output_folder = input_folder + "/output"
    
   # if not os.path.isdir(output_folder):
    #    errors['output_folder'] = "Invalid path."

        #give error if primer schemes folder path is invalid or empty
    if not os.path.isdir(primer_scheme_dir):
        errors['primer_scheme_dir'] = "Invalid path."
    elif len(os.listdir(primer_scheme_dir)) == 0:
        errors['primer_scheme_dir'] = "Directory is empty."

        #if read file is specified by user
    if read_file:
        if not os.path.isfile(read_file):
            errors['read_file'] = "Invalid path/file."
    else:
        #to be filled later
        read_file = ""
    
    #both pipelines running
    if pipeline == "both":
        #if the output folder does not exist, it is created
        if not os.path.exists(output_folder + "/medaka"):
            make_dir = 'mkdir "' + output_folder + '"'
            os.system(make_dir)
            make_dir_m = 'mkdir "' + output_folder + '/medaka"'
            os.system(make_dir_m)
        #if the output folder does not exist, it is created
        if not os.path.exists(output_folder + "/nanopolish"):
            make_dir = 'mkdir "' + output_folder + '"'
            os.system(make_dir)
            make_dir_n = 'mkdir "' + output_folder + '/nanopolish"'
            os.system(make_dir_n)
        #only one pipeline running
        else:
            #if the output folder does not exist, it is created
            if not os.path.exists(output_folder):
                make_dir = 'mkdir "' + output_folder + '"'
                os.system(make_dir)
                
    #override files in output folder checks
    if pipeline == "both":
        if check_override(output_folder + "/medaka", override_data):
            # removeFiles(output_folder + "/medaka", override_data, job_name)
            os.system('rm ' + output_folder + '/medaka/all_cmds_log.txt')
            flash("Output folder has been overwritten.")

        if check_override(output_folder + "/medaka", override_data):
            # removeFiles(output_folder + "/nanopolish", override_data, job_name)
            os.system('rm ' + output_folder + '/nanopolish/all_cmds_log.txt')
            flash("Output folder has been overwritten.")

    if pipeline != "both":
        if check_override(output_folder, override_data):
            # removeFiles(output_folder, override_data, job_name)
            os.system('rm ' + output_folder + '/all_cmds_log.txt')
            flash("Output folder has been overwritten.")
        # Make empty log file for initial progress rendering
            make_log = 'touch \"' + output_folder + '\"/all_cmds_log.txt'
            os.system(make_log)
        else:
            # Make empty log file for initial progress rendering
            make_log_m = 'touch \"' + output_folder + '\"/medaka/all_cmds_log.txt'
            make_log_n = 'touch \"' + output_folder + '\"/nanopolish/all_cmds_log.txt'
            os.system(make_log_m)
            os.system(make_log_n)

        #check length parameters are valid
        if min_length.isdigit() == False:
            errors['invalid_length'] = "Invalid minimum length."
            if max_length.isdigit() == False:
                errors['invalid_length'] = "Invalid maximum and minimum length."
        elif max_length.isdigit() == False:
            errors['invalid_length'] = "Invalid maximum length."
        elif int(max_length) < int(min_length):
            errors['invalid_length'] = "Invalid parameters: Maximum length smaller than minimum length."

    return errors
    

@app.route("/parameters", methods = ["POST","GET"])
def parameters():
    if request.method == "POST":
        #get parameters
        job_name = request.form.get('job_name')
        input_folder = request.form.get('input_folder')
        read_file = request.form.get('read_file')
        primer_scheme_dir = request.form.get('primer_scheme_dir')
        primer_scheme = request.form.get('primer_scheme')
        primer_type = request.form.get('primer_type')
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
        barcode_type = request.form.get('barcode_type')

        #if user agrees output can override files with the same name in output folder
        if request.form.get('override_data'):
            override_data = True
        else:
            override_data = False

        errors = {}
        errors = checkInputs(input_folder, output_folder, primer_scheme_dir, read_file, pipeline, override_data, min_length, max_length)
        
        if qSys.queue.full():
            errors['full_queue'] = "Job queue is full."
            
        print("Errors: ", errors)
        if len(errors) != 0:
            #Update displayed queue on home page
            queueList = []
            if qSys.queue.empty():
                return render_template("parameters.html", job_name=job_name, queue = None, input_folder=input_folder, output_folder=output_folder, read_file=read_file, pipeline=pipeline, min_length=min_length, max_length=max_length, primer_scheme=primer_scheme, primer_type=primer_type, num_samples=num_samples,primer_scheme_dir=primer_scheme_dir, barcode_type=barcode_type,errors=errors)

            for item in qSys.queue.getItems():
                queueList.append({item._job_name : url_for('progress', job_name=item._job_name, task_id = item._task_id)})

            queueDict = {'jobs': queueList}
            displayQueue = json.htmlsafe_dumps(queueDict)

            return render_template("parameters.html", job_name=job_name, queue = None, input_folder=input_folder, output_folder=output_folder, read_file=read_file, pipeline=pipeline, min_length=min_length, max_length=max_length, primer_scheme=primer_scheme, primer_type=primer_type, num_samples=num_samples,primer_scheme_dir=primer_scheme_dir, barcode_type=barcode_type,errors=errors)

        #no spaces in the job name - messes up commands
        job_name = job_name.replace(" ", "_")

        if pipeline != "both":
            #Create a new instance of the Job class
            new_job = qSys.newJob(job_name, input_folder, read_file, primer_scheme_dir, primer_scheme, primer_type, output_folder, normalise, num_threads, pipeline, min_length, max_length, bwa, skip_nanopolish, dry_run, override_data, num_samples,barcode_type)

            #Add job to queue
            qSys.addJob(new_job)
        #if both pipelines
        else:
            #Create a new medaka instance of the Job class
            new_job_m = qSys.newJob(job_name + "_medaka", input_folder, read_file, primer_scheme_dir, primer_scheme, primer_type, output_folder + "/medaka", normalise, num_threads, "medaka", min_length, max_length, bwa, skip_nanopolish, dry_run, override_data, num_samples,barcode_type)
            #Create a new nanopolish instance of the Job class
            new_job_n = qSys.newJob(job_name + "_nanopolish", input_folder, read_file, primer_scheme_dir, primer_scheme, primer_type, output_folder + "/nanopolish", normalise, num_threads, "nanopolish", min_length, max_length, bwa, skip_nanopolish, dry_run, override_data, num_samples,barcode_type)

            #Add medaka job to queue
            qSys.addJob(new_job_m)
            #Add nanopolish job to queue
            qSys.addJob(new_job_n)

        if pipeline == "both":
            return redirect(url_for('progress', job_name=job_name+"_medaka"))
        else:
            return redirect(url_for('progress', job_name=job_name))

    #Update displayed queue on home page
    queueList = []
    if qSys.queue.empty():
        return render_template("parameters.html", job_name=job_name, queue = None, input_folder=input_folder, output_folder=output_folder, read_file=read_file, pipeline=pipeline, min_length=min_length, max_length=max_length, primer_scheme=primer_scheme, primer_type=primer_type, num_samples=num_samples,primer_scheme_dir=primer_scheme_dir, barcode_type=barcode_type,errors=errors)

    for item in qSys.queue.getItems():
        queueList.append({item._job_name : url_for('progress', job_name=item._job_name, task_id = item._task_id)})

    queueDict = {'jobs': queueList}
    displayQueue = json.htmlsafe_dumps(queueDict)
    return render_template("parameters.html", job_name=job_name, queue = None, input_folder=input_folder, output_folder=output_folder, read_file=read_file, pipeline=pipeline, min_length=min_length, max_length=max_length, primer_scheme=primer_scheme, primer_type=primer_type, num_samples=num_samples,primer_scheme_dir=primer_scheme_dir, barcode_type=barcode_type,errors=errors)


@app.route("/error/<job_name>", methods = ["POST","GET"])
def error(job_name):
    print("does it also hit this?")
    job = qSys.getJobByName(job_name)
    if (job != None):
        input_folder = job.input_folder
        output_folder = job.output_folder
        read_file = job.read_file
        pipeline = job.pipeline
        min_length = job.min_length
        max_length = job.max_length
        primer_scheme = job.primer_scheme
        primer_scheme_dir = job.primer_scheme_dir
        primer_type = job.primer_type
        num_samples = job.num_samples
        barcode_type = job.barcode_type   
        
    if request.method == "POST":
        #get parameters
        job_name = request.form.get('job_name')
        input_folder = request.form.get('input_folder')
        read_file = request.form.get('read_file')
        primer_scheme_dir = request.form.get('primer_scheme_dir')
        primer_scheme = request.form.get('primer_scheme')
        primer_type = request.form.get('primer_type')
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
        errors = checkInputs(input_folder, output_folder, primer_scheme_dir, read_file, pipeline, override_data, min_length, max_length)
        
        if qSys.queue.full():
            errors['full_queue'] = "Job queue is full."

        print("Errors: ", errors)
        if len(errors) != 0:
            #Update displayed queue on home page
            queueList = []
            if qSys.queue.empty():
                return render_template("parameters.html", name=job_name, input_folder=input_folder, output_folder=output_folder, read_file=read_file, pipeline=pipeline, min_length=min_length, max_length=max_length, primer_scheme=primer_scheme, primer_type=primer_type, num_samples=num_samples,barcode_type=barcode_type,primer_scheme_dir=primer_scheme_dir, errors=errors)
            for item in qSys.queue.getItems():
                queueList.append({item._job_name : url_for('progress', job_name=item._job_name, task_id = item._task_id)})

            queueDict = {'jobs': queueList}
            displayQueue = json.htmlsafe_dumps(queueDict)

            return render_template("parameters.html", job_name=job_name, input_folder=input_folder, output_folder=output_folder, read_file=read_file, pipeline=pipeline, min_length=min_length, max_length=max_length, primer_scheme=primer_scheme, primer_type=primer_type, num_samples=num_samples,barcode_type=barcode_type, primer_scheme_dir=primer_scheme_dir,errors=errors)

        #no spaces in the job name - messes up commands
        job_name = job_name.replace(" ", "_")

        if pipeline != "both":
            #Create a new instance of the Job class
            new_job = qSys.newJob(job_name, input_folder, read_file, primer_scheme_dir, primer_scheme, primer_type, output_folder, normalise, num_threads, pipeline, min_length, max_length, bwa, skip_nanopolish, dry_run, override_data, num_samples, barcode_type)

            #Add job to queue
            qSys.addJob(new_job)
        #if both pipelines
        else:
            #Create a new medaka instance of the Job class
            new_job_m = qSys.newJob(job_name + "_medaka", input_folder, read_file, primer_scheme_dir, primer_scheme, primer_type, output_folder + "/medaka", normalise, num_threads, "medaka", min_length, max_length, bwa, skip_nanopolish, dry_run, override_data, num_samples,barcode_type)
            #Create a new nanopolish instance of the Job class
            new_job_n = qSys.newJob(job_name + "_nanopolish", input_folder, read_file, primer_scheme_dir, primer_scheme, primer_type, output_folder + "/nanopolish", normalise, num_threads, "nanopolish", min_length, max_length, bwa, skip_nanopolish, dry_run, override_data, num_samples,barcode_type)

            #Add medaka job to queue
            qSys.addJob(new_job_m)
            #Add nanopolish job to queue
            qSys.addJob(new_job_n)

        if pipeline == "both":
            return redirect(url_for('progress', job_name=job_name+"_medaka"))
        else:
            return redirect(url_for('progress', job_name=job_name))

    #Update displayed queue on home page
    queueList = []
    if qSys.queue.empty():
        return render_template("parameters.html", job_name=job_name, queue = None, input_folder=input_folder, output_folder=output_folder, read_file=read_file, pipeline=pipeline, min_length=min_length, max_length=max_length, primer_scheme=primer_scheme, primer_type=primer_type, num_samples=num_samples,primer_scheme_dir=primer_scheme_dir, barcode_type=barcode_type,errors=errors)

    for item in qSys.queue.getItems():
        queueList.append({item._job_name : url_for('progress', job_name=item._job_name, task_id = item._task_id)})

    queueDict = {'jobs': queueList}
    displayQueue = json.htmlsafe_dumps(queueDict)
    return render_template("parameters.html", job_name=job_name, queue = displayQueue, input_folder=input_folder, output_folder=output_folder, read_file=read_file, pipeline=pipeline, min_length=min_length, max_length=max_length, primer_scheme=primer_scheme, primer_type=primer_type, num_samples=num_samples,primer_scheme_dir=primer_scheme_dir,barcode_type=barcode_type,errors=errors)

@app.route("/progress/<job_name>", methods = ["GET", "POST"])
def progress(job_name):
    #print(jobQueue.getJob)
    job = qSys.getJobByName(job_name)
    # job_name = job.job_name

    path = job.output_folder
    path +="/all_cmds_log.txt"

    print(path)
    with open(path, "r") as f:
        outputLog = f.read().replace("\n","<br/>")

    if re.findall(r':D', outputLog):
        frac = "3"
    elif len(re.findall(r'STARTING', outputLog)) == 2:
        frac = "1"
    elif len(re.findall(r'STARTING', outputLog)) > 2:
        frac = "2"
    else:
        frac = "0"

    pattern = "^ERROR"
    error = 0;
    with open(path, "r") as f:
        for line in f:
            result = re.match(pattern, line)
            if (result):
                error = 1;

    # num_in_queue = jobQueue.getJobNumber(job_name)
    # queue_length = jobQueue.getNumberInQueue()
    num_in_queue = qSys.queue.getJobNumber(job_name)
    queue_length = qSys.queue.getNumberInQueue()
    input_folder = job.input_folder
    output_folder = job.output_folder
    read_file = job.read_file
    pipeline = job.pipeline
    min_length = job.min_length
    max_length = job.max_length
    primer_scheme = job.primer_scheme
    primer_type = job.primer_type
    num_samples = job.num_samples
    barcode_type = job.barcode_type

    return render_template("progress.html", outputLog=outputLog, num_in_queue=num_in_queue, queue_length=queue_length, job_name=job_name, frac=frac, input_folder=input_folder, output_folder=output_folder, read_file=read_file, pipeline=pipeline, min_length=min_length, max_length=max_length, primer_scheme=primer_scheme, primer_type=primer_type, num_samples=num_samples,barcode_type=barcode_type,error=error)

@app.route("/abort/<job_name>", methods = ["GET", "POST"])
def abort(job_name):
    job = qSys.getJobByName(job_name)
    task = job.task_id
    celery.control.revoke(task,terminate=True, signal='SIGKILL')
    qSys.removeJob(job_name)

    return redirect(url_for("home"))
    # return "TRYING TO ABORT"

#not sure if this should be a get method
@app.route("/output/<job_name>", methods = ["GET", "POST"])
def output(job_name): #need to update to take in job name as parameter
    #job_name = request.args.get('job_name')
    #output_folder = request.args.get('output_folder')
    job = qSys.getJobByName(job_name)
    output_folder = job._output_folder
    save_graphs = job.save_graphs
    save_able = 'Disabled'
    if(save_graphs):
        save_able = 'Enabled'
    output_files = []
    barplots = []
    boxplots = []
    static = os.path.dirname(os.path.realpath(__file__))+'/static/'  # instead of os.getcwd()
    if output_folder:
        if os.path.exists(output_folder):
            for (dirpath, dirnames, filenames) in os.walk(output_folder):
                for name in filenames:
                    if fnmatch.fnmatch(name, '*barplot.png'):
                        barplots.append('../static/'+name)
                        if save_graphs:
                            os.system('cp '+ os.path.join(dirpath,name) + ' ' + static)
                    if fnmatch.fnmatch(name, '*boxplot.png'):
                        boxplots.append('../static/'+name)
                        if save_graphs:
                            os.system('cp '+ os.path.join(dirpath,name) + ' ' + static)
                output_files.extend(filenames)

        if request.method == "POST":
            plot = request.form.get('plot')
            save = request.form.get('save')
            if request.form['submit_button'] == 'Confirm':
                if save == 'enable':
                    job.enableSave()
                    save_able = 'Enabled'
                if save == 'disable':
                    for plot in barplots:
                        os.system('rm '+ plot[3:])
                    for plot in boxplots:
                        os.system('rm '+ plot[3:])
                    job.disableSave()
                    save_able = 'Disabled'
                return render_template("output.html", job_name=job_name, output_folder=output_folder, output_files=output_files, save_graphs=save_able)
            else:
                if save_graphs:
                    if request.form['submit_button'] == 'Preview':
                        if plot == 'barplot':
                            return render_template("output.html", job_name=job_name, output_folder=output_folder, output_files=output_files, barplots=barplots, save_graphs=save_able)
                        if plot == 'boxplot':
                            return render_template("output.html", job_name=job_name, output_folder=output_folder, output_files=output_files, boxplots=boxplots, save_graphs=save_able)
                        if plot == 'both':
                            return render_template("output.html", job_name=job_name, output_folder=output_folder, output_files=output_files, barplots=barplots, boxplots=boxplots, save_graphs=save_able)

                    #if request.form['submit_button'] == 'Download':
                    #    return render_template("output.html", job_name=job_name, output_folder=output_folder, output_files=output_files, boxplots=boxplots, save_graphs=save_able)

    return render_template("output.html", job_name=job_name, output_folder=output_folder, output_files=output_files, save_graphs=save_able)


if __name__ == "__main__":
    app.run(debug=True)
