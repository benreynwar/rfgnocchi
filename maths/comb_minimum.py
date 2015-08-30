import os

from pyvivado import builder, interface, signal, utils

from rfgnocchi import config

class CombMinimumBuilder(builder.Builder):

    def __init__(self, params):
        super().__init__(params)
        self.simple_filenames = [
            os.path.join(config.basedir, 'maths', 'comb_minimum.vhd'),
            os.path.join(config.basedir, 'maths', 'comb_minimum_generic.vhd'),
            os.path.join(config.basedir, 'maths', 'comb_minimum_two.vhd'),
            os.path.join(config.basedir, 'maths', 'comb_minimum_zero_remainder.vhd'),
            os.path.join(config.basedir, 'maths', 'comb_minimum_non_zero_remainder.vhd'),
        ]

def get_comb_minimum_interface(params):
    module_name = 'CombMinimum'
    width = params['width']
    n_inputs = params['n_inputs']
    module_parameters = {
        'WIDTH': width,
        'N_INPUTS': n_inputs,
    }
    builder = CombMinimumBuilder({})
    wires_in = (
        ('i_data', signal.StdLogicVector(width=n_inputs*width)),
    )
    wires_out = (
        ('o_data', signal.StdLogicVector(width=width)),
        ('o_address', signal.StdLogicVector(width=signal.logceil(n_inputs))),
    )
    iface = interface.Interface(
        wires_in, wires_out, module_name=module_name,
        parameters=params, builder=builder, clock_names=[],
        module_parameters=module_parameters,
    )
    return iface

interface.add_to_module_register('CombMinimum', get_comb_minimum_interface)


