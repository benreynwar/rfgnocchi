import os
import unittest
import random
import logging

import testfixtures

from pyvivado import project, signal

from rfgnocchi.maths import comb_minimum
from rfgnocchi import config

logger = logging.getLogger(__name__)

class TestCombMinimum(unittest.TestCase):

    def test_one(self):
        for n_inputs in range(1, 16):
            self.helper(n_inputs)

    def helper(self, n_inputs):

        directory = os.path.abspath('proj_qa_comb_minimum_{}'.format(n_inputs))
        width = 5
        n_data = 100
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
                'i_data': 0,
            })

        # Make input and expected data
        input_data = []
        expected_data = []
        expected_indices = []
        for values in data:
            input_data.append({
                'i_data': signal.list_of_uints_to_uint(values, width=width),
            })
            minval = None
            for i, v in enumerate(values):
                if minval is None or v < minval:
                    minval = v
                    minindex = i
            expected_data.append(minval)
            expected_indices.append(minindex)
        input_data.append({
            'i_data': 0,
        })

        interface = comb_minimum.get_comb_minimum_interface({
            'width': width,
            'n_inputs': n_inputs,
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
        trimmed_data = output_data[n_wait_lines+1:n_wait_lines+n_data+1]
        self.assertEqual(len(errors), 0)
        assert(len(expected_data) == n_data)
        assert(len(expected_indices) == n_data)
        o_data = [d['o_data'] for d in trimmed_data]
        o_address = [d['o_address'] for d in trimmed_data]
        self.assertEqual(expected_data, o_data)
        self.assertEqual(expected_indices, o_address)
        
if __name__ == '__main__':
    config.setup_logging(logging.DEBUG)
    unittest.main()
