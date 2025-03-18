# CROSSBOW PROJECT

Crossbow project is a tool designed to analyse and determine the kinematics of an object.  
The kinematics are determined thanks to an experimental setup consisting of two cameras.  
In the early stages of the development, the main purpose was to exctract the kinematics of a sphere-shaped object (i.e. a ball). Eventually, it was designed to be scalable and detect any kind of object (providing close to no modification).  
The results of the analysis can be visualized and saved.

*Note : Please keep in mind that this code was developped in the context of a student project. The code quality and consistency is not always optimal. Any improvement idea is welcomed.* 

## Installation

The project was entirely developped and tested in Linux, and the tutorial will only be for this OS.  
First install the required packages using the package manager [pip](https://pip.pypa.io/en/stable/).  
> It is adivsed (but not mandatory) to create a venv
```bash
pip install -r requirements.txt
```

## Usage

### A. Tuning the file for your needs

The usage can be tuned for your specific experiment. To do so, you may modify the [run_experience.py](src/run_experience.py) file. At the end of this section will be attached the default file (as a backup).  A list of the available methods will be provided in the [documentation](documentation/README.md).  
To run, the program needs a JSON configuration file. This file is a description of your experimental setup. An example is provided [here](utils/configuration_example.json).  
The creation of this file for your own needs is provided in the [documentation](./documentation/README.md#the-configuration-file).
### B. Running the program

Once you are ready to run the program, you may perform the following steps:  
1. Run the following in your terminal, where `<path_to_src_directory>` is the path to the [src](src) directory of this repository :  
`export PYTHONPATH="${PYTHONPATH}:<path_to_src_directory>"`


2. Run, from the root of the repository :
`python3 exec/entrypoint.py --config <path_to_your_config_file>`

### C. Default [run_experience.py](src/run_experience.py) file
The default file is as follows:

```commandline
from constants import AvailableProjectileFinderMethods
from src.constants import ColorDomain
from src.experience_manager import ExperienceManager


def run_experience(config: str):
    experience_manager = ExperienceManager(configuration_file_path=config)

    experience_manager.set_projectile_finder_method(AvailableProjectileFinderMethods.FIND_CIRCLES)
    experience_manager.set_color_domain_to_find_projectile(ColorDomain.GRAYSCALE)

    experience_manager.compute_kinematics()
    experience_manager.save_results_as_csv()

```



## Contributing

The project was intentionally designed to be scalable and easily modifiable. It is likely that I will not work further on the project. Therefore, this repository can be forked and used/improved for your own specific needs.  
The main point for improvement is the possibility to add other detector functions. These functions could be, for example, machine learning models trained on specific objects (let's say a drone for instance...).  
The process for adding your own function is described in the [documentation](documentation/README.md).

## License

This code was developped in the context of a school project for ISAE-SUPAERO (Toulouse, France) and is completely free to use. There is no license whatsoever related to this.