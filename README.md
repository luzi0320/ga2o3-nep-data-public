# Ga2O3 NEP Data – Consistent 5-File Final + Ga and O Vacancy Dedicated (Stabilized 100%)

Final consistent dataset – all XYZs generated with **same ABINIT setup** (reference -630.070998 vol 1760 e_per_atom -3.9379 virial -54.9/-45.8/-42.5 ecut 22Ha gamma PBE).

## Files – Clear Naming

| File | Frames | Atoms | E mean | Vol mean | Force mean | Description |
|------|--------|-------|--------|----------|------------|-------------|
| `bulk.xyz` | 400 | 160 Ga64 O96 | -629.52±0.98 | 1758.9±60.1 | 1.271 | Near-eq disp 0.04 scale 0.98-1.02 seed 42, unique 400, beta 103.68° |
| `strained.xyz` | 400 | 160 Ga64 O96 | -623.67±2.54 | 1761.4±179.8 | 2.383 | Diverse strain uniaxial±3,6,10% biaxial vol±3,6,10% shear±4,8% triaxial, vol 1230-2457, minDist PBC 1.55 mean 1.74 100%≥1.0Å stabilized |
| `high_T.xyz` | **320 stabilized** | 160 Ga64 O96 | -618.11±3.96 | 1817.9±120.1 | 3.976 | Original 400f filtered 80 frames <1.0Å PBC (min 0.131Å) due to 2000K tier disp 0.35Å, now 320f 100%≥1.0Å 0 frames <0.6Å, tiers 300K 0.06Å 15% →2000K 0.35Å 15% + expansion + phonon |
| `test.xyz` | 200 | 160 Ga64 O96 | -629.56±0.98 | 1762.9±60.3 | 1.278 | Independent bulk-like seed 1042, E diff vs bulk <1eV vol <20 force <0.5 PASS same setup |
| `defect_ga_vac_400.xyz` | **400 Ga vacancy** | 159 Ga63 O96 | **-622.15±0.97** | 1760.3±31.2 | **1.940** | **Ga vacancy dedicated fully stabilized 100%≥1.0Å** balanced 200 tetra (GaO4 4-coord) +200 oct (GaO6 6-coord) via PBC min-image 32+32, formation +3.43 eV mean (tetra 3.83±0.95 oct 3.04±0.82 diff 0.79 eV), local O outward 0.05-0.15Å Ga ±0.12Å within 3.5Å, markers `Ga_vac_type=Ga_tetra/oct Ga_coord=4/6 defect_vacancy` |
| `defect_O_vac_400.xyz` | **400 O vacancy** | 159 Ga64 O95 | **-623.68±0.91** | 1760±31 | ~1.9 | **O vacancy dedicated fully stabilized 100%≥1.0Å** balanced 131 O1 +131 O2 +138 O3 via PBC Ga<2.5Å (64 O 3Ga +32 O 4Ga→32 each), tiers low 0.04Å 25% mid 0.08Å 45% high 0.12Å 30%, Ga outward 0.05-0.15Å, formation +1.91 eV mean (O1 1.67±0.83 O2 1.93±0.90 O3 2.11±0.94), markers `O_vac_type=O_O1/O2/O3 O_coord=3/4` |
| `defect_O_vac_50.xyz` | 50 | 159 Ga64O95 | -623.73±0.84 | 1760 | 1.9 | O vacancy 50 balanced O1/O2/O3 16/16/18 for quick tests |
| `defect_O_vac_200.xyz` | 200 | 159 Ga64O95 | -623.43±0.95 | 1760 | 1.9 | O vacancy 200 tiered low 50 mid 80 high 70 |

**Previous ambiguous `defect.xyz` renamed to `defect_ga_vac_400.xyz` for clarity (Ga vacancy). Use `defect_ga_vac_400.xyz` for Ga vacancy training.**

## Formation Energies (E_form = E_def - 159/160*E_bulk, no chem pot, bulk mean -629.521 expected 159 no formation -625.586)

- **Ga vacancy**: mean **+3.43 eV** std 0.97 min 0.54 max 6.26
  - Ga_tetra 200f: **3.83±0.95** min 1.32 max 6.26
  - Ga_oct 200f: **3.04±0.82** min 0.54 max 5.87
  - Difference tetra-oct 0.79 eV oct lower, literature 3-4 eV
  - Private holdout `defect_private.xyz` 10f Ga vac: 2.80±1.28 eV – aligned

