

class EgoAgent(AutonomousAgent):
    
    def setup(self, path_to_conf_file):
        """
        Setup the agent parameters
        """

    def sensors(self):
        """
        Define the sensor suite required by the agent
        """

        sensors = []

        return sensors
    
    def run_step(self, input_data, timestep):
        """
        Execute one step of navigation.
        """

        control = do_something_smart(input_data, timestamp)
        
        return control
    