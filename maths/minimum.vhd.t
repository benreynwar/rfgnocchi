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
entity minimum is
  generic (
    WIDTH: integer
    );
  port (
    clk: in std_logic;
    reset: in std_logic;
    i_valid: in std_logic;
    i_data: in std_logic_vector(({{n_inputs}})*WIDTH-1 downto 0);
    i_ready: out std_logic;
    o_valid: out std_logic;
    o_data: out std_logic_vector(WIDTH-1 downto 0);
    o_index: out std_logic_vector({{n_stages}}-1 downto 0);
    o_ready: in std_logic
    );
end minimum;


architecture arch of minimum is
  constant N_STAGES: integer := {{n_stages}};
  constant N_INPUTS: integer := {{n_inputs}};
  {% for i in range(n_stages) %}
  signal to_stage{{i}}_valid: std_logic;
  signal to_stage{{i}}_data: std_logic_vector(2**(N_STAGES-{{i}})*WIDTH-1 downto 0);
  signal to_stage{{i}}_indices: std_logic_vector(2**(N_STAGES-{{i}})*{{i}}-1 downto 0);
  signal to_stage{{i}}_ready: std_logic;
  signal from_stage{{i}}_valid: std_logic;
  signal from_stage{{i}}_data: std_logic_vector(2**(N_STAGES-{{i}}-1)*WIDTH-1 downto 0);
  signal from_stage{{i}}_indices: std_logic_vector(2**(N_STAGES-{{i}}-1)*{{i+1}}-1 downto 0);
  signal from_stage{{i}}_ready: std_logic;
  {% endfor %}
begin
  to_stage0_valid <= i_valid;
  to_stage0_data(N_INPUTS*WIDTH-1 downto 0) <= i_data;
  to_stage0_data(2**N_STAGES*WIDTH-1 downto N_INPUTS*WIDTH) <= (others => '1');
  to_stage0_indices <= "";
  i_ready <= to_stage0_ready;
  o_valid <= from_stage{{n_stages-1}}_valid;
  o_data <= from_stage{{n_stages-1}}_data;
  o_index <= from_stage{{n_stages-1}}_indices;
  from_stage{{n_stages-1}}_ready <= o_ready;

  {% for i in range(n_stages-1) %}
    to_stage{{i+1}}_valid <= from_stage{{i}}_valid;
    to_stage{{i+1}}_data <= from_stage{{i}}_data;
    to_stage{{i+1}}_indices <= from_stage{{i}}_indices;
    to_stage{{i}}_ready <= from_stage{{i+1}}_ready;
  {% endfor %}  

  {% for i in range(n_stages) %}
    stage{{i}}: entity work.minimum_stage
      generic map (
        N_INPUTS => 2**(N_STAGES-{{i}}),
        INPUT_INDEX_WIDTH => {{i}},
        WIDTH => WIDTH
        )
      port map (
        clk => clk,
        reset => reset,
        i_valid => to_stage{{i}}_valid,
        i_data => to_stage{{i}}_data,
        i_indices => to_stage{{i}}_indices,
        i_ready => to_stage{{i}}_ready,
        o_valid => from_stage{{i}}_valid,
        o_data => from_stage{{i}}_data,
        o_indices => from_stage{{i}}_indices,
        o_ready => from_stage{{i}}_ready
        );
        
  {% endfor %}
  
end arch;
