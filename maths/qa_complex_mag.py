import os
import unittest
import random
import logging

import testfixtures

from pyvivado import project, signal
from pyvivado import config as pyvivado_config

from rfgnocchi.maths import complex_mag
from rfgnocchi import config

logger = logging.getLogger(__name__)

class TestComplexMag(unittest.TestCase):
    
    def test_one(self):

        directory = os.path.abspath('proj_qa_testcomplexmag')
        width = 16
        params = {
            'width': width,
        }

        def make_random_complex(width):
            max_val = pow(2, width-1)-1
            min_val = -pow(2, width-1)
            real_v = random.randint(min_val, max_val)
            imag_v = random.randint(min_val, max_val)
            c = complex(real_v, imag_v)
            return c

        n_values = 100
        values = [make_random_complex(width) for i in range(n_values)]

        # Make wait data.  Sent while initialising.
        n_data = 100
        n_wait_lines = 20
        wait_data = []
        for wait_index in range(n_wait_lines):
            if wait_index < n_wait_lines/2:
                reset = 1
            else:
                reset = 0
            input_d = {
                'reset': reset,
                'i_tdata': 0,
                'i_tlast': 0,
                'i_tvalid': 0,
                'o_tready': 0,
            }
            wait_data.append(input_d)

        # Make input and expected data
        input_data = []
        for v in values:
            input_d = {
                'reset': 0,
                'i_tdata': signal.complex_to_uint(v, width),
                'i_tlast': 0,
                'i_tvalid': 1,
                'o_tready': 1,
            }
            input_data.append(input_d)
        # Wait for reset
        for i in range(20):
            input_d = {
                'reset': 0,
                'i_tdata': 0,
                'i_tlast': 0,
                'i_tvalid': 0,
                'o_tready': 1,
            }
            input_data.append(input_d)
            

        interface = complex_mag.get_complex_mag_interface(params)
        p = project.FileTestBenchProject.create_or_update(
            interface=interface, directory=directory,
            board=config.default_board,
            part=config.default_part,
        )
        t = p.wait_for_most_recent_task()
        errors = t.get_errors()
        self.assertEqual(len(errors), 0)

        # Run the simulation
        runtime = '{} ns'.format((len(wait_data+input_data) + 20) * 10)
        errors, output_data = p.run_simulation(
            input_data=wait_data+input_data, runtime=runtime)

        output_mags = [d['o_tdata'] for d in output_data if d['o_tvalid']]
        expected_mags = [int(abs(v)) for v in values]
        testfixtures.compare(output_mags, expected_mags)
        
if __name__ == '__main__':
    config.setup_logging(logging.DEBUG)
    unittest.main()
