---
layout: default
title: Installation
nav_order: 2
---

![](assets/installation.png)

# Installation Instructions

This is a python project but it does have a few non-python dependencies. I have created an `environment.yaml` file 
that would make the installation process a little bit easier I hope. This `yaml` file will change in the future as 
we add more functionalities and move some of them to the `ContainerRunner` module.

## Installing Conda

This one is fairly straightforward, you can follow the instructions [here](https://docs.conda.io/projects/conda/en/stable/user-guide/install/index.html) after running the installation script you should
be able to activate/deactivate conda environments. If you are installing this under HPC, I suggest that you move the location
of your conda cache to a different location. You can do that by following the instructions [here](https://stackoverflow.com/questions/58131555/how-to-change-the-path-of-conda-base), the other option
is that you can create a [symbolic link](https://stackoverflow.com/questions/1951742/how-can-i-symlink-a-file-in-linux) to your `.cache`, `.singularity` and `.conda` folders in your `~` where the actual
folders are in a partition with more storage. 

## Installing Benchmate

### Using the installation script

This project has a decent number of dependencies, to overcome some hurdles we have created an installation script but this 
has only been tested on Linux systems. 

```bash
# clone the repository
git clone https://github.com/ccmbioinfo/ccm_benchmate

# enter benchmate director
cd benchmate

bash install_benchmate.sh

```

This will create the minimum installation instance without any database support. If you want to install a postgres
database locally you will need to set some parameters

```bash
# install postgres and create the database
bash install_benchmate.sh -p -c -e .env_file -d <database_dir>
```

The env file contains all the secrets you will need to set up the database. Below is a quick example. The 
variable names **have to** match otherwise the script will fail. 

```dotenv
PG_USER=<username>
PG_PASSWORD=<password>
PG_DATABASE=benchmate
PG_HOST=localhost
PG_PORT=5432
```

After the installation is complete you should have a benchmate installation under the conda environment named "benchmate"

You can activate this by usint `conda activate benchmate`. Your database instance should already be running under
`PG_HOST:PG_PORT`. All the data associated with the database will be under the `<database_dir>` you specified in the installation
script. The database will continue running until the machine running the database is turned off (or if this is running in HPC) until
that specific job is completed. This does not mean that you will need to re-do the calculations and queries all over again. You will
just need to re-start the database instance.

```bash
conda activate benchmate

pg_ctl -D <database_dir> -l <database_dir>/logfile start
```

### Manual installation (reccomended at the moment)

The `install_benchmate.sh` has not gone through rigourous testing. Currently if you want to install the package you can follow these steps. 

1. Install conda (same as above)
2. Clone the repo (still the same)
3. create a conde environment:

The script is designed to do this for you but it is a rather simple step:

```bash
cd ccm_bencmate

conda create env -f environmemt.yaml
```

This will create a conda envrionment and intall all the non-python dependencies. It currently does not include postgres because 
the functionalities related to the knowledgebase is still under heavy development. You will still be able to use apis, genome, 
structure, sequence, molecule, ranges, genomic_ranges and literature modules. Whenever applicable they can interact with each other. All the 
class instances save for genome are pickleable. Unless you create an in-memory sqlite database there is no need to pickle a genome
instance. All the information is saved as a database. 

After creating the environment, you can install python dependencies

```bash
pip install -r requirements. txt
```

After you install all the dependencies you can install benchmate. Assuming you are inside the ccm_bencmate root directory 
(where the `setup.py` file is) 

```bash
pip install .
```

If you run into issued during installation this might be due to detectron installation. To get around this you can try installing detectron
manually after all the other dependencies installed. To do this simply remove the detectron line from the `requirements.txt` file and run the above command again.
After all the other dependencies are installed you can run the following commands to install detectron

```bash
pip install git+https://github.com/facebookresearch/detectron2.git@ff53992b1985b63bd3262b5a36167098e3dada02
```


## A Quick note about model selection

You can see in the config.py file that we have made some decisions about which models to use as a default in the package. 
These decisions were made with a couple of important considerations in ming. 

1. The models need to be robust and actually follow instructions (not every instruction tuned model does that or does it reliably)
2. They need to be small enough to be run in <40GB of VRAM (you can probably run benchmate no problem with a GTX5090 that you can buy at a computer hardware store)
3. They are fast(-ish), this was the main consideration for choosing a static model for semantic chunking. 

## Containers

We are working on creating docker containers and a `docker_compose.yaml` file to make this a less painful process. 
Once those developments are done this documentation will be updated. 

## Conda package

Similarly, once all the core components are completed we are planning on creating a conda package that would make this 
installation process a single line of code. 

Please create an issue with all the error messages if you run into problems. 