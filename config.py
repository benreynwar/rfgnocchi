import os
import logging

basedir = os.path.dirname(__file__)
ettus_fpgadir = os.path.join(basedir, '..', 'fpga', 'usrp3', 'lib')
ettus_coregendir = os.path.join(basedir, '..', 'fpga', 'usrp3', 'lib', 'coregen')
ettus_rfnocdir = os.path.join(basedir, '..', 'fpga', 'usrp3', 'lib', 'rfnoc')

default_part = 'xc7a200tfbg676-2'
default_board = 'xilinx.com:ac701:part0:1.0'

def setup_logging(level):
    "Utility function for setting up logging."
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    # Which packages do we want to log from.
    packages = ('__main__', 'pyvivado', 'rfgnocchi')
    for package in packages:
        logger = logging.getLogger(package)
        logger.addHandler(ch)
        logger.setLevel(level)
    # Warning only packages
    packages = []
    for package in packages:
        logger = logging.getLogger(package)
        logger.addHandler(ch)
        logger.setLevel(logging.WARNING)
    logger.info('Setup logging at level {}.'.format(level))
