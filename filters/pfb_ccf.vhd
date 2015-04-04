library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

use pyvivado_utils.all;

entity pfb_ccf is
  generic (
    DATA_WIDTH: positive;
    USER_WIDTH: positive;
    N_FILTERS: positive;
    PHASE_WIDTH: positive;
    )
  port (
    clk: in std_logic;
    reset: in std_logic;
    -- The input data to go through the PFB.
    i_data_tdata: in std_logic_vector(DATA_WIDTH*2-1 downto 0);
    i_data_tvalid: in std_logic;
    i_data_tuser: in std_logic_vector(USER_WIDTH-1 downto 0);
    i_data_tready: out std_logic;
    -- The phase determines which two filters we'll
    -- use to generate the results.
    -- The phase data holds the width of the phase and also
    -- whether we should consume an extra bit or produce an
    -- extra bit.
    i_phase_tdata: in std_logic_vector(PHASE_WIDTH+1 downto 0);
    i_phase_tvalid: in std_logic;
    o_data_tdata: out std_logic_vector(DATA_WIDTH*2-1 downto 0);
    o_data_tvalid: out std_logic;
    o_data_tuser: out std_logic_vector(USER_WIDTH-1 downto 0);
    o_data_tready: in std_logic
    );

architecture arch of pfb_ccf is
  signal new_phase: unsigned(PHASE_WIDTH-1 downto 0);
  signal new_filter: unsigned(PHASE_WIDTH+FILTER_INDEX_WIDTH-1 downto 0);
  signal phase: unsigned(PHASE_WIDTH-1 downto 0);
  constant FILTER_INDEX_WIDTH: logceil(N_FILTERS);
  signal filter_index_A: unsigned(FILTER_INDEX_WIDTH-1 downto 0);
  signal filter_index_B: unsigned(FILTER_INDEX_WIDTH-1 downto 0);
  signal stepped_forward: std_logic;
  signal stepped_back: std_logic;
begin

  new_phase <= i_phase_tdata(PHASE_WIDTH-1 downto 0);
  
  process(clk)
  begin
    if rising_edge(clk) then
      if (reset = '1') then
        phase <= (others => '0');
        filter_index_A <= to_unsigned(0, FILTER_INDEX_WIDTH);
        filter_index_B <= to_unsigned(1, FILTER_INDEX_WIDTH);
        stepped_forward <= '0';
        stepped_back <= '0';
      else
        if (i_phase_tvalid = '1') then
          phase <= new_phase;
          filter_index_A <= 
          stepped_forward <= i_phase_tdata(PHASE_WIDTH+1);
          stepped_back <= i_phase_tdata(PHASE_WIDTH);
        end if;
      end if;
    end if;
  end process;


  
end arch;
