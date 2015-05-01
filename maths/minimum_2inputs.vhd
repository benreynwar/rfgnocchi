library ieee;

use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity minimum_2inputs is
  generic (
    WIDTH: integer
    );
  port (
    i_valid: in std_logic;
    i_data: in std_logic_vector(2*WIDTH-1 downto 0);
    i_ready: out std_logic;
    o_valid: out std_logic;
    o_data: out std_logic_vector(WIDTH-1 downto 0);
    o_index: out std_logic;
    o_ready: in std_logic
    );
end minimum_2inputs;

architecture arch of minimum_2inputs is
  signal dataA: unsigned(WIDTH-1 downto 0);
  signal dataB: unsigned(WIDTH-1 downto 0);
  signal o_index_2: std_logic;
begin

  dataA <= unsigned(i_data(WIDTH-1 downto 0));
  dataB <= unsigned(i_data(2*WIDTH-1 downto WIDTH));

  i_ready <= o_ready;
  o_valid <= i_valid;
  o_index_2 <= '0' when (dataA <= dataB) else
               '1';
  o_index <= o_index_2;
  o_data <= std_logic_vector(dataA) when o_index_2 = '0' else
            std_logic_vector(dataB);
end arch;
