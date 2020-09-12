from flask import Flask, render_template, request, redirect, url_for, json, jsonify, flash
#from src.job import Job
import src.queue as q
import os
import base64
from celery import Celery
import subprocess
from src.system import System
from celery.utils.log import get_task_logger
import random
import time
import fnmatch
import subprocess
from subprocess import Popen, PIPE, CalledProcessError
import sys
import re
import threading
import gzip

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

#Define maximum queue size
max_queue_size = 10

#Create a System object with a queue of length maximum_queue_size
qSys = System(max_queue_size)

@app.route('/getCheckTasksUrl', methods = ['POST'])
def getCheckTasksUrl():
    return jsonify({}), 202, {'Location': url_for('checkTasks')}

@app.route('/checkTasks')
def checkTasks():
    queueList = []
    completedList = []
    changed = False

    for job in qSys.queue.getItems():
        if job.task_id:
            task = executeJob.AsyncResult(job.task_id)
            if task.ready():
                qSys.moveJobToComplete(job.job_name)
                changed = True
                #Don't add this job to queueList (we don't want it to display in the queue)
                continue
        queueList.append({job.job_name : url_for('progress', job_name=job.job_name, task_id = job.task_id)})

    for job in qSys.completed:
        completedList.append({job.job_name : url_for('delete', job_name=job.job_name)})

    queueDict = {'jobs': queueList}
    for key, value in queueDict.items():
        print(key, value)

    completedDict = {'jobs': completedList}
    for key, value in completedDict.items():
        print(key, value)

    return json.htmlsafe_dumps({'changed': changed, 'queue': queueDict, 'completed': completedDict})


def check_override(output_folder, override_data):
    if(not os.path.exists(output_folder)):
        return True
    dir_files = os.listdir(output_folder)
    if len(dir_files) > 0 and override_data is False:
        return True
    return False


@celery.task(bind=True)
def executeJob(self, job_name, gather_cmd, demult_cmd, min_cmd):
    logger.info("In celery task, executing job...")

    self.update_state(state='PROGRESS', meta={'current':10, 'status':'Beginning execution'})

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
            n = 90

        self.update_state(state='PROGRESS', meta={'current': n, 'status': status, 'command': cmd})
        returnCode = po.returncode
        if returnCode != 0:
            self.update_state(state='FAILURE', meta={'current': n, 'status': 'Command failed', 'command': cmd})
            raise Exception("Command {} got return code {}.\nSTDOUT: {}\nSTDERR: {}".format(cmd, returnCode, stdout, stderr))

        print("JOB CMD {} RETURNED: {}".format(cmd, returnCode))

    self.update_state(state='FINISHED', meta={'current': 100, 'status': 'Finishing', 'result': returnCode}) #Don't know if this is actually used
    return {'current': 100, 'total': 100, 'status': 'Task completed!', 'result': returnCode}


@app.route('/task/<job_name>', methods = ['POST'])
def task(job_name):
    job = qSys.getJobByName(job_name)
    return jsonify({}), 202, {'Location': url_for('task_status', task_id = job.task_id, job_name = job.job_name)}

@app.route('/status/<task_id>')
def task_status(task_id):
    task = executeJob.AsyncResult(task_id)
    print("TASK.READY: ", task.ready())
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

@app.route("/")
def route():
    return redirect(url_for('home'))

@app.route("/home")
def home():
    #Update displayed queue and completed jobs on home page
    # queueList = []
    # completedList = []

    # checkTasks()

    # def completedToJSON():
    #     for item in qSys.completed:
    #         completedList.append({item.job_name : url_for('output', job_name=item.job_name)})

    #     completedDict = {'jobs': completedList}
    #     for key, value in completedDict.items():
    #         print(key, value)

    #     return json.htmlsafe_dumps(completedDict)

    # def queueToJSON():
    #     for item in qSys.queue.getItems():
    #         queueList.append({item.job_name : url_for('progress', job_name=item.job_name, task_id = item.task_id)})

    #     queueDict = {'jobs': queueList}
    #     for key, value in queueDict.items():
    #         print(key, value)

    #     return json.htmlsafe_dumps(queueDict)
    # if qSys.queue.empty():
    #     displayQueue = None
    # else:
    #     displayQueue = queueToJSON()


    # if not qSys.completed:
    #     displayCompleted = None
    # else:
    #     for j in qSys.completed:
    #         print("COMPLETED JOB: ", j)
    #     displayCompleted = completedToJSON()

    #return render_template("home.html", queue = displayQueue, completed = displayCompleted)
    return render_template("home.html")


