import os

class Job:
    def __init__(self, job_name, input_folder, read_file, primer_scheme, output_folder, normalise, num_threads, pipeline, min_length, max_length, bwa, skip_nanopolish, dry_run, override_data):
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
        self._gather_cmd = self.__generateGatherCmd()
        self._min_cmd = self.__generateMinionCmd()


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
    def gather_cmd(self):
        return self._gather_cmd
        
    @property
    def min_cmd(self):
        return self._min_cmd

        
    def __generateGatherCmd(self):
        if self._pipeline == "medaka":
            gather_cmd = "artic gather --min-length " + self._min_length + " --max-length " + self._max_length + " --prefix " + self._job_name + " --directory " + self._input_folder +" --no-fast5s"
        elif self._pipeline == "nanopolish":
            gather_cmd = "artic gather --min-length " + self._min_length + " --max-length " + self._max_length + " --prefix " + self._job_name + " --directory " + self._input_folder + " --fast5-directory " + self._input_folder + "/fast5_pass"
        elif self._pipeline == "both":
            gather_cmd = "echo 'no gather command for both pipelines yet'"
        return gather_cmd

    #add demultiplex cmd function too - whether nanopolish or medaka it will always be: 
    #dem_cmd = "artic demultiplex --threads " + self._num_threads + " " + self._job_name + "_fastq_pass.fastq"
        
    def __generateMinionCmd(self):
        if self._pipeline == "medaka":
            minion_cmd = "artic minion --minimap2 --medaka --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._input_folder + "/primer_schemes --read-file " + self._read_file + " " + self._primer_scheme + " \"" + self._job_name + "\""
        elif self._pipeline == "nanopolish":
            minion_cmd = "artic minion --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._input_folder + "/primer_schemes --read-file " + self._read_file + " --fast5-directory " + self._input_folder + "/fast5_pass --sequencing-summary " + self._input_folder + "/*sequencing_summary*.txt " + self._primer_scheme + " " + self._job_name
        elif self._pipeline == "both":
            minion_cmd = "echo 'no minion command for both pipelines yet'"
        return minion_cmd
        
    def execute(self):
        # Execute this job
        # Run gather command
        # Run minion command
        print("EXECUTING JOB: ", self._job_name)
        os.system(self._gather_cmd)
        os.system(self._min_cmd)
        # Not sure if i need to do anything here to direct output???
        os.system('mv ' + self._job_name + '* ' + self._output_folder)
        
    def abort(self):
        # If job is running, abort it and remove output
        pass
        

