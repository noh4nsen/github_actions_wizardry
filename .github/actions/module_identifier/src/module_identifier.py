#!.venv/bin/python

import os, io, yaml, time, logging
from github import Github, Auth

class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[94m',    # Blue
        'INFO': '\033[92m',     # Green
        'WARNING': '\033[93m',  # Yellow
        'ERROR': '\033[91m',    # Red
        'RESET': '\033[0m'      # Reset color
    }
    def format(self, record):
        log_message = super().format(record)
        log_level_color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        log_date = time.strftime('%H:%M:%S | %m/%d/%Y', time.localtime(record.created))
        return f'[{log_date}]\t::\t{log_level_color}{record.levelname}{self.COLORS["RESET"]}\t::>\t{log_message}'

logger = logging.getLogger()
logger.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setFormatter(ColoredFormatter('%(message)s'))
logger.addHandler(console_handler)

def main():
    GITHUB_TOKEN, REPO, PULL_NUMBER, MULTI_PROJECT_DIRECTORY, IGNORED_DIRECTORIES = load_environment_variables(load_config())
    validate_and_set_output(*traverse_files(initialize(GITHUB_TOKEN, REPO, PULL_NUMBER), IGNORED_DIRECTORIES, MULTI_PROJECT_DIRECTORY))

def initialize(GITHUB_TOKEN, REPO, PULL_NUMBER):
    files = Github(auth=Auth.Token(GITHUB_TOKEN)).get_repo(REPO).get_pull(PULL_NUMBER).get_files()
    logger.info(f"Retrieved files from pull request: https://github.com/{REPO}/pull/{PULL_NUMBER}")
    return files

def load_config():
    if os.path.exists('config.yml'):
        with io.open('config.yml', 'r') as stream:
            config = yaml.safe_load(stream)
            logger.info("Loaded config.yml.")
    elif os.path.exists('config.yaml'):
        with io.open('config.yaml', 'r') as stream:
            config = yaml.safe_load(stream)
            logger.info("Loaded config.yaml.")
    return config

def load_environment_variables(config):
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    REPO = os.getenv("REPO")
    PULL_NUMBER = int(os.getenv("PULL_NUMBER"))
    MULTI_PROJECT_DIRECTORY = config["multi_project_directory"]
    IGNORED_DIRECTORIES = config["ignored_directories"]
    logger.info("Loaded environment variables.")
    return GITHUB_TOKEN, REPO, PULL_NUMBER, MULTI_PROJECT_DIRECTORY, IGNORED_DIRECTORIES

def traverse_files(files, IGNORED_DIRECTORIES, MULTI_PROJECT_DIRECTORY):
    module_name = error_message = ""
    logger.info("Identifying module being changed.")
    for file in files:
        parts = file.filename.split("/")
        if parts[0] in IGNORED_DIRECTORIES:
            continue       
        module_name_aux = set_project_name(parts, MULTI_PROJECT_DIRECTORY)
        if module_name != module_name_aux and module_name != "":
            error_message="Multiple modules are being modified in this PR. Use [skip ci] and/or handle them separately if needed."
            module_name = ""
            break
        module_name = module_name_aux
    if module_name != "":
        logger.info(f"Module {module_name} is being modified in this PR.")
    return module_name, error_message

def set_project_name(parts, MULTI_PROJECT_DIRECTORY):
    module_name = parts[0]
    if parts[1] in MULTI_PROJECT_DIRECTORY:
        module_name = f"{module_name}/{parts[1]}"
    return module_name

def validate_and_set_output(module_name, error_message):
    if module_name == "" and error_message == "":
        error_message = "No root module is being modified in this PR."
        logger.error(error_message)
        set_github_output(module_name, error_message)
    elif module_name == "":
        logger.error(error_message)
        set_github_output(module_name, error_message)
    else:
        logger.info(f"Setting module {module_name} as an output.")
        set_github_output(module_name, error_message)

def set_github_output(module_name, error_message):
    with open(os.getenv("GITHUB_OUTPUT"), "a") as gho:
        print(f"module_name={module_name}", file=gho)
        print(f"error={error_message}", file=gho)

if __name__ == '__main__':
    main()