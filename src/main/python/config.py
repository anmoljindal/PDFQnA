import yaml
import os

class ConfigLoader:
    def __init__(self, config_path="resources/config.yaml"):
        """
        Initializes the ConfigLoader with the path to the YAML configuration file.
        
        :param config_path: Path to the YAML configuration file.
        """
        self.config_path = config_path

    def get_config(self):
        """
        Reads the YAML configuration file and returns the configuration as a dictionary.
        
        :return: Configuration dictionary.
        :raises FileNotFoundError: If the configuration file is not found.
        :raises yaml.YAMLError: If there is an error parsing the YAML file.
        """
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found at path: {self.config_path}")

        with open(self.config_path, 'r') as file:
            try:
                config = yaml.safe_load(file)
                return config
            except yaml.YAMLError as e:
                raise yaml.YAMLError(f"Error parsing the YAML file: {e}")