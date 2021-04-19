# Usage

[TOC]

## Configuring interARTIC

Configuring interARTIC should be done only at the first time. It will save the coniguration details for the future. 

- On the interARTIC web interface, click on `Edit Input and Sample .csv Directories`.

- Fill the first two fields 
   1. location of your input data. This should be an absolute path of a directory. This should usually be where Minknow outputs the data. On the GridION this is `/data`. If you use a MinION on a laptop by default it is `/var/lib/minknow/data/`. You can also set this to a custom directory location if you wish to manually copy the sequencing data.
   
   2. location of your sample-barcode .csv files. This should be an absolute path of a directory. We expect you to put the sample-barcode .csv files here directly, not inside any sub directories.

- Click `confirm` to save the settings.



## Adding a job

To begin the process of adding a job, click the 'Add Job' button located underneath the Jobs Queue on the home page. Now it will go to the paramers page.


Input the necessary parameters (see Parameter Descriptions below). Parameters required for any type of job run are denoted with an asterix (*).

### Input Folders

By default, the data input folder should be set up as:

```
/data/
    input_folder1/                               
        name/
            uuid/
                # input files here
    input_folder2/
        name/
            uuid/
                # input files here
                    
```

When prompted to select an input folder, click the drop down menu or type in the name of the input folder as in the data folder in the file tree above. For example, if you want to run the pipeline on ```input_folder1```, type ```input_folder1``` into the search bar or select it in the drop down menu.

#### Input directory file structure

* You must rename each file in the input folder to: fast5_pass, fast5_fail, fastq_pass, fastq_fail, sequencing_summary.txt
* If multiple samples are being run through the pipeline:
    * A CSV file containing the data's sample names and barcodes should be placed in the sample-barcodes folder and named ‘sample-barcode.csv’. 
    * A sample CSV file is below:

```
sample3,NB03
sample4,NB04
sample5,NB05
sample6,NB06
```

A sample file structure is as below:

```
input_folder/
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
    sequencing_summary.txt
```

### Parameter Descriptions

You can customize the parameters by typing into the respective text box. 

* **Job name:** A unique name for your job, so you may identify your output files with it.
* **Input folder:** Your main data folder. 
    * This folder contains folders such as fast5_pass, fastq_pass, etc.
* **Single or Multiple samples:** Select the appropriate option.
* **Output folder:** If your chosen output folder is already created, enter the file path for this folder. 
    * Otherwise, you may enter a file path to a folder that doesn’t exist yet. Can be a reltive directory name or an absolute path. If you do this, ensure that the parent directory exists. 
        * For example, if you are inputting this file path as your output folder: path/to/file/hello/world, the folder “hello” must already exist for the “world” folder to be created.
    * If this is not inputted, an output folder will be generated within the input folder.

* **Primer scheme directory:** Enter the file path to your primer schemes. 
    * This is the folder containing, for example, the folder nCoV-2019 which contains the V1, V2, etc folders.
* **Primer scheme name:** Enter the primer scheme name used for your nanopore sequencing run.
    * Following a similar example to the previous parameter description, here you will enter a path such as nCoV-2019/V1.
* **Primer/Barcode type:** Enter the type of primer/barcode used. 
    * Either select from the options available or enter the name of the primer/barcode in the text box. 
    * This is only used for folder-naming purposes.
* **Pipeline:** Select the pipeline within ARTIC that you wish to run your data files through.
* **Minimum/Maximum length:** If you selected from the available options in the primer/barcode type section, you may find the minimum and maximum length already filled out. 
    * If not, set this to the minimum/maximum length of your primers.
* **Thread usage/Normalise:** Change the prefilled values if you wish.
    * Please note that changing the threads/normalise values, they are changed globally for all commands.

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

The 'Abort Job' button can be used to terminate the job. A confirmation window will appear when you click on the abort button. If you continue, you will then be asked to confirm whether you wish to delete the files created by the job. After this, you will then be directed back to the home page.

### What happens if an error occurs during the run?

If an **error** occurs during a run, a **red** notification will appear. You can either let the job continue to run, or click the ‘Re-run’ button. Harmless errors sometimes occur in the ARTIC pipeline, so it may be worth waiting for the run to finish and then assessing your output.

Clicking the ‘Re-run’ button will allow you to abort the currently running job and re-run the job with editted parameters.

A confirmation window will appear when you click on the ‘Re-run’ button asking you to confirm that you wish to abort the current job and whether to delete the files created by the job. 

You will then be redirected to the parameters page where the information from the job in question will be automatically filled in. 

You can make any changes necessary, and the new job will be added to the end of the queue following submission. 

### What happens when a job is completed?

When a job is completed, a ‘Go to Output’ button will appear at the top of the page. Click the button to be redirected to the output page. The job will also be moved to the 'Completed Jobs' list on the home page where you can click on the job name and be redirected to the output page for that job.

## Output Page

The Output Page is for data visualisation to enable a fast quality check of the sample. At the bottom of the page, there is a 'Go to Progress' button which will redirect you to the progress page of the job if you click on it.

### Files Produced

This section contains a list of the files produced from the job, along with the location in which they were saved. This location should be the output folder that you inputted on the parameters page, or if you did not input one, it will be a folder named “output” created inside your input folder.

### Data Visualisation

The “Data Visualisation” section comprises two main parts.

* Plots produced from pipeline
* Variants found

#### Plots Produced From Pipeline

This section enables you to preview the mean amplicon read depth plots produced from the pipeline and simple graph/s from the data inside the ```<sample_name>.pass.vcf.gz``` file/s produced by the pipeline.  To download the graph, click on the 'Download' hyperlink in the lower-left corner of the graph of interest. If no ```<sample_name>.pass.vcf.gz``` files are found in the output folder, the message “Vcf graph could not be made: No pass.vfc.gz file/s found in the output folder.” will be displayed. As no files of the suitable format have been found, these graph/s cannot be produced. This may be due to errors or problems during the pipeline, so checking error messages in the progress page's standard output section is important. 

#### Variants Found

Beneath each of the graphs, a summarised version of the ```<sample_name>.pass.vcf.gz``` file is displayed in the form of a table. Each row corresponds to a different variant found and they are ordered in increasing numerical order based on their position on the chromosome.


