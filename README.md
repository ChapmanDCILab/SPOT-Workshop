# SPOT Automation Helper 
## Written by: Michael [@cdnmonitor](https://github.com/cdnmonitor)
## Contributors: Kalin Richardson [@kalrich](https://github.com/kalrich)
## Version: 1.0 
## Description: 
This script is designed to help students learn Boston Dynamic's SPOT robot programming. This code automates movement using a helper class with some basic functions (spot_helper.py) and a main function where students will be editing their own code (code_here.py).
## Requirements:

1. **[INSTALL/DOWNLOAD PYTHON](https://www.python.org/downloads/)** 

   - **for WINDOWS:** install from the [Microsoft Store](https://apps.microsoft.com/detail/9ncvdn91xzqp?hl=en-us&gl=US) instead of downloading!
   - **for MAC:** the download should do!


2. **INSTALL PIP:** ```curl https://bootstrap.pypa.io/get-pip.py | python3```

3. **CHECK THAT BOTH ARE INSTALLED**
   - ```python3 --version```
   - ```pip --version```


## Usage:
**INSTALL BOSDYN PACKAGES:**

```python3 -m pip install bosdyn-client==3.3.2 bosdyn-mission==3.3.2 bosdyn-choreography-client==3.3.2```

**INSTALL REQUIREMENTS.TXT:**

```pip install -r requirements.txt```

**TO RUN CODE:**

```python3 code_here.py ```


## Understanding the Emergency Stop
code_here.py has a function that listens for when the enter button is pressed. When this happens, the function in spot_helper.py (request_stop) is called. This sets stop_requested's value to True, as it starts as False. Each movement function checks if stop_requested is True, and if it is, it will stop the robot. This is done so no action after the stop is requested is executed.

## Understanding the SpotHelper Class
The SpotHelper class is a class that contains all the functions needed to move SPOT. This class can be imported into any file, for now code_here.py. These functions can do things from moving SPOT forward, sitting, tilting, standing, and rotating its body.

#### This codebase is intended to be used with Chapman University's Fowler School of Engineering, Design Create Innovate Makerspace workshop. This code can be used for SPOT and soon for SPOT's Arm manipulation.