@app.route("/about")
def about():
	return render_template("about.html")

def checkInputs(input_folder, output_folder, primer_scheme_dir, read_file, pipeline, override_data, min_length, max_length, job_name):

    errors = {}

    #Check of jobname is used
    if qSys.getJobByName(job_name) is not None:
        errors['job_name'] = "Job Name has already been used."

    if input_folder[-1] == "/":
        input_folder = input_folder[:-1]
    #give error if input folder path is invalid or empty
    if not os.path.isdir(input_folder):
        errors['input_folder'] = "Invalid path."
    elif len(os.listdir(input_folder)) == 0:
        errors['input_folder'] = "Directory is empty."

    #if no output folder entered, creates one inside of input folder
    if not output_folder and not os.path.isdir(input_folder):
        return errors, output_folder
    elif not output_folder and os.path.isdir(input_folder):
        output_folder = input_folder + "/output"


    if output_folder[-1] == "/":
        output_folder = output_folder[:-1]

    if primer_scheme_dir[-1] == "/":
        primer_scheme_dir = primer_scheme_dir[:-1]


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

        if override_data is True and os.path.exists(output_folder):
            remove = "rm -r " + output_folder + "/*"
            os.system(remove)
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

        if check_override(output_folder + "/medaka", override_data) and os.path.exists(input_folder):
            # removeFiles(output_folder + "/medaka", override_data, job_name)
            os.system('rm ' + output_folder + '/medaka/all_cmds_log.txt')
            flash("Warning: Output folder is NOT empty. Please choose another folder or delete/move files in it.")
            errors['override'] = True

        if check_override(output_folder + "/medaka", override_data) and os.path.exists(input_folder):
            # removeFiles(output_folder + "/nanopolish", override_data, job_name)
            os.system('rm ' + output_folder + '/nanopolish/all_cmds_log.txt')
            flash("Warning: Output folder is NOT empty. Please choose another folder or delete/move files in it.")
            errors['override'] = True

        # Make empty log file for initial progress rendering
        make_log_m = 'touch \"' + output_folder + '\"/medaka/all_cmds_log.txt'
        make_log_n = 'touch \"' + output_folder + '\"/nanopolish/all_cmds_log.txt'
        os.system(make_log_m)
        os.system(make_log_n)

    else:
        #if the output folder does not exist, it is created
        if not os.path.exists(output_folder):
            make_dir = 'mkdir "' + output_folder + '"'
            os.system(make_dir)

        if override_data is True:
            remove = "rm -r " + output_folder + "/*"
            os.system(remove)
        elif check_override(output_folder, override_data) and os.path.exists(input_folder):
            # removeFiles(output_folder, override_data, job_name)
            os.system('rm ' + output_folder + '/all_cmds_log.txt')
            flash("Warning: Output folder is NOT empty. Please choose another folder or delete/move files in it.")
            errors['override'] = True
        # Make empty log file for initial progress rendering
        make_log = 'touch \"' + output_folder + '\"/all_cmds_log.txt'
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

    return errors, output_folder

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

        #if no output folder entered, creates one inside of input folder
        if not output_folder:
            output_folder = input_folder + "/output"

        #if user agrees output can override files with the same name in output folder
        if request.form.get('override_data'):
            override_data = True
        else:
            override_data = False

        errors = {}
        errors, output_folder_checked = checkInputs(input_folder, output_folder, primer_scheme_dir, read_file, pipeline, override_data, min_length, max_length,job_name)

        if not output_folder:
            output_folder = output_folder_checked
        print("output folder:", output_folder)

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

            return render_template("parameters.html", job_name=job_name, queue = displayQueue, input_folder=input_folder, output_folder=output_folder, read_file=read_file, pipeline=pipeline, min_length=min_length, max_length=max_length, primer_scheme=primer_scheme, primer_type=primer_type, num_samples=num_samples,primer_scheme_dir=primer_scheme_dir, barcode_type=barcode_type,errors=errors)

        #no spaces in the job name - messes up commands
        job_name = job_name.replace(" ", "_")

        if pipeline != "both":
            #Create a new instance of the Job class
            new_job = qSys.newJob(job_name, input_folder, read_file, primer_scheme_dir, primer_scheme, primer_type, output_folder, normalise, num_threads, pipeline, min_length, max_length, bwa, skip_nanopolish, dry_run, override_data, num_samples,barcode_type)

            #Add job to queue
            qSys.addJob(new_job)
            print("qSys has jobs: ", qSys.printQueue())
            new_task = executeJob.apply_async(args=[new_job.job_name, new_job.gather_cmd, new_job.demult_cmd, new_job.min_cmd])
            new_job.task_id = new_task.id
        #if both pipelines
        else:
            #Create a new medaka instance of the Job class
            new_job_m = qSys.newJob(job_name + "_medaka", input_folder, read_file, primer_scheme_dir, primer_scheme, primer_type, output_folder + "/medaka", normalise, num_threads, "medaka", min_length, max_length, bwa, skip_nanopolish, dry_run, override_data, num_samples,barcode_type)
            #Create a new nanopolish instance of the Job class
            new_job_n = qSys.newJob(job_name + "_nanopolish", input_folder, read_file, primer_scheme_dir, primer_scheme, primer_type, output_folder + "/nanopolish", normalise, num_threads, "nanopolish", min_length, max_length, bwa, skip_nanopolish, dry_run, override_data, num_samples,barcode_type)

            #Add medaka job to queue
            qSys.addJob(new_job_m)
            task_m = executeJob.apply_async(args=[new_job_m.job_name, new_job_m.gather_cmd, new_job_m.demult_cmd, new_job_m.min_cmd])
            new_job_m.task_id = task_m.id
            #Add nanopolish job to queue
            qSys.addJob(new_job_n)
            task_n = executeJob.apply_async(args=[new_job_n.job_name, new_job_n.gather_cmd, new_job_n.demult_cmd, new_job_n.min_cmd])
            new_job_n.task_id = task_n.id

        if pipeline == "both":
            return redirect(url_for('progress', job_name=job_name+"_medaka"))
        else:
            return redirect(url_for('progress', job_name=job_name))

    #Update displayed queue on home page
    queueList = []
    if qSys.queue.empty():
        return render_template("parameters.html", queue=None)

    for item in qSys.queue.getItems():
        queueList.append({item._job_name : url_for('progress', job_name=item._job_name, task_id = item._task_id)})

    queueDict = {'jobs': queueList}
    displayQueue = json.htmlsafe_dumps(queueDict)
    return render_template("parameters.html", queue = displayQueue)

