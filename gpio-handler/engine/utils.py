import yaml


# Function to load configuration from YAML file
def load_config(config_path):
    with open(config_path, "r") as file:
        return yaml.safe_load(file)
