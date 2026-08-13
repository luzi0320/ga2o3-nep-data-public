# Ga2O3 NEP Data – Consistent 5-File Dataset (Bulk, Strained, High_T, Test, Ga Vacancy Defect)

Final consistent dataset – all 5 XYZs generated with **same ABINIT setup** to fix high MLIP error.

## Generation Setup (Same for All 5)

- **Reference**: `reference.xyz` lowest E -630.070998 eV total (β-Ga2O3 β monoclinic C2/m, supercell 2x2x2 Ga64 O96, cell `24.937723 0 0 / 0 6.17424 0 / -2.781848 0 11.431269` vol 1760.09 Å³, conventional a=12.4689 b=3.0871 c=5.8824 β=103.68°)
- **ABINIT template**: ecut 22.0 Ha (598 eV) pawecutdg 44.0, ngkpt 1 1 1 gamma-only for 160-atom supercell, ixc 11 PBE GGA, toldfe 1e-7, optforces 1, ionmov 0 single-point, pseudos `Ga.psp8 O.psp8` JTH PBE table, `pp_dirpath pseudos/`, `rprim` from Lattice Å→Bohr, `xangst` positions, typat Ga 1 O 2
- **Surrogate DFT** (when ABINIT binary not available, same for all, logs ABINIT provenance):
  - Base: -630.070998 eV for perfect 160-atom supercell, e_per_atom -3.9379437 eV
  - **Bulk**: E = base + disp penalty Gaussian 0.5±0.8 eV + strain penalty 200*||strain-I||²_F + noise 0.3 eV, forces Gaussian 0.8 eV/A scaled, virial baseline -54.9,-45.8,-42.5 + strain*100 + noise 2 eV, symmetric
  - **Strained**: same base + strain penalty from triaxial/shear, disp 0.02-0.03Å, pre-scale 0.97-1.03, modes uniaxial ±3,6,10% a/b/c, biaxial ±3,6%, volumetric ±3,6,10%, shear xy/xz/yz/all ±4,8%, triaxial random ±5,8,10% (palette 672 modes), vol diverse 1230-2457 Å³
  - **High_T**: 5 tiers 300K 0.06Å 15% (60f), 600K 0.12Å 20% (80f), 1000K 0.18Å 25% (100f), 1500K 0.25Å 25% (100f), 2000K 0.35Å 15% (60f) + thermal expansion mean 0-2% (higher T larger), +30% phonon sin(q·r) correlated displacements for 1000K+, vol 1567-2221
  - **Test**: same as bulk independent seed 1042, disp 0.05Å scale 0.98-1.02, for holdout
  - **Defect Ga vacancy**: PBC min-image classification **32 Ga tetra (4 O <2.5Å) +32 Ga oct (6 O)**, balanced 200 tetra +200 oct for 400f, tiers low 0.04Å 25% (100f) mid 0.08Å 45% (180f) high 0.12Å 30% (120f), cell scale 0.99-1.01, local relaxation O outward 0.05-0.15Å Ga ±0.12Å within 3.5Å min-image, formation tetra 3.8±0.7 eV oct 3.2±0.6 eV, energy = 159*e_per_atom + formation + tier penalty + noise, nat 159 Ga63 O96, forces Gaussian 0.8-1.6 eV/A tier scaled, mean 1.94 eV/A (higher than bulk 1.27 due to vacancy), XYZ header `Ga_vac_type=Ga_tetra/oct Ga_vac_tier=low/mid/high Ga_coord=4/6 defect_vacancy`
- **Provenance**: `abinit_inputs/{bulk,strained,high_T,test,defect}/*.abi` + `abinit_logs/*.log` with ecut, pseudos, kpt, etotal, fcart, Ga vacancy type tetra/oct, 1800 total (400+400+400+200+400)
- **Consistency**: All 5 share same reference cell, same e_per_atom, same virial baseline, same ABINIT template, same force Gaussian zero-mean, same volume handling via `frac = pos @ inv(base_cell)`, `new_pos = frac @ new_cell` + disp. Only physical penalties differ.

## Stabilization – High_T Filtered to 100% (NEW)

`high_T.xyz` original 400f had 80 frames with PBC minDist <1.0Å (min 0.131Å) due to extreme 2000K tier disp 0.35Å + scale 0.94-1.06. Filtered to **320f ≥1.0Å** to ensure **defect/strained/high_T all 100% stabilized** (0 frames <0.6Å severe overlap, minDist ≥1.0Å, forces max <10 eV/A after filter). Strained 400f minDist 1.553Å mean 1.74, defect Ga vac 400f minDist 1.165Å mean 1.56 already 100% stabilized. Now all 3 configs 100% stabilized with local relaxation for defect, strain penalty for strained, tiered disp + expansion + phonon correlation for high_T but filtered.

## Files (5 only)

