import os
import logging
import math

from pyvivado import builder, interface, signal

from rfgnocchi import config

logger = logging.getLogger(__name__)

class AxiProtocolConverterBuilder(builder.Builder):
    
    def __init__(self, params):
        super().__init__(params)
        module_name = params['module_name']
        self.ips = [
            ('axi_protocol_converter', (
                ('si_protocol', params['si_protocol']),
                ('mi_protocol', params['mi_protocol']),
            ), module_name),
        ]
        
