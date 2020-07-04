
class Job:
    def __init__(self, job_name, input_folder, scheme_dir, read_file, primer_scheme, output_folder, normalise, num_threads, pipeline, min_length, max_length, bwa, skip_nanopolish, dry_run, override_data):
        self._job_name = job_name
        self._input_folder = input_folder
        self._scheme_dir = scheme_dir
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

    @property
    def job_name(self):
        return self._job_name

    @property
    def input_folder(self):
        return self._input_folder
        
    @property
    def scheme_dir(self):
        return self._scheme_dir

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


    def add_to_queue(self):
        jobQueue.put(self)
        print(jobQueue)
        
    def generateGatherCmd(self):
        if self._pipeline == "medaka":
            gather_cmd = "artic gather --min-length " + self._min_length + " --max-length " + self._max_length + " --prefix " + self._job_name + " --directory " + self._input_folder +" --no-fast5s"
        elif self._pipeline == "nanopolish":
            gather_cmd = "echo 'no gather command for nanopolish yet'"
        elif self._pipeline == "both":
            gather_cmd = "echo 'no gather command for nanopolish yet'"
        return gather_cmd
        
    def generateMinionCmd(self):
        if self._pipeline == "medaka":
            minion_cmd = "artic minion --minimap2 --medaka --normalise " + self._normalise + " --threads " + self._num_threads + " --scheme-directory " + self._scheme_dir + " --read-file " + self._read_file + " " + self._primer_scheme + " \"" + self._job_name + "\""
        elif self._pipeline == "nanopolish":
            minion_cmd = "echo 'no minion command for nanopolish yet'"
        elif self._pipeline == "both":
            minion_cmd = "echo 'no minion command for nanopolish yet'"
        return minion_cmd