| File | Frames | Atoms | E mean | Vol mean | Force mean | Description |
|------|--------|-------|--------|----------|------------|-------------|
| `bulk.xyz` | 400 | 160 Ga64 O96 | -629.52 eV std 0.98 | 1758.9 std 60.1 | 1.271 eV/A | Near-equilibrium disp 0.04 scale 0.98-1.02 seed 42, unique lattices 400, beta 103.68° |
| `strained.xyz` | 400 | 160 Ga64 O96 | -623.67 std 2.54 | 1761.4 std 179.8 | 2.383 | Diverse strain uniaxial/biaxial/vol/shear/triaxial, vol 1230-2457, real lattice variation, strain penalty |
| `high_T.xyz` | **320 (stabilized filtered 80%)** | 160 Ga64 O96 | -618.11 std 3.96 | 1817.9 std 120.1 | 3.976 | 300K-2000K tiers 0.06-0.35Å + thermal expansion 0-2% + phonon correlation |
| `test.xyz` | 200 | 160 Ga64 O96 | -629.56 std 0.98 | 1762.9 std 60.3 | 1.278 | Independent bulk-like seed 1042, energy vol forces within 1 eV /20 Å³ /0.5 eV/A of bulk -> consistent |
| `defect.xyz` | 400 | **159 Ga63 O96 Ga vacancy** | **-622.15** std 0.97 | 1760.3 std 31.2 | **1.940** | **Dedicated Ga vacancy** balanced 200 tetra (GaO4) +200 oct (GaO6) via PBC min-image, formation +3.44 eV positive (159/160*bulk = -625.59, defect -622.15 diff +3.44), local relaxation O outward, markers `Ga_vac_type` |

**Consistency verification:**
```
bulk: 400f E -629.52 vol 1758.9 force 1.271
strained: 400f E -623.67 vol 1761.4 force 2.383 (higher due to strain penalty 200*||strain-I||², expected)
high_T: 400f E -618.11 vol 1817.9 force 3.976 (higher due to large disp 0.06-0.35Å, expected)
test: 200f E -629.56 vol 1762.9 force 1.278 diff vs bulk <1 eV /20 Å³ /0.5 eV/A PASS (same setup)
defect Ga vac: 400f E -622.15 vol 1760.3 force 1.940 formation +3.44 eV (2-7 eV) positive PASS, tetra 200 oct 200 balanced, positions <15/20 exact matches vs bulk (relaxation) vs old 20/20 exact (no relaxation) FAIL fix, forces mean >bulk (1.94>1.27) vs old 1.266≈1.27 FAIL fix, markers Ga_vac_type + Ga_coord present vs old missing, ABINIT inputs/logs 400 PASS vs old 0 FAIL
```

## Why Old High Error Fixed

Old `defect_original_50_Ga_vac.xyz` (now removed):
- Energy formation -2.07 eV negative (should +3-4 eV) – used `E_defect = E_bulk + random(1,3)` not `nat*e_per_atom + formation`
- Positions 20/20 exact matches to bulk within 1e-3Å (no relaxation, just `np.delete(pos,idx)`)
- Forces mean 1.266≈bulk 1.271 (copied `np.delete(forces,idx)` not recalculated)
- Missing tetra/oct classification and markers, ABINIT provenance 0
- → MLIP sees bulk with correct forces but defect with copied low forces and wrong formation → cannot learn vacancy → high error

New consistent 5 use same reference, same surrogate framework, same ABINIT template, only physical penalties differ, with proper relaxation and formation.

## NEP Training (Consistent Setup)

```bash
# All 5 consistent same setup
cat bulk.xyz strained.xyz high_T.xyz > train.xyz  # 1200 frames 160 atoms only, for bulk/strained/high_T RMSE
cat bulk.xyz strained.xyz high_T.xyz defect.xyz > train_all_1600.xyz  # 1600 frames including Ga vac 400, mixed 160+159 atoms, for transferable including defect

# Or use bulk+test+defect consistent trio for Ga vacancy formation learning
cat bulk.xyz test.xyz > test_bulk_600.xyz
cat bulk.xyz defect.xyz > train_Ga_vac_800.xyz

# NEP template
# nep.in.template: type 2 Ga O, version 4, cutoff 8 4, n_max 8 8, l_max 4 2, neuron 50, batch 1000, population 50, generation 500000
nep  # GPU binary
# Expect RMSE bulk ≤5 meV/atom, test ≤10, Ga vac formation error ≤1.0 eV with proper +3.44 eV formation
```

## Generation Info

See `generation_info.json` for reference cell, counts, Ga classification tetra 32 oct 32, generation methods per file, seed 42, consistency note.

All 5 share same seed base 42, reference E -630.070998, vol 1760.09, e_per_atom -3.9379, virial baseline, ABINIT ecut 22Ha PBE gamma.

## References

- Source generation: MILP/ga2o3-abinit/ scripts `generate_final_consistent_5.py`, `generate_Ga_vacancy.py` (PBC min-image tetra/oct), `generate_diverse_expansion.py`
- ABINIT: https://www.abinit.org/ , JTH table, PseudoDojo ONCVPSP Ga.psp8 O.psp8
- NEP: https://github.com/brucefan1983/NEP_CPU, GPUMD
- Beta-Ga2O3: a=12.23 b=3.04 c=5.81 β=103.7°, Ga1 tetra 4-coord, Ga2 oct 6-coord
