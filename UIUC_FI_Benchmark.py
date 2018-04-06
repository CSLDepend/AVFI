from carla.benchmarks.corl_2017 import *
import csv

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
        return  self._city_name + '_' + self.f_i.get_ip_injector_name() + '_' +\
                self.f_i.get_op_injector_name()

    @staticmethod
    def _get_experiments_names(experiments):

        name_cat = 'w'
        unique_weathers =list(set([x.Conditions.WeatherId for x in experiments]))
        unique_weathers.sort()
        for weather in unique_weathers:
            name_cat += str(weather) + '.'

        return name_cat

    def _write_summary_results(self, experiment, pose, rep,
                               path_distance, remaining_distance,
                               final_time, time_out, result):

        self._dict_stats['exp_id'] = experiment.id
        self._dict_stats['rep'] = rep
        self._dict_stats['weather'] = experiment.Conditions.WeatherId
        self._dict_stats['start_point'] = pose[0]
        self._dict_stats['end_point'] = pose[1]
        self._dict_stats['result'] = result
        self._dict_stats['initial_distance'] = path_distance
        self._dict_stats['final_distance'] = remaining_distance
        self._dict_stats['final_time'] = final_time
        self._dict_stats['time_out'] = time_out
        #Added two new fields
        self._dict_stats['vehicles'] = experiment.Conditions.NumberOfVehicles
        self._dict_stats['pedestrians'] = experiment.Conditions.NumberOfPedestrians
        self._dict_stats['IpInjectProb'] = self.f_i.input_fm.inject_prob
        self._dict_stats['OpInjectProb'] = self.f_i.output_fm.inject_prob
        self._dict_stats['FrameDelay'] = self.f_i.output_fm.frames_to_delay
        #End of modification

        with open(os.path.join(self._full_name, self._suffix_name), 'a+') as ofd:

            w = csv.DictWriter(ofd, self._dict_stats.keys())

            w.writerow(self._dict_stats)

    def _write_details_results(self, experiment, rep, reward_vec):

        with open(os.path.join(self._full_name,
                               'details_' + self._suffix_name), 'a+') as rfd:

            rw = csv.DictWriter(rfd, self._dict_rewards.keys())

            for i in range(len(reward_vec)):
                self._dict_rewards['exp_id'] = experiment.id
                self._dict_rewards['rep'] = rep
                self._dict_rewards['weather'] = experiment.Conditions.WeatherId
                self._dict_rewards['collision_gen'] = reward_vec[
                    i].collision_other
                self._dict_rewards['collision_ped'] = reward_vec[
                    i].collision_pedestrians
                self._dict_rewards['collision_car'] = reward_vec[
                    i].collision_vehicles
                self._dict_rewards['lane_intersect'] = reward_vec[
                    i].intersection_otherlane
                self._dict_rewards['sidewalk_intersect'] = reward_vec[
                    i].intersection_offroad
                self._dict_rewards['pos_x'] = reward_vec[
                    i].transform.location.x
                self._dict_rewards['pos_y'] = reward_vec[
                    i].transform.location.y
                #Added two new fields
                self._dict_rewards['vehicles'] = experiment.Conditions.NumberOfVehicles
                self._dict_rewards['pedestrians'] = experiment.Conditions.NumberOfPedestrians
                #End of modification

                rw.writerow(self._dict_rewards)

    #Modified to write summary to a file as well
    def _plot_summary(self, weathers):
        """
        We plot the summary of the testing for the set selected weathers.
        The test weathers are [4,14]

        """

        metrics_summary = compute_summary(os.path.join(
            self._full_name, self._suffix_name), [3])
        summary_f = open(os.path.join(self._full_name,self._suffix_name+'summary'), 'w')

        for metric, values in metrics_summary.items():

            print('Metric : ', metric)
            summary_f.write('Metric : ' + str(metric)+"\n")
            for weather, tasks in values.items():
                if weather in set(weathers):
                    print('  Weather: ', weather)
                    summary_f.write('  Weather: ' + str(weather)+"\n")
                    count = 0
                    for t in tasks:
                        print('    Task ', count, ' -> ', t)
                        summary_f.write('    Task '+ str(count) +' -> '+str(t)+"\n")
                        count += 1

                    print('    AvG  -> ', float(sum(tasks)) / float(len(tasks)))
                    summary_f.write('    AvG  -> '+ str(float(sum(tasks)) / float(len(tasks)))+"\n")
        summary_f.close()
