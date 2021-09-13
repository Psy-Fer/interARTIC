# -*- coding: utf-8 -*-
import os
import sys
#from .tasks import executeJob
from flask import jsonify, url_for
import subprocess
from celery.app.control import Inspect
import celery
import fnmatch

import csv, subprocess, time

class Job:
    def __init__(self, job_name, input_folder, read_file, primer_scheme_dir, primer_scheme, primer_type, output_folder, normalise, num_threads, pipeline, min_length, max_length, bwa, skip_nanopolish, dry_run, override_data, num_samples, guppyplex, barcode_type, run_name, csv_file, primer_select, input_name):
        self._job_name = job_name
        self._input_folder = input_folder
        self._run_name = run_name
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
        self._guppyplex = guppyplex
        self._barcode_type = barcode_type
        self._csv_file = csv_file
        self._gather_cmd = self.__generateGatherCmd()
        self._guppyplex_cmd = self.__generateGuppyplexCmd()
        self._demult_cmd = self.__generateDemultCmd()
        self._min_cmd = self.__generateMinionCmd()
        self._plot_cmd = self.__generatePlotCmd()
        self._task_id = None
        self._primer_select = primer_select
        self._input_name = input_name
        self._metadata = {}

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
    def guppyplex_cmd(self):
        return self._guppyplex_cmd

    @property
    def demult_cmd(self):
        return self._demult_cmd

    @property
    def min_cmd(self):
        return self._min_cmd

    @property
    def plot_cmd(self):
        return self._plot_cmd

    @property
    def task_id(self):
        return self._task_id

    @property
    def guppyplex(self):
        return self._guppyplex

    @property
    def barcode_type(self):
        return self._barcode_type

    @property
    def csv_file(self):
        return self._csv_file

    @property
    def primer_select(self):
        return self._primer_select

    @property
    def input_name(self):
        return self._input_name

    @task_id.setter
    def task_id(self, val):
        if val:
            self._task_id = val

    @property
    def metadata(self):
        return self._metadata

    @metadata.setter
    def metadata(self, val):
        if val:
            self._metadata = val

    def __generateGatherCmd(self):
        gather_cmd = ""
        # if job is running medaka
        if self._pipeline == "medaka":
            gather_cmd = "echo '*****RUNNING GATHER COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; artic gather --min-length " + self._min_length + " --max-length " + self._max_length + " --prefix " + self._job_name + " --directory " + self._input_folder +" --no-fast5s" + " >> " + self._output_folder + "/all_cmds_log.txt 2>>" + self._output_folder + "/all_cmds_log.txt"
        # if job is running nanopolish
        elif self._pipeline == "nanopolish":
            gather_cmd = "echo '*****RUNNING GATHER COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; artic gather --min-length " + self._min_length + " --max-length " + self._max_length + " --prefix " + self._job_name + " --directory " + self._input_folder + " --fast5-directory " + self._input_folder + "/fast5_pass" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
        #change directory into output folder
        gather_cmd = "cd " + self._output_folder + "; " + gather_cmd
        return gather_cmd

    def __generateGuppyplexCmd(self):
        # Add in quality filering if not parsed into pass/fail folders.
        # If it can find pass/fail, use pass only
        # If not, run quality filtering
        # Also need to do loop over barcode directories, to run command for each barcode
        # for nanopolish, need to manually run nanopolish index command
        #artic guppyplex --directory /home/jamfer/data/SARS-CoV-2/test_interARTIC/FLFL031920/output/nCoV_2019_eden_V1_sample4_FLFL031920_plot_thickens_NB04_medaka/bc4/
        # --max-length 2700 --min-length 2300 --prefix plot_thickens --output /home/jamfer/data/SARS-CoV-2/test_interARTIC/FLFL031920/output/blah.fastq >> /all_cmds_log.txt 2>> /all_cmds_log.txt

        guppyplex_cmd = ""
        if self._guppyplex == "on":
            # Build dir struct. Use barcodes to match, if more than 1 hit, check pass/fail
            dir_list = []
            for dName, sdName, fList in os.walk(self._input_folder):
                for fileName in fList:
                    if fnmatch.fnmatch(fileName, "*.fastq"):
                        dir_list.append(dName)
                        break
            # sys.stderr.write(", ".join(dir_list)+"\n")

            if self._pipeline == "medaka":
                #open csv file
                with open(self._csv_file,'rt')as f:
                    data = csv.reader(f)
                    for row in data:
                        barcode = row[1]
                        bc_count = 0
                        barcode_pass_dir = ""
                        barcode_dir = ""
                        for d in dir_list:
                            if fnmatch.fnmatch(d, "*barcode"+barcode[-2:]+"*"):
                                bc_count += 1
                                if fnmatch.fnmatch(d, "*fastq_pass*"):
                                    barcode_pass_dir = d
                                barcode_dir = d
                        if bc_count > 1:
                            if barcode_pass_dir:
                                barcode_dir = barcode_pass_dir
                            else:
                                sys.stderr.write("barcode PASS directory not found. Either directory structure is broken/changed, or the barcode does not exist for this dataset.\n")
                                continue
                        elif bc_count == 0:
                            sys.stderr.write("barcode directory not found. Either directory structure is broken/changed, or the barcode does not exist for this dataset.\n")
                            continue
                        guppyplex_cmd = guppyplex_cmd + " echo '*****RUNNING GUPPYPLEX COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; artic guppyplex --min-length " + self._min_length + " --max-length " + self._max_length + " --prefix " + self._job_name + " --directory " + barcode_dir + " --output " + self._output_folder + "/" + self._job_name + "_fastq_pass-" + barcode + ".fastq " + " >> " + self._output_folder +"/all_cmds_log.txt 2>>" + self._output_folder + "/all_cmds_log.txt;"
            # if job is running nanopolish
            elif self._pipeline == "nanopolish":
                # get fast5 dirs
                fast5_dir_list = []
                for dName, sdName, fList in os.walk(self._input_folder):
                    for fileName in fList:
                        if fnmatch.fnmatch(fileName, "*.fast5"):
                            fast5_dir_list = dName
                            break
                with open(self._csv_file,'rt')as f:
                    data = csv.reader(f)
                    for row in data:
                        barcode = row[1]
                        bc_count = 0
                        barcode_pass_dir = ""
                        barcode_dir = ""
                        for d in dir_list:
                            if fnmatch.fnmatch(d, "*barcode"+barcode[-2:]+"*"):
                                bc_count += 1
                                if fnmatch.fnmatch(d, "*fastq_pass*"):
                                    barcode_pass_dir = d
                                barcode_dir = d
                        if bc_count > 1:
                            if barcode_pass_dir:
                                barcode_dir = barcode_pass_dir
                            else:
                                sys.stderr.write("barcode PASS directory not found. Either directory structure is broken/changed, or the barcode does not exist for this dataset.\n")
                                continue
                        elif bc_count == 0:
                            sys.stderr.write("barcode directory not found. Either directory structure is broken/changed, or the barcode does not exist for this dataset.\n")
                            continue
                        f5_dir_list = []
                        for dName, sdName, fList in os.walk(self._input_folder):
                            for fileName in fList:
                                if fnmatch.fnmatch(fileName, "*.fast5"):
                                    f5_dir_list.append(dName)
                                    break
                        f5_count = 0
                        general_pass = 0
                        barcode_fast5_pass_dir = ""
                        barcode_fast5_dir = ""
                        fast5_pass_dir = ""
                        for d in f5_dir_list:
                            if fnmatch.fnmatch(d, "*barcode"+barcode[-2:]+"*"):
                                if fnmatch.fnmatch(d, "*fast5_pass*"):
                                    f5_count += 1
                                    barcode_fast5_pass_dir = d
                                barcode_fast5_dir = d
                            elif fnmatch.fnmatch(d, "*fast5_pass*"):
                                general_pass += 1
                                fast5_pass_dir = d
                        if f5_count > 1:
                            if barcode_fast5_pass_dir:
                                barcode_fast5_dir = barcode_fast5_pass_dir
                            else:
                                sys.stderr.write("barcode fast5 PASS directory not found. Either directory structure is broken/changed, or the barcode does not exist for this dataset.\n")
                                continue
                        if barcode_fast5_dir == "":
                            if fast5_pass_dir != "":
                                barcode_fast5_dir = fast5_pass_dir
                        elif f5_count == 0 and general_pass == 0:
                            sys.stderr.write("barcode fast5 directory not found. Either directory structure is broken/changed, or the barcode does not exist for this dataset.\n")
                            continue
                        guppyplex_cmd = guppyplex_cmd + " echo '*****RUNNING GUPPYPLEX COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; artic guppyplex --min-length " + self._min_length + " --max-length " + self._max_length + " --prefix " + self._job_name + " --directory " + barcode_dir + " --output " + self._output_folder + "/" + self._job_name + "_fastq_pass-" + barcode + ".fastq" + " >> " + self._output_folder +"/all_cmds_log.txt 2>>" + self._output_folder + "/all_cmds_log.txt;" + " nanopolish index -d " + barcode_fast5_dir + " " + self._job_name + "_fastq_pass-" + barcode + ".fastq;"
                # change directory into output folder
                guppyplex_cmd = "cd " + self._output_folder + "; " + guppyplex_cmd
        return guppyplex_cmd

    def __generateDemultCmd(self):
        demult_cmd = ""
        #demultiplex cmd only runs on multiple samples
        if self._num_samples == "multiple":
            if self._barcode_type == "rapid":
                demult_cmd = "echo '*****GATHER COMMAND COMPLETE!*****\n*****RUNNING PORECHOP COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; echo 'porechop --verbosity 2 --untrimmed -i " + self._job_name + "_fastq_pass.fastq -b ./ --rapid_barcodes --discard_middle --barcode_threshold 80 --threads " + self._num_threads + " --check_reads 10000 --barcode_diff 5 > " + self._job_name + "_fastq_pass.fastq.demultiplexreport.txt' >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; porechop --verbosity 2 --untrimmed -i " + self._job_name + "_fastq_pass.fastq -b ./ --rapid_barcodes --discard_middle --barcode_threshold 80 --threads " + self._num_threads + " --check_reads 10000 --barcode_diff 5 > " + self._job_name + "_fastq_pass.fastq.demultiplexreport.txt;"
                #open csv file
                with open(self._csv_file,'rt')as f:
                    data = csv.reader(f)
                    for row in data:
                        barcode = row[1]
                        demult_cmd = demult_cmd + " echo '*****MOVING FILES INTO CORRECT FOLDERS!*****\n'; mv " + barcode + ".fastq " + self._job_name + "_fastq_pass-" + barcode + ".fastq 2>>" + self._output_folder + "/all_cmds_log.txt;"
            else:
                demult_cmd = "echo '*****GATHER COMMAND COMPLETE!*****\n*****RUNNING DEMULTIPLEX COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; artic demultiplex --threads " + self._num_threads + " " + self._job_name + "_fastq_pass.fastq" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
            #change directory into output folder
            demult_cmd = "cd " + self._output_folder + "; " + demult_cmd
        return demult_cmd

    def __generateMinionCmd(self):
        minion_cmd = ""
        # if only one sample in input
        if self._num_samples == "single":
            #create directory for minion output
            dir_path = self._output_folder + "/" + self._primer_type + "_sample1_" + self._run_name + "_" + self._job_name + "_single_" + self._pipeline
            #make directory
            minion_cmd = "mkdir " + dir_path
            # if read file is provided by user
            if self._read_file != "":
                dummy = "this is not being used for now"
                # if medaka is chosen
                # if self._pipeline == "medaka":
                #
                #     minion_cmd = minion_cmd + "; echo '*****MOVING FILES INTO CORRECT FOLDERS!*****\n'; mv " + self._read_file " + dir_path + "/ 2>> " + self._output_folder + "/all_cmds_log.txt"
                #     minion_cmd = minion_cmd + "; echo '*****DEMULTIPLEX/PORECHOP COMMAND COMPLETE!*****\n*****RUNNING MINION COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; cd " + dir_path + "; artic minion --minimap2 --medaka --medaka-model r941_min_high_g360 --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._primer_scheme_dir + " --read-file " + self._read_file + " " + self._primer_scheme + " \"" + self._job_name + "\"" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
                # # if nanopolish is chosen
                # elif self._pipeline == "nanopolish":
                #     minion_cmd = minion_cmd + "; echo '*****MOVING FILES INTO CORRECT FOLDERS!*****\n'; mv " + self._read_file " + dir_path + "/ 2>> " + self._output_folder + "/all_cmds_log.txt"
                #     minion_cmd = minion_cmd + "; echo '*****DEMULTIPLEX/PORECHOP COMMAND COMPLETE!*****\n*****RUNNING MINION COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; cd " + dir_path + "; artic minion --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._primer_scheme_dir + " --read-file ../" + self._read_file + " --fast5-directory " + self._input_folder + "/fast5_pass --sequencing-summary " + self._input_folder + "/*sequencing_summary*.txt " + self._primer_scheme + " " + self._job_name + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
            #if read file isn't provided by user
            else:
                # if medaka is chosen
                if self._pipeline == "medaka":
                    minion_cmd = minion_cmd + "; echo '*****MOVING FILES INTO CORRECT FOLDERS!*****\n'; mv " + self._job_name + "_fastq_pass.fastq " + dir_path + "/ 2>> " + self._output_folder + "/all_cmds_log.txt"
                    minion_cmd = minion_cmd + "; echo '*****DEMULTIPLEX/PORECHOP COMMAND COMPLETE!*****\n*****RUNNING MINION COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; cd " + dir_path + "; artic minion --minimap2 --medaka --medaka-model r941_min_high_g360 --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._primer_scheme_dir + " --read-file " + self._job_name + "_fastq_pass.fastq " + self._primer_scheme + " \"" + self._job_name + "\"" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
                # if nanopolish is chosen
                elif self._pipeline == "nanopolish":
                    minion_cmd = minion_cmd + "; echo '*****MOVING FILES INTO CORRECT FOLDERS!*****\n'; mv " + self._job_name + "_fastq_pass.fastq " + dir_path + "/ 2>> " + self._output_folder + "/all_cmds_log.txt"
                    minion_cmd = minion_cmd + "; echo '*****DEMULTIPLEX/PORECHOP COMMAND COMPLETE!*****\n*****RUNNING MINION COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt; cd " + dir_path + "; artic minion --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._primer_scheme_dir + " --read-file " + self._job_name + "_fastq_pass.fastq --fast5-directory " + self._input_folder + "/fast5_pass --sequencing-summary " + self._input_folder + "/*sequencing_summary*.txt " + self._primer_scheme + " " + self._job_name + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
        # if multiple samples in input
        elif self._num_samples == "multiple":
            minion_cmd = "echo '*****DEMULTIPLEX/PORECHOP COMMAND COMPLETE!*****\n*****RUNNING MINION COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
            # if medaka is chosen
            if self._pipeline == "medaka":
                #open csv file
                with open(self._csv_file,'rt')as f:
                    data = csv.reader(f)
                    for row in data:
                        sample_name = row[0]
                        barcode = row[1]
                        #create directory for barcode with naming system
                        dir_path = self._output_folder + "/" + self._primer_type + "_" + sample_name + "_" + self._run_name + "_" + self._job_name + "_" + barcode + "_" + self._pipeline
                        #make directory
                        minion_cmd = minion_cmd + "; mkdir " + dir_path
                        #move fastq_pass file into folder
                        minion_cmd = minion_cmd + ";echo '*****MOVING FILES INTO CORRECT FOLDERS!*****\n'; mv " + self._output_folder + "/" + self._job_name + "_fastq_pass-" + barcode + ".fastq " + dir_path + "/ 2>> " + self._output_folder + "/all_cmds_log.txt"
                        #append minion cmd in barcode directory
                        minion_cmd = minion_cmd + "; cd " + dir_path + "; artic minion --minimap2 --medaka --medaka-model r941_min_high_g360 --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._primer_scheme_dir + " --read-file ./" + self._job_name + "_fastq_pass-" + barcode + ".fastq " + self._primer_scheme + " " + self._job_name + "_" + sample_name + "_" + barcode + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"

            elif self._pipeline == "nanopolish":
                #open csv file
                with open(self._csv_file,'rt')as f:
                    data = csv.reader(f)
                    for row in data:
                        sample_name = row[0]
                        barcode = row[1]
                        #create directory for barcode with naming system
                        dir_path = self._output_folder + "/" + self._primer_type + "_" + sample_name + "_" + self._run_name + "_" + self._job_name + "_" + barcode + "_" + self._pipeline
                        #make directory
                        minion_cmd = minion_cmd + "; mkdir " + dir_path
                        #move fastq_pass file into folder
                        minion_cmd = minion_cmd + ";echo '*****MOVING FILES INTO CORRECT FOLDERS!*****\n'; mv " + self._output_folder + "/" + self._job_name + "_fastq_pass-" + barcode + ".fastq " + dir_path + "/ 2>> " + self._output_folder + "/all_cmds_log.txt"
                        if self._guppyplex == "on":
                             minion_cmd = minion_cmd + "; mv " + self._output_folder + "/*" + barcode + ".fastq.index* " + dir_path + "/ 2>> " + self._output_folder + "/all_cmds_log.txt"
                        #append minion cmd in barcode directory
                        minion_cmd = minion_cmd + "; cd " + dir_path + "; artic minion --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._primer_scheme_dir + " --read-file  ./" + self._job_name + "_fastq_pass-" + barcode + ".fastq --fast5-directory " + self._input_folder + "/fast5_pass --sequencing-summary " + self._input_folder + "/*sequencing_summary*.txt " + self._primer_scheme + " " + self._job_name + "_" + sample_name + "_" + barcode + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"

        # minion_cmd = minion_cmd + "; \necho 'Job: " + self._job_name + " is finished running :D'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
        #change directory into output folder at the start
        minion_cmd = "cd " + self._output_folder + "; " + minion_cmd
        return minion_cmd

    def __generatePlotCmd(self):
        plot_cmd = "echo '*****MINION COMMAND COMPLETE!*****\n*****RUNNING PLOT COMMAND*****'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
        if self._num_samples == "single":
            # sys.stderr.write("SINGLE FILE\n")
            primer_path = self._primer_scheme_dir + "/" + "/".join(self._primer_scheme.split("_"))
            # sys.stderr.write("primer_path: ")
            # sys.stderr.write(primer_path)
            # sys.stderr.write("\n")
            dir_path = self._output_folder + "/" + self._primer_type + "_sample1_" + self._run_name + "_" + self._job_name + "_single_" + self._pipeline
            # for dName, sdName, fList in os.walk(primer_path):
            #     for fileName in fList:
            #         # sys.stderr.write(fileName)
            #         # sys.stderr.write("\n")
            #         if fnmatch.fnmatch(fileName, "*.scheme.bed"):
            #             # sys.stderr.write("MATCH!!!!")
            #             # sys.stderr.write("\n")
            #             bed_file = os.path.join(dName, fileName)
            # # sys.stderr.write("bed_file: ")
            # # sys.stderr.write(bed_file)
            # # sys.stderr.write("\n")
            #
            # with open(bed_file, 'r') as b:
            #     for l in b:
            #         l = l.strip("\n")
            #         l = l.strip("\t")
            #         l = l.split("\t")
            #         virus = l[-1][:-2]
            #         break
            # sys.stderr.write("virus: ")
            # sys.stderr.write(virus)
            # sys.stderr.write("\n")
            depth1 = ""
            depth2 = ""
            vcf_file = ""
            file_start = self._job_name
            for (dirpath, dirnames, filenames) in os.walk(dir_path):
                for name in filenames:
                    if fnmatch.fnmatch(name, '*1.depths'):
                        depth1 = os.path.join(dirpath, name)
                    if fnmatch.fnmatch(name, '*2.depths'):
                        depth2 = os.path.join(dirpath, name)
            # depth1 = "{}/{}.coverage_mask.txt.{}_1.depths".format(dir_path, file_start, virus)
            # depth2 = "{}/{}.coverage_mask.txt.{}_2.depths".format(dir_path, file_start, virus)
            vcf_file = "{}/{}.pass.vcf.gz".format(dir_path, file_start)
            if len(depth1) < 1:
                plot_cmd = plot_cmd + "ERROR: depth1 file not found! Plots not generated" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
            if len(depth2) < 1:
                plot_cmd = plot_cmd + "ERROR: depth2 file not found! Plots not generated" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
            if len(vcf_file) < 1:
                plot_cmd = plot_cmd + "ERROR: vcf_file file not found! Plots not generated" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"

            if depth1 and depth2 and vcf_file:
                plot_cmd = plot_cmd + "; covarPlots.py -v {} -d1 {} -d2 {} -b {}".format(vcf_file, depth1, depth2, bed_file) + " >> " + self._output_folder + "/all_cmds_log.txt 2>>" + self._output_folder + "/all_cmds_log.txt"
            # "python3 plots.py -v {} -d1 {} -d2 {} -b {}".format(vcf_file, depth1, depth2, bed_file)

        if self._num_samples == "multiple":
            # sys.stderr.write("MULTIPLE FILES\n")
            primer_path = self._primer_scheme_dir + "/" + "/".join(self._primer_scheme.split("_"))
            # sys.stderr.write("primer_path: ")
            # sys.stderr.write(primer_path)
            # sys.stderr.write("\n")
            # for dName, sdName, fList in os.walk(primer_path):
            #     for fileName in fList:
            #         sys.stderr.write(fileName)
            #         sys.stderr.write("\n")
            #         if fnmatch.fnmatch(fileName, "*.scheme.bed"):
            #             sys.stderr.write("MATCH!!!!")
            #             sys.stderr.write("\n")
            #             bed_file = os.path.join(dName, fileName)
            #
            # # sys.stderr.write("bed_file: ")
            # # sys.stderr.write(bed_file)
            # # sys.stderr.write("\n")
            # with open(bed_file, 'r') as b:
            #     for l in b:
            #         l = l.strip("\n")
            #         l = l.strip("\t")
            #         l = l.split("\t")
            #         virus = l[-1][:-2]
            #         break
            # sys.stderr.write("virus: ")
            # sys.stderr.write(virus)
            # sys.stderr.write("\n")
            depth1 = ""
            depth2 = ""
            vcf_file = ""
            with open(self._csv_file,'rt')as f:
                data = csv.reader(f)
                for row in data:
                    sample_name = row[0]
                    barcode = row[1]
                    # sys.stderr.write(sample_name+"\n")
                    #create directory for barcode with naming system
                    dir_path = self._output_folder + "/" + self._primer_type + "_" + sample_name + "_" + self._run_name + "_" + self._job_name + "_" + barcode + "_" + self._pipeline
                    for (dirpath, dirnames, filenames) in os.walk(dir_path):
                        for name in filenames:
                            if fnmatch.fnmatch(name, '*1.depths'):
                                depth1 = os.path.join(dirpath, name)
                            if fnmatch.fnmatch(name, '*2.depths'):
                                depth2 = os.path.join(dirpath, name)
                    file_start = self._job_name + "_" + sample_name + "_" + barcode
                    # depth1 = "{}/{}.coverage_mask.txt.{}_1.depths".format(dir_path, file_start, virus)
                    # depth2 = "{}/{}.coverage_mask.txt.{}_2.depths".format(dir_path, file_start, virus)
                    vcf_file = "{}/{}.pass.vcf.gz".format(dir_path, file_start)
                    if len(depth1) < 1:
                        plot_cmd = plot_cmd + "ERROR: depth1 file not found! Plots not generated" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
                    if len(depth2) < 1:
                        plot_cmd = plot_cmd + "ERROR: depth2 file not found! Plots not generated" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
                    if len(vcf_file) < 1:
                        plot_cmd = plot_cmd + "ERROR: vcf_file file not found! Plots not generated" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
                    if depth1 and depth2 and vcf_file:
                        plot_cmd = plot_cmd + "; covarPlots.py -v {} -d1 {} -d2 {} -b {}".format(vcf_file, depth1, depth2, bed_file) + " >> " + self._output_folder + "/all_cmds_log.txt 2>>" + self._output_folder + "/all_cmds_log.txt"

        #change directory into output folder
        plot_cmd = plot_cmd + "; \necho 'Job: " + self._job_name + " is finished running :D'" + " >> " + self._output_folder + "/all_cmds_log.txt 2>> " + self._output_folder + "/all_cmds_log.txt"
        plot_cmd = "cd " + self._output_folder + "; " + plot_cmd
        # sys.stderr.write("plot_cmd: ")
        # sys.stderr.write(plot_cmd)
        # sys.stderr.write("\n")
        return plot_cmd

    def disableSave(self):
        self._save_graphs = False

    def enableSave(self):
        self._save_graphs = True

    def disableVCF(self):
        self._create_vcfs = False

    def enableVCF(self):
        self._create_vcfs = True
