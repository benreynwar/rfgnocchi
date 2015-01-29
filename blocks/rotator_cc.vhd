library ieee;
use ieee.std_logic_1164.all;

entity rotator_cc is
  port (
    clk: in std_logic;
    reset: in std_logic;
    i_data_tdata: in std_logic_vector(31 downto 0);
    i_data_tvalid: in std_logic;
    i_data_tlast: in std_logic;
    i_data_tready: out std_logic;
    i_config_tdata: in std_logic_vector(31 downto 0);
    i_config_tvalid: in std_logic;
    i_config_tready: out std_logic;
    o_tdata: out std_logic_vector(31 downto 0);
    o_tvalid: out std_logic;
    o_tlast: out std_logic;
    o_tready: in std_logic
    );
end rotator_cc;

architecture arch of rotator_cc is
  signal int_data: std_logic_vector(31 downto 0);
  signal int_valid: std_logic;
  signal int_ready: std_logic;
  signal resetn: std_logic;
  signal long_tdata: std_logic_vector(79 downto 0);
  signal long_tvalid: std_logic;
  signal long_tready: std_logic;
  signal long_tlast: std_logic;
begin

  resetn <= not reset;

  the_nco: entity work.nco
    port map (
      aclk => clk,
      aresetn => resetn,
      s_axis_config_tdata => i_config_tdata,
      s_axis_config_tvalid => i_config_tvalid,
      s_axis_config_tready => i_config_tready,
      m_axis_data_tdata => int_data,
      m_axis_data_tvalid => int_valid,
      m_axis_data_tready => int_ready
      );

  the_mult: entity work.complex_multiply
    port map (
      aclk => clk,
      s_axis_a_tdata => i_data_tdata,
      s_axis_a_tvalid => i_data_tvalid,
      s_axis_a_tlast => i_data_tlast,
      s_axis_a_tready => i_data_tready,
      s_axis_b_tdata => int_data,
      s_axis_b_tvalid => int_valid,
      s_axis_b_tready => int_ready,
      m_axis_dout_tdata => long_tdata,
      m_axis_dout_tvalid => long_tvalid,
      m_axis_dout_tlast => long_tlast,
      m_axis_dout_tready => long_tready
      );

  chopper: entity work.axi_round_and_clip_complex
    generic map (
      WIDTH_IN => 40,
      WIDTH_OUT => 16,
      CLIP_BITS => 9
      )
    port map (
      clk => clk,
      reset => reset,
      i_tdata => long_tdata,
      i_tvalid => long_tvalid,
      i_tlast => long_tlast,
      i_tready => long_tready,
      o_tdata => o_tdata,
      o_tvalid => o_tvalid,
      o_tlast => o_tlast,
      o_tready => o_tready
      );
      
end arch;
