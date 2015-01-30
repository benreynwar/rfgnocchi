library ieee;
use ieee.std_logic_1164.all;
use ieee.numeric_std.all;

entity controller_inner is
  port (
    clk: in std_logic;
    reset: in std_logic;
    clear: in std_logic;
    -- We assume that error is scaled so it makes good
    -- use of the 16 bits.
    i_error_tdata: in std_logic_vector(15 downto 0);
    i_error_tvalid: in std_logic;
    i_config_tdata: in std_logic_vector(31 downto 0);
    i_config_tvalid: in std_logic;
    i_config_tready: out std_logic;
    o_phase_tdata: out std_logic_vector(15 downto 0);
    o_phase_tvalid: out std_logic;
    o_phase_tready: in std_logic
    );
end controller_inner;

architecture arch of controller_inner is
  constant PHASE_WIDTH: positive := 16;
  constant FREQUENCY_WIDTH: positive := 16;
  constant ERROR_WIDTH: positive := 16;
  constant ALPHA_WIDTH: positive := 16;
  constant BETA_WIDTH: positive := 16;
  signal alpha: std_logic_vector(ALPHA_WIDTH-1 downto 0);
  signal beta: std_logic_vector(BETA_WIDTH-1 downto 0);
  signal frequency: unsigned(FREQUENCY_WIDTH-1 downto 0);
  signal phase: unsigned(PHASE_WIDTH-1 downto 0);
  signal alpha_tready: std_logic;
  signal beta_tready: std_logic;
  signal A_error_tready: std_logic;
  signal B_error_tready: std_logic;
  -- The alpha*error stream
  signal ae_tdata: std_logic_vector(PHASE_WIDTH-1 downto 0);
  signal ae_tvalid: std_logic;
  signal ae_tlast: std_logic;
  -- The beta*error stream
  signal be_tdata: std_logic_vector(FREQUENCY_WIDTH-1 downto 0);
  signal be_tvalid: std_logic;
  signal be_tlast: std_logic;

  -- Updating frequency intermediates.
  signal adj_frequency: unsigned(FREQUENCY_WIDTH downto 0);
  signal new_frequency: unsigned(FREQUENCY_WIDTH-1 downto 0);
  signal big_new_frequency: unsigned(FREQUENCY_WIDTH downto 0);
  -- Updating phase intermediates.
  signal adj_phase: unsigned(PHASE_WIDTH+1 downto 0);
  signal step_phase: unsigned(PHASE_WIDTH+1 downto 0);
  signal new_phase: unsigned(PHASE_WIDTH-1 downto 0);
  signal big_new_phase: unsigned(PHASE_WIDTH+1 downto 0);

begin

  adj_frequency <= resize(unsigned(be_tdata), FREQUENCY_WIDTH+1)
                   when (be_tvalid = '1') else
                   (others => '0');
  adj_phase <= resize(unsigned(ae_tdata), PHASE_WIDTH+2)
               when (ae_tvalid = '1') else
               (others => '0');
  step_phase <= resize(frequency, PHASE_WIDTH+2)
                when (o_phase_tready='1') else
                (others => '0');

  big_new_frequency <= frequency + adj_frequency;
  new_frequency <= big_new_frequency(FREQUENCY_WIDTH-1 downto 0);
  big_new_phase <= phase + step_phase + adj_phase;
  new_phase <= big_new_phase(PHASE_WIDTH-1 downto 0);

  o_phase_tdata <= std_logic_vector(phase);
  o_phase_tvalid <= '1';
  i_config_tready <= '1';
  
  process(clk)
  begin
    if rising_edge(clk) then
      if (reset = '1') then
        alpha <= (others => '0');
        beta <= (others => '0');
        frequency <= (others => '0');
        phase <= (others => '0');
      else
        if (clear = '1') then
          frequency <= (others => '0');
          phase <= (others => '0');
        else
          frequency <= new_frequency;
          phase <= new_phase;
        end if;
        if (i_config_tvalid = '1') then
          alpha <= i_config_tdata(ALPHA_WIDTH+BETA_WIDTH-1 downto BETA_WIDTH);
          beta <= i_config_tdata(BETA_WIDTH-1 downto 0);
        end if;
      end if;  
    end if;
  end process;

  alpha_mult: entity work.mult
    generic map (
      WIDTH_A => ALPHA_WIDTH,
      WIDTH_B => ERROR_WIDTH,
      WIDTH_P => PHASE_WIDTH,
      DROP_TOP_P => 6 
    )
    port map (
      clk => clk,
      reset => reset,
      a_tdata => alpha,
      a_tvalid => '1',
      a_tlast => '0',
      a_tready => alpha_tready,
      b_tdata => i_error_tdata,
      b_tvalid => i_error_tvalid,
      b_tlast => '0',
      b_tready => A_error_tready,
      p_tdata => ae_tdata,
      p_tvalid => ae_tvalid,
      p_tlast => ae_tlast,
      p_tready => '1'
    );

  beta_mult: entity work.mult
    generic map (
      WIDTH_A => BETA_WIDTH,
      WIDTH_B => ERROR_WIDTH,
      WIDTH_P => FREQUENCY_WIDTH,
      DROP_TOP_P => 6 
    )
    port map (
      clk => clk,
      reset => reset,
      a_tdata => beta,
      a_tvalid => '1',
      a_tlast => '0',
      a_tready => beta_tready,
      b_tdata => i_error_tdata,
      b_tvalid => i_error_tvalid,
      b_tlast => '0',
      b_tready => B_error_tready,
      p_tdata => be_tdata,
      p_tvalid => be_tvalid,
      p_tlast => be_tlast,
      p_tready => '1'
    );
  
end arch;
