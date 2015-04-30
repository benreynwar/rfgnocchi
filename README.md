# rfgnocchi

Library of HDL signal-processing blocks for use with RFNoC.

At the moment this repository is less a library of useful blocks, and more an example of
how to use [pyvivado](https://github.com/benreynwar/pyvivado) to develop new modules for
use with RFNoC.

Since I don't have compatible hardware these modules have only been tested through simulation.

The license is MIT.
But since most of the modules are tied pretty tightly to Xilinx or Ettus Research IP those
licenses will be constraining.

Some of the blocks use code from the Ettus Research repository at https://github.com/ettusresearch/fpga/tree/rfnoc-devel which you'll have to clone independently.