@app.route("/error/<job_name>", methods = ["POST","GET"])
def error(job_name):
    job = qSys.getJobByName(job_name)

    if job != None:
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
        # abort existing job
        task = job.task_id
        celery.control.revoke(task, terminate=True, signal='SIGKILL')
        qSys.removeQueuedJob(job_name)

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
        errors, output_folder_checked = checkInputs(input_folder, output_folder, primer_scheme_dir, read_file, pipeline, override_data, min_length, max_length,job_name)

        if not output_folder:
            output_folder = output_folder_checked

        if qSys.queue.full():
            errors['full_queue'] = "Job queue is full."

        print("Errors: ", errors)
        if len(errors) != 0:
            #Update displayed queue on home page
            queueList = []
            if qSys.queue.empty():
                return render_template("parameters.html", queue=None, job_name=job_name, input_folder=input_folder, output_folder=output_folder, read_file=read_file, pipeline=pipeline, min_length=min_length, max_length=max_length, primer_scheme=primer_scheme, primer_type=primer_type, num_samples=num_samples,barcode_type=barcode_type,primer_scheme_dir=primer_scheme_dir, errors=errors)
            for item in qSys.queue.getItems():
                queueList.append({item.job_name : url_for('progress', job_name=item.job_name, task_id = item.task_id)})

            queueDict = {'jobs': queueList}
            displayQueue = json.htmlsafe_dumps(queueDict)

            return render_template("parameters.html", queue=displayQueue, job_name=job_name, input_folder=input_folder, output_folder=output_folder, read_file=read_file, pipeline=pipeline, min_length=min_length, max_length=max_length, primer_scheme=primer_scheme, primer_type=primer_type, num_samples=num_samples,barcode_type=barcode_type, primer_scheme_dir=primer_scheme_dir,errors=errors)

        #no spaces in the job name - messes up commands
        job_name = job_name.replace(" ", "_")

        if pipeline != "both":
            #Create a new instance of the Job class
            new_job = qSys.newJob(job_name, input_folder, read_file, primer_scheme_dir, primer_scheme, primer_type, output_folder, normalise, num_threads, pipeline, min_length, max_length, bwa, skip_nanopolish, dry_run, override_data, num_samples, barcode_type)

            #Add job to queue
            qSys.addJob(new_job)
            print("qSys has jobs: ", qSys.printQueue())
            new_task = executeJob.apply_async(args=[new_job.job_name, new_job.gather_cmd, new_job.demult_cmd, new_job.min_cmd])
            new_job.task_id = new_task.id

        #if both pipelines
        else:
            #Create a new medaka instance of the Job class
            new_job_m = qSys.newJob(job_name + "_medaka", input_folder, read_file, primer_scheme_dir, primer_scheme, primer_type, output_folder + "/medaka", normalise, num_threads, "medaka", min_length, max_length, bwa, skip_nanopolish, dry_run, override_data, num_samples,barcode_type)
            #Create a new nanopolish instance of the Job class
            new_job_n = qSys.newJob(job_name + "_nanopolish", input_folder, read_file, primer_scheme_dir, primer_scheme, primer_type, output_folder + "/nanopolish", normalise, num_threads, "nanopolish", min_length, max_length, bwa, skip_nanopolish, dry_run, override_data, num_samples,barcode_type)

            #Add medaka job to queue
            qSys.addJob(new_job_m)
            task_m = executeJob.apply_async(args=[new_job_m.job_name, new_job_m.gather_cmd, new_job_m.demult_cmd, new_job_m.min_cmd])
            new_job_m.task_id = task_m.id
            #Add nanopolish job to queue
            qSys.addJob(new_job_n)
            task_n = executeJob.apply_async(args=[new_job_n.job_name, new_job_n.gather_cmd, new_job_n.demult_cmd, new_job_n.min_cmd])
            new_job_n.task_id = task_n.id
        if pipeline == "both":
            return redirect(url_for('progress', job_name=job_name+"_medaka"))
        else:
            return redirect(url_for('progress', job_name=job_name))

    #Update displayed queue on home page
    queueList = []
    if qSys.queue.empty():
        return render_template("parameters.html", job_name=job_name, queue = None, pipeline=pipeline, input_folder=input_folder, output_folder=output_folder, read_file=read_file, min_length=min_length, max_length=max_length, primer_scheme=primer_scheme, primer_type=primer_type, num_samples=num_samples,barcode_type=barcode_type, primer_scheme_dir=primer_scheme_dir)

    for item in qSys.queue.getItems():
        queueList.append({item.job_name : url_for('progress', job_name=item.job_name, task_id = item.task_id)})

    queueDict = {'jobs': queueList}
    displayQueue = json.htmlsafe_dumps(queueDict)
    return render_template("parameters.html", job_name=job_name, queue = displayQueue, pipeline=pipeline, input_folder=input_folder, output_folder=output_folder, read_file=read_file, min_length=min_length, max_length=max_length, primer_scheme=primer_scheme, primer_type=primer_type, num_samples=num_samples,barcode_type=barcode_type, primer_scheme_dir=primer_scheme_dir)

