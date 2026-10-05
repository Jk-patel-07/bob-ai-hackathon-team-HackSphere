# Synthetic Static Timing Analysis — Setup and Constraints Guide

> **SYNTHETIC DOCUMENT — FOR DEMO PURPOSES ONLY**
> This document is entirely fabricated for educational demonstration of the
> Chip Design Knowledge Assistant. It does not represent real timing libraries,
> SDC constraints, or EDA tool configuration from any actual project.

---

## 1. Introduction to Static Timing Analysis (STA)

Static Timing Analysis (STA) is the process of verifying that all data signals
in a synchronous digital design propagate from their launch flip-flop to
their capture flip-flop within the available timing window, across all
process, voltage, and temperature (PVT) corners.

STA is performed after synthesis (pre-layout) and after place-and-route
(post-layout, with extracted parasitics). Post-layout STA with extracted
RC parasitics is the definitive timing signoff check.

---

## 2. Timing Paths and Constraints

### 2.1 Setup Check (Max Delay Path)

The setup check verifies that data arrives at the capture flip-flop's D pin
at least one setup time (T_setup) before the capture clock edge.

```
Slack (setup) = T_period - T_launch_to_capture - T_setup - T_uncertainty
```

Where:
- T_period = clock period
- T_launch_to_capture = combinational path delay
- T_setup = setup time of the capture flip-flop
- T_uncertainty = clock uncertainty (jitter + skew)

A positive setup slack means the path meets timing. A negative setup slack
is a setup violation and must be fixed before tapeout.

### 2.2 Hold Check (Min Delay Path)

The hold check verifies that data holds long enough at the capture flip-flop's
D pin after the previous clock edge. Unlike the setup check, the hold check
is independent of clock frequency.

```
Slack (hold) = T_data_min - T_hold - T_uncertainty_hold
```

Where:
- T_data_min = minimum (best case) data path delay
- T_hold = hold time of the capture flip-flop
- T_uncertainty_hold = hold-mode clock uncertainty

For the ST130 educational process with standard cell libraries:
- Typical flip-flop setup time (TT, 1.2V, 27°C): 50 ps
- Typical flip-flop hold time (TT, 1.2V, 27°C): 30 ps
- Clock-to-Q delay (TT, 1.2V, 27°C): 100 ps

---

## 3. SDC Constraint File Guidelines

SDC (Synopsys Design Constraints) files define the timing intent for the
design. A correct SDC file is mandatory for synthesis and STA.

### 3.1 Creating a Clock

```tcl
# Define a 500 MHz clock on the CK pin of the top-level module
create_clock -name clk -period 2.0 -waveform {0 1.0} [get_ports CK]
```

The clock period is in nanoseconds. For a 500 MHz design, the period is 2.0 ns.

### 3.2 Input and Output Delays

All primary inputs must have set_input_delay constraints relative to the
capturing clock. All primary outputs must have set_output_delay constraints.

```tcl
# Input data arrives 0.4 ns after the clock edge (20% of period)
set_input_delay -clock clk -max 0.4 [get_ports data_in]
set_input_delay -clock clk -min 0.1 [get_ports data_in]

# Output data must be valid 0.3 ns before the next clock edge
set_output_delay -clock clk -max 0.3 [get_ports data_out]
set_output_delay -clock clk -min 0.0 [get_ports data_out]
```

Omitting input/output delay constraints causes the STA tool to ignore those
paths, which produces optimistic (incorrect) results.

### 3.3 Clock Uncertainty

Clock uncertainty models jitter (random cycle-to-cycle variation in the PLL)
and skew (systematic spatial variation in clock arrival times).

```tcl
# Total clock uncertainty: 100 ps (50 ps jitter + 50 ps skew)
set_clock_uncertainty 0.1 [get_clocks clk]

# Separate hold and setup uncertainty if tool supports it
set_clock_uncertainty -setup 0.1 [get_clocks clk]
set_clock_uncertainty -hold  0.05 [get_clocks clk]
```

For the ST130 educational process using an on-chip PLL:
- Setup uncertainty (jitter dominated): 80–120 ps
- Hold uncertainty: 30–50 ps

### 3.4 Multi-Clock Designs

