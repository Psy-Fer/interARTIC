import os, csv, subprocess, time

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

        
    def __generateGatherCmd(self):
        if self._pipeline == "medaka":
            gather_cmd = "artic gather --min-length " + self._min_length + " --max-length " + self._max_length + " --prefix " + self._job_name + " --directory " + self._input_folder +" --no-fast5s" + " >> all_cmds_log.txt 2>>all_cmds_log.txt"
        elif self._pipeline == "nanopolish":
            gather_cmd = "artic gather --min-length " + self._min_length + " --max-length " + self._max_length + " --prefix " + self._job_name + " --directory " + self._input_folder + " --fast5-directory " + self._input_folder + "/fast5_pass" + " >> all_cmds_log.txt 2>>all_cmds_log.txt"
        elif self._pipeline == "both":
            gather_cmd = "echo 'no gather command for both pipelines yet'"
        return gather_cmd

    def __generateDemultCmd(self):
        demult_cmd = "artic demultiplex --threads " + self._num_threads + " " + self._job_name + "_fastq_pass.fastq" + " >> all_cmds_log.txt 2>>all_cmds_log.txt"
        return demult_cmd

    def __generateMinionCmd(self):
        if self._num_samples == "single":
            #if read file is provided by user
            if self._read_file != "":
                if self._pipeline == "medaka":
                    minion_cmd = "artic minion --minimap2 --medaka --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._input_folder + "/primer_schemes --read-file " + self._read_file + " " + self._primer_scheme + " \"" + self._job_name + "\"" + " >> all_cmds_log.txt 2>>all_cmds_log.txt"
                elif self._pipeline == "nanopolish":
                    minion_cmd = "artic minion --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._input_folder + "/primer_schemes --read-file " + self._read_file + " --fast5-directory " + self._input_folder + "/fast5_pass --sequencing-summary " + self._input_folder + "/*sequencing_summary*.txt " + self._primer_scheme + " " + self._job_name + " >> all_cmds_log.txt 2>>all_cmds_log.txt"
                elif self._pipeline == "both":
                    minion_cmd = "echo 'no minion command for both pipelines yet'"
            #if read file isn't provided by user
            else:
                if self._pipeline == "medaka":
                    minion_cmd = "artic minion --minimap2 --medaka --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._input_folder + "/primer_schemes --read-file ./" + self._job_name + "_fastq_pass.fastq " + self._primer_scheme + " \"" + self._job_name + "\"" + " >> all_cmds_log.txt 2>>all_cmds_log.txt"
                elif self._pipeline == "nanopolish":
                    minion_cmd = "artic minion --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._input_folder + "/primer_schemes --read-file ./" + self._job_name + "_fastq_pass.fastq --fast5-directory " + self._input_folder + "/fast5_pass --sequencing-summary " + self._input_folder + "/*sequencing_summary*.txt " + self._primer_scheme + " " + self._job_name + " >> all_cmds_log.txt 2>>all_cmds_log.txt"
                elif self._pipeline == "both":
                    minion_cmd = "echo 'no minion command for both pipelines yet'"
        elif self._num_samples == "multiple":
            #going to run multiple minion cmds
            minion_cmd = []
            if self._pipeline == "medaka":
                #open the csv file
                csv_filepath = self._input_folder + '/sample-barcode.csv'
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
                        minion_cmd.append("mkdir " + dir_path)
                        #append minion cmd in barcode directory
                        minion_cmd.append("artic minion --minimap2 --medaka --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._input_folder + "/primer_schemes --read-file ./" + self._job_name + "_fastq_pass-" + barcode + ".fastq " + self._primer_scheme + " " + self._job_name + "_" + barcode + " >> all_cmds_log.txt 2>>all_cmds_log.txt")
                        #output goes into current directory so this moves all output files to correct folder
                        minion_cmd.append("mv " + self._job_name + "_" + barcode + "* " + dir_path)
                        #minion_cmd.append('mv ./all_cmds_log.txt ' + dir_path)

            elif self._pipeline == "nanopolish":
                #open the csv file
                csv_filepath = self._input_folder + '/sample-barcode.csv'
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
                        minion_cmd.append("mkdir " + dir_path)
                        #append minion cmd in barcode directory
                        minion_cmd.append("artic minion --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._input_folder + "/primer_schemes --read-file  ./" + self._job_name + "_fastq_pass-" + barcode + ".fastq --fast5-directory " + self._input_folder + "/fast5_pass --sequencing-summary " + self._input_folder + "/*sequencing_summary*.txt " + self._primer_scheme + " " + self._job_name + "_" + barcode + " >> all_cmds_log.txt 2>>all_cmds_log.txt")
                        #output goes into current directory so this moves all output files to correct folder
                        minion_cmd.append("mv ./" + self._job_name + "_" + barcode + "* " + dir_path)
            elif self._pipeline == "both":
                minion_cmd.append("echo 'no minion command for both pipelines yet'")

        return minion_cmd

    def executeCmds(self):
        if self._num_samples == "single":
            #create string of all cmds want to run
            cmd_combine = "echo 'Starting gather cmd';" + self._gather_cmd + ";" + "echo 'Starting minion cmd';" + self._min_cmd + ";" + "mv ./" + self._job_name + "* " + self._output_folder + ";" + "mv ./all_cmds_log.txt " + self._output_folder + "; echo 'Job: " + self._job_name + " is finished running :D'"
            #start process that runs these cmds in the background
            p = subprocess.Popen(cmd_combine, shell=True)

        if self._num_samples == "multiple":
            #create string of minion commands
            minion_string = ""
            for cmd in self._min_cmd:
                if minion_string == "":
                    minion_string = cmd
                else:
                    minion_string = minion_string + "; " + cmd
            #create string of all cmds want to run
            cmd_combine = "echo 'Starting gather cmd';" + self._gather_cmd + ";" + "echo 'Starting demultiplex cmd';" + self._demult_cmd + ";" + "echo 'Starting minion cmds';"  + minion_string + ";" + "mv ./" + self._job_name + "* " + self._output_folder + ";" + "mv ./all_cmds_log.txt " + self._output_folder + "; echo 'Job: " + self._job_name + " is finished running :D'"
            #start process that runs these cmds in the background
            p = subprocess.Popen(cmd_combine, shell=True)
