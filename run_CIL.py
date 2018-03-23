import argparse
import logging
import sys

#Fault Injector Class
from agents.imitation.fault_injector import FaultInjector
#Camera Fault Model Class
from agents.imitation.camera_fault_model import *
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
        default=True,
        help=' Uses the speed prediction branch to avoid unwanted agent stops'
    )

    args = argparser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)

    logging.info('listening to server %s:%s', args.host, args.port)

    agent = ImitationLearning(args.city_name,args.avoid_stopping)
    #Test Parameters
    #WaterDrop(300,400,100,100,2.0,2.0),TransparentOcclusion(200,300,200,200),
    f_i_list=[WaterDrop(300,400,100,100,2.0,2.0)]
    path_types=[True,False,False]
    path_cases=[1,0,0]
    weather_list=[1]
    #Vehicle and ppl_density lists should be of the same length
    vehicle_density=[50]
    ppl_density=[50]

    for cfm in f_i_list:
        print("TOP_LEVEL_DEBUG:",args.city_name,cfm.get_name())
        f_i=FaultInjector(cfm,args.city_name)
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
        f_i.saveVideo()
        del(f_i)
