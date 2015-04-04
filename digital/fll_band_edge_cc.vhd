library ieee;
use ieee.std_logic_1164.all;

entity fll_band_edge_cc is
  port (
    clk: in std_logic;
    reset: in std_logic;
    clear: in std_logic;
    i_data_tdata: in std_logic_vector(31 downto 0);
    i_data_tvalid: in std_logic;
    i_data_tready: out std_logic;
    i_data_tlast: in std_logic;
    i_reload_upper_filter_tdata: in std_logic_vector(31 downto 0);
    i_reload_upper_filter_tvalid: in std_logic;
    i_reload_upper_filter_tready: out std_logic;
    i_reload_upper_filter_tlast: in std_logic;
    i_reload_lower_filter_tdata: in std_logic_vector(31 downto 0);
    i_reload_lower_filter_tvalid: in std_logic;
    i_reload_lower_filter_tready: out std_logic;
    i_reload_lower_filter_tlast: in std_logic;
    i_config_filter_tdata: in std_logic_vector(8 downto 0);
    i_config_filter_tvalid: in std_logic;
    i_config_filter_tready: out std_logic;
    i_config_controller_tdata: in std_logic_vector(31 downto 0);
    i_config_controller_tvalid: in std_logic;
    i_config_controller_tready: out std_logic;
    o_data_tdata: out std_logic_vector(31 downto 0);
    o_data_tvalid: out std_logic;
    o_data_tready: in std_logic;
    o_data_tlast: in std_logic
    );
end fll_band_edge_cc;

architecture arch of fll_band_edge_cc is
  signal lower_band_tdata: std_logic_vector(31 downto 0);
  signal lower_band_tvalid: std_Logic;
  signal upper_band_tdata: std_logic_vector(31 downto 0);
  signal upper_band_tvalid: std_logic;
  signal large_error: unsigned(16 downto 0);
  signal error_tdata: std_logic_vector(15 downto 0);
  signal error_tvalid: std_logic;
  signal shifted_tdata: std_logic_vector(31 downto 0);
  signal shifted_tvalid: std_logic;
  signal shifted_tlast: std_logic;
  signal shifted_tready: std_logic;
  signal lower_mag_tdata: std_logic_vector(15 downto 0);
  signal lower_mag_tvalid: std_logic;
  signal upper_mag_tdata: std_logic_vector(15 downto 0);
  signal upper_mag_tvalid: std_logic;
begin

  the_controller: entity work.controller
    port map (
      clk => clk,
      reset => reset,
      clear => clear,
      i_config_tdata => i_config_controller_tdata,
      i_config_tvalid => i_config_controller_tvalid,
      i_config_tready => i_config_controller_tready,
      i_data_tdata => i_data_tdata,
      i_data_tvalid => i_data_tvalid,
      i_data_tlast => i_data_tlast,
      i_data_tready => i_data_tready,
      o_data_tdata => shifted_tdata,
      o_data_tvalid => shifted_tvalid,
      o_data_tlast => shifted_tlast,
      o_data_tready => shifted_tready,
      i_error_tdata => error_tdata,
      i_error_tvalid => error_tvalid,
    );

  o_data_tdata <= shifted_tdata;
  o_data_tvalid <= shifted_tvalid;
  shifted_tready <= o_data_tready;
  o_data_tlast <= shifted_tlast;

  upper_filter: entity work.fir_ccc
    port map (
      aclk => clk,
      aresetn => resetn,
      i_data_tdata => shifted_tdata,
      i_data_tvalid => shifted_tvalid,
      o_data_tdata => upper_band_tdata,
      o_data_tvalid => upper_band_tvalid,
      i_reload_tdata => i_reload_upper_filter_tdata,
      i_reload_tvalid => i_reload_upper_filter_tvalid,
      i_reload_tready => i_reload_upper_filter_tready,
      i_config_tdata => i_config_filter_tdata,
      i_config_tvalid => i_config_filter_tvalid,
      i_config_tready => i_config_filter_tready
      );

  upper_to_mag: entity work.complex_mag
    port map (
      clk => clk,
      reset => reset,
      i_tdata => upper_band_tdata,
      i_tvalid => upper_band_tvalid,
      i_tlast => '0',
      --i_tready => 
      o_tdata => upper_mag_tdata,
      o_tvalid => upper_mag_tvalid,
      --o_tlast => 
      o_tready => '1'
      );

  lower_filter: entity work.fir_ccc
    port map (
      aclk => clk,
      aresetn => resetn,
      i_data_tdata => shifted_tdata,
      i_data_tvalid => shifted_tvalid,
      o_data_tdata => lower_band_tdata,
      o_data_tvalid => lower_band_tvalid,
      i_reload_tdata => i_reload_lower_filter_tdata,
      i_reload_tvalid => i_reload_lower_filter_tvalid,
      i_reload_tready => i_reload_lower_filter_tready,
      i_config_tdata => i_config_filter_tdata,
      i_config_tvalid => i_config_filter_tvalid,
      i_config_tready => i_config_filter_tready
      );
  
  lower_to_mag: entity work.complex_mag
    port map (
      clk => clk,
      reset => reset,
      i_tdata => lower_band_tdata,
      i_tvalid => lower_band_tvalid,
      i_tlast => '0',
      --i_tready => 
      o_tdata => lower_mag_tdata,
      o_tvalid => lower_mag_tvalid,
      --o_tlast => 
      o_tready => '1'
      );

  large_error = unsigned(upper_mag_tdata) - unsigned(lower_mag_tdata);
  error_tdata <= large_error(16 downto 1);
  error_tvalid <= lower_mag_tvalid and upper_mag_tvalid;
  
end arch;
