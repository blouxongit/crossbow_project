# Crossbow Project Documentation

The purpose of this README is to document as much as possible this project. The objective is to provide all the necessary informations for someone to be able to understand its mechanics and work on its development.

As of today (March 2025), we remind that the aim of this tool is to extract the kinematics of a moving target, by using a setup of high speed cameras.

## Simplified class diagram

The overall (simplified) architecture of this project is visible hereafter:
![General simplified architecture of the crossbow project](./images/class_diagram.svg)

## The configuration file

First things first, in order to run, the tool needs to be provided a configuration file. This configuration file is a simple JSON file that gives information about the conditions of the experience. This is the only thing that needs to be filled out manually by the user.  
An example of configuration file is provided : [./utils/configuration_example.json](../utils/configuration_example.json).  

### The content of the configuration file

This configuration file requires the characteristics of both cameras used:  
- The intrinsic parameters (they are dependent on the camera used)
- The extrinsic parameters (they are independant on the camera used)

**You are free to chose your unit system, but no matter what you do, you MUST remain consistent !!!**
> I highly recommend using the metric system since the focals of the cameras are almost always given in the metric system.

The extrinsic parameters also require angles. The choice not to use the classical yaw, pitch, roll angles was made intentionally, to not confuse the reader, since the frame used is not the same as the one on an aircraft. Instead, we use the alpha, beta and gamma angles. These angles design the rotations around the X,Y and Z axis, with respect to the world coordinate system.  
The camera reference system is an orthogonal direct frame, as shown below : 

![camera_reference_system](./images/camera_frame.png)  

Regarding the world reference system, it is up to you to decide it. The choice of this system should be mentionned in your experience plan.
> Usually, this system is chosen to be one of the camera's reference system. Therefore, only 6 measurements needs to be done (3 translations, 3 rotations corresponding to 1 camera) instead of 12 (same for 2 cameras).

### The Config

The reader of the configuration file is a simple JSON reader. It is located at [./src/configuration_reader.py](../src/configuration_reader.py).
This is a simple class that ensures the validity of the config, and stores it into two class objects called *CameraConfig*. The attributes of a *CameraConfig* instance are visible in the [simplified class diagram](#simplified-class-diagram).  
In the event someone would like to modify the architecture of the configuration file, the verification schema should also be modified. This schema is located in the [./src/constants.py](../src/constants.py) file.

The Config class created with the configuration file is then used to create/update other classes of the tool:

- The FilesManager
- The CameraSetup
- The ExperienceManager


## The FilesManager

The FilesManager class is designed to... manage the files. More especially, it is the class that will provide the appropriate images path on which we will perform image processing.  
This class is crucial in order to get precise and valid results. The main objective of this class is to yield pairs of images taken by both cameras at the same time. Concretely, at each step of time, the FilesManager is called to get the image taken from the left camera and from the right camera at this specific time.


### What path does it use ?

The FilesManager will only consider path to images in the following formats: *.jpg .png, .jpeg, .tif*.  
You can choose to add other formats in the [./src/constants.py](../src/constants.py) file.

### How does it create the pair of images 

When I asked about the high speed cameras used at the school, it appears there is already a mechanism to synchronize the capture of many cameras. This is increadibly useful for us, as we do not have to deal with complex matching methods (based on timestamps for instance).  
The function we use is `create_list_timed_matching_image_path_pair`. It itself calls `find_closest_image_path_to_form_pair`.  
Because we are lucky to have this setup (synchronization), the last function is trivial. Otherwise, this is the function that would require a bit of logic to form the appropriate pairs of images.

## The CameraSetup

This class is used to store the information on the cameras. It is used to store the intrinsic and extrinsic matrix of both cameras. The product of those matrix is called the projection matrix. The projection matrix is the one that will be used afterwards to compute the 3D points from a pair of 2D points.  
It simply contains two instances of `HighSpeedCameras`

## The DataTypes

Before going further into this documention, it appears wise to explain the different data types used. I will be honest here, even I get confused sometimes regarding the architecture of the different data types.  
The said architecture is shown below :

![Data types](./images/data_types.svg)

Here is a fast tour on how this works:

### The basic types 

The most basic types created are: 

- Point2D
- Point3D
- default types (str for path, np.ndarray for images...)

### The Pair type

This type is simply a pair of variables of the same type. It can be anything, as long as it is the same type.  
It was created because we encounter pairs almost all the time in this repository: pair of cameras, pairs of images, pairs of points...  
The attributes of this class are simply called `left` and `right`. For this reason, we will always talk about left camera, left point, left image... This has nothing to do whatsoever with the position of the cameras on the experiment.

### The TimedData type

In addition to dealing with lots of pairs, we also deal with lots of timed data. Indeed, we have timed images, timed coordinates, timed path...  
For this reason, it was decided to add create a `TimedData` class. This class simply possesses a `timestamp` and a `data` attribute. There exists no restriction on the type of the data.

### Combination of data types

Of course, now that we set our data types, we can combine them to make more useful ones. For instance we have:

- Point2DPair
- ImagePair
- TimedPoint3D
- TimedPoint2DPair
- ...

At this point, I am pretty sure the code is ugly and could be optimized and much prettier. However, this works like that and we are not yet at the point where we have types that we lose track of some.




