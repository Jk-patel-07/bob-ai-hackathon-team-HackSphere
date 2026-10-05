# Synthetic Latch-Up Prevention Guidelines

> **SYNTHETIC DOCUMENT — FOR DEMO PURPOSES ONLY**
> This document is entirely fabricated for educational demonstration of the
> Chip Design Knowledge Assistant. It does not represent any real semiconductor
> process latch-up rules, ESD guidelines, or reliability requirements.

---

## 1. What Is Latch-Up?

Latch-up is a failure mode in CMOS circuits in which a parasitic PNPN
thyristor structure formed by adjacent P-type and N-type regions is triggered
into a low-impedance conducting state. Once triggered, latch-up creates a
short-circuit path between VDD and VSS, which can draw destructive current
and permanently damage the device.

In bulk CMOS processes such as the synthetic ST130 educational process,
latch-up susceptibility is an inherent consequence of the device structure.
All physical design must include latch-up mitigation measures.

---

## 2. Triggering Conditions

Latch-up is most commonly triggered by:

1. **Parasitic BJT activation** — A forward-biased source-bulk junction
   injects minority carriers into the substrate or well. This occurs if
   either supply rail transiently overshoots (VDD above VDD_MAX) or
   undershoots (VSS below GND) by more than one diode drop (~0.6 V).

2. **Substrate or well current injection** — I/O pads receiving voltage
   transitions exceeding the supply rails cause substrate current, which
   forward-biases the local well/substrate junction.

3. **Radiation-induced transients** — High-energy particle strikes (for
   space or high-reliability applications) can deposit enough charge to
   forward-bias junctions and trigger latch-up.

4. **Excessive supply ramp rates** — Applying VDD faster than
   approximately 0.1 V/µs during power-up can momentarily forward-bias
   internal junctions before well clamps are established.

---

## 3. Guard Ring Requirements

### 3.1 N-Well Guard Rings

Every N-well containing PMOS devices must be surrounded by an N+ guard ring.
The N+ guard ring must be connected to VDD.

Minimum N+ guard ring width: **400 nm**
Maximum distance from PMOS source/drain to N+ guard ring: **10 µm**

For high-drive-strength output drivers (drive strength ≥ 8×), the maximum
distance from PMOS source/drain to N+ guard ring is reduced to **5 µm**.

### 3.2 P-Substrate Guard Rings

Every NMOS block must be surrounded by a P+ guard ring connected to VSS.

Minimum P+ guard ring width: **400 nm**
Maximum distance from NMOS source/drain to P+ guard ring: **10 µm**

For output drivers and any circuit connected directly to an I/O pad, the
maximum distance from NMOS source/drain to P+ guard ring is **3 µm**.

### 3.3 Double Guard Ring for I/O Cells

All I/O cells must use a double guard ring structure:
1. An inner P+ guard ring connected to the digital VSS
2. An outer N+ guard ring connected to the digital VDD

The inner P+ ring must completely surround the I/O NMOS driver.
The outer N+ ring must completely surround the entire I/O cell.

This double guard ring reduces the substrate current collection efficiency
of the parasitic NPN bipolar transistor by a factor of approximately 10×.

---

## 4. Well Tap Placement Rules

### 4.1 N-Well Tap Density

N-well taps (N+ diffusion contacts connected to VDD within the N-well) must
be placed such that no PMOS source/drain diffusion is more than **20 µm**
from the nearest N-well tap.

In standard cell rows, N-well taps are inserted automatically by the
standard cell fill flow using the NWELL_TAP cell. Designers using custom
transistors must verify tap density manually.

### 4.2 P-Substrate Tap Density

P-substrate taps (P+ diffusion contacts connected to VSS) must be placed
such that no NMOS source/drain diffusion is more than **20 µm** from the
nearest substrate tap.

In standard cell rows, substrate taps are inserted by the PTAP cell.
For custom analog blocks and I/O cells, designers must add substrate taps
explicitly.

### 4.3 Tap Placement in Dense Arrays

For NMOS transistor arrays (e.g., memory sense amplifiers, large datapaths)
with row counts greater than 8, insert a dedicated substrate tap row every
8 rows of transistors.

For PMOS transistor arrays, insert a dedicated N-well tap column every
8 columns of transistors.

### 4.4 Well Tap Cell Reference

The standard cell library provides the following tap cells:

| Cell Name | Function | Recommended Spacing |
|---|---|---|
| NWELL_TAP | N-well tap (VDD) | Every ≤20 µm in N-well |
| PTAP | P-substrate tap (VSS) | Every ≤20 µm in P-substrate |
| IO_GUARD_RING | Double guard ring for I/O | Per I/O cell placement |

---

## 5. Separation Rules for Mixed-Voltage Designs

### 5.1 Isolation Between Core and I/O Domains

Core logic (1.2 V domain) must be separated from I/O logic (3.3 V domain)
by a guard ring barrier. The guard ring barrier must be at least one well
width (1.2 µm minimum) wide and must be connected to the relevant supply
without any break in the ring.

### 5.2 Analog-Digital Separation

Analog circuit blocks must be isolated from digital switching logic by
a minimum separation of **5 µm** at the P-substrate level.

For sensitive analog blocks (e.g., PLL, bandgap reference, ADC), the
recommended minimum separation from any digital clock buffer is **20 µm**.
Use a grounded P+ guard ring to prevent substrate noise coupling from
digital switching into the analog domain.

### 5.3 Substrate Noise Coupling

Large switching digital blocks (clock buffers, I/O drivers) inject
substrate currents that can couple into sensitive analog nodes.

Mitigation strategies (in order of effectiveness):
1. Deep N-well isolation for analog NMOS transistors
2. Physical separation (>20 µm)
3. Dedicated analog VSS/VDD rails with separate pads
4. Guard rings around analog blocks

---

## 6. ESD Protection and Latch-Up Interaction

ESD protection structures (diodes, SCRs) are intentionally designed to
trigger before latch-up occurs. The ESD trigger voltage must be lower than
the latch-up trigger voltage for any signal pin.

For the ST130 educational process, the design target is:
- ESD clamp trigger voltage: ≤ 5 V
- Latch-up trigger voltage (VDD sustaining): ≥ 1.8 V (with guard rings)

Placing ESD diodes too close to the core logic can cause the diode's
injection current to trigger core latch-up. Recommended minimum distance
between ESD diode active and core NMOS active: **15 µm**.

---

## 7. Design Checklist for Latch-Up Prevention

Before submitting a layout for DRC signoff, verify the following:

- [ ] Every N-well has at least one N+ tap connected to VDD
- [ ] Every P-substrate region has at least one P+ tap connected to VSS
- [ ] N-well tap-to-PMOS distance ≤ 20 µm (≤ 5 µm for output drivers)
- [ ] Substrate tap-to-NMOS distance ≤ 20 µm (≤ 3 µm for I/O cells)
- [ ] All I/O cells have double guard rings
- [ ] Core-to-I/O separation ≥ 1.2 µm (one well width)
- [ ] Analog-digital separation ≥ 5 µm (≥ 20 µm for PLL/bandgap)
- [ ] No floating N-wells in the design
- [ ] Well tap rows inserted every ≤8 rows in transistor arrays

---

*End of Synthetic Latch-Up Prevention Guidelines — ST130 Educational Process — FOR DEMO ONLY*
