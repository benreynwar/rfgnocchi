-- -*- vhdl -*-

library ieee;

use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use work.pyvivado_utils.all;

-- Takes in N_INPUTS unsigned numbers of width=WIDTH.
-- Returns the minimum value along with the index of that value.
-- Organized as a tree of binary minimums.
-- Currently has to pass through all stages in one clock cycle,
-- although this should really be a parameter to the builder.

-- Ports are all std_logic and std_logic_vector so that it plays
-- nicely with Verilog modules.
entity CombMinimum is
  generic (
    WIDTH: integer;
    N_INPUTS: integer
    );
  port (
    i_data: in std_logic_vector(N_INPUTS*WIDTH-1 downto 0);
    o_data: out std_logic_vector(WIDTH-1 downto 0);
    o_address: out std_logic_vector(logceil(N_INPUTS)-1 downto 0)
    );
end CombMinimum;


architecture arch of CombMinimum is
   signal i_addresses: std_logic_vector(-1 downto 0);
begin
  gen: entity work.CombMinimumGeneric
    generic map (
      WIDTH => WIDTH,
      INPUT_ADDRESS_WIDTH => 0,      
      N_INPUTS => N_INPUTS
      )
    port map(
      i_data => i_data,
      i_addresses => i_addresses,
      o_data => o_data,
      o_address => o_address
      );
end arch;
