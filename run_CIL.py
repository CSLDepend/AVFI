import argparse
import logging
import sys

#Fault Injector Class
from agents.imitation.fault_injector import FaultInjector
#Camera Fault Model Class
from agents.imitation.camera_fault_model import *
#Controls Fault Model Class
from agents.imitation.output_fault_model import *
#Custom Benchmark Class
from UIUC_FI_Benchmark import *

from carla.benchmarks.corl_2017 import CoRL2017

from carla.tcp import TCPConnectionError
from carla.client import make_carla_client
from agents.imitation.imitation_learning import ImitationLearning
import time

try:
    from carla import carla_server_pb2 as carla_protocol
except ImportError:
    raise RuntimeError('cannot import "carla_server_pb2.py", run the protobuf compiler to generate this file')

if (__name__ == '__main__'):

    argparser = argparse.ArgumentParser(description=__doc__)
    argparser.add_argument(
        '-v', '--verbose',
        action='store_true',
        dest='debug',
        help='print debug information')
    argparser.add_argument(
        '--host',
        metavar='H',
        default='localhost',
        help='IP of the host server (default: localhost)')
    argparser.add_argument(
        '-p', '--port',
        metavar='P',
        default=2000,
        type=int,
        help='TCP port to listen to (default: 2000)')
    argparser.add_argument(
        '-c', '--city-name',
        metavar='C',
        default='Town01',
        help='The town that is going to be used on benchmark'
             + '(needs to match active town in server, options: Town01 or Town02)')
    argparser.add_argument(
        '-n', '--log_name',
        metavar='T',
        default='test',
        help='The name of the log file to be created by the scripts'
    )

    argparser.add_argument(
         '--avoid-stopping',
        action='store_true',
        default=False,
        help=' Uses the speed prediction branch to avoid unwanted agent stops'
    )

    argparser.add_argument(
         '--dump-dashcam',
        action='store_true',
        default=False,
        help=' Dumps the fault injected dash cam to an mp4 video'
    )

    args = argparser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    logging.info('listening to server %s:%s', args.host, args.port)

    agent = ImitationLearning(args.city_name,args.avoid_stopping)
    #Test Parameters
    #WaterDrop(300,400,100,100,2.0,2.0),TransparentOcclusion(200,300,200,200),
    fi_list=[{"ip":PassThrough(1),"op":ControlPassThrough(1)},
             {"ip":SolidOcclusion(0.7),"op":ControlPassThrough(1)},
             {"ip":TransparentOcclusion(0.7),"op":ControlPassThrough(1)},
             {"ip":WaterDrop(300,400,100,100,2.0,2.0),"op":ControlPassThrough(1)},
             {"ip":SaltAndPepper(0.7),"op":ControlPassThrough(1)},
             {"ip":Gaussian(0.7),"op":ControlPassThrough(1)},
             {"ip":PassThrough(1),"op":ControlDelayInjector(0.1)},
             {"ip":PassThrough(1),"op":ControlDropInjector(0.1)},
             {"ip":PassThrough(1),"op":ControlRandomInjector(0.2)},
    ]
    path_types=[True,True,True]
    path_cases=[10,10,10]
    weather_list=[1, 3, 6, 8]
    #Vehicle and ppl_density lists should be of the same length
    vehicle_density=[20]
    ppl_density=[50]
    for fm in fi_list:
        print("TOP_LEVEL_DEBUG:",args.city_name,fm["ip"].get_name(),fm["op"].get_name())
        f_i=FaultInjector(fm["ip"],fm["op"],args.city_name,args.dump_dashcam)
        agent.set_f_i(f_i)
        while True:
            try:
                with make_carla_client(args.host, args.port) as client:
                    uiuc_fi = UIUC_FI_Benchmark(args.city_name, args.log_name,f_i,path_types,
                            path_cases,weather_list,vehicle_density,ppl_density)
                    results = uiuc_fi.benchmark_agent(agent, client)
                    uiuc_fi._plot_summary(weather_list)
                    break
            except TCPConnectionError as error:
                logging.error(error)
                time.sleep(1)
            except Exception as exception:
                logging.exception(exception)
                sys.exit(1)
        if(args.dump_dashcam==True):
            f_i.saveVideo()
        del(f_i)
