# Usage

[TOC]

## Adding a job

To begin to add a job, click the “Add Job” button located underneath the Jobs Queue on the home page. 

## Parameters

Input the necessary parameters (see Parameter Descriptions below). Any parameters required for all runs are denoted with an asterix (*).

For the file path inputs, please enter absolute paths. 

### Input folders

* Folders should be inputted by their file paths.
* This can be retrieved by running pwd in the appropriate directory/ folder on any terminal.
* These should start with “/” or “C:\”. If you have not worked with navigating folders and files in the terminal before, take a look at this resource: https://www.earthdatascience.org/courses/intro-to-earth-data-science/python-code-fundamentals/work-with-files-directories-paths-in-python/.

For example:

```
$ pwd
/Users/YOURNAME
$ cd documents                           # change directory to documents
/Users/YOURNAME/documents
$ cd inputFolder                         # change directory to input folder
$ pwd
/Users/YOURNAME/documents/inputFolder
```

#### Input directory file structure

* You must rename each folder in the input folder to: fast5_pass, fast5_fail, fastq_pass, fastq_fail, sequencing_summary.txt
* If a single sample is being run through the pipeline:
    * If available, the file path for a read file should be inputted. 
    * If unavailable, the artic gather/demultiplex command will generate one.
* If multiple samples are being run through the pipeline:
    * A CSV file containing sample names and barcodes should be placed in the input folder and named ‘sample-barcode.csv’. 

ADD IN IMG

A sample file structure is as below:

```
input_directory/
    fast5_pass/
        A_30.fast5
        A_31.fast5
    fast5_fail/
        A_0.fast5
        A_1.fast5
    fastq_pass/
        B_0.fastq
        B_1.fastq
    fastq_fail/
        B_10.fast5
        B_11.fast5
    primer-schemes/
        IturiEBOV/
              V1/
                IturiEBOV.log
                IturiEBOV.pdf
                IturiEBOV.pickle
                IturiEBOV.reference.fasta
                IturiEBOV.reference.fasta.amb
                IturiEBOV.reference.fasta.ann
                IturiEBOV.reference.fasta.bwt
                IturiEBOV.reference.fasta.fai
                IturiEBOV.reference.fasta.pac
                IturiEBOV.reference.fasta.sa
                IturiEBOV.scheme.bed
                IturiEBOV.svg
                IturiEBOV.tsv
    sample-barcode.csv
    sequencing_summary.txt
    readfile
```

### Parameters

You can customize the parameters by typing into the respective text box. 

* **Job name:** A unique name for your job, so you may identify your output files with it.
* **Pipeline:** Select the pipeline within ARTIC that you wish to run your data files through.
* **Input folder:** Enter the file path to your main data folder. 
    * This folder contains folders such as fast5_pass, fastq_pass, etc.
* **Read file:** If you are inputting data files for a single sample run where you have a file ending in “.fastq” already made, input the file path for this read file. 
    * You may get this error in your output, but this can be ignored: Include screenshot of harmless error that might occur
* **Output folder:** If your chosen output folder is already created, enter the file path for this folder. 
    * Otherwise, you may enter a file path to a folder that doesn’t exist yet. If you do this, ensure that the parent directory exists. 
        * For example, if you are inputting this file path as your output folder: path/to/file/hello/world, the folder “hello” must already exist for the “world” folder to be created.
    * If this is not inputted, an output folder will be generated within the input folder.
* **Primer scheme folder:** Enter the file path to your primer schemes. 
    * This is the folder containing, for example, the folder nCoV-2019 which contains the V1, V2, etc folders.
* **Primer scheme name:** Enter the primer scheme name used for your nanopore sequencing run.
    * Following a similar example to the previous parameter description, here you will enter a path such as nCoV-2019/V1.
* **Primer/Barcode type:** Enter the type of primer/barcode used. 
    * Either select from the options available or enter the name of the primer/barcode in the text box. 
    * This is only used for folder-naming purposes.
* **Minimum/Maximum length:** If you selected from the available options in the primer/barcode type section, you may find the minimum and maximum length already filled out. 
    * If not, set this to the minimum/maximum length of your primers.
* **Thread usage/Normalise:** Change the prefilled values if you wish.
    * Please note that changing the threads/normalise values, they are changed globally for all commands.
* **Single or Multiple samples:** Select the appropriate option.

When you are confident that your parameter selections are correct, click on the “Submit Job(s)” button. You will be redirected to the progress page after clicking this button.

## Progress Page

The progress displays the progress of the run in question. Each run will have its own progress page, which can be accessed either via the home page by clicking the job name in the queue.

For each job, the progress page will display:

* The job name
* The place in queue
* The overall job progress in the form of a progress bar and the number of steps remaining in the pipeline
* The current output obtained from the job

There is a **View Parameters** button that will display the parameters that have been entered for the job when clicked.

There is an **Abort Job** button which can be used to terminate the job. A confirmation window will appear when you click on the abort button. If you continue, you will then be asked to confirm whether you wish to delete the files created by the job. After this, you will then be taken back to the home page where you can add a new job or view the currenty completed jobs.

### What happens if an error occurs during the run?

If an **error** occurs during a run, a **red** notification will appear. You can either continue with the job as is, or click the ‘Re-run’ button. 

Clicking the ‘Re-run’ button will allow you to abort the currently running job and re-run the job.

A confirmation window will appear when you click on the ‘Re-run’ button asking you to confirm that you wish to abort the current job and whether to delete the files created by the job. 

You will then be redirected to the parameters page where the information from the job in question will be automatically filled in. 

You can make any changes necessary, and the new job will be added to the end of the queue following submission. 

### What happens when a job is completed?

When a job is completed, a ‘Go to Output’ button will appear at the top of the page. Click the button to be redirected to the output page.

## Output Page

