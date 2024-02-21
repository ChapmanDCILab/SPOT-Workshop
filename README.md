# SPOT Automation Helper 
## Written by: Michael @cdnmonitor 
## Version: 1.0 
## Description: 
This script is designed to help students learning Boston Dynamic's SPOT robot to automate movement using a helper class with some basic functions. 
## Requirements:
bosdyn-client, bosdyn-mission, bosdyn-choreography-client 
## [Read more about the process:]
(https://sites.google.com/chapman.edu/the-dci-lab/home/tech-shop-equipment/boston-dynamics-spot-dog/spot-dog-coding?authuser=0)
## Usage:
To install:
```pip install requirements.txt```

To run code:
```python3 code_here.py ```

This codebase is intended to be used with Chapman University's Fowler School of Engineering, Design Create Innovate Makerspace workshop. This code can be used for SPOT and soon for SPOT's Arm manipulation.

## Understanding the Emergency Stop
code_here.py has a function that listens for when the enter button is pressed. When this happens, the function in spot_helper.py (request_stop) is called. This sets stop_requested's value to True, as it starts as False. Each movement function checks if stop_requested is True, and if it is, it will stop the robot. This is done so no action after the stop is requested is executed.

## Understanding the SpotHelper Class
The SpotHelper class is a class that contains all the functions needed to move SPOT. This class can be imported into any file, for now code_here.py. These functions can do things from moving SPOT forward, sitting, tilting, standing, and rotating its body.
