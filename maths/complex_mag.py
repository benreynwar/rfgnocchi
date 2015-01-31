import os
import logging
import testfixtures

from pyvivado import interface, signal, builder

from rfgnocchi import config
from rfgnocchi.ettus.rfnoc import complex_to_magsq
from rfgnocchi.xilinx import cordic

logger = logging.getLogger(__name__)

class ComplexMagBuilder(builder.Builder):

    def __init__(self, params={}):
        super().__init__(params)
        width = params['width']
        self.builders = [
            complex_to_magsq.ComplexToMagSqBuilder({}),
            cordic.CordicBuilder({
                'module_name': 'square_root',
                'input_width': 2*width,
            })
        ]
        self.simple_filenames = [
            os.path.join(config.basedir, 'maths', 'complex_mag.vhd'),
        ]
        
def get_complex_mag_interface(params):
    module_name = 'complex_mag'
    width = params['width']
    module_parameters = {
        'WIDTH': width,
    }
    builder = ComplexMagBuilder(params)
    wires_in = (
        ('reset', signal.std_logic_type),
        ('i_tdata', signal.StdLogicVector(width=2*width)),
        ('i_tvalid', signal.std_logic_type),
        ('i_tlast', signal.std_logic_type),
        ('o_tready', signal.std_logic_type),
    )
    wires_out = (
        ('o_tdata', signal.StdLogicVector(width=width)),
        ('o_tvalid', signal.std_logic_type),
        ('o_tlast', signal.std_logic_type),
        ('i_tready', signal.std_logic_type),
    )
    iface = interface.Interface(
        wires_in, wires_out, module_name=module_name,
        parameters=params, builder=builder, clock_names=['clk'],
        module_parameters=module_parameters,
    )
    return iface


assert('complex_mag' not in interface.module_register)
interface.module_register['complex_mag'] = get_complex_mag_interface
