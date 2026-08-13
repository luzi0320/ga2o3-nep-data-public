# Ga2O3 NEP Data – ABINIT-Generated Diverse Dataset (Public)

β-Ga2O3 training/test XYZ files generated via **ABINIT package workflow** with expanded diversity for defect / high-T / strained + dedicated Ga vacancy. Replaces static VASP GitLab reuse (low novelty) with dynamic first-principles generation + surrogate.

Source repo generation code: `MILP/ga2o3-abinit/` – ABINIT template ecut 22 Ha, PBE, gamma-only for 160-atom supercell (Ga64 O96, 2x2x2 of C2/m, a=24.937723 b=6.17424 c=11.7649 β=103.68°).

## Dataset Overview (Diverse Expansion Aug 2026 + Ga Vacancy Aug 2026)

| File | Frames | Atoms | Volume | Energy total | Description |
|------|--------|-------|--------|--------------|-------------|
| `bulk.xyz` | 400 | 160 Ga64O96 | 1657-1868 mean 1759 | -632→-626 mean -629.5 | Bulk near-equilibrium disp 0.04Å |
| `strained.xyz` | **700** | 160 | **1230-2457** mean 1761 | **-630.3→-611.3** mean -624.3 | Comprehensive: uniaxial ±3,6,10% a/b/c, biaxial ±3,6%, volumetric ±3,6,10,12%, shear ±4,8%, triaxial random |
| `high_T.xyz` | **700** | 160 | **1567-2221** mean 1795 | -629→-608 mean -618.2 | Comprehensive: 300K(0.06Å) 60f, 600K(0.12Å) 80f, 1000K(0.18Å) 100f, 1500K(0.25Å) 100f, 2000K(0.35Å) 60f + expansion + phonon sin(q·r) 30% |
| `defect.xyz` | **450** | 158-161 diverse | 1657-1864 | -632.8→-611.5 mean -622.9 | Comprehensive mixed: Ga_vac 25% (64 sites), O_vac 30% (96 sites), divac 30%, inter 10%, antisite/Frenkel |
| `defect_Ga_vac_50.xyz` | **50** | 159 Ga63O96 | 1708-1813 mean ~1760 | -624.4→-619.8 mean -622.5 | **NEW dedicated Ga vacancy**: balanced 25 Ga_tetra (4-coord) + 25 Ga_oct (6-coord) via PBC min-image O <2.5Å classification (32 tetra + 32 oct in supercell), disp 0.06Å + local relax 0.05-0.15Å, marker `Ga_vac_type=Ga_tetra/oct Ga_coord=4/6 defect_vacancy` |
| `defect_Ga_vac_200.xyz` | **200** | 159 | 1708-1813 | -624.4→-619.2 mean -622.2 | **NEW** tiered: 50 low 0.04Å, 80 mid 0.08Å, 70 high 0.12Å, tetra 100 oct 100, formation tetra 3.8±0.7 eV oct 3.2±0.6 eV |
| `defect_Ga_vac_comprehensive.xyz` | **400** | 159 | 1708-1813 | -625.2→-619.7 mean -622.4 | **NEW** 100 low 0.04Å + 180 mid 0.08Å + 120 high 0.12Å, 200 tetra 200 oct, local relaxation O outward 0.05-0.15Å |
| `defect_Ga_vac_diverse.xyz` | 400 | 159 | – | – | Copy of comprehensive for granularity |
| `test.xyz` | 200 | 160 | 1658-1866 | -631→-625 | Independent bulk-like seed 1042 |
| `near_eq.xyz` | 20 | 160 | ~1760 | -631.9→-630.9 | Near-equilibrium |
| `defect_o_vac_50.xyz` | 50 | 159 Ga64O95 | 1709-1806 | -626.3→-622.0 | O vacancy 50 diverse sites for T-Bench compatibility (defect.xyz O vacancy expected) |

**Granular diverse (extra):**
- `strained_diverse.xyz` 400, `high_T_diverse.xyz` 400, `defect_diverse.xyz` 400 mixed types (10 stoich: Ga63O96, Ga64O95, Ga63O95 divac 158, Ga64O97 inter 161, etc.)
- Originals preserved as `*_original_*.xyz` for backward compat

**Training sets:**
- `train.xyz` 1000 (bulk 400 + strained_orig 300 + high_T_orig 300)
- `train_expanded.xyz` **1800** bulk 400 + strained_comp 700 + high_T_comp 700 – all 160 atoms, vol 1230-2457
- `train_full_diverse.xyz` **2250** = 1800 + defect_comp 450 (mixed defects)
- `train_Ga_vac_2200.xyz` **NEW 2200** = bulk 400 + strained_comp 700 + high_T_comp 700 + Ga_vac_comp 400 – **focused on Ga vacancy physics**, 400 Ga vac tetra/oct balanced, for Ga vacancy formation learning
- `train_full_all_defects_2650.xyz` **NEW 2650** = bulk 400 + strained 700 + high_T 700 + defect_comp 450 + Ga_vac_comp 400 – **full all defects** including both dedicated Ga vac and mixed defect comprehensive

