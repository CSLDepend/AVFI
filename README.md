AVFI: Fault Injection for Autonmous Vehicles using CARLA
===============

We have provided the Dockerfile which will build an image with all
the required packages and dependencies installed. Using this image
is the easiest way to run the CARLA client with the Fault Injection
campaign.

The self driving agent with the fault injector will run from within
the docker container. The server (world simulator with the AV) has 
to be started separately before running the agent from the docker
container. 

Make sure both the server and the client are using CARLA 0.8.1
https://github.com/carla-simulator/carla/releases/tag/0.8.1

First start the Carla World Server <br>
Example for Town01<br>
On Windows: `.\CarlaUE4.exe /Game/Maps/Town01 -carla-server -benchmark -fps=15 -windowed -ResX=800 -ResY=600 -carla-settings=.\Example.CarlaSettings.ini`

The settings file can be found here: https://github.com/carla-simulator/carla/blob/9a9ce7bfa1cc22c77e7ba36713af1ff3bd768392/Docs/Example.CarlaSettings.ini <br>
Ensure the the 'UseNetworking' property is set to 'true'. Take note of the 'WorldPort' number. This port number should be used when starting the agent.

To start the fault injection campaign using the client, run 
`python ./run_CIL.py --host [serverhostname] -p [serverport] -c [citymap]` <br>
Example for Town01 <br>
`python ./run_CIL.py --host [serverhostname] -p 2000 -c Town01`

The server and the client should have matching port and city parameters
For more information on how to run the client and the server, check the
README_CARLA_IL.md and the CARLA manual online.

UIUC FI Codebase
---------
1. **UIUC_FI_Benchmark.py** - This file sets up the experiments that the self-driving
agent will execute alongside the fault injection campaign. It also logs the metrics 
from the AV and Fault Injector

2. **/agents/imitation/fault_injector.py** - Given an input and output fault model,
this file is reponsible for perturbing the input measurements from the AV sensors 
and the output controls from the self driving agent. Takes as argument objects from
classes defined in `input_fault_model` and `output_fault_model`.

3. **/agents/imitation/input_fault_model.py** - Defines the CameraFaultModel,
MeasureFaultModel and CommandFaultModel classes as input fault models. 

4. **/agents/imitation/output_fault_model.py** - Defines Control fault models
that perturb control information from the self driving agent to the AV.

5. **/agents/imitation/imitation_learning.py** - Original IL agent code has been
modified to incorporate fault inejction through the FaultInjector class defined
in `fault_injector.py`.

Papers
-----

If you use AVFI, please cite the following papers.

1. Avfi: Fault injection for autonomous vehicles. <br>
Jha, Saurabh, Subho S. Banerjee, James Cyriac,
Zbigniew T. Kalbarczyk, and Ravishankar K. Iyer. DSN 2018
[[PDF](http://ssbaner2.cs.illinois.edu/publications/dsn2018_avfi/Paper.pdf)]

```
@inproceedings{jha2018avfi,
  title={AVFI: Fault Injection for Autonomous Vehicles},
  author={Jha, Saurabh and Banerjee, Subho S and Cyriac, James and Kalbarczyk, Zbigniew T and Iyer, Ravishankar K},
  booktitle={2018 48th Annual IEEE/IFIP International Conference on Dependable Systems and Networks Workshops (DSN-W)},
  pages={55--56},
  year={2018},
  organization={IEEE}
}
```


2. End-to-end Driving via Conditional Imitation Learning. <br> Codevilla,
Felipe and Müller, Matthias and López, Antonio and Koltun, Vladlen and
Dosovitskiy, Alexey. ICRA 2018
[[PDF](http://vladlen.info/papers/conditional-imitation.pdf)]


```
@inproceedings{Codevilla2018,
  title={End-to-end Driving via Conditional Imitation Learning},
  author={Codevilla, Felipe and M{\"u}ller, Matthias and L{\'o}pez,
Antonio and Koltun, Vladlen and Dosovitskiy, Alexey},
  booktitle={International Conference on Robotics and Automation (ICRA)},
  year={2018},
}
```
