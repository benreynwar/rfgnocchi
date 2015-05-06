library ieee;

use ieee.std_logic_1164.all;
use ieee.math_real.all;

entity complex_mag is
  generic (
    WIDTH: positive
    );
  port (
    clk: in std_logic;
    reset: in std_logic;
    i_tdata: in std_logic_vector(2*WIDTH-1 downto 0);
    i_tvalid: in std_logic;
    i_tlast: in std_logic;
    i_tready: out std_logic;
    o_tdata: out std_logic_vector(WIDTH-1 downto 0);
    o_tvalid: out std_logic;
    o_tlast: out std_logic;
    o_tready: in std_logic
    );
end complex_mag;

architecture arch of complex_mag is
  -- SE_MAG_WIDTH is WIDTH+1 sign extended to 8 bits
  constant SE_DOUBLE_WIDTH: positive := integer(ceil(real(2*WIDTH)/8.0)*8.0);
  constant SE_MAG_WIDTH: positive := integer(ceil(real(WIDTH+1)/8.0)*8.0);
  signal magsq_data_notextended: std_logic_vector(2*WIDTH-1 downto 0);
  signal magsq_tdata: std_logic_vector(SE_DOUBLE_WIDTH-1 downto 0);
  signal magsq_tvalid: std_logic;
  signal magsq_tlast: std_logic;
  signal magsq_tready: std_logic;
  signal resetn: std_logic;
  signal mag_tdata: std_logic_vector(SE_MAG_WIDTH-1 downto 0);
begin

  resetn <= not reset;
  
  c2m2: entity work.complex_to_magsq
    generic map (
      WIDTH => WIDTH
      )
    port map (
      clk => clk,
      clear => '0',
      reset => reset,
      i_tdata => i_tdata,
      i_tvalid => i_tvalid,
      i_tlast => i_tlast,
      i_tready => i_tready,
      o_tdata => magsq_data_notextended,
      o_tvalid => magsq_tvalid,
      o_tlast => magsq_tlast,
      o_tready => magsq_tready
      );

  magsq_tdata(2*WIDTH-1 downto 0) <= magsq_data_notextended;
  magsq_tdata(SE_DOUBLE_WIDTH-1 downto 2*WIDTH) <= (others => '0');

  sr: entity work.square_root
    port map (
      aclk => clk,
      aresetn => resetn,
      s_axis_cartesian_tdata => magsq_tdata,
      s_axis_cartesian_tvalid => magsq_tvalid,
      s_axis_cartesian_tlast => magsq_tlast,
      s_axis_cartesian_tready => magsq_tready,
      m_axis_dout_tdata => mag_tdata,
      m_axis_dout_tvalid => o_tvalid,
      m_axis_dout_tlast => o_tlast,
      m_axis_dout_tready => o_tready
      );

  o_tdata <= mag_tdata(WIDTH-1 downto 0);
  
end arch;
