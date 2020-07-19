import os, fnmatch

for (dirpath, dirnames, filenames) in os.walk('./sample_output'):
    for name in filenames:
        print(name)
        if fnmatch.fnmatch(name, '*barplot*'):
            print("I found"+name)
            barplot = name
        if fnmatch.fnmatch(name, '*boxplot*'):
            print("I found"+name)
            boxplot = name
    print(filenames)
