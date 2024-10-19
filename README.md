# Disengagement Interface

This repo is connected to my forked and modified version of the carlaviz repo: https://github.com/bbhardin/carlaviz_disengagementinterface

## Abstract

Autonomous Vehicles (AVs) and vehicles equipped with Advanced Driver Assistance Systems (ADAS) still face many situations in which they are unable to function safely, leaving their abilities limited and often requiring human intervention. A disengagement occurs when the system determines that it is no longer fit to operate in the given scenario or when a human manually takes control of or disables the system. However, not all disengagements are created equally. In particular, there are two types of disengagements that result in dangerous situations: 1) automation failures requiring immediate driver takeover of control and 2) driver disengagement due to the automation not handling a driving scenario correctly. These situations represent both automation-initiated and driver-initiated disengagement and can leave the driver little time to respond to the developing situation, particularly if their attention to the driving task is low because the automation is engaged. To make these situations safer, we present a novel methodology for advanced warning of potential disengagements based on past disengagements at the same location, and we design multiple interface prototypes for presenting these disengagement warnings. The system learns from disengagements that occur both due to algorithm decisions and those due to driver takeover related to impending events. We present some guidelines for distinguishing between takeovers due to driver interest in driving vs driver prevention of an impending situation. In this way, the system learns predictions from the human’s knowledge as well.


## General Structure

app_play.py starts the scene and calls the python file related to running the desired town, i.e. town03_disengage_scenario.py

townXX_disengage_scenario.py sets up the waypoints and route for the vehicle to follow as well as the points where we will disengage and reengage the automation.
[Picture of these points to be added]
