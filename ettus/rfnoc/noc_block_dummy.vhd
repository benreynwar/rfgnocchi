library ieee;
use ieee.std_logic_1164.all;

use ieee.numeric_std.all;

--- Packets are returned but the returns values of sums of three of the input
--- values (i.e. running sum).
--- Also a configurable parameter is added to the sum to test config.
entity noc_block_dummy is
generic (
  NOC_ID: std_logic_vector(63 downto 0) := x"FFFF_0000_0000_0000"
  );
port (
  bus_clk: in std_logic;
  bus_rst: in std_logic;
  ce_clk: in std_logic;
  ce_rst: in std_logic;
  i_tdata: in std_logic_vector(63 downto 0);
  i_tlast: in std_logic;
  i_tvalid: in std_logic;
  i_tready: out std_logic;
  o_tdata: out std_logic_vector(63 downto 0);
  o_tlast: out std_logic;
  o_tvalid: out std_logic;
  o_tready: in std_logic;
  debug: out std_logic_vector(63 downto 0)
);
end noc_block_dummy;

architecture arch of noc_block_dummy is
  constant SR_READBACK: integer := 255;
  constant NUM_AXI_CONFIG_BUS: integer := 1;
  constant AXI_WRAPPER_BASE: integer := 128;
  constant SR_NEXT_DST: integer := AXI_WRAPPER_BASE;
  constant SR_AXI_CONFIG_BASE: integer := AXI_WRAPPER_BASE + 1;
  constant STR_SINK_FIFOSIZE: integer := 10;
  -- Settings Sink
  signal set_data: std_logic_vector(31 downto 0);
  signal set_addr: std_logic_vector(7 downto 0);
  signal set_stb: std_logic;
  signal rb_data: std_logic_vector(63 downto 0);
  -- Settings Source
  signal cmdout_tdata: std_logic_vector(63 downto 0);
  signal ackin_tdata: std_logic_vector(63 downto 0);
  signal cmdout_tlast: std_logic;
  signal cmdout_tvalid: std_logic;
  signal cmdout_tready: std_logic;
  signal ackin_tlast: std_logic;
  signal ackin_tvalid: std_logic;
  signal ackin_tready: std_logic;
  -- Data streams between noc_shell and axi_wrapper
  signal str_sink_tdata: std_logic_vector(63 downto 0);
  signal str_src_tdata: std_logic_vector(63 downto 0);
  signal str_sink_tlast: std_logic_vector(0 downto 0);
  signal str_sink_tvalid: std_logic_vector(0 downto 0);
  signal str_sink_tready: std_logic_vector(0 downto 0);
  signal str_src_tlast: std_logic_vector(0 downto 0);
  signal str_src_tvalid: std_logic_vector(0 downto 0);
  signal str_src_tready: std_logic_vector(0 downto 0);
  -- Misc
  signal clear_tx_seqnum: std_logic;
  signal next_dst: std_logic_vector(15 downto 0);
  -- Data streams to/from AXI IP 
  signal m_axis_data_tdata: std_logic_vector(31 downto 0);
  signal m_axis_data_tlast: std_logic;
  signal m_axis_data_tvalid: std_logic;
  signal m_axis_data_tready: std_logic;
  signal s_axis_data_tdata: std_logic_vector(31 downto 0);
  signal s_axis_data_tlast: std_logic;
  signal s_axis_data_tvalid: std_logic;
  signal s_axis_data_tready: std_logic;
  signal s_axis_data_tuser: std_logic_vector(127 downto 0);
  signal m_axis_config_tdata: std_logic_vector(31 downto 0);
  signal m_axis_config_tvalid: std_logic_vector(0 downto 0);
  signal m_axis_config_tlast: std_logic_vector(0 downto 0);
  signal m_axis_config_tready: std_logic_vector(0 downto 0);
  signal summed_tdata: unsigned(33 downto 0);
  signal summed_tvalid: std_logic;
  signal summed_tlast: std_logic;
  signal resized_newdata: unsigned(33 downto 0);
  signal history0: unsigned(33 downto 0);
  signal history1: unsigned(33 downto 0);
  signal configed: unsigned(33 downto 0);

