import os
import logging
import math

from pyvivado import builder, interface, signal

from rfgnocchi import config

logger = logging.getLogger(__name__)

class ClkWizBuilder(builder.Builder):
    
    def __init__(self, params):
        super().__init__(params)
        module_name = params['module_name']
        self.ips = [
            ('clk_wiz', (
                ('PRIM_IN_FREQ', params['clock_frequency']),
                ('PRIM_SOURCE', params['clock_type']),
                ('CLKOUT1_REQUESTED_OUT_FREQ', params['frequency']),
            ), module_name),
        ]
        
