import logging
from logging import Handler, LogRecord, Formatter, FileHandler
import datetime
import os

# create formatter
FORMATTER = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')



class StdOutHandler(Handler):
    """Class for standard input and output handler (terminal print)
    """
    def emit(self, record: LogRecord) -> None:
        # Get the logging level from the root logger
        root_logger = logging.getLogger()
        logging_level = root_logger.getEffectiveLevel()
        # Only print messages at or above the logging level set
        if record.levelno >= logging_level:
            print(FORMATTER.format(record))

class FileHandlerCustom(FileHandler):
    """Class for file handler (file)
    """
    def __init__(self, name):
        super().__init__(name)

    def emit(self, record: LogRecord) -> None:
        # Get the logging level from the root logger
        root_logger = logging.getLogger()
        logging_level = root_logger.getEffectiveLevel()
        # Only write messages at or above the logging level set
        if record.levelno >= logging_level:
            record.msg = FORMATTER.format(record)
            FileHandler.emit(self, record)

def init_logger(logging_level: int = logging.DEBUG,
                print_to_stdout: bool = True, log_in_file: bool = False, new_file: bool = False):
    """This function adds custom handlers to the root logger to send logging info.

    Args:
        logging_level (int, optional): _description_. Defaults to logging.DEBUG.
        print_to_stdout (bool, optional): Set to true if logging is also written to the standard output. Defaults to True.
        log_in_file (bool, optional): Set to true if logging is also written to the file. Defaults to False.
        new_file (bool, optional): Set to true if a new log file should be created on each run. Defaults to False.
    Examples:
    --------
    >>> import logging
    >>> from logger import init_logger
    >>> init_logger(logging.DEBUG, print_to_stdout=False, log_in_file=True)
    >>> logging.info('Write log info')
    >>> logging.error('Write log error')
    >>> logging.warning('Write log warning')
    >>> logging.debug('Write log debug')
    """
    
    # If no name is provided we will add handlers to the root logger, which is Best practice imho
    root_logger = logging.getLogger()
    root_logger.setLevel(logging_level)
    # Clear handlers before adding new handlers
    root_logger.handlers.clear()

    # Set up handler for standard output
    if print_to_stdout:
        standard_handler = StdOutHandler()
        root_logger.addHandler(standard_handler)
    
    if log_in_file:
        if not os.path.exists("log/"):
            os.makedirs("log/")
        today_date = datetime.datetime.today().strftime('%Y%m%d')
        log_folder_path = os.path.join("log", today_date)
        if not os.path.exists(log_folder_path):
            os.makedirs(log_folder_path)
        
        current_time = datetime.datetime.now().strftime('%H%M%S')
        log_file_name = f"log.log"  # Log file name with start time
        
        if new_file:
            existing_logs = os.listdir(log_folder_path)
            count = 1
            for logname in existing_logs:
                if current_time in logname:  # Checking if the file name contains 'log'
                    count += 1
            if count > 1:
                log_file_name = f"log_{current_time}_{count}.log"
            else:
                log_file_name = f"log_{current_time}.log"
        
        file_handler = FileHandlerCustom(os.path.join(log_folder_path, log_file_name))
        root_logger.addHandler(file_handler)
