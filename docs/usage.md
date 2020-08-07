# Usage

[TOC]

## Adding a job

To begin the process of adding a job, click the 'Add Job' button located underneath the Jobs Queue on the home page. 

## Parameters

Input the necessary parameters (see Parameter Descriptions below). Parameters required for any type of job run are denoted with an asterix (*).

For the file path inputs, please enter absolute paths. See below for help.

### File path input

* Folders and files should be inputted by their file paths.
* File paths can be retrieved by running 'pwd' in the appropriate folder on any terminal.
* Folders may also be referred to as directories.
* File paths should start with “/” (Mac or Linux) or “C:\” (Windows). If you have not worked with navigating folders and files in the terminal before, take a look at this resource: https://www.earthdatascience.org/courses/intro-to-earth-data-science/python-code-fundamentals/work-with-files-directories-paths-in-python/.

For example:

```
$ pwd                                    # get file path of current directory
/Users/YOURNAME
$ ls                                     # list contents of current directory
folder1     folder2     file1       documents
$ cd documents                           # change current directory to documents
$ pwd
/Users/YOURNAME/documents
$ cd inputFolder                         # change current directory to your input folder
$ ls                                     # check contents of folder are correct
fast5_fail      fast5_pass      fastq_fail      fastq_pass      sample-barcode.csv     sequencing_summary.txt 
$ pwd                                    # obtain file path you will input into interARTIC
/Users/YOURNAME/documents/inputFolder
```
Note: your input folder may not be located in documents folder. Simply navigate, using these commands, to inside your input folder and obtain the file path. 


#### Input directory file structure

* You must rename each folder/ file in the input folder to: fast5_pass, fast5_fail, fastq_pass, fastq_fail, sequencing_summary.txt, sample-barcode.csv
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
        A_10.fast5
        A_11.fast5
    fast5_fail/
        A_0.fast5
        A_1.fast5
    fastq_pass/
        B_0.fastq
        B_1.fastq
    fastq_fail/
        B_10.fastq
        B_11.fastq
    sample-barcode.csv
    sequencing_summary.txt
    readfile.fastq                        #optional file
primer-schemes/
    nCoV-2019/
        V1/
            nCoV-2019.log
            nCoV-2019.pdf
            nCoV-2019.pickle
            nCoV-2019.reference.fasta
            nCoV-2019.reference.fasta.fai
            nCoV-2019.scheme.bed
            nCoV-2019.svg
            nCoV-2019.tsv
```

### Parameter Descriptions

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

The progress page displays the stream of standard output being produced by your job run. Here you can see which commands are currently running and any errors that occur. Each job run has its own progress page which can be accessed via the home page or parameters page by clicking on the job name in the jobs queue.

For each job, the progress page will display:

* The job name
* The job's place in queue
* An 'Abort Job' button
* The overall progress of the job in the form of a progress bar and the number of steps remaining in the pipeline
* A 'View Job Parameters here' button
* The current standard output obtained from the job

The 'View Job Parameters here' button, when clicked, will display the job's parameters that have been entered by the user.

There is an 'Abort Job' button which can be used to terminate the job. A confirmation window will appear when you click on the abort button. If you continue, you will then be asked to confirm whether you wish to delete the files created by the job. After this, you will then be directed back to the home page.

### What happens if an error occurs during the run?

If an **error** occurs during a run, a **red** notification will appear. You can either let the job continue to run, or click the ‘Re-run’ button. Harmless errors sometimes occur in the ARTIC pipeline, so it may be worth waiting for the run to finish and then assessing your output.

Clicking the ‘Re-run’ button will allow you to abort the currently running job and re-run the job with editted parameters.

A confirmation window will appear when you click on the ‘Re-run’ button asking you to confirm that you wish to abort the current job and whether to delete the files created by the job. 

You will then be redirected to the parameters page where the information from the job in question will be automatically filled in. 

You can make any changes necessary, and the new job will be added to the end of the queue following submission. 

### What happens when a job is completed?

When a job is completed, a ‘Go to Output’ button will appear at the top of the page. Click the button to be redirected to the output page. The job will also be moved to the 'Completed Jobs' list on the home page where you can click on the job name and be redirected to the output page for that job.

## Output Page

The Output Page has two main sections, one for the files produced during the run, and the other for data visualisation to enable a fast quality analysis of the sample. At the bottom of the page, there is a 'Go to Progress' button which will redirect you to the progress page of the job if you click on it.

### Files Produced

This section contains a list of the files from the job, along with the location in which they were saved. This should be the output folder that you inputted, or if you did not input one, it will be a folder named “output” made inside your input folder.

### Data Visualisation

The “Data Visualisation” section also comprises two main parts.

#### Variants Found

This section produces a simple graph/s from the information from the <sample_name>.pass.vcf.gz file/s produced by the pipeline. If multiple samples are selected, multiple files will be produced (assuming all runs are successful).

The 'Produce Graphs' button creates the graph/s. The vertical lines on the graph represent a variant, with the specific numerical position of the variant on the bottom. The mutation that occurred is labelled REF -> ALT, meaning that the nucleotide/s in the reference genome are on the left of the arrow, and the variant is on the right. The height of the vertical line represents the read depth of the specific variant. To download the graph, click on the 'Download' hyperlink in the lower-left corner of the desired graph.

These graphs, as mentioned, require interARTIC to read the <sample_name>.pass.vcf.gz file/s from the output folder. If there are no such files found, then no graphs will be produced. If you would not like the web app to access this, please click the “Disable” option under “Enable VCF graphs to be generated?” and click the 'Confirm' button. When you are no longer given the option to produce the graphs, and the status of the “Enable VCF graphs to be generated?” section is “Disabled” this is complete. If you would like to re-enable the graphs to be produced, just select “Enable” and once again confirm. The functionality should be restored.

If no .pass.vcf.gz files are found in the output folder, the message “Vcf graph could not be made: No pass.vfc.gz file/s found in the output folder.” will be displayed. As no files in suitable format have been found, the graph cannot be produced. This may be due to problems during the pipeline, and checking of error messages is important. 

#### Plots Produced From Pipeline

This section enables you to preview the mean amplicon read depth plots produced from the pipeline. The bar plot shows the mean amplicon read depth over the amplicons, while the box plot shows the mean amplicon read depth over the read groups.

These plots are accessed from the output folder, and require a copy of them to be saved into the web app’s folder to enable previewing. If you would not like this to happen, please disable the feature by selecting the “Disable” option under the “Would you like the plots to be previewed?” section, and clicking the 'Confirm' button. The status should be updated to say “Disabled” and the plots will be automatically removed from the folder. To re-enable previewing, just select “Enable” and press the 'Confirm' button again and the option to preview graphs should be restored. 

If no barplot.png or boxplot.png files are found in the output folder, the message “Plots cannot be previewed: No plots were found in the output folder.” will be displayed. As no files in suitable format have been found, they cannot be previewed. This may be due to problems during the pipeline, and checking of error messages is important.