@app.route("/progress/<job_name>", methods = ["GET", "POST"])
def progress(job_name):
    job = qSys.getJobByName(job_name)

    path = job.output_folder
    path +="/all_cmds_log.txt"

    ################## TODO: NEED TO CHANGE
    print(path)
    with open(path, "r") as f:
        outputLog = f.read().replace("\n","<br/>")

    # find the status of the current job
    if re.findall(r':D', outputLog):
        frac = "3"
    elif len(re.findall(r'STARTING', outputLog)) == 2:
        frac = "1"
    elif len(re.findall(r'STARTING', outputLog)) > 2:
        frac = "2"
    else:
        frac = "0"

    # find any errors that occur in the output log
    # might have to change depending on what other letters appear
    pattern = "<br\/>[A-Za-z0-9\s]*ERROR"
    numErrors = len(re.findall(pattern, outputLog, re.IGNORECASE))
    print(numErrors)

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

    return render_template("progress.html", outputLog=outputLog, num_in_queue=num_in_queue,
                            queue_length=queue_length, job_name=job_name, frac=frac, input_folder=input_folder, output_folder=output_folder,
                            read_file=read_file, pipeline=pipeline, min_length=min_length, max_length=max_length, primer_scheme=primer_scheme,
                            primer_type=primer_type, num_samples=num_samples,barcode_type=barcode_type,numErrors=numErrors)

