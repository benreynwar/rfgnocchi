library ieee;

use ieee.std_logic_1164.all;

entity freq_xlating_fir_filter_ccf is
  port (
    clk: in std_logic;
    reset: in std_logic;
    -- The input stream of complex numbers.
    i_data_tvalid: in std_logic;
    i_data_tlast: in std_logic;
    i_data_tdata: in std_logic_vector(31 downto 0);
    i_data_tready: out std_logic;
    -- For setting new filter taps.
    i_fir_reload_tvalid: in std_logic;
    i_fir_reload_tdata: in std_logic_vector(31 downto 0);
    i_fir_reload_tready: out std_logic;
    -- For activating the new filter taps.
    i_fir_config_tvalid: in std_logic;
    i_fir_config_tlast: in std_logic;
    i_fir_config_tdata: in std_logic_vector(31 downto 0);
    i_fir_config_tready: out std_logic;
    -- For setting the rotator frequency.
    i_rotator_config_tvalid: in std_logic;
    i_rotator_config_tlast: in std_logic;
    i_rotator_config_tdata: in std_logic_vector(31 downto 0);
    i_rotator_config_tready: out std_logic;
    -- The output stream of complex numbers.
    o_data_tvalid: out std_logic;
    o_data_tlast: out std_logic;
    o_data_tdata: out std_logic_vector(31 downto 0);
    o_data_tready: in std_logic
    );
end freq_xlating_fir_filter_ccf;

architecture arch of freq_xlating_fir_filter_ccf is
  signal int_data_tvalid: std_logic;
  signal int_data_tlast: std_logic;
  signal int_data_tdata: std_logic_vector(31 downto 0);
  signal int_data_tready: std_logic;
  signal resetn: std_logic;
begin
  
  resetn <= not reset;
  
  the_fir: entity work.simple_fir
    port map (
      aclk => clk,
      aresetn => resetn,
      s_axis_data_tvalid => i_data_tvalid,
      s_axis_data_tlast => i_data_tlast,
      s_axis_data_tdata => i_data_tdata,
      s_axis_data_tready => i_data_tready,
      s_axis_reload_tvalid => i_fir_reload_tvalid,
      s_axis_reload_tlast => i_fir_reload_tlast,
      s_axis_reload_tdata => i_fir_reload_tdata,
      s_axis_reload_tready => i_fir_reload_tready,
      s_axis_config_tvalid => i_fir_config_tvalid,
      s_axis_config_tdata => i_fir_config_tdata,
      s_axis_config_tready => i_fir_config_tready,
      m_axis_data_tvalid => int_data_tvalid,
      m_axis_data_tlast => int_data_tlast,
      m_axis_data_tdata => int_data_tdata,
      m_axis_data_tready => int_data_tready
      );
  
  the_rotator: entity work.rotator_cc
    port map (
      clk => clk,
      reset => reset,
      i_data_tdata => int_data_tdata,
      i_data_tvalid => int_data_tvalid,
      i_data_tlast => int_data_tlast,
      i_data_tready => int_data_tready,
      i_config_tdata => i_rotator_config_tdata,
      i_config_tvalid => i_rotator_config_tvalid,
      i_config_tready => i_rotator_config_tready,
      o_tdata => o_data_tdata,
      o_tvalid => o_data_tvalid,
      o_tlast => o_data_tlast,
      o_tready => o_data_tready
      );
  
end arch;
