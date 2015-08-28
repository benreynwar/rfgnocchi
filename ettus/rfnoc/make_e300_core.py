import os
import logging
import math

from pyvivado import builder, interface, signal, project

from rfgnocchi import config, noc, ettus

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    config.setup_logging(logging.DEBUG)
    builder = ettus.get_builder('e300')
    directory = os.path.abspath('proj_qa_e300')
    p = project.BuilderProject.create_or_update(
        design_builders=[builder],
        simulation_builders=[],
        part='xc7z020clg484-1',
        parameters={'factory_name': 'e300'}, 
        directory=directory,
    )

