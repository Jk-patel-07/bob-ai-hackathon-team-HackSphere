# Synthetic SPICE Model Usage Notes

> **SYNTHETIC DOCUMENT — FOR DEMO PURPOSES ONLY**
> This document is entirely fabricated for educational demonstration of the
> Chip Design Knowledge Assistant. It does not represent real foundry SPICE
> models, BSIM parameters, or any actual device characterisation data.

---

## 1. Overview of the ST130 SPICE Model Set

The synthetic ST130 educational process provides SPICE models for all
supported device types. Models are provided in BSIM4 format for MOS
transistors and in standard SPICE diode/BJT format for passive and
parasitic devices.

### 1.1 Model Files

| Model File | Device Type | Model Type |
|---|---|---|
| `nmos_core.spi` | NMOS core (1.2 V, L=130 nm) | BSIM4 |
| `pmos_core.spi` | PMOS core (1.2 V, L=130 nm) | BSIM4 |
| `nmos_io.spi` | NMOS I/O (3.3 V, L=350 nm) | BSIM4 |
| `pmos_io.spi` | PMOS I/O (3.3 V, L=350 nm) | BSIM4 |
| `diode_nwell.spi` | N-well/P-substrate diode | Standard diode |
| `res_poly.spi` | Poly resistor | RES model |
| `cap_mim.spi` | MIM capacitor (M4–M5) | CAP model |

### 1.2 Model Corners

The model set includes five PVT corners:

| Corner Label | Process | Voltage | Temperature |
|---|---|---|---|
| TT | Typical NMOS, Typical PMOS | 1.2 V | 27°C |
| FF | Fast NMOS, Fast PMOS | 1.32 V | -40°C |
| SS | Slow NMOS, Slow PMOS | 1.08 V | 125°C |
| FS | Fast NMOS, Slow PMOS | 1.2 V | 27°C |
| SF | Slow NMOS, Fast PMOS | 1.2 V | 27°C |

For digital synthesis timing signoff, always use both SS (hold) and FF
(setup) corners. For analog design, use TT for schematic validation and
SS/FF/FS/SF for corners verification.

---

## 2. Correctly Invoking SPICE Models

### 2.1 Library Include Syntax

Include the model files at the top of every SPICE netlist:

```spice
.lib '/path/to/st130_pdk/models/nmos_core.spi' TT
.lib '/path/to/st130_pdk/models/pmos_core.spi' TT
```

Always specify the corner label (TT, FF, SS, FS, SF) when including the
library. Omitting the corner defaults to TT but will generate a warning.

### 2.2 Instance Naming Conventions

NMOS core transistors: Use the subcircuit call `M{name} D G S B nmos_core`
PMOS core transistors: Use the subcircuit call `M{name} D G S B pmos_core`

The body (B) terminal must always be explicitly connected:
- NMOS body: connect to the local substrate tap (VSS or tied P-well contact)
- PMOS body: connect to the local N-well tie (VDD or tied N-well contact)

Connecting the body terminal to the wrong supply causes incorrect threshold
voltage simulation and will not match silicon.

### 2.3 Instance Parameters

Required parameters for every MOS transistor instance:

| Parameter | Description | Example |
|---|---|---|
| W | Gate width (drawn) | `W=500n` |
| L | Gate length (drawn) | `L=130n` |
| NF | Number of fingers | `NF=4` |
| AD, AS | Drain/source area | Calculated by layout extractor |
| PD, PS | Drain/source perimeter | Calculated by layout extractor |

The drain/source area (AD, AS) and perimeter (PD, PS) parameters must be
extracted from the actual layout — do NOT use estimated values for
post-layout simulation. Pre-layout simulations may use a standard rule-of-thumb
estimate: AD = AS = W × 0.5 µm, PD = PS = W + 1 µm.

---

## 3. Key Model Parameters for Manual Calculations

> Note: The values below are illustrative for educational use and are NOT
> extracted from real silicon. Do not use these for silicon prediction.

### 3.1 NMOS Core Transistor (TT Corner)

| Parameter | Symbol | Typical Value | Units |
|---|---|---|---|
| Threshold voltage (Vth0) | V_th0 | 0.42 | V |
| Carrier mobility (µ_0) | u0 | 380 | cm²/V·s |
| Oxide thickness | tox | 2.8 | nm |
| DIBL coefficient | eta0 | 0.055 | — |
| Subthreshold slope | n | 1.35 | — |
| Saturation velocity | vsat | 9.5 × 10⁶ | cm/s |

