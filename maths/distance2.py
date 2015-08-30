import os

from pyvivado import builder, interface, signal

from rfgnocchi import config, ettus
from rfgnocchi.maths import complex_mag

class Distance2Builder(builder.Builder):

    def __init__(self, params):
        super().__init__(params)
        self.simple_filenames = [
            os.path.join(config.basedir, 'maths', 'distance2.vhd')]
        self.builders = [
            ettus.get_builder('complex_to_magsq'),
            ettus.get_builder('axi_fifo'),
        ]
            
def get_distance2_interface(params):
    module_name = 'distance2'
    width = params['complex_half_width']
    module_parameters = {'COMPLEX_HALF_WIDTH': width}
    builder = Distance2Builder(params)
    wires_in = (
        ('reset', signal.std_logic_type),
        ('i_tdata', signal.StdLogicVector(width=4*width)),
        ('i_tvalid', signal.std_logic_type),
        ('i_tlast', signal.std_logic_type),
        ('o_tready', signal.std_logic_type),
    )
    wires_out = (
        ('o_tdata', signal.StdLogicVector(width=width+1)),
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


name = 'distance2'
assert(name not in interface.module_register)
interface.module_register[name] = get_distance2_interface