For designs with multiple clocks, define crossing paths explicitly:

```tcl
create_clock -name clk_fast -period 1.0 [get_ports CK_FAST]
create_clock -name clk_slow -period 4.0 [get_ports CK_SLOW]

# Paths crossing clock domains are false unless explicitly modelled
set_false_path -from [get_clocks clk_fast] -to [get_clocks clk_slow]
```

If CDC (Clock Domain Crossing) synchronisers are used, replace the
false_path with a multicycle_path or proper CDC timing model for the
synchroniser flip-flop chain.

---

## 4. PVT Corner Strategy for Timing Signoff

### 4.1 Setup (Max Delay) Signoff Corners

| Priority | Corner | Rationale |
|---|---|---|
| Primary | SS (slow, 1.08 V, 125°C) | Worst-case slow corner; maximum path delays |
| Secondary | FS (fast N, slow P, 1.2 V, 27°C) | Data-critical asymmetric corner |

All setup path slacks must be ≥ 0 ps at the SS corner.

### 4.2 Hold (Min Delay) Signoff Corners

| Priority | Corner | Rationale |
|---|---|---|
| Primary | FF (fast, 1.32 V, -40°C) | Worst-case hold: minimum path delays |
| Secondary | SF (slow N, fast P, 1.2 V, 27°C) | Hold-critical asymmetric corner |

All hold path slacks must be ≥ 0 ps at the FF corner.

### 4.3 On-Chip Variation (OCV) Derating

For post-layout STA, apply OCV derating to account for within-die process
variation:

- Launch path derating (late): +5% (multiply cell delays by 1.05)
- Capture path derating (early): -5% (multiply cell delays by 0.95)

```tcl
set_timing_derate -late  1.05 -cell_delay
set_timing_derate -early 0.95 -cell_delay
```

Advanced OCV (AOCV) or Parametric OCV (POCV) may be used when the foundry
provides statistical variation tables (SSTA) for more accurate derating.

---

## 5. Clock Tree Synthesis (CTS) Targets

The clock tree synthesiser targets specific skew and insertion delay budgets.
These targets affect hold timing and must be agreed before CTS.

| Metric | Target | Maximum |
|---|---|---|
| Clock skew (local) | ≤ 50 ps | 100 ps |
| Clock insertion delay | 400–700 ps | 900 ps |
| Maximum clock tree depth | 12 buffers | 16 buffers |
| Clock buffer cell | CLK_BUF_X4, CLK_BUF_X8 | — |

Using data buffers (BUF_X4) rather than clock buffers (CLK_BUF_X4) in the
clock tree is a common error. Clock buffers have symmetric rise/fall
characteristics that reduce skew; data buffers do not.

---

## 6. Common Timing Violations and Fixes

| Violation | Symptom | Root Cause | Recommended Fix |
|---|---|---|---|
| Setup violation | Negative setup slack | Long combinational path | Resize/upsize cells; restructure logic; pipeline |
| Hold violation | Negative hold slack | Short direct path (fanout of FF) | Insert delay buffers or use hold fixer in P&R tool |
| Max transition | Cell drives net with transition > limit | Weak driver, large capacitive load | Upsize driver; reduce fanout; buffer net |
| Max capacitance | Net capacitance exceeds cell limit | Long net or high fanout | Buffer insertion; widen metal |
| Clock glitch | PLL lock failure or CTS DRC | Incorrect clock tree cells | Verify CLK_BUF cells used; check CTS blockages |

---

## 7. Timing Signoff Checklist

Before releasing to tapeout, verify:

- [ ] Setup slack ≥ 0 ps at SS corner (all paths)
- [ ] Hold slack ≥ 0 ps at FF corner (all paths)
- [ ] Max transition violations: none
- [ ] Max capacitance violations: none
- [ ] OCV derating applied (1.05 / 0.95 or AOCV tables)
- [ ] Clock uncertainty ≥ 80 ps for setup, ≥ 30 ps for hold
- [ ] SDC has input_delay and output_delay for all I/O ports
- [ ] All multi-clock crossings explicitly constrained
- [ ] CDC synchronisers meet minimum hold margin

---

*End of Synthetic Timing Constraints Guide — ST130 Educational Process — FOR DEMO ONLY*
