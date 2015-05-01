library ieee;

use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity minimum_stage is
  generic (
    N_INPUTS: integer;
    INPUT_INDEX_WIDTH: integer;
    WIDTH: integer
    );
  port (
    clk: in std_logic;
    reset: in std_logic;
    -- Stream from stage above
    i_valid: in std_logic;
    i_data: in std_logic_vector(N_INPUTS*WIDTH-1 downto 0);
    i_indices: in std_logic_vector(N_INPUTS*INPUT_INDEX_WIDTH-1 downto 0);
    i_ready: out std_logic;
    -- Stream to stage below
    o_valid: out std_logic;
    o_data: out std_logic_vector(N_INPUTS/2*WIDTH-1 downto 0);
    o_indices: out std_logic_vector(N_INPUTS/2*(INPUT_INDEX_WIDTH+1)-1 downto 0);
    o_ready: in std_logic
    );
end minimum_stage;

architecture arch of minimum_stage is
  signal i_readys: std_logic_vector(N_INPUTS/2-1 downto 0);
  signal o_valids: std_logic_vector(N_INPUTS/2-1 downto 0);
  signal o_indices_lastbits: std_logic_vector(N_INPUTS/2-1 downto 0);
  subtype t_inputindex is std_logic_vector(INPUT_INDEX_WIDTH-1 downto 0);
  type inputindexarray is array(integer range <>) of t_inputindex;
  signal i_split_indices: inputindexarray(N_INPUTS-1 downto 0);
  subtype t_outputindex is std_logic_vector(INPUT_INDEX_WIDTH downto 0);
  type outputindexarray is array(integer range <>) of t_outputindex;
  signal o_split_indices: outputindexarray(N_INPUTS-1 downto 0);
begin

  minimums: for ii in 0 to N_INPUTS/2-1 generate
    min2: entity work.minimum_2inputs
      generic map (
        WIDTH => WIDTH
        )
      port map (
        i_valid => i_valid,
        i_data => i_data((ii+1)*2*WIDTH-1 downto ii*2*WIDTH),
        i_ready => i_readys(ii),
        o_valid => o_valids(ii),
        o_data => o_data((ii+1)*WIDTH-1 downto ii*WIDTH),
        o_index => o_indices_lastbits(ii),
        o_ready => o_ready
        );

    o_valid <= o_valids(ii);
    
    i_split_indices(2*ii) <= i_indices((2*ii+1)*INPUT_INDEX_WIDTH-1 downto (2*ii)*INPUT_INDEX_WIDTH);
    i_split_indices(2*ii+1) <= i_indices((2*ii+2)*INPUT_INDEX_WIDTH-1 downto (2*ii+1)*INPUT_INDEX_WIDTH);
    o_split_indices(ii)(INPUT_INDEX_WIDTH-1 downto 0) <=
      i_split_indices(2*ii) when o_indices_lastbits(ii) = '0' else
      i_split_indices(2*ii+1);
    o_split_indices(ii)(INPUT_INDEX_WIDTH) <= o_indices_lastbits(ii);

    o_indices((ii+1)*(INPUT_INDEX_WIDTH+1)-1 downto ii*(INPUT_INDEX_WIDTH+1)) <= o_split_indices(ii);
    
  end generate;
  
end arch;
