library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity controller is
  port (
    clk: in std_logic;
    reset: in std_logic;
    clear: in std_logic;
    i_error_tdata: in std_logic_vector(15 downto 0);
    i_error_tvalid: in std_logic;
    i_data_tdata: in std_logic_vector(31 downto 0);
    i_data_tvalid: in std_logic;
    i_data_tlast: in std_logic;
    i_data_tready: out std_logic;
    i_config_tdata: in std_logic_vector(31 downto 0);
    i_config_tvalid: in std_logic;
    i_config_tready: out std_logic;
    o_data_tdata: out std_logic_vector(31 downto 0);
    o_data_tvalid: out std_logic;
    o_data_tlast: out std_logic;
    o_data_tready: in std_logic
    );
end controller;

architecture arch of controller is
  signal phase_tdata: std_logic_vector(15 downto 0);
  signal phase_tvalid: std_logic;
  signal phase_tready: std_logic;
  signal corrector_tdata: std_logic_vector(15 downto 0);
  signal corrector_tvalid: std_logic;
  signal corrector_tready: std_logic;
  signal resetn: std_logic;
begin

  resetn <= not reset;
  
  cl: entity work.controller_inner
    port map (
      clk => clk,
      reset => reset,
      clear => clear,
      i_error_tdata => i_error_tdata,
      i_error_tvalid => i_error_tvalid,
      i_config_tdata => i_config_tdata,
      i_config_tvalid => i_config_tvalid,
      i_config_tready => i_config_tready,
      o_phase_tdata => phase_tdata,
      o_phase_tvalid => phase_tvalid,
      o_phase_tready => phase_tready
      );

  noc: entity work.sincoslut
    port map (
      aclk => clk,
      s_axis_phase_tdata => phase_tdata,
      s_axis_phase_tvalid => phase_tvalid,
      s_axis_phase_tready => phase_tready,
      m_axis_data_tdata => corrector_tdata,
      m_axis_data_tvalid => corrector_tvalid,
      m_axis_data_tready => corrector_tready
      );

  the_mult: entity work.complex_multiply
    port map (
      aclk => clk,
      s_axis_a_tdata => i_data_tdata,
      s_axis_a_tvalid => i_data_tvalid,
      s_axis_a_tlast => i_data_tlast,
      s_axis_a_tready => i_data_tready,
      s_axis_b_tdata => corrector_tdata,
      s_axis_b_tvalid => corrector_tvalid,
      s_axis_b_tready => corrector_tready,
      m_axis_dout_tdata => o_data_tdata,
      m_axis_dout_tvalid => o_data_tvalid,
      m_axis_dout_tready => o_data_tready,
      m_axis_dout_tlast => o_data_tlast
      );
      
end arch;
