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
entity minimum is
  generic (
    WIDTH: integer;
    N_INPUTS: integer
    );
  port (
    clk: in std_logic;
    reset: in std_logic;
    i_valid: in std_logic;
    i_data: in std_logic_vector(N_INPUTS*WIDTH-1 downto 0);
    i_ready: out std_logic;
    o_valid: out std_logic;
    o_data: out std_logic_vector(WIDTH-1 downto 0);
    o_index: out std_logic_vector(logceil(N_INPUTS)-1 downto 0);
    o_ready: in std_logic
    );
end minimum;


architecture arch of minimum is
  constant N_STAGES: integer := logceil(N_INPUTS);

  subtype t_value is unsigned(WIDTH-1 downto 0);
  -- Intentionally making t_value bigger than needed so that
  -- 'less than' comparison never has invalid index.
  -- Hopefully synthesis will get rid of the wastage.
  type t_stage_values is array(N_INPUTS downto 0) of t_value;
  subtype t_stage_indices is std_logic_vector(N_INPUTS-1 downto 0);
  subtype t_stage_index is integer range 0 to N_STAGES-1;
  type t_all_stage_values is array(N_STAGES downto 0) of t_stage_values;
  type t_all_stage_indices is array(N_STAGES downto 0) of t_stage_indices;

  signal all_stage_values: t_all_stage_values;
  signal all_stage_indices: t_all_stage_indices;
  signal best_index: std_logic_vector(logceil(N_INPUTS)-1 downto 0);

  type t_stage_info is
  record
    n_stage_inputs: integer;
    extra: std_logic;
  end record;

  function get_stage_info(input: t_stage_index) return t_stage_info is
    variable output: t_stage_info;
    variable current_outputs: integer := N_INPUTS;
    variable current_inputs: integer;
    variable extra: std_logic;
  begin
    for ii in 0 to input loop
      current_inputs := current_outputs;
      current_outputs := current_inputs/2;
      if (current_inputs = current_outputs*2) then
        extra := '0';
      else
        extra := '1';
        current_inputs := current_inputs - 1;
        current_outputs := current_outputs + 1;
      end if;
    end loop;
    output.n_stage_inputs := current_inputs;
    output.extra := extra;
    return output;
  end function;

  function get_n_stage_inputs(input: t_stage_index) return integer is
    variable info: t_stage_info;
  begin
    info := get_stage_info(input); 
    return info.n_stage_inputs;
  end function;

  type t_all_n_stage_inputs is array(N_STAGES-1 downto 0) of integer;
  signal all_n_stage_inputs: t_all_n_stage_inputs;
  signal all_n_stage_extras: std_logic_vector(N_STAGES-1 downto 0);
  
begin

  loop_inputs: for i in 0 to N_INPUTS-1 generate
    all_stage_values(0)(i) <= unsigned(i_data(WIDTH*(i+1)-1 downto WIDTH*I));
  end generate;

  loop_stages: for i in 0 to N_STAGES-1 generate
    all_n_stage_inputs(i) <= get_stage_info(i).n_stage_inputs;
    all_n_stage_extras(i) <= get_stage_info(i).extra;
    loop_stage: for j in 0 to (N_INPUTS+1)/2-1 generate
      all_stage_indices(i+1)(j) <=
        '0' when j >= all_n_stage_inputs(i)/2 else
        '0' when all_stage_values(i)(2*j) <= all_stage_values(i)(2*j+1) else
        '1';
      all_stage_values(i+1)(j) <=
        all_stage_values(i)(2*j) when j >= all_n_stage_inputs(i)/2 else
        all_stage_values(i)(2*j) when all_stage_indices(i+1)(j) = '0' else
        all_stage_values(i)(2*j+1);
    end generate;
    
  end generate;
  
  o_valid <= i_valid;
  i_ready <= o_ready;

  best_index(N_STAGES-1) <= all_stage_indices(N_STAGES)(0);
  make_best_index: for ii in N_STAGES-2 downto 0 generate
    best_index(ii) <= all_stage_indices(ii+1)(to_integer(unsigned(best_index(N_STAGES-1 downto ii+1))));
  end generate;
  o_index <= best_index;

  o_data <= std_logic_vector(all_stage_values(N_STAGES)(0));
  
end arch;
