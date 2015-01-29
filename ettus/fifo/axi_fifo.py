import os
import logging
import testfixtures

from pyvivado import interface, signal, builder

from rfgnocchi import config

logger = logging.getLogger(__name__)

class AxiFifoBuilder(builder.Builder):

    def __init__(self, params={}):
        super().__init__(params)
        self.simple_filenames = [
            os.path.join(config.ettus_fpgadir, 'fifo', 'axi_fifo.v'),
            os.path.join(config.ettus_fpgadir, 'fifo', 'axi_fifo_flop.v'),
            os.path.join(config.ettus_fpgadir, 'fifo', 'axi_fifo_flop2.v'),
            os.path.join(config.ettus_fpgadir, 'fifo', 'axi_fifo_short.v'),
            os.path.join(config.ettus_fpgadir, 'fifo', 'axi_fifo_bram.v'),
            os.path.join(config.ettus_fpgadir, 'control', 'ram_2port.v'),
        ]
