import os
import unittest
import shutil
import random
import logging

import testfixtures

from pyvivado import project, signal
from pyvivado import config as pyvivado_config

from rfgnocchi.filters import noc_block_fir_filter
from rfgnocchi import config

logger = logging.getLogger(__name__)

class TestNocBlockFirFilter(unittest.TestCase):
    
    def test_one(self):

        directory = os.path.abspath('proj_qa_testnocblockfirfilter')
        if os.path.exists(directory):
            shutil.rmtree(directory)
        os.mkdir(directory)

        interface = noc_block_fir_filter.get_noc_block_fir_filter_interface(params={})

        p = project.FileTestBenchProject.create(
            interface=interface, directory=directory,
            board=config.default_board,
            part=config.default_part,
        )
        t = p.wait_for_most_recent_task()
        errors = t.get_errors()
        self.assertEqual(len(errors), 0)

        errors, output_data = p.run_hdl_simulation(
            input_data=[], runtime='20 ns')
        self.assertEqual(len(errors), 0)
        

        
if __name__ == '__main__':
    pyvivado_config.use_test_db()
    config.setup_logging(logging.DEBUG)
    unittest.main()