### 3.2 PMOS Core Transistor (TT Corner)

| Parameter | Symbol | Typical Value | Units |
|---|---|---|---|
| Threshold voltage (Vth0) | V_th0 | -0.40 | V |
| Carrier mobility (µ_0) | u0 | 110 | cm²/V·s |
| Oxide thickness | tox | 2.8 | nm |
| DIBL coefficient | eta0 | 0.048 | — |
| Subthreshold slope | n | 1.30 | — |

### 3.3 I/O Transistor (NMOS I/O, TT Corner)

| Parameter | Symbol | Typical Value | Units |
|---|---|---|---|
| Threshold voltage (Vth0) | V_th0 | 0.60 | V |
| Carrier mobility (µ_0) | u0 | 280 | cm²/V·s |
| Oxide thickness | tox | 6.8 | nm |
| Max operating voltage | VGS_max | 3.6 | V |

---

## 4. Common Simulation Issues and Solutions

### 4.1 Convergence Failures

**Symptom**: SPICE simulation exits with "no convergence" or "iteration limit exceeded"

**Common causes and fixes**:
1. Body terminal floating — ensure all body terminals are connected.
2. Extremely large or small W/L — avoid W/L > 200 or < 0.5 in a single instance.
   Use multiple fingers (NF parameter) instead.
3. Missing initial conditions for bistable nodes (latches, flip-flops) —
   use `.IC V(node)=0` or `.NODESET`.
4. Default time step too large for fast edges — use `.TRAN 10p 10n UIC` for
   fast digital simulations instead of the default time step.

### 4.2 Incorrect Threshold Voltage

**Symptom**: Simulated V_th differs from hand-calculation by more than 50 mV

**Most common cause**: Incorrect body connection. Verify that the B terminal
of every MOSFET instance is connected to its local well/substrate contact.

For NMOS in a deep N-well (for isolation from P-substrate), the body must
be connected to the local P-well contact, NOT to the global VSS pin. Using
global VSS for the body of a deep-N-well NMOS will give incorrect V_th
due to the missing body effect.

### 4.3 Current Mismatch Between Schematic and Post-Layout

**Symptom**: Post-layout simulation shows 10–30% lower drain current than
schematic simulation at the same W/L.

**Cause**: Parasitics from extracted layout (R_contacts, R_metal, C_drain)
are now included. This is expected behaviour.

**What to check**:
- If the mismatch is >30%, verify that the layout W/L matches the schematic W/L.
- Check for unintended series resistance from narrow metal routing on the
  drain or source node.
- Verify that the number of drain/source contacts (NF × fingers) is correct.

### 4.4 Monte Carlo Analysis

For statistical yield analysis, use the Monte Carlo model library section:

```spice
.lib '/path/to/st130_pdk/models/nmos_core.spi' MC
```

The MC section includes mismatch parameters (AVT0, AU0) for Pelgrom's
mismatch model. Run a minimum of 200 Monte Carlo iterations for meaningful
mismatch statistics.

---

## 5. Passive Device Models

### 5.1 Poly Resistor

Sheet resistance: **150 Ω/□** (nominal, TT corner)
Temperature coefficient (TC1): +600 ppm/°C
Process variation: ±15% (3σ)

Minimum poly resistor dimensions: Width 400 nm, Length 1 µm
Maximum recommended sheet count: 200 squares

For matching-critical applications (e.g., reference voltage dividers),
always use poly resistors wider than 1 µm to reduce random mismatch from
LER (Line Edge Roughness). Minimum recommended width for matched resistors: 2 µm.

### 5.2 MIM Capacitor

Capacitance density: **2.0 fF/µm²** (nominal)
Voltage coefficient (VC1): -50 ppm/V
Temperature coefficient: +20 ppm/°C
Process variation: ±10% (3σ)

MIM capacitor is formed between Metal 4 and Metal 5 using a dedicated
high-K dielectric layer. The minimum MIM capacitor size is 2 µm × 2 µm
(4 µm², 8 fF).

---

*End of Synthetic SPICE Model Usage Notes — ST130 Educational Process — FOR DEMO ONLY*
