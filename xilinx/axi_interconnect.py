import os
import logging
import math

from pyvivado import builder, interface, signal

from rfgnocchi import config

logger = logging.getLogger(__name__)

class AxiInterconnectBuilder(builder.Builder):
    
    def __init__(self, params):
        super().__init__(params)
        module_name = params['module_name']
        self.ip_params = [
        ]
        self.ip_params_dict = dict(self.ip_params)
        self.ips = [
            ('axi_interconnect', self.ip_params, module_name),
        ]