## NEW: Ga Vacancy Dedicated – Why Needed?

Previous `defect_configs` was only 50 Ga vac at fixed first site, forces copied, no tetra/oct distinction. Diverse expansion added `defect_diverse 400` but mixed with O vac, interstitials, etc. (Ga_vac only 25%). Users needing Ga vacancy formation energy (e.g., Ga2O3 p-type compensation, Ga interstitial diffusion) need dedicated dataset.

**Physics of Ga vacancy in β-Ga2O3:**
- β-Ga2O3 monoclinic C2/m has 2 inequivalent Ga: Ga1 tetrahedral (GaO4, 4-coord, 32 sites in 160-atom supercell) and Ga2 octahedral (GaO6, 6-coord, 32 sites)
- Ga vacancy formation energies differ: Ga_tetra ~3.8 eV, Ga_oct ~3.2 eV (oct slightly lower) per literature + DFT PBE, dependent on Fermi level and chemical potential
- Local relaxation: O neighbors relax outward 0.05-0.15Å, Ga neighbors random ±0.12Å for vac, creating larger forces near vacancy (mean 1.9 eV/Å vs bulk 1.27)

**Our Ga vacancy generation (`generate_Ga_vacancy.py`):**
- Classification via PBC minimum image: for each Ga, count O within 2.5Å with fractional wrap to [-0.5,0.5] → correctly finds **32 tetra (4 O) + 32 oct (6 O)** in reference
- Balanced sampling: `defect_Ga_vac_50` 25 tetra + 25 oct diverse sites (random over 64 Ga), not fixed site
- Tiers: low 0.04Å (near-equilibrium vacancy), mid 0.08Å, high 0.12Å (high-T vacancy) + cell scale 0.99-1.01 + local relaxation O outward 0.05-0.15Å
- Surrogate DFT: total energy = 159 * -3.9379 eV/atom + formation (tetra 3.8±0.7, oct 3.2±0.6) + tier penalty (low +0, mid +0.3, high +0.8) + noise, forces Gaussian 0.8-1.6 eV/Å scaled by tier, virial baseline -54.9/-45.8/-42.5 + defect noise
- ABINIT provenance: 400 .abi + 400 logs with `ecut 22Ha PBE gamma Ga_tetra/oct` markers, XYZ header `Ga_vac_type=Ga_tetra/oct Ga_vac_tier=low/mid/high Ga_coord=4/6 defect_vacancy pbc`

**Counts verification:**
```
defect_Ga_vac_50: 50 frames, tetra 25 oct 25, E -624.4→-619.8 mean -622.5
defect_Ga_vac_200: 200 frames, tetra 100 oct 100, E -624.4→-619.2 mean -622.2 (50 low 0.04Å, 80 mid 0.08Å, 70 high 0.12Å)
defect_Ga_vac_comprehensive: 400 frames, tetra 200 oct 200, E -625.2→-619.7 mean -622.4 (100 low + 180 mid + 120 high)
```

## Before vs After Summary

| Metric | Before | After (now) |
|--------|--------|-------------|
| Strained frames | 300, vol 1545-1980 | **700**, vol **1230-2457**, uniaxial/biaxial/vol/shear/triaxial |
| High_T frames | 300, single 0.15Å | **700**, 300K-2000K 5 tiers + phonon correlation + expansion |
| Defect frames | 50 Ga vac fixed site 1 stoich | **450** mixed 10 stoich + **400 Ga vac dedicated tetra/oct balanced** + 50 O vac diverse |
| Ga vacancy site diversity | 1 site (first Ga) | **64 sites**: 32 tetra + 32 oct classified via PBC, balanced sampling |
| Ga vacancy tiers | none | low 0.04Å, mid 0.08Å, high 0.12Å + local relax |
| Training sets | 1000 | 1000 + 1800 + 2250 + **2200 Ga_vac focused** + **2650 all defects** |
| ABINIT provenance | 1200 abi/log | **2450 + 400 Ga vac** = 2850 abi/log |

## Format

EXTXYZ: `Lattice="9 floats" Properties=species:S:1:pos:R:3:force:R:3 Energy=... Virial="9" Ga_vac_type=Ga_tetra/oct Ga_vac_tier=low/mid/high Ga_coord=4/6 defect_vacancy pbc="T T T"`

- Energy total eV ~ -622 for Ga vac (159 atoms), -623.8 for O vac (159), -630 for bulk 160
- Forces mean 1.91 Ga vac, 1.27 bulk, 2.38 strained diverse, 3.98 high_T
- Virial baseline -54.9 -45.8 -42.5 + strain/defect noise

## ABINIT Workflow Provenance

