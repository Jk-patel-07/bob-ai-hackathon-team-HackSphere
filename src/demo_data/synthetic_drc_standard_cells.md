# Synthetic DRC Rule Deck — Standard Cell Library

> **SYNTHETIC DOCUMENT — FOR DEMO PURPOSES ONLY**
> This document is entirely fabricated for educational demonstration of the
> Chip Design Knowledge Assistant. It does not represent any real foundry DRC
> deck, EDA rule file, or proprietary design rule specification.

---

## 1. Introduction to DRC for Standard Cells

Design Rule Check (DRC) verifies that a physical layout conforms to the
manufacturing constraints of the fabrication process. For standard cell
design in the synthetic ST130 educational process, DRC is divided into:

1. **Layer geometry rules** — width, spacing, enclosure, extension
2. **Device rules** — transistor geometry and well isolation
3. **Connectivity rules** — contact and via placement
4. **Density rules** — CMP planarity requirements
5. **Antenna rules** — plasma charging protection

All DRC rules are checked against the drawn layout. The process bias (the
difference between drawn and printed dimensions) is accounted for in the
model files, not in the DRC rules.

---

## 2. Active Layer Rules

### Rule AA.1 — Active Minimum Width

The minimum width of an active (OD, Oxide Definition) region is **200 nm**.

Violations of AA.1 indicate diffusion fingers that are too narrow to print
reliably. The most common cause is an unintended sliver during boolean
operations in the layout tool.

### Rule AA.2 — Active Minimum Spacing

The minimum spacing between any two active regions on the same implant type
is **300 nm**. The minimum spacing between N-type and P-type active regions
is **400 nm** (enforced by rule AA.2b).

### Rule AA.3 — Active Enclosure of Contact

Active must enclose each contact by at least **60 nm** on all sides.

DRC error message: `AA.3: Contact extends beyond active region`

Typical fix: Increase the active region to fully enclose the contact array,
or move the contacts so they are inside the active enclosure boundary.

### Rule AA.4 — Active to Gate Edge Extension (Source/Drain Extension)

Diffusion (active without gate) must extend at least **80 nm** beyond the
gate edge on the source and drain sides. This rule ensures that the
source/drain diffusion is adequate for silicide formation.

---

## 3. Poly Gate Rules

### Rule PO.1 — Poly Minimum Width

The minimum poly width is **130 nm** when the poly crosses active (i.e., the
gate region). For poly that does not cross active (local interconnect use),
the minimum width is **150 nm**.

### Rule PO.2 — Poly Minimum Spacing

Minimum poly-to-poly spacing: **160 nm**

For two gate poly fingers of the same transistor, the minimum finger-to-finger
spacing is **160 nm** which corresponds to the minimum pitch of **290 nm**
(130 nm gate + 160 nm space).

### Rule PO.3 — Poly Extension Beyond Active (Gate Overhang)

Poly must extend beyond the edge of the active region by a minimum of **150 nm**
on both the source side and the drain side. This gate overhang prevents gate
shortening at the active boundary due to lithographic lens effects.

DRC error message: `PO.3: Poly overhang below minimum on active edge`

Typical fix: Extend the poly end cap beyond the active boundary.

### Rule PO.4 — Poly to Active Spacing (Non-Gate)

Poly that is NOT crossing active (non-gate poly) must be spaced at least
**100 nm** from the nearest active boundary.

### Rule PO.5 — Poly Contact Enclosure

A poly contact must be enclosed by poly by at least **100 nm** on the
gate side and **50 nm** on the non-gate side.

---

## 4. N-Well and Implant Rules

### Rule NW.1 — N-Well Minimum Width

Minimum N-well drawn width: **1200 nm (1.2 µm)**

N-wells narrower than 1.2 µm produce unreliable isolation and will cause
punch-through failures in proximity to NMOS devices.

### Rule NW.2 — N-Well Minimum Spacing

Minimum spacing between two separate N-wells: **1800 nm (1.8 µm)**

### Rule NW.3 — N-Well Must Contain PMOS Tap

Every N-well instance must contain at least one N+ active tap connected to
VDD. N-wells without taps fail NW.3 and indicate a missing body contact,
which is a latch-up risk.

DRC error message: `NW.3: N-well region has no VDD tap`

### Rule NW.4 — Tap to PMOS Distance

N-well tap must be within **20 µm** of the nearest PMOS source/drain active.

---

## 5. Metal Interconnect DRC Rules

### Rule M1.1 — Metal 1 Minimum Width

Minimum M1 width: **200 nm**

M1 segments narrower than 200 nm are below the lithographic resolution limit
and will result in open failures in manufacturing.

### Rule M1.2 — Metal 1 Minimum Spacing

Minimum M1 to M1 spacing: **200 nm**

For M1 segments longer than 10 µm, the spacing must be increased to **250 nm**
to account for long-range optical proximity effects.

