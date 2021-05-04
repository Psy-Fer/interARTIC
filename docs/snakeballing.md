
# Software packaging (aka "snake charming")

InterARTIC development involved the use of the Python programming language and depends on several third-party Python modules and software written predominantly in Python (e.g., *Flash*, *Celery*, *ARTIC* tools, etc). The Python ecosystem (including the language itself, in addition to Python libraries) has limited backward compatibility. As a result, Python software is often compatible only with the exact version of the Python interpreter and library versions it was developed with (sometimes specific even to the minor version level).

Python virtual environments and Anaconda are designed to resolve issues related to version compatibility but - at least in our experience - software installation via these methods can be complicated, especially for novice users. To experience the headache yourself, try to install InterARTIC and its dependencies from the scratch by following the instructions [here](https://psy-fer.github.io/interARTIC/installation).

Fortunately, the Python interpreter is predominantly written in C. Generally speaking, both the C language and system libraries have good backward compatibility. For instance, GLIBC is fully backward compatible. Thus, if you compile a C program on an older Linux system (e.g., Ubuntu 14) with an older compiler (e.g., gcc 4.8) and statically link third party libraries with limited backward compatibility, while dynamically linking the basic backward compatible libraries, the compiled binary would be portable on most (if not all) modern Linux systems. Of course, x86_64 binaries will not work on ARM processors, but if you compile for an older x86_64 instruction-set, it will work on all modern x86_64 processors, thanks to the backward compatibility in processor instruction sets. ARM also benefits from a similar level of backward compatibility.

In summary, if the relevant Python interpreter, all the modules and third party software are compiled and packaged with your Python code, it will be 'portable'. We call this process “snake charming", since it prevents Python modules from biting one another. For interested developers, we provide detailed instructions below on how snake charming was used in the development of InterARTIC, and how to use this technique to improve their own tools.

1, Setup a virtual machine with a fresh minimal installation of Ubuntu 14. Do everything below inside that virtual machine.

2. Obtain Python binaries compiled in the aforementioned fashion from https://github.com/indygreg/python-build-standalone. Refer to https://python-build-standalone.readthedocs.io/en/latest/ for more information.

```bash
wget https://github.com/indygreg/python-build-standalone/releases/download/20200408/cpython-3.7.7-linux64-20200409T0045.tar.zst #python 3.7 needed for interARTIC
zstd -d cpython-3.7.7-linux64-20200409T0045.tar.zst #extract zstd archive
tar xvf cpython-3.7.7-linux64-20200409T0045.tar
mkdir interartic_bin && mv python/install/* interartic_bin/
```

3. Now clone the interARTIC repository and copy the relevant scripts and data.

```bash
git clone https://github.com/Psy-Fer/interARTIC.git
mv interARTIC/templates interARTIC/scripts interARTIC/static interARTIC/src interARTIC/primer-schemes interARTIC/run.sh interARTIC/main.py interARTIC/config.init interartic_bin/
```

3. Now install the required dependencies using pypi in a virtual environment and move those to our snakeball directory.

```bash
cd interartic_bin/
bin/python3.7m -m venv interartic-venv
source interartic-venv/bin/activate  
pip install pip --upgrade
pip install celery==4.4.6 redis==3.5.3 flask==1.1.2 redis-server==6.0.9 pandas==1.2.4
REDIS=$(python -c 'import redis_server
print(redis_server.REDIS_SERVER_PATH)
')
deactivate
```

```bash
mv interartic-venv/bin/celery interartic-venv/bin/flask $REDIS bin/
mv interartic-venv/lib/python3.7/site-packages/* lib/python3.7/site-packages/
rm -rf interartic-venv/
```

4. Now the interARTIC environment is done, but the hard part is the artic pipeline which needs a different python environment. Now let us grab compiled binaries for artic and its dependencies through conda repositories.

   i) In the same virtual machine install an older miniconda

    ```bash
    rm -rf ~/miniconda3/
    wget https://repo.anaconda.com/miniconda/Miniconda3-4.3.11-Linux-x86_64.sh
    ./Miniconda3-4.3.11-Linux-x86_64.sh -b -p $HOME/miniconda3
    rm Miniconda3-4.3.11-Linux-x86_64.sh
    ```

    ii) Now clone the artic repository
    ```bash
    cd ..
    git clone https://github.com/artic-network/artic-ncov2019.git
    cd artic-ncov2019 && git checkout 7e359dae37d894b40ae7e35c3582f14244ef4d36
    cd ..
    ```

    iii) Grab the dependencies for artic through conda. This will take ages.
    ```bash
    ~/miniconda3/bin/conda env create -f artic-ncov2019/environment.yml
    ```

    iv) Move the relavent binaries and library modules
    ```bash
    cd interartic_bin
    mkdir artic_bin
    mv ~/miniconda3/envs/artic-ncov2019/bin artic_bin/
    mv ~/miniconda3/envs/artic-ncov2019/lib artic_bin/
    rm -rf artic_bin/lib/node_modules
    ```

    v) Cleanup pcaches
    ```bash
    find ./ -name __pycache__ -type d | xargs rm -r
    ```

    vi) Hard coded paths such as `/home/user/miniconda3/envs/artic-ncov2019/bin/python3.6` must be replaced with `/usr/bin/env python3.6`

    Some ugly and lazy example grep commands to patch these:

    ```bash
    cd artic_bin/bin
    grep -l "#\!/home\/hasindu\/miniconda3\/envs\/artic\-ncov2019\/bin/python3.6" * | while read p; do
      echo $p;
      sed -i "s/\/home\/hasindu\/miniconda3\/envs\/artic\-ncov2019\/bin\/python3.6/\/usr\/bin\/env python3.6/g" $p;  
    done

    grep -l "#\!/home\/hasindu\/miniconda3\/envs\/artic\-ncov2019\/bin/python" * | while read p; do
      echo $p;
      sed -i "s/\/home\/hasindu\/miniconda3\/envs\/artic\-ncov2019\/bin\/python/\/usr\/bin\/env python/g" $p;  
    done

    grep -l "#\!/home\/hasindu\/miniconda3\/envs\/artic\-ncov2019\/bin/perl" * | while read p; do
      echo $p;
      sed -i "s/\/home\/hasindu\/miniconda3\/envs\/artic\-ncov2019\/bin\/perl/\/usr\/bin\/env perl/g" $p;  
    done
    ```

    vii) Hard coded paths such as `exec' /home/user/miniconda3/envs/artic-ncov2019/bin/python/` must be replaced with  `exec' /usr/bin/env python`

    ```bash
    grep -l "exec' \/home\/hasindu\/miniconda3\/envs\/artic\-ncov2019\/bin/python" * | while read p; do
      echo $p;
      sed -i  "s/exec' \/home\/hasindu\/miniconda3\/envs\/artic\-ncov2019\/bin\/python/exec' \/usr\/bin\/env python/g" $p;  
    done
    ```

5) Now tarball

```bash
cd ../../../
tar zcvf interartic_bin.tar.gz interartic_bin
```

6) Extract on another Linux computer and thoroughly test.


Look at the (run.sh)[https://github.com/Psy-Fer/interARTIC/blob/master/run.sh] to see how this is run. The following are some important environmental variables.


```bash
export PYTHONNOUSERSITE=1
unset PYTHONHOME
unset PYTHONPATH
```

Run the main.py from the extracted directory inside a subshell:

```bash
( bin/python3.7 main.py ... )&
```

Run the celery from the extracted directory inside a subshell by exporting the artic_bin/bin to PATH and /artic_bin/lib/ to LD_LIBRARY_PATH:

```bash
( export PATH=`pwd`/artic_bin/bin:`pwd`/scripts:$PATH; export LD_LIBRARY_PATH=`pwd`/artic_bin/lib/:$LD_LIBRARY_PATH; bin/python3.7m bin/celery worker -A main.celery )&
```
