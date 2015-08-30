-- -*- vhdl -*-

library ieee;

use ieee.std_logic_1164.all;
use ieee.numeric_std.all;
use ieee.math_real.all;

use work.pyvivado_utils.all;

entity CombMinimumGeneric is
  generic (
    WIDTH: positive;
    N_INPUTS: positive;
    INPUT_ADDRESS_WIDTH: natural
    );
  port (
    i_data: in std_logic_vector(N_INPUTS*WIDTH-1 downto 0);
    i_addresses: in std_logic_vector(N_INPUTS*INPUT_ADDRESS_WIDTH-1 downto 0);
    o_data: out std_logic_vector(WIDTH-1 downto 0);
    o_address: out std_logic_vector(INPUT_ADDRESS_WIDTH+logceil(N_INPUTS)-1 downto 0)
    );
end CombMinimumGeneric;


architecture arch of CombMinimumGeneric is
  constant LARGEST_CONTAINED_POWER_OF_TWO: positive := 2 ** (logceil(N_INPUTS+1)-1);
  constant REMAINDER: natural := N_INPUTS - LARGEST_CONTAINED_POWER_OF_TWO;
  constant TEST: integer := logceil(N_INPUTS);
  constant TEST0: integer := logceil(0);
  constant TEST1: integer := logceil(1);
  constant TEST2: integer := logceil(2);
  constant TEST3: integer := logceil(3);
  constant TEST4: integer := logceil(4);
  constant TEST5: integer := logceil(5);
  constant TEST6: integer := logceil(6);
begin

  single_input: if N_INPUTS = 1 generate
    assert(logceil(N_INPUTS) = 0);
    assert(o_address'HIGH = 1);
    o_data <= i_data;
    with_input_address: if INPUT_ADDRESS_WIDTH > 0 generate
      o_address(INPUT_ADDRESS_WIDTH-1 downto 0) <= i_addresses;
      o_address(INPUT_ADDRESS_WIDTH downto INPUT_ADDRESS_WIDTH-1) <= (others => '0');
    end generate;
    no_input_address: if INPUT_ADDRESS_WIDTH = 0 generate
      o_address(0) <= '0';
    end generate; 
  end generate;
  
  no_remainder: if REMAINDER = 0 and N_INPUTS > 1 generate
    no_remainder_inst: entity work.CombMinimumZeroRemainder
      generic map (
        WIDTH => WIDTH,
        N_INPUTS => N_INPUTS,
        INPUT_ADDRESS_WIDTH => INPUT_ADDRESS_WIDTH
        )
      port map (
        i_data => i_data,
        i_addresses => i_addresses,
        o_data => o_data,
        o_address => o_address
        );
  end generate;
  with_remainder: if REMAINDER > 0 and N_INPUTS > 1  generate
    with_remainder_inst: entity work.CombMinimumNonZeroRemainder
      generic map (
        WIDTH => WIDTH,
        N_INPUTS => N_INPUTS,
        INPUT_ADDRESS_WIDTH => INPUT_ADDRESS_WIDTH
        )
      port map (
        i_data => i_data,
        i_addresses => i_addresses,
        o_data => o_data,
        o_address => o_address
        );
   end generate;
end arch;
