import os
import unittest
import shutil
import random
import logging
import math
import cmath

import testfixtures

from pyvivado import project, signal
from pyvivado import config as pyvivado_config

from rfgnocchi.xilinx import cordic
from rfgnocchi import config

logger = logging.getLogger(__name__)


class TestCordicCompiler(unittest.TestCase):

    def test_one(self):

        directory = os.path.abspath('proj_qa_coric')
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)

        input_width = 16
        output_width = 16

        params = {'module_name': 'square_root'
                  'input_width': input_width,
        }
        interface = cordic.get_cordic_interface(params)

        # Make wait data.  Sent while initialising.
        n_wait_lines = 20
        wait_data = []
        for wait_index in range(n_wait_lines):
            if wait_index < 10:
                aresetn = 0
            else:
                aresetn = 1
            input_d = {
                'aresetn': aresetn,
                's_axis_cartesian_tvalid': 0,
                's_axis_cartesian_tdata': 0,
            }
            wait_data.append(input_d)
        # Make input and expected data
        input_data = []
        n_data = 100
        max_input = pow(2, input_width)-1
        values = [random.randint(0, max_input)
                for i in range(n_data)]
        for v in values:
            input_d = {
                'aresetn': 1,
                's_axis_cartesian_tvalid': 1,
                's_axis_cartesian_tdata': v,
            }
            input_data.append(input_d)
        # And gather data for a bit.
        n_gather = 20
        for index1 in range(n_gather):
            input_d = {
                'aresetn': 1,
                's_axis_config_tvalid': 0,
                's_axis_config_tdata': 0,
            }
            input_data.append(input_d)

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

        out_tdata = [d['m_axis_dout_tdata']
                     for d in output_data if d['m_axis_dout_tvalid']]
        
        expected_data = [int(pow(v, 0.5)) for v in values]

        self.assertEqual(len(errors), 0)
        testfixtures.compare(out_tdata, expected_data)

if __name__ == '__main__':
    pyvivado_config.use_test_db()
    config.setup_logging(logging.DEBUG)
    unittest.main()