begin

  shell: entity work.noc_shell
    generic map (
      NOC_ID => NOC_ID,
      STR_SINK_FIFOSIZE => STR_SINK_FIFOSIZE
      )
    port map (
      bus_clk => bus_clk,
      bus_rst => bus_rst,
      i_tdata => i_tdata,
      i_tlast => i_tlast,
      i_tvalid => i_tvalid,
      i_tready => i_tready,
      o_tdata => o_tdata,
      o_tlast => o_tlast,
      o_tvalid => o_tvalid,
      o_tready => o_tready,
      clk => ce_clk,
      reset => ce_rst,
      set_data => set_data,
      set_addr => set_addr,
      set_stb => set_stb,
      rb_data => rb_data,
      cmdout_tdata => cmdout_tdata,
      cmdout_tlast => cmdout_tlast,
      cmdout_tvalid => cmdout_tvalid,
      cmdout_tready => cmdout_tready,
      ackin_tdata => ackin_tdata,
      ackin_tlast => ackin_tlast,
      ackin_tvalid => ackin_tvalid,
      ackin_tready => ackin_tready,
      str_sink_tdata => str_sink_tdata,
      str_sink_tlast => str_sink_tlast,
      str_sink_tvalid => str_sink_tvalid,
      str_sink_tready => str_sink_tready,
      str_src_tdata => str_src_tdata,
      str_src_tlast => str_src_tlast,
      str_src_tvalid => str_src_tvalid,
      str_src_tready => str_src_tready,
      clear_tx_seqnum => clear_tx_seqnum,
      debug => debug
      );

  wrapper: entity work.axi_wrapper
    generic map (
      SR_AXI_CONFIG_BASE => SR_AXI_CONFIG_BASE,
      NUM_AXI_CONFIG_BUS => NUM_AXI_CONFIG_BUS,
      CONFIG_BUS_FIFO_DEPTH => 7
      )
    port map (
      clk => ce_clk,
      reset => ce_rst,
      clear_tx_seqnum => clear_tx_seqnum,
      next_dst => next_dst,
      set_stb => set_stb,
      set_addr => set_addr,
      set_data => set_data,
      i_tdata => str_sink_tdata,
      i_tlast => str_sink_tlast(0),
      i_tvalid => str_sink_tvalid(0),
      i_tready => str_sink_tready(0),
      o_tdata => str_src_tdata,
      o_tlast => str_src_tlast(0),
      o_tvalid => str_src_tvalid(0),
      o_tready => str_src_tready(0),
      m_axis_data_tdata => m_axis_data_tdata,
      m_axis_data_tlast => m_axis_data_tlast,
      m_axis_data_tvalid => m_axis_data_tvalid,
      m_axis_data_tready => m_axis_data_tready,
      s_axis_data_tdata => s_axis_data_tdata,
      s_axis_data_tlast => s_axis_data_tlast,
      s_axis_data_tvalid => s_axis_data_tvalid,
      s_axis_data_tready => s_axis_data_tready,
      s_axis_data_tuser => s_axis_data_tuser,
      m_axis_config_tdata => m_axis_config_tdata,
      m_axis_config_tlast => m_axis_config_tlast,
      m_axis_config_tvalid => m_axis_config_tvalid,
      m_axis_config_tready => m_axis_config_tready
    );
  m_axis_config_tready <= (others => '1');
  s_axis_data_tuser <= (others => '0');
  next_dst <= (others => '0');

  -- Define the dummy
  -------------------
  
  -- Update the configurable parameter.
  process(ce_clk)
  begin
    if rising_edge(ce_clk) then
      if (ce_rst = '1') then
        configed <= (others => '0');
      else
        if (m_axis_config_tvalid(0) = '1') then
          configed <= resize(unsigned(m_axis_config_tdata), 34);
        end if;
      end if;
    end if;
  end process;
    
  
  -- Sum last 3 inputs add a configurable parameter.
  process(ce_clk)
  begin
    if rising_edge(ce_clk) then
      s_axis_data_tlast <= m_axis_data_tlast;
      if (ce_rst = '1') then
        history0 <= (others => '0');
        history1 <= (others => '0');
        summed_tvalid <= '0';
      else
        if ((m_axis_data_tvalid and m_axis_data_tready) = '1') then
          if (m_axis_data_tlast = '1') then
            history0 <= (others => '0');
            history1 <= (others => '0');
          else
            history0 <= resized_newdata;
            history1 <= history0;
          end if;
          summed_tdata <= resized_newdata + history0 + history1 + configed;
          summed_tlast <= m_axis_data_tlast;
          summed_tvalid <= '1';
        elsif (s_axis_data_tready = '1') then
          summed_tvalid <= '0';
        end if;
      end if;
    end if;
  end process;
  resized_newdata <= resize(unsigned(m_axis_data_tdata), 34);
  s_axis_data_tvalid <= summed_tvalid;
  s_axis_data_tdata <= std_logic_vector(summed_tdata(31 downto 0));
  m_axis_data_tready <= (not summed_tvalid) or (s_axis_data_tready);

end arch;