@app.route("/abort/<job_name>", methods = ["GET", "POST"])
def abort(job_name):
    job = qSys.getJobByName(job_name)
    task = job.task_id
    celery.control.revoke(task,terminate=True, signal='SIGKILL')

    # Remove files
    currdir = os.path.dirname(os.path.realpath(__file__))
    path = currdir +'/'+job_name
    print("removing after abort:",path)
    os.system('rm -r ' + path +'*')
    os.system('rm -r ' + currdir + '/tmp*' )

    qSys.removeQueuedJob(job_name)
    return redirect(url_for("home"))
    # return "TRYING TO ABORT"

@app.route("/delete/<job_name>", methods = ["GET", "POST"])
def delete(job_name):
    images = os.path.dirname(os.path.realpath(__file__)) + '/static/' + job_name
    print(images)
    os.system('rm -r ' + images + '*' )
    qSys.removeCompletedJob(job_name)
    return redirect(url_for("home"))

@app.route("/output/<job_name>", methods = ["GET", "POST"])
def output(job_name):
    job = qSys.getJobByName(job_name)
    output_folder = job.output_folder
    save_graphs = job.save_graphs
    save_able = 'Disabled'
    if(save_graphs):
        save_able = 'Enabled'
    create_vcfs = job.create_vcfs
    create_able = 'Disabled'
    if(create_vcfs):
        create_able = 'Enabled'
    output_files = []
    barplots = []
    boxplots = []
    plots_found = False
    vcf_found = False
    vcfs = []
    variant_graphs = []
    static = os.path.dirname(os.path.realpath(__file__))+'/static/'

    if output_folder:
        if os.path.exists(output_folder):
            for (dirpath, dirnames, filenames) in os.walk(output_folder):
                for name in filenames:
                    if fnmatch.fnmatch(name, '*barplot.png'):
                        barplots.append('../static/'+name)
                        plots_found = True
                        if save_graphs:
                            os.system('cp '+ os.path.join(dirpath,name) + ' ' + static)
                    if fnmatch.fnmatch(name, '*boxplot.png'):
                        boxplots.append('../static/'+name)
                        plots_found = True
                        if save_graphs:
                            os.system('cp '+ os.path.join(dirpath,name) + ' ' + static)
                    if fnmatch.fnmatch(name, '*.pass.vcf.gz'):
                        vcf_found = True
                        vcfs.append(os.path.join(dirpath,name))
                output_files.extend(filenames)

        if create_vcfs:
            for vcf in vcfs:
                with gzip.open(vcf, "rt") as f:
                    graph = []
                    max_DP = 0
                    graph.append(vcf)
                    for line in f:
                        point = []
                        if re.match("^[A-Z]", line):
                            m = re.split("\\t", line)
                            if m:
                                point.append(int(m[1]))  #position of variant
                                point.append(m[3])  #original/reference value
                                point.append(m[4])  #original/reference value
                                depth = re.sub(r';.*', "", m[7])
                                if job.pipeline == "medaka":
                                    depth = int(re.sub("DP=","",depth))
                                elif job.pipeline == "nanopolish":
                                    depth = int(re.sub("TotalReads=","",depth))
                                if depth > max_DP:
                                    max_DP = depth
                                point.append(depth)  #read depth value
                                graph.append(point)
                    graph.append(max_DP)
                variant_graphs.append(graph)

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
                if save == 'enable_vcf':
                    job.enableVCF()
                    create_able = 'Enabled'
                    if not variant_graphs:
                        for vcf in vcfs:
                            with gzip.open(vcf, "rt") as f:
                                graph = []
                                max_DP = 0
                                graph.append(vcf)
                                for line in f:
                                    point = []
                                    if re.match("^[A-Z]", line):
                                        m = re.split("\\t", line)
                                        if m:
                                            point.append(int(m[1]))  #position of variant
                                            point.append(m[3])  #original/reference value
                                            point.append(m[4])  #original/reference value
                                            depth = re.sub(r';.*', "", m[7])
                                            if job.pipeline == "medaka":
                                                depth = int(re.sub("DP=","",depth))
                                            elif job.pipeline == "nanopolish":
                                                depth = int(re.sub("TotalReads=","",depth))
                                            if depth > max_DP:
                                                max_DP = depth
                                            point.append(depth)  #read depth value
                                            graph.append(point)
                                graph.append(max_DP)
                            variant_graphs.append(graph)
                if save == 'disable_vcf':
                    job.disableVCF()
                    create_able = 'Disabled'
                return render_template("output.html", job_name=job_name, output_folder=output_folder, output_files=output_files, save_graphs=save_able, variant_graphs=variant_graphs, create_vcfs=create_able, plots_found=plots_found, vcf_found=vcf_found)
            else:
                if save_graphs:
                    if request.form['submit_button'] == 'Preview':
                        if plot == 'barplot':
                            return render_template("output.html", job_name=job_name, output_folder=output_folder, output_files=output_files, barplots=barplots, save_graphs=save_able, variant_graphs=variant_graphs, create_vcfs=create_able, plots_found=plots_found, vcf_found=vcf_found)
                        if plot == 'boxplot':
                            return render_template("output.html", job_name=job_name, output_folder=output_folder, output_files=output_files, boxplots=boxplots, save_graphs=save_able, variant_graphs=variant_graphs, create_vcfs=create_able, plots_found=plots_found, vcf_found=vcf_found)
                        if plot == 'both':
                            return render_template("output.html", job_name=job_name, output_folder=output_folder, output_files=output_files, barplots=barplots, boxplots=boxplots, save_graphs=save_able, variant_graphs=variant_graphs, create_vcfs=create_able, plots_found=plots_found, vcf_found=vcf_found)

    return render_template("output.html", job_name=job_name, output_folder=output_folder, output_files=output_files, save_graphs=save_able, variant_graphs=variant_graphs, create_vcfs=create_able, plots_found=plots_found, vcf_found=vcf_found)


if __name__ == "__main__":
    app.run(debug=True)
