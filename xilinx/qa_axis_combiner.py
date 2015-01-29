import os
import unittest
import shutil
import random
import logging

import testfixtures

from pyvivado import project, signal
from pyvivado import config as pyvivado_config

from rfgnocchi.axi import axis_combiner
from rfgnocchi import config

logger = logging.getLogger(__name__)

class TestAxiPipe(unittest.TestCase):
    
    def test_one(self):

        directory = os.path.abspath('proj_qa_testaxiscombiner')
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)

        n_input_streams = 3
        input_stream_width = 24

        params = {
            'module_name': 'axis_combiner_0',
            'n_input_streams': n_input_streams,
            'input_stream_width': input_stream_width,
        }

        # Make wait data.  Sent while initialising.
        n_data = 10
        n_wait_lines = 20
        wait_data = []
        for wait_index in range(n_wait_lines):
            if wait_index == 10:
                aresetn = 0
            else:
                aresetn = 1
            input_d = {
                'aresetn': aresetn,
                's_axis_tdata': signal.list_of_uints_to_uint(
                    [0, 0, 0], input_stream_width),
                's_axis_tlast': signal.list_of_uints_to_uint(
                    [0, 0, 0], 1),
                's_axis_tvalid': signal.list_of_uints_to_uint(
                    [0, 0, 0], 1),
                'm_axis_tready': 0,
            }
            wait_data.append(input_d)
        # Make input and expected data
        input_data = []
        expected_data = []
        
        for data_index in range(n_data):
            t_data = [random.randint(0, pow(2, input_stream_width)-1)
                      for i in range(n_input_streams)]
            input_d = {
                'aresetn': 1,
                's_axis_tdata': signal.list_of_uints_to_uint(
                    t_data, input_stream_width),
                's_axis_tlast': signal.list_of_uints_to_uint(
                    [0, 0, 0], 1),
                's_axis_tvalid': signal.list_of_uints_to_uint(
                    [1, 1, 1], 1),
                'm_axis_tready': 1,
            }
            expected_d = {
                'm_axis_tdata': input_d['s_axis_tdata'],
                'm_axis_tlast': 0,
                'm_axis_tvalid': 1,
                's_axis_tready': signal.list_of_uints_to_uint(
                    [1, 1, 1], 1),
            }
            input_data.append(input_d)
            expected_data.append(expected_d)

        interface = axis_combiner.get_axis_combiner_interface(params)
        p = project.FileTestBenchProject.create(
            interface=interface, directory=directory,
            board=config.default_board,
            part=config.default_part,
        )
        t = p.wait_for_most_recent_task()
        errors = t.get_errors()
        self.assertEqual(len(errors), 0)

        # Run the simulation
        runtime = '{} ns'.format((len(input_data) + 20) * 10)
        errors, output_data = p.run_hdl_simulation(
            input_data=wait_data+input_data, runtime=runtime)
        latency = 0
        delay = 1 + n_wait_lines + latency
        import pdb
        pdb.set_trace()
        self.check_output(output_data[delay:], expected_data)
        self.assertEqual(len(errors), 0)

    def check_output(self, output_data, expected_data):
        self.assertTrue(len(output_data) >= len(expected_data))
        output_data = output_data[:len(expected_data)]
        testfixtures.compare(output_data, expected_data)
        
        
if __name__ == '__main__':
    pyvivado_config.use_test_db()
    config.setup_logging(logging.DEBUG)
    unittest.main()
