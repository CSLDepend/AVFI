from carla.benchmarks.corl_2017 import *

class UIUC_FI_Benchmark(CoRL2017):
    def __init__(self,city_name,name_to_save,f_i_in,path_types_in,path_cases_in,weather_list,veh_tasks,ppl_tasks):
        self.f_i=f_i_in
        self.path_types=path_types_in # boolean list of the form [straight,curved,nav]
        self.path_cases=path_cases_in
        self.weather_list = weather_list
        self.vehicle_tasks=veh_tasks
        self.ppl_tasks=ppl_tasks
        super().__init__(city_name,name_to_save)

    def _poses_town01(self):
        modified_paths=[]
        paths = super()._poses_town01()
        if self.path_types[0] == True:
            modified_paths.append(paths[0][:self.path_cases[0]])
        if self.path_types[1] == True:
            modified_paths.append(paths[1][:self.path_cases[1]])
        if self.path_types[2] == True:
            modified_paths.append(paths[2][:self.path_cases[2]])

        return modified_paths

    def _poses_town02(self):
        modified_paths=[]
        paths = super()._poses_town02()
        if self.path_types[0] == True:
            modified_paths.append(paths[0][:self.path_cases[0]])
        if self.path_types[1] == True:
            modified_paths.append(paths[1][:self.path_cases[1]])
        if self.path_types[2] == True:
            modified_paths.append(paths[2][:self.path_cases[2]])

        return modified_paths

    def _build_experiments(self):
        """
        Creates the whole set of experiment objects,
        The experiments created depend on the selected Town.
        """

        # We set the camera
        # This single RGB camera is used on every experiment

        camera = Camera('CameraRGB')
        camera.set(CameraFOV=100)

        camera.set_image_size(800, 600)

        camera.set_position(200, 0, 140)
        camera.set_rotation(-15.0, 0, 0)

        #weathers = [1, 3, 6, 8, 4, 14]
        weathers = self.weather_list

        vehicles_tasks = self.vehicle_tasks
        pedestrians_tasks = self.ppl_tasks

        if self._city_name == 'Town01':
            poses_tasks = self._poses_town01()
        else:
            poses_tasks = self._poses_town02()

        experiments_vector = []
        exp_counter=0
        for weather in weathers:
            for density in range(min(len(vehicles_tasks),len(pedestrians_tasks))):
                for iteration in range(len(poses_tasks)):
                    poses = poses_tasks[iteration]
                    vehicles = vehicles_tasks[density]
                    pedestrians = pedestrians_tasks[density]
    
                    conditions = CarlaSettings()
                    conditions.set(
                        SynchronousMode=True,
                        SendNonPlayerAgentsInfo=True,
                        NumberOfVehicles=vehicles,
                        NumberOfPedestrians=pedestrians,
                        WeatherId=weather,
                        SeedVehicles=123456789,
                        SeedPedestrians=123456789
                    )
                    # Add all the cameras that were set for this experiments

                    conditions.add_sensor(camera)

                    experiment = Experiment()
                    experiment.set(
                        Conditions=conditions,
                        Poses=poses,
                        Id=exp_counter,
                        Repetitions=1
                    )
                    experiments_vector.append(experiment)
                    exp_counter+=1

        return experiments_vector

    def _get_details(self):
        # Function to get automatic information from the experiment for writing purposes
        return 'uiuc_fi_2018_' + self._city_name + '_' + self.f_i.get_injector_name()
        