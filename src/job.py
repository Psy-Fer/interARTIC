import os
#from .tasks import executeJob
from flask import jsonify, url_for
import subprocess
from celery.app.control import Inspect
import celery

import csv, subprocess, time

class Job:
    def __init__(self, job_name, input_folder, read_file, primer_scheme_dir, primer_scheme, primer_type, output_folder, normalise, num_threads, pipeline, min_length, max_length, bwa, skip_nanopolish, dry_run, override_data, num_samples, barcode_type):
        self._job_name = job_name
        self._input_folder = input_folder
        self._read_file = read_file
        self._primer_scheme_dir = primer_scheme_dir
        self._primer_scheme = primer_scheme
        self._primer_type = primer_type
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
        self._save_graphs = True
        self._create_vcfs = True
        self._barcode_type = barcode_type
        self._gather_cmd = self.__generateGatherCmd()
        self._demult_cmd = self.__generateDemultCmd()
        self._min_cmd = self.__generateMinionCmd()
        self._task_id = None

    @property
    def job_name(self):
        return self._job_name

    @property
    def input_folder(self):
        return self._input_folder

    @property
    def read_file(self):
        return self._read_file

    @property
    def primer_scheme_dir(self):
        return self._primer_scheme_dir

    @property
    def primer_scheme(self):
        return self._primer_scheme

    @property
    def primer_type(self):
        return self._primer_type

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
    def save_graphs(self):
        return self._save_graphs

    @property
    def create_vcfs(self):
        return self._create_vcfs

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
    
    @property
    def barcode_type(self):
        return self._barcode_type

    @task_id.setter
    def task_id(self, val):
        if val:
            self._task_id = val


    def __generateGatherCmd(self):
        gather_cmd = ""
        # if job is running medaka 
        if self._pipeline == "medaka":
            gather_cmd = "echo '*****STARTING GATHER COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; artic gather --min-length " + self._min_length + " --max-length " + self._max_length + " --prefix " + self._job_name + " --directory " + self._input_folder +" --no-fast5s" + " >> " + self._output_folder + "/all_cmds_log.txt 2>>" + self._output_folder + "/all_cmds_log.txt"
        # if job is running nanopolish
        elif self._pipeline == "nanopolish":
            gather_cmd = "echo '*****STARTING GATHER COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; artic gather --min-length " + self._min_length + " --max-length " + self._max_length + " --prefix " + self._job_name + " --directory " + self._input_folder + " --fast5-directory " + self._input_folder + "/fast5_pass" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
        #change directory into output folder
        gather_cmd = "cd " + self._output_folder + "; " + gather_cmd
        return gather_cmd

    def __generateDemultCmd(self):
        demult_cmd = ""
        #demultiplex cmd only runs on multiple samples
        if self._num_samples == "multiple":
            if self._barcode_type == "rapid":
                demult_cmd = "echo '*****STARTING PORECHOP COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; echo 'porechop --verbosity 2 --untrimmed -i " + self._job_name + "_fastq_pass.fastq -b ./ --rapid_barcodes --discard_middle --barcode_threshold 80 --threads " + self._num_threads + " --check_reads 10000 --barcode_diff 5 > " + self._job_name + "_fastq_pass.fastq.demultiplexreport.txt' >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; porechop --verbosity 2 --untrimmed -i " + self._job_name + "_fastq_pass.fastq -b ./ --rapid_barcodes --discard_middle --barcode_threshold 80 --threads " + self._num_threads + " --check_reads 10000 --barcode_diff 5 > " + self._job_name + "_fastq_pass.fastq.demultiplexreport.txt;"
                #open the csv file
                csv_filepath = self._input_folder + '/sample-barcode.csv'
                # check 
                if self._input_folder.startswith('C:\\'):
                    run_name = self._input_folder.split('\\')[-2]
                else:
                    run_name = self._input_folder.split('/')[-2]
                #open csv file
                with open(csv_filepath,'rt')as f:
                    data = csv.reader(f)
                    for row in data:
                        barcode = row[1]
                        demult_cmd = demult_cmd + " mv " + barcode + ".fastq " + self._job_name + "_fastq_pass-" + barcode + ".fastq;"
            else:
                demult_cmd = "echo '*****STARTING DEMULTIPLEX COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; artic demultiplex --threads " + self._num_threads + " " + self._job_name + "_fastq_pass.fastq" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
            #change directory into output folder
            demult_cmd = "cd " + self._output_folder + "; " + demult_cmd
        return demult_cmd

    def __generateMinionCmd(self):
        minion_cmd = ""
        # if only one sample in input
        if self._num_samples == "single":
            # if read file is provided by user
            if self._read_file != "":
                # if medaka is chosen
                if self._pipeline == "medaka":
                    minion_cmd = "echo '*****STARTING MINION COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; artic minion --minimap2 --medaka --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._primer_scheme_dir + " --read-file " + self._read_file + " " + self._primer_scheme + " \"" + self._job_name + "\"" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
                # if nanopolish is chosen
                elif self._pipeline == "nanopolish":
                    minion_cmd = "echo '*****STARTING MINION COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; artic minion --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._primer_scheme_dir + " --read-file " + self._read_file + " --fast5-directory " + self._input_folder + "/fast5_pass --sequencing-summary " + self._input_folder + "/*sequencing_summary*.txt " + self._primer_scheme + " " + self._job_name + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
            #if read file isn't provided by user
            else:
                # if medaka is chosen
                if self._pipeline == "medaka":
                    minion_cmd = "echo '*****STARTING MINION COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; artic minion --minimap2 --medaka --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._primer_scheme_dir + " --read-file ./" + self._job_name + "_fastq_pass.fastq " + self._primer_scheme + " \"" + self._job_name + "\"" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
                # if nanopolish is chosen
                elif self._pipeline == "nanopolish":
                    minion_cmd = "echo '*****STARTING MINION COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; artic minion --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._primer_scheme_dir + " --read-file ./" + self._job_name + "_fastq_pass.fastq --fast5-directory " + self._input_folder + "/fast5_pass --sequencing-summary " + self._input_folder + "/*sequencing_summary*.txt " + self._primer_scheme + " " + self._job_name + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
        # if multiple samples in input
        elif self._num_samples == "multiple":
            minion_cmd = "echo '*****STARTING MINION COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
            # if medaka is chosen
            if self._pipeline == "medaka":
                #open the csv file
                csv_filepath = self._input_folder + '/sample-barcode.csv'
                # check 
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
                        #create directory for barcode with naming system
                        dir_path = self._output_folder + "/" + self._primer_type + "_" + sample_name + "_" + run_name + "_" + barcode + "_" + self._pipeline
                        minion_cmd = minion_cmd + "; mkdir " + dir_path
                        #append minion cmd in barcode directory
                        minion_cmd = minion_cmd + "; artic minion --minimap2 --medaka --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._primer_scheme_dir + " --read-file ./" + self._job_name + "_fastq_pass-" + barcode + ".fastq " + self._primer_scheme + " " + self._job_name + "_" + barcode + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
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
                        #create directory for barcode with naming system
                        dir_path = self._output_folder + "/" + self._primer_type + "_" + sample_name + "_" + run_name + "_" + barcode + "_" + self._pipeline
                        minion_cmd = minion_cmd + "; mkdir " + dir_path
                        #append minion cmd in barcode directory
                        minion_cmd = minion_cmd + "; artic minion --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._primer_scheme_dir + " --read-file  ./" + self._job_name + "_fastq_pass-" + barcode + ".fastq --fast5-directory " + self._input_folder + "/fast5_pass --sequencing-summary " + self._input_folder + "/*sequencing_summary*.txt " + self._primer_scheme + " " + self._job_name + "_" + barcode + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
                        #output goes into current directory so this moves all output files to correct folder
                        minion_cmd = minion_cmd + "; mv ./" + self._job_name + "_" + barcode + "* " + dir_path
        #minion_cmd = minion_cmd + "; mv ./" + self._job_name + "* " + self._output_folder + "; \necho 'Job: " + self._job_name + " is finished running :D'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
        minion_cmd = minion_cmd + "; \necho 'Job: " + self._job_name + " is finished running :D'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
        #change directory into output folder at the start
        minion_cmd = "cd " + self._output_folder + "; " + minion_cmd
        return minion_cmd

    def disableSave(self):
        self._save_graphs = False

    def enableSave(self):
        self._save_graphs = True

    def disableVCF(self):
        self._create_vcfs = False

    def enableVCF(self):
        self._create_vcfs = True
