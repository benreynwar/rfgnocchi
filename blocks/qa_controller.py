import os
import unittest
import shutil
import logging
import cmath
import math

import testfixtures

from pyvivado import project, signal
from pyvivado import config as pyvivado_config

from rfgnocchi.blocks import controller
from rfgnocchi import config

logger = logging.getLogger(__name__)

def make_blank_d():
    return {
        'reset': 0,
        'clear': 0,
        'i_data_tdata': 0,
        'i_data_tvalid': 0,
        'i_data_tlast': 0,
        'i_config_tdata': 0,
        'i_config_tvalid': 0,
        'o_data_tready': 0,
        'i_error_tdata': 0,
        'i_error_tvalid': 0,
    }


class TestControllerCompiler(unittest.TestCase):

    def test_one(self):
    
        directory = os.path.abspath('proj_qa_testcontroller')
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)

        interface = controller.get_controller_interface({})

        n_wait_lines = 20
        wait_data = []
        for wait_index in range(n_wait_lines):
            if wait_index < 10:
                reset = 1
            else:
                reset = 0
            input_d = make_blank_d()
            input_d['reset'] = reset
            wait_data.append(input_d)
        input_data = []
        
        p = project.FileTestBenchProject.create(
            interface=interface, directory=directory,
            board=config.default_board,
            part=config.default_part,
        )

        t = p.wait_for_most_recent_task()
        errors = t.get_errors_and_warnings()
        self.assertEqual(len(errors), 0)

        # Run the simulation
        runtime = '{} ns'.format((len(input_data) + 20) * 10)
        errors, output_data = p.run_simulation(
            input_data=wait_data+input_data, runtime=runtime)
        
        self.assertEqual(len(errors), 0)

        
if __name__ == '__main__':
    config.setup_logging(logging.DEBUG)
    unittest.main()
