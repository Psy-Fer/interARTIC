import os
#from .tasks import executeJob
from flask import jsonify, url_for
import subprocess
from celery.app.control import Inspect
import celery

import csv, subprocess, time

class Job:
    def __init__(self, job_name, input_folder, read_file, primer_scheme, output_folder, normalise, num_threads, pipeline, min_length, max_length, bwa, skip_nanopolish, dry_run, override_data, num_samples):
        self._job_name = job_name
        self._input_folder = input_folder
        self._read_file = read_file
        self._primer_scheme = primer_scheme
        self._output_folder = output_folder
        self._normalise = normalise
        self._num_threads = num_threads
        self._pipeline = pipeline
        self._min_length = min_length
        self._max_length = max_length
        self._bwa = bwa
        self._skip_nanopolish = skip_nanopolish
        self._dry_run = dry_run
        self._override_data = override_data
        self._num_samples = num_samples
        self._gather_cmd = self.__generateGatherCmd()
        self._demult_cmd = self.__generateDemultCmd()
        self._min_cmd = self.__generateMinionCmd()
        self._task_id = None


    @property
    def get_job_name(self):
        return self._job_name

    @property
    def input_folder(self):
        return self._input_folder

    @property
    def read_file(self):
        return self._read_file

    @property
    def primer_scheme(self):
        return self._primer_scheme

    @property
    def output_folder(self):
        return self._output_folder

    @property
    def normalise(self):
        return self._normalise

    @property
    def num_threads(self):
        return self._num_threads

    @property
    def pipeline(self):
        return self._pipeline

    @property
    def min_length(self):
        return self._min_length

    @property
    def max_length(self):
        return self._max_length

    @property
    def bwa(self):
        return self._bwa

    @property
    def skip_nanopolish(self):
        return self._skip_nanopolish

    @property
    def dry_run(self):
        return self._dry_run

    @property
    def override_data(self):
        return self._override_data

    @property
    def num_samples(self):
        return self._num_samples

    @property
    def gather_cmd(self):
        return self._gather_cmd

    @property
    def demult_cmd(self):
        return self._demult_cmd


    @property
    def min_cmd(self):
        return self._min_cmd

    @property
    def task_id(self):
        return self._task_id

    @task_id.setter
    def task_id(self, val):
        if val:
            self._task_id = val


    def __generateGatherCmd(self):
        if self._pipeline == "medaka":
            gather_cmd = "echo '*****STARTING GATHER COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; artic gather --min-length " + self._min_length + " --max-length " + self._max_length + " --prefix " + self._job_name + " --directory " + self._input_folder +" --no-fast5s" + " >> " + self._output_folder + "/all_cmds_log.txt 2>>" + self._output_folder + "/all_cmds_log.txt"
        elif self._pipeline == "nanopolish":
            gather_cmd = "echo '*****STARTING GATHER COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; artic gather --min-length " + self._min_length + " --max-length " + self._max_length + " --prefix " + self._job_name + " --directory " + self._input_folder + " --fast5-directory " + self._input_folder + "/fast5_pass" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
        elif self._pipeline == "both":
            gather_cmd = "echo 'no gather command for both pipelines yet'"
        return gather_cmd

    def __generateDemultCmd(self):
        demult_cmd = "echo '*****STARTING DEMULTUIPLEX COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; artic demultiplex --threads " + self._num_threads + " " + self._job_name + "_fastq_pass.fastq" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
        return demult_cmd

    def __generateMinionCmd(self):
        if self._num_samples == "single":
            #if read file is provided by user
            if self._read_file != "":
                if self._pipeline == "medaka":
                    minion_cmd = "echo '*****STARTING MINION COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; artic minion --minimap2 --medaka --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._input_folder + "/primer_schemes --read-file " + self._read_file + " " + self._primer_scheme + " \"" + self._job_name + "\"" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
                elif self._pipeline == "nanopolish":
                    minion_cmd = "echo '*****STARTING MINION COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; artic minion --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._input_folder + "/primer_schemes --read-file " + self._read_file + " --fast5-directory " + self._input_folder + "/fast5_pass --sequencing-summary " + self._input_folder + "/*sequencing_summary*.txt " + self._primer_scheme + " " + self._job_name + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
                elif self._pipeline == "both":
                    minion_cmd = ""
            #if read file isn't provided by user
            else:
                if self._pipeline == "medaka":
                    minion_cmd = "echo '*****STARTING MINION COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; artic minion --minimap2 --medaka --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._input_folder + "/primer_schemes --read-file ./" + self._job_name + "_fastq_pass.fastq " + self._primer_scheme + " \"" + self._job_name + "\"" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
                elif self._pipeline == "nanopolish":
                    minion_cmd = "echo '*****STARTING MINION COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; artic minion --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._input_folder + "/primer_schemes --read-file ./" + self._job_name + "_fastq_pass.fastq --fast5-directory " + self._input_folder + "/fast5_pass --sequencing-summary " + self._input_folder + "/*sequencing_summary*.txt " + self._primer_scheme + " " + self._job_name + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
                elif self._pipeline == "both":
                    minion_cmd = ""
        elif self._num_samples == "multiple":
            #going to run multiple minion cmds
            minion_cmd = "echo '*****STARTING MINION COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
            if self._pipeline == "medaka":
                #open the csv file
                csv_filepath = self._input_folder + '/sample-barcode.csv'
                if self._input_folder.startswith('C:\\'):
                    run_name = self._input_folder.split('\\')[-2]
                else:
                    run_name = self._input_folder.split('/')[-2]
                #open csv file
                with open(csv_filepath,'rt')as f:
                    data = csv.reader(f)
                    for row in data:
                        sample_name = row[0]
                        barcode = row[1]
                        #TODO - need to add this as option for user input
                        primer_type = 'artic'
                        #create directory for barcode with naming system
                        dir_path = self._output_folder + "/" + primer_type + "_" + sample_name + "_" + run_name + "_" + barcode + "_" + self._pipeline
                        minion_cmd = minion_cmd + "; mkdir " + dir_path
                        #append minion cmd in barcode directory
                        minion_cmd = minion_cmd + "; artic minion --minimap2 --medaka --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._input_folder + "/primer_schemes --read-file ./" + self._job_name + "_fastq_pass-" + barcode + ".fastq " + self._primer_scheme + " " + self._job_name + "_" + barcode + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
                        #output goes into current directory so this moves all output files to correct folder
                        minion_cmd = minion_cmd + "; mv " + self._job_name + "_" + barcode + "* " + dir_path

            elif self._pipeline == "nanopolish":
                #open the csv file
                csv_filepath = self._input_folder + '/sample-barcode.csv'
                if self._input_folder.startswith('C:\\'):
                    run_name = self._input_folder.split('\\')[-2]
                else:
                    run_name = self._input_folder.split('/')[-2]
                #open csv file
                with open(csv_filepath,'rt')as f:
                    data = csv.reader(f)
                    for row in data:
                        sample_name = row[0]
                        barcode = row[1]
                        #TODO - need to add this as option for user input
                        primer_type = 'artic'
                        #create directory for barcode with naming system
                        dir_path = self._output_folder + "/" + primer_type + "_" + sample_name + "_" + run_name + "_" + barcode + "_" + self._pipeline
                        minion_cmd = minion_cmd + "; mkdir " + dir_path
                        #append minion cmd in barcode directory
                        minion_cmd = minion_cmd + "; artic minion --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._input_folder + "/primer_schemes --read-file  ./" + self._job_name + "_fastq_pass-" + barcode + ".fastq --fast5-directory " + self._input_folder + "/fast5_pass --sequencing-summary " + self._input_folder + "/*sequencing_summary*.txt " + self._primer_scheme + " " + self._job_name + "_" + barcode + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
                        #output goes into current directory so this moves all output files to correct folder
                        minion_cmd = minion_cmd + "; mv ./" + self._job_name + "_" + barcode + "* " + dir_path
            elif self._pipeline == "both":
                minion_cmd = "echo 'no minion command for both pipelines yet'"

        minion_cmd = minion_cmd + "; mv ./" + self._job_name + "* " + self._output_folder + "; \necho 'Job: " + self._job_name + " is finished running :D'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt" 

        return minion_cmd

    def executeCmds(self):
        cmd_combine = ""
        if self._num_samples == "single":
            #create string of all cmds want to run
            cmd_combine = self._gather_cmd + ";" + self._min_cmd

        if self._num_samples == "multiple":
            cmd_combine = self._gather_cmd + ";" + self._demult_cmd + ";" + minion_string

        #start process that runs these cmds in the background
        p = subprocess.Popen(cmd_combine, shell=True)

    def execute(self):
        # Execute this job
        # Run gather command
        # Run minion command
        # print("EXECUTING JOB: ", self._job_name)
        # os.system(self._gather_cmd)
        # os.system(self._min_cmd)
        # # Not sure if i need to do anything here to direct output???
        # os.system('mv ' + self._job_name + '* ' + self._output_folder)
        print("IN JOB")

        #task = celery.current_app.send_task('myapp.tasks.executeJob')
        #print(task.get())
        #print(task.state())
        print("IN JOB PT 2")
        #return jsonify({}), 202, {'Location': url_for('taskstatus',task_id=task.id)}


    def abort(self):
        # If job is running, abort it and remove output
        pass
