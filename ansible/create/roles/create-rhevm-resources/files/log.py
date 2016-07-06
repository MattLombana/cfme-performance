import time


def log(string):
    """write string to file"""
    with open('fakevdsm.log', 'a') as file:
        file.write(string)
        file.write('\n')


def debug(string):
    time_stamp = time.strftime('%Y-%m-%d %H:%M:%S')
    log('{} DEBUG {}'.format(time_stamp, string))


def info(string):
    time_stamp = time.strftime('%Y-%m-%d %H:%M:%S')
    log('{} INFO {}'.format(time_stamp, string))


def warning(string):
    time_stamp = time.strftime('%Y-%m-%d %H:%M:%S')
    log('{} WARNING {}'.format(time_stamp, string))


def error(string):
    time_stamp = time.strftime('%Y-%m-%d %H:%M:%S')
    log('{} ERROR {}'.format(time_stamp, string))
