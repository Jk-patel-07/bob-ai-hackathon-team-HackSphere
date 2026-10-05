# Synthetic PDK Design Rules Reference

> **SYNTHETIC DOCUMENT — FOR DEMO PURPOSES ONLY**
> This document is entirely fabricated for educational demonstration of the
> Chip Design Knowledge Assistant. It does not represent any real foundry PDK,
> process node, or proprietary specifications.

---

## 1. Overview

This document describes the synthetic design rules for the fictional
**SynthTech 130nm CMOS Process (ST130)** educational PDK. All values are
illustrative and chosen to be plausible for a generic bulk CMOS process.

Process node: 130 nm nominal
Substrate: P-type bulk silicon
Gate dielectric: Silicon dioxide (SiO2)
Interconnect layers: 6 metal layers (M1–M6)

---

## 2. MOSFET Transistor Rules

### 2.1 Minimum Gate Length and Width

The minimum drawn gate length (L) for core transistors is 130 nm. Use of
minimum L is permitted only for digital logic; for analog circuits and
high-voltage tolerant devices a minimum L of 260 nm is recommended to
reduce short-channel effects.

The minimum gate width (W) for NMOS and PMOS transistors is 200 nm. Widths
narrower than 200 nm produce significant narrow-width effect shifts in
threshold voltage and are not characterised in the device models.

For I/O transistors operating at 3.3 V, the minimum gate length is 350 nm
and the minimum gate width is 400 nm.

### 2.2 Poly Gate to Active Edge Spacing

The poly gate must extend beyond the active (diffusion) region by a minimum
of 150 nm on each side. This is the poly overhang rule and it applies to
both NMOS and PMOS devices.

Poly-to-active spacing (for non-gate poly) must be at least 100 nm.

### 2.3 Gate Oxide Reliability

Core transistors (1.2 V supply) must not have a gate-to-source or
gate-to-drain voltage exceeding 1.5 V in steady state.

I/O transistors (3.3 V supply) are rated for up to 3.6 V gate voltage.

Gate stress beyond these limits will cause time-dependent dielectric breakdown
(TDDB) and is not covered by the process reliability guarantee.

### 2.4 Multiplier Rules for Wide Transistors

Transistors wider than 10 µm must be implemented using a parallel combination
of unit transistors. The recommended unit width is 5 µm. A single-finger
transistor wider than 10 µm is disallowed because of current non-uniformity
and layout DRC violations related to active enclosure rules.

Example: A W = 40 µm transistor should be implemented as 8 fingers of W = 5 µm.

---

## 3. Well and Implant Rules

### 3.1 N-Well Rules

Minimum N-well width: 1.2 µm
Minimum N-well spacing (N-well to N-well): 1.8 µm
Minimum N-well to P-substrate contact spacing: 0.9 µm

Every N-well must contain at least one N-well tap (N+ diffusion connected to VDD).
N-well taps must be placed within 20 µm of any PMOS source/drain diffusion to
maintain adequate latch-up immunity.

### 3.2 P-Well Rules

Minimum P-well width: 1.0 µm
Minimum P-well to P-well spacing: 1.5 µm

Every P-well must contain at least one P-well tap (P+ diffusion connected to VSS).
P-well taps must be placed within 20 µm of any NMOS source/drain diffusion.

### 3.3 Retrograde Well Profiles

The ST130 process uses a retrograde well profile. Designers must NOT model
the body effect using surface doping parameters. Use the provided SPICE model
parameters (see the Synthetic SPICE Model Notes document) which correctly
account for the retrograde profile.

---

## 4. Metal Interconnect Rules

### 4.1 Metal 1 (M1) Rules

Minimum M1 width: 200 nm
Minimum M1 spacing: 200 nm
Minimum M1 to M1 (different net) spacing: 200 nm
Maximum M1 current density: 1.0 mA/µm width (DC)

For electromigration reliability at 125°C, the M1 maximum current density
must be derated to 0.7 mA/µm for continuous DC operation.

### 4.2 Metal 2 through Metal 5 Rules

M2 minimum width: 280 nm
M2 minimum spacing: 280 nm
M3–M5 minimum width: 400 nm
M3–M5 minimum spacing: 400 nm

Current density limits for M2–M5: 1.5 mA/µm (DC, 125°C derated: 1.0 mA/µm)

### 4.3 Metal 6 (Thick Metal) Rules

M6 minimum width: 800 nm
M6 minimum spacing: 800 nm
M6 maximum current density: 10 mA/µm (DC, 125°C derated: 7 mA/µm)

M6 is intended for power distribution (VDD and VSS stripes) and clock routing
only. Signal routing on M6 is discouraged due to coupling capacitance.

### 4.4 Via Rules

Via1 (M1–M2): Minimum size 200 nm × 200 nm, enclosure by M1 and M2: 50 nm each side
Via2 (M2–M3): Minimum size 260 nm × 260 nm, enclosure by M2 and M3: 60 nm each side
Via3–Via5: Minimum size 360 nm × 360 nm, enclosure: 70 nm each side

Vias must not be stacked directly on top of each other without metal landing pads.
For fat via arrays (current > 5 mA), use a 2×2 or larger via array.

---

## 5. Contact Rules

### 5.1 Contact to Active (COA)

Contact minimum size: 180 nm × 180 nm
Contact-to-contact spacing: 250 nm
Contact enclosure by active: 60 nm each side
Contact enclosure by metal 1: 50 nm each side

Do not place contacts at the corner of an active region (within 50 nm of an
active corner). Corner contacts cause lithographic rounding effects that
result in systematic open failures.

### 5.2 Contact to Poly (COP)

Contact minimum size: 180 nm × 180 nm
Poly enclosure of contact: 100 nm on poly-gate side, 50 nm elsewhere
Metal 1 enclosure of contact: 50 nm each side

---

## 6. Density Rules

Metal and active density must fall within the following ranges to ensure
CMP (Chemical Mechanical Polishing) planarity:

| Layer | Minimum Density | Maximum Density |
|-------|----------------|----------------|
| Active | 5% | 60% |
| Poly | 5% | 50% |
| M1 | 10% | 70% |
| M2–M5 | 10% | 70% |
| M6 | 10% | 60% |

Density is measured over any 50 µm × 50 µm window using a sliding window
algorithm. If your layout does not meet density requirements, use metal fill
(dummy metal) or active fill (dummy diffusion) provided by the fill utilities.

---

## 7. Antenna Rules

Antenna ratio is defined as the ratio of the connected metal area to the
connected gate oxide area. Exceeding the antenna ratio can cause gate oxide
damage during plasma etching steps.

Maximum allowed antenna ratios:
- Metal 1 only: 400:1
- Metal 1–2 cumulative: 800:1
- Metal 1–3 cumulative: 2000:1
- Metal 1–4 cumulative: 5000:1

If the antenna ratio is exceeded, insert an antenna diode on the net at the
violated layer. The PDK provides pre-characterised antenna diode cells in the
standard cell library.

---

*End of Synthetic PDK Design Rules Reference — ST130 Educational Process*