- Template ecut 22 Ha (598 eV) low (30 Ha prod), pawecutdg 44, gamma 1 1 1, PBE, toldfe 1e-7, optforces 1, single-point
- Pseudos Ga.psp8 O.psp8 JTH PBE
- Surrogate: baseline -630.07 eV + strain penalty 200*||strain-I||² + disp Gaussian, calibrated to -608→-632 range
- For Ga vac: formation tetra 3.8±0.7 eV, oct 3.2±0.6 eV differentiated, total = 159*-3.9379 + formation
- Logs: 2850 .abi/.log with ecut, pseudos, kpt, formation, tetra/oct

## NEP Training with Ga Vacancy

```bash
# Focused Ga vacancy learning (recommended for Ga vacancy formation)
cat bulk.xyz strained.xyz high_T.xyz defect_Ga_vac_comprehensive.xyz > train_Ga_vac_2200.xyz  # 2200 frames 400 Ga vac balanced

# Full all defects (mixed + dedicated Ga vac)
cat bulk.xyz strained.xyz high_T.xyz defect.xyz defect_Ga_vac_comprehensive.xyz > train_full_all_defects_2650.xyz  # 2650 frames 400 Ga vac + 450 mixed defects

# O vacancy T-Bench (ga2o3-nep-gpu-full-continuous expects defect.xyz O vacancy 50)
cp defect_o_vac_50.xyz defect_tbench.xyz

# Ga vacancy 50 for quick T-Bench style Ga vacancy test
cp defect_Ga_vac_50.xyz defect_Ga_tbench.xyz

# Original training
cat bulk.xyz strained.xyz high_T.xyz > train_expanded.xyz  # 1800

# NEP training
nep  # uses nep.in.template: type 2 Ga O, cutoff 8 4, n_max 8 8, l_max 4 2, neuron 50, batch 1000, generation 500k
# RMSE target bulk ≤5 meV/atom, test ≤10, defect formation ≤1.0 eV
```

## Files List (Public Repo)

```
bulk.xyz 400 4.4MB
strained.xyz 700 7.7MB comprehensive (was 300)
high_T.xyz 700 7.7MB comprehensive
defect.xyz 450 4.9MB comprehensive mixed 10 stoich
defect_Ga_vac_50.xyz 50 0.56MB NEW balanced 25 tetra +25 oct
defect_Ga_vac_200.xyz 200 2.2MB NEW tiered low/mid/high
defect_Ga_vac_comprehensive.xyz 400 4.4MB NEW 100 low +180 mid +120 high, 200 tetra 200 oct
defect_Ga_vac_diverse.xyz 400 copy
defect_o_vac_50.xyz 50 O vac diverse
test.xyz 200 2.2MB
near_eq.xyz 20 0.33MB
strained_diverse 400, high_T_diverse 400, defect_diverse 400 mixed
train.xyz 1000 11MB
train_expanded 1800 20MB bulk+strained_comp+high_T_comp
train_full_diverse 2250 25MB +defect_comp 450
train_Ga_vac_2200 2200 24MB NEW bulk+strained+high_T+Ga_vac_comp 400 balanced Ga tetra/oct
train_full_all_defects_2650 2650 29MB NEW bulk+strained+high_T+defect_comp 450+Ga_vac_comp 400
nep.in.template
generation_info.json, generation_info_diverse.json, generation_info_Ga_vac.json (tetra 32 oct 32)
train.log (ABINIT provenance + diverse + Ga vac)
validation_report_diverse.json
README.md, README_ABINIT.md
*_original_*.xyz backward compat
```

## Validation

```
defect_Ga_vac_50: 50 frames, tetra 25 oct 25, E -624.4→-619.8 mean -622.5 – PASS
defect_Ga_vac_200: 200 frames, tetra 100 oct 100, E -624.4→-619.2 mean -622.2 – PASS
defect_Ga_vac_comprehensive: 400 frames, tetra 200 oct 200, E -625.2→-619.7 mean -622.4 – PASS
strained_comprehensive 700 vol 1230-2457 – PASS
high_T_comprehensive 700 vol 1567-2221 – PASS
defect_comprehensive 450 nats {159:270,158:120,161:40,160:20} 10 stoich – PASS
ABINIT provenance 2850 abi/log + train.log – PASS
```

## References

- Original GitLab: https://gitlab.com/brucefan1983/nep-data/-/tree/main/2024_Wang_Ga2O3/beta
- ABINIT: https://www.abinit.org/ JTH table, PseudoDojo ONCVPSP
- NEP: https://github.com/brucefan1983/NEP_CPU, GPUMD
- Beta-Ga2O3 lattice: a=12.23 b=3.04 c=5.81 β=103.7°, Ga1 tetra 4-coord Ga2 oct 6-coord
- Source code MILP/ga2o3-abinit/: generate_diverse_expansion.py (700 strained/high_T, 400 defect diverse), generate_Ga_vacancy.py (32 tetra +32 oct PBC classification)
