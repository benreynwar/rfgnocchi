import os
import unittest
import random
import logging

import testfixtures

from pyvivado import project, signal

from rfgnocchi.maths import minimum
from rfgnocchi import config

logger = logging.getLogger(__name__)

class TestMinimum(unittest.TestCase):
    
    def test_one(self):

        directory = os.path.abspath('proj_testminimum')
        width = 8
        n_stages = 5
        n_inputs = pow(2, n_stages)
        n_data = 10
        data = []
        maxvalue = pow(2, width)-1
        for i in range(n_data):
            values = [random.randint(0, maxvalue) for j in range(n_inputs)]
            data.append(values)

        # Make wait data.  Sent while initialising.
        n_wait_lines = 20
        wait_data = []
        for wait_index in range(n_wait_lines):
            wait_data.append({
                'reset': 0 ,
                'i_valid': 0,
                'i_data': 0,
                'o_ready': 1,
            })

        # Make input and expected data
        input_data = []
        expected_data = []
        expected_indices = []
        for values in data:
            input_data.append({
                'reset': 0,
                'i_data': signal.list_of_uints_to_uint(values, width=width),
                'i_valid': 1,
                'o_ready': 1,
            })
            minval = None
            for i, v in enumerate(values):
                if minval is None or v < minval:
                    minval = v
                    minindex = i
            expected_data.append(minval)
            expected_indices.append(minindex)
        input_data.append({
            'reset': 0,
            'i_data': 0,
            'i_valid': 0,
            'o_ready': 1,
        })

        interface = minimum.get_minimum_interface({
            'width': width,
            'n_stages': n_stages,
        })

        p = project.FileTestBenchProject.create_or_update(
            interface=interface, directory=directory,
            board=config.default_board,
            part=config.default_part,
        )
        t = p.wait_for_most_recent_task()
        errors = t.get_errors()
        self.assertEqual(len(errors), 0)

        # Run the simulation
        errors, output_data = p.run_simulation(input_data=wait_data+input_data)
        self.assertEqual(len(errors), 0)
        self.assertEqual(expected_data,
                         [d['o_data'] for d in output_data if d['o_valid']])
        self.assertEqual(expected_indices,
                         [d['o_index'] for d in output_data if d['o_valid']])
        
if __name__ == '__main__':
    config.setup_logging(logging.DEBUG)
    unittest.main()
