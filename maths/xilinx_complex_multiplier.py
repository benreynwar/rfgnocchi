import logging

from pyvivado import builder

logger = logging.getLogger(__name__)

class XilinxComplexMultiplierBuilder(builder.Builder):

    def __init__(self, params):
        super().__init__(params)
        # Input width is 16+16 for inputs
        # Output is (33+7) + (33+7)
        self.ip_params = {
            'flowcontrol': 'blocking',
            'hasatlast': 'true',
        }
        self.ips = [
            ('complex_multiplier', self.ip_params, params['module_name'])
        ] 
        self.constants = {
            'input_width': 16,
            'output_width': 33,
            'se_output_width': 40,
            'latency': 6,
        }
