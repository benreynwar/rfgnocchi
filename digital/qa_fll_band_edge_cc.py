import os
import unittest
import shutil
import logging
import cmath
import math

import testfixtures

from pyvivado import project, signal
from pyvivado import config as pyvivado_config

from rfgnocchi.digital import fll_band_edge_cc
from rfgnocchi import config

logger = logging.getLogger(__name__)

def make_blank_d():
    return {
        'reset': 0,
        'clear': 0,
        'i_data_tdata': 0,
        'i_data_tvalid': 0,
        'i_data_tlast': 0,
        'i_reload_upper_filter_tdata': 0,
        'i_reload_upper_filter_tvalid': 0,
        'i_reload_upper_filter_tlast': 0,
        'i_reload_lower_filter_tdata': 0,
        'i_reload_lower_filter_tvalid': 0,
        'i_reload_lower_filter_tlast': 0,
        'i_config_filter_tdata': 0,
        'i_config_filter_tvalid': 0,
        'i_config_controller_tdata': 0,
        'i_config_controller_tvalid': 0,
        'o_data_tready': 0,
    }


class TestFLLBandEdgeCC(unittest.TestCase):

    def test_one(self):
    
        directory = os.path.abspath('proj_qa_testfllbandedgecc')
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)

        interface = fll_band_edge_cc.get_fll_band_edge_cc_interface({})

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
        errors, output_data = p.run_hdl_simulation(
            input_data=wait_data+input_data, runtime=runtime)
        
        import pdb
        pdb.set_trace()

        self.assertEqual(len(errors), 0)

        
if __name__ == '__main__':
    pyvivado_config.use_test_db()
    config.setup_logging(logging.DEBUG)
    unittest.main()
