library ieee;

use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity distance2 is
  generic (
    COMPLEX_HALF_WIDTH: positive
    );
  port (
    clk: in std_logic;
    reset: in std_logic;
    i_tvalid: in std_logic;
    i_tdata: in std_logic_vector(4*COMPLEX_HALF_WIDTH-1 downto 0);
    i_tlast: in std_logic;
    i_tready: out std_logic;
    o_tvalid: out std_logic;
    o_tdata: out unsigned(2*COMPLEX_HALF_WIDTH+1 downto 0);
    o_tlast: out std_logic;
    o_tready: in std_logic
    );
end distance2;

architecture arch of distance2 is
  constant CHW: positive := COMPLEX_HALF_WIDTH;
  signal i_tdataA_real: signed(CHW-1 downto 0);
  signal i_tdataA_imag: signed(CHW-1 downto 0);
  signal i_tdataB_real: signed(CHW-1 downto 0);
  signal i_tdataB_imag: signed(CHW-1 downto 0);
  signal i_tdataC_real: signed(CHW+1-1 downto 0);
  signal i_tdataC_imag: signed(CHW+1-1 downto 0);
  signal i_tdataC_slv: std_logic_vector(CHW*2+1 downto 0);
  signal o_tdata_slv: std_logic_vector(CHW downto 0);
begin
  i_tdataA_real <= signed(i_tdata(CHW-1 downto 0));
  i_tdataA_imag <= signed(i_tdata(2*CHW-1 downto CHW));
  i_tdataB_real <= signed(i_tdata(3*CHW-1 downto 2*CHW));
  i_tdataB_imag <= signed(i_tdata(4*CHW-1 downto 3*CHW));
  i_tdataC_real <= resize(i_tdataA_real, CHW+1) + resize(i_tdataB_real, CHW+1);
  i_tdataC_imag <= resize(i_tdataA_imag, CHW+1) + resize(i_tdataB_imag, CHW+1);
  i_tdataC_slv(CHW downto 0) <= std_logic_vector(i_tdataC_real);
  i_tdataC_slv(2*CHW+1 downto CHW+1) <= std_logic_vector(i_tdataC_imag);

  mag: entity work.complex_to_magsq
    generic map (
      WIDTH => CHW+1
      )
    port map (
     clk => clk,
     clear => reset,
     reset => reset,
     i_tdata => i_tdataC_slv,
     i_tvalid => i_tvalid,
     i_tready => i_tready,
     i_tlast => i_tlast,
     o_tdata => o_tdata,
     o_tvalid => o_tvalid,
     o_tready => o_tready,
     o_tlast => o_tlast
    );
  
end arch;
