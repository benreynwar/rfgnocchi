import os
import logging
import math

from pyvivado import builder, interface, signal

from rfgnocchi import config

logger = logging.getLogger(__name__)

class AxiDataFifoBuilder(builder.Builder):
    
    def __init__(self, params):
        super().__init__(params)
        module_name = params['module_name']
        self.ips = [
            ('axi_data_fifo', (
                ('data_width', params['data_width']), #64
                ('write_fifo_depth', params['write_fifo_depth']),
                ('read_fifo_depth', params['read_fifo_depth']),
             ), module_name),
        ]
        