### Rule M1.3 — Metal 1 Notch

The minimum notch (re-entrant gap) in a Metal 1 polygon is **200 nm**. Metal
shapes with notches narrower than 200 nm will be filled in by the OPC
(Optical Proximity Correction) step and may cause short circuits.

### Rule M1.4 — Metal 1 End-to-End Spacing

Metal 1 segment end-to-end spacing (collinear segments on the same layer)
must be at least **200 nm**. End-cap proximity closer than 200 nm can cause
merging during lithography.

### Rule M2.1 through M5.1 — Metal 2–5 Minimum Width

M2 minimum width: **280 nm**
M3 minimum width: **400 nm**
M4 minimum width: **400 nm**
M5 minimum width: **400 nm**

### Rule M6.1 — Metal 6 Minimum Width

Minimum M6 width: **800 nm**

M6 is the thick top metal. The increased minimum width is due to the greater
metal thickness (used for lower resistance) which requires wider features for
adequate lithographic control.

---

## 6. Via Rules

### Rule V1.1 — Via 1 Size

Via 1 (connecting M1 to M2) minimum size: **200 nm × 200 nm**
Via 1 must be rectangular or square; irregular via shapes are not supported.

### Rule V1.2 — Via 1 Enclosure by Metal 1

Metal 1 must enclose Via 1 by at least **50 nm** on all sides.

DRC error message: `V1.2: Via1 not enclosed by M1 minimum enclosure`

### Rule V1.3 — Via 1 Enclosure by Metal 2

Metal 2 must enclose Via 1 by at least **50 nm** on all sides.

### Rule V1.4 — Via 1 to Via 1 Spacing

Minimum spacing between two Via 1 instances: **200 nm** (measured edge to edge).

### Rule V2.1 through V5.x — Higher-Layer Via Rules

Via 2: minimum size 260 nm × 260 nm, enclosure by M2 and M3: 60 nm each side
Via 3: minimum size 360 nm × 360 nm, enclosure by M3 and M4: 70 nm each side
Via 4: minimum size 360 nm × 360 nm, enclosure by M4 and M5: 70 nm each side
Via 5: minimum size 400 nm × 400 nm, enclosure by M5 and M6: 80 nm each side

---

## 7. Density DRC Rules

Density is measured using a 50 µm × 50 µm sliding window at 10 µm steps.

### Rule DEN.1 — Poly Density

Minimum poly density: **5%** (DEN.1a — sparse poly violation)
Maximum poly density: **50%** (DEN.1b — dense poly violation)

### Rule DEN.2 — Metal 1 Density

Minimum M1 density: **10%** (add metal fill if below)
Maximum M1 density: **70%** (remove or reroute if above)

### Rule DEN.3 — Metal 2–5 Density

Minimum density for M2–M5: **10%**
Maximum density for M2–M5: **70%**

Density fill for M2–M5 is automatically inserted by the fill utility in the
PDK. Do not manually add floating metal fill — it must go through the
licensed fill utility to ensure correct net assignment (FILLN for N-well
domains, FILLP for P-substrate domains).

---

## 8. Common DRC Error Messages and Fixes

| DRC Rule | Error Message | Most Common Cause | Typical Fix |
|---|---|---|---|
| AA.1 | Active width below minimum | Sliver from boolean operation | Clean up boolean result; minimum active width is 200 nm |
| PO.3 | Poly gate overhang violation | Gate poly too short at active edge | Extend poly end cap by 150 nm beyond active boundary |
| NW.3 | N-well missing VDD tap | Copied N-well without well tap cell | Add nwell_tap standard cell inside the N-well |
| M1.1 | M1 width violation | Narrow wire from auto-routing | Increase wire width to ≥200 nm |
| V1.2 | Via1 M1 enclosure violation | Via placed at M1 end without end-cap | Add end-cap extension; minimum 50 nm enclosure required |
| DEN.2a | M1 density too low | Large open areas in floorplan | Run metal fill utility on the under-dense region |
| ANT.1 | Antenna ratio exceeded on M2 | Long M2 stub connected to gate | Insert antenna diode at the M2 layer |

---

## 9. Antenna DRC Rules

### Rule ANT.1 — Cumulative Metal Antenna Ratio

The cumulative antenna ratio at any metal layer is defined as:
  AR = (Total connected metal area at layer L) / (Total connected gate area)

Maximum allowed cumulative antenna ratios:
- At M1: 400
- At M2: 800
- At M3: 2000
- At M4: 5000
- At M5 and above: 10000

### Rule ANT.2 — Antenna Diode Requirement

When ANT.1 is violated, an antenna diode cell (ANT_DIODE) must be inserted
on the violating net at the layer that first causes the ratio to be exceeded.
The ANT_DIODE cell is available in the standard cell library.

---

*End of Synthetic DRC Rule Deck — ST130 Standard Cells — FOR DEMO ONLY*