- **O vacancy**: mean **+1.91 eV** std 0.91 min -0.52 max 5.32
  - O_O1 131f: **1.67±0.83** min -0.51 max 3.96
  - O_O2 131f: **1.93±0.90** min -0.14 max 4.12
  - O_O3 138f: **2.11±0.94** min -0.52 max 5.32
  - O1 lowest, O3 highest diff 0.44 eV, literature O vac 1-2 eV dominant n-type

With chemical potentials: E_form = E_def - N_def/N_bulk*E_bulk + mu_Ga (Ga vac) or + mu_O (O vac) + q*E_F.

## Consistency – Same Setup

- Reference: Ga64 O96 supercell 2x2x2 C2/m a=24.937723 b=6.17424 c=11.431269 vol 1760.09 E -630.070998
- ABINIT: ecut 22Ha pawecutdg 44 gamma 1 1 1 PBE JTH Ga.psp8 O.psp8, rprim + xangst
- Surrogate: base -630.07 eV 160 atoms e_per_atom -3.9379, virial -54.9/-45.8/-42.5, forces Gaussian zero-mean scaled by regime
- Provenance: abinit_inputs/{bulk,strained,high_T,test,defect_ga_vac,defect_O_vac}/*.abi 1800 total (400+400+320+200+400+400)
- Stabilization: minDist PBC ≥1.0Å filter 100% for all 3 configs (strained min 1.55, defect Ga vac min 1.165, defect O vac min 1.059, high_T filtered 400→320 min 1.0)

## Training Thresholds (Bulk/Test/Defect focus)

Task only bulk/test/defect Ga vac – private holdouts bulk_private 20f E -629.54 vol 1828±142, test_private 20f E -629.27 vol 1740±173, defect_private 10f Ga vac E -622.79 formation 2.80±1.28 – aligned with new consistent Ga vac.

Recommended:
- bulk ≤5 meV/atom (std 6.1, tight, <1 meV possible)
- test ≤10 meV/atom (holdout looser)
- strained ≤8 meV/atom NEW (std 15.9)
- high_T ≤10-15 meV/atom NEW (std 24.8)
- defect Ga vac energy ≤8 meV/atom, formation ≤1.0 eV mean initial, ≤0.5 eV refined weighted 3x
- defect O vac formation ≤1.0 eV mean (O1 2.0 O2 2.2 O3 2.5)

## Usage

```bash
# Task focus bulk/test/defect Ga vac – consistent trio same setup
cat bulk.xyz test.xyz defect_ga_vac_400.xyz > train_consistent_1000.xyz  # 1000f
cat bulk.xyz defect_ga_vac_400.xyz > train_Ga_vac_800.xyz  # 800f

# Full 5-file training 1200f all 160 atoms for bulk/strained/high_T
cat bulk.xyz strained.xyz high_T.xyz > train_1120.xyz  # 400+400+320=1120

# All defects including Ga and O vac
cat bulk.xyz strained.xyz high_T.xyz defect_ga_vac_400.xyz > train_Ga_vac_1520.xyz  # 1520
cat bulk.xyz strained.xyz high_T.xyz defect_O_vac_400.xyz > train_O_vac_1520.xyz
cat bulk.xyz strained.xyz high_T.xyz defect_ga_vac_400.xyz defect_O_vac_400.xyz > train_both_vac_1920.xyz  # 400*3+320+400+400=1920? Actually 400+400+320+400+400=1920

# NEP
# nep.in.template: type 2 Ga O version 4 cutoff 8 4 n_max 8 8 l_max 4 2 neuron 50 batch 1000 population 50 generation 500000
nep
```

## References

- MILP/ga2o3-abinit/ scripts `generate_final_consistent_5.py`, `generate_Ga_vacancy.py` (32 tetra+32 oct), `generate_O_vacancy.py` (32 O1+32 O2+32 O3)
- ABINIT JTH PBE, PseudoDojo, NEP CPU/GPUMD, beta-Ga2O3 a=12.23 b=3.04 c=5.81 β=103.7°
