import os

from pyvivado import builder, interface, signal

from rfgnocchi import config

minimum_2inputs_builder = builder.make_simple_builder(
    filenames=[os.path.join(config.basedir, 'maths', 'minimum_2inputs.vhd')],
)({})

minimum_stage_builder = builder.make_simple_builder(
    filenames=[os.path.join(config.basedir, 'maths', 'minimum_stage.vhd')],
    builders=[minimum_2inputs_builder],
    )({})

# Takes one parameter (n_stages)
MinimumBuilder = builder.make_template_builder(
    template_fn=os.path.join(config.basedir, 'maths', 'minimum.vhd.t'),
    builders=[minimum_stage_builder],
)

def get_minimum_interface(params):
    module_name = 'minimum'
    width = params['width']
    n_stages = params['n_stages']
    n_inputs = pow(2, n_stages)
    module_parameters = {
        'WIDTH': width,
    }
    builder = MinimumBuilder({
        'n_stages': n_stages,
    })
    wires_in = (
        ('reset', signal.std_logic_type),
        ('i_valid', signal.std_logic_type),
        ('i_data', signal.StdLogicVector(width=n_inputs*width)),
        ('o_ready', signal.std_logic_type),
    )
    wires_out = (
        ('o_data', signal.StdLogicVector(width=width)),
        ('o_valid', signal.std_logic_type),
        ('o_index', signal.StdLogicVector(width=n_stages)),
        ('i_ready', signal.std_logic_type),
    )
    iface = interface.Interface(
        wires_in, wires_out, module_name=module_name,
        parameters=params, builder=builder, clock_names=['clk'],
        module_parameters=module_parameters,
    )
    return iface

interface.add_to_module_register('minimum', get_minimum_interface)


