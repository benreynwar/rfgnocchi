import os
import unittest
import random
import logging

import testfixtures

from pyvivado import project, signal
from pyvivado import config as pyvivado_config

from rfgnocchi.xilinx import blk_mem_gen
from rfgnocchi import config

logger = logging.getLogger(__name__)


class TestFirCompiler(unittest.TestCase):

    def test_one(self):
        width = 4
        depth = 60
        params = {
            'read_width_A': width,
            'write_width_A': width,
            'read_depth_A': width,
            'write_depth_A': width,
            'module_name': 'super_memory',
        }
        directory = os.path.abspath('proj_qa_blkmemgen')
        interface = blk_mem_gen.get_blk_mem_gen_interface(params)

        # Make wait data.  Sent while initialising.
        n_wait_lines = 20
        wait_data = []
        for wait_index in range(n_wait_lines):
            if wait_index in (10, 11):
                aresetn = 0
            else:
                aresetn = 1
            input_d = {
                'aresetn': aresetn,
                's_axis_data_tvalid': 0, 
                's_axis_data_tlast': 0,
                's_axis_data_tdata': 0,
                's_axis_config_tvalid': 0,
                's_axis_config_tdata': 0,
                's_axis_reload_tvalid': 0, 
                's_axis_reload_tlast': 0,
                's_axis_reload_tdata': 0,
                'm_axis_data_tready': 0,
            }
            wait_data.append(input_d)
            
        p = project.FileTestBenchProject.create_or_update(
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

        out_decimated = [
            signal.uint_to_complex(d['m_axis_data_tdata'], width=se_output_width)
            for d in output_data if d['m_axis_data_tvalid']]
        self.assertEqual((decimated0 + decimated1), out_decimated)

        
if __name__ == '__main__':
    config.setup_logging(logging.DEBUG)
    unittest.main()
