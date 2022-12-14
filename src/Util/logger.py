import logging

_log_format = f"%(asctime)s - %(name)s - %(levelname)s - %(message)s"
_log_level = logging.DEBUG

#logging.basicConfig(
    #level=logging.DEBUG,
    #format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
   # handlers=[logging.StreamHandler()]
#)

def get_file_handler():
    file_handler = logging.FileHandler("x.log")
    file_handler.setLevel(logging.WARNING)
    file_handler.setFormatter(logging.Formatter(_log_format))
    return file_handler

def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(_log_level)
    stream_handler.setFormatter(logging.Formatter(_log_format))
    return stream_handler

def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(_log_level)
    #logger.addHandler(get_file_handler())
    logger.addHandler(get_stream_handler())
    return logger