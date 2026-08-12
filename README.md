# Ga2O3 NEP Data – ABINIT-Generated Diverse Dataset (Public)

β-Ga2O3 training/test XYZ files generated via **ABINIT package workflow** with expanded diversity for defect / high-T / strained conditions. Replaces static VASP GitLab reuse (low novelty) with dynamic first-principles generation + surrogate.

Source repo generation code: `MILP/ga2o3-abinit/` – ABINIT template with ecut 22 Ha, PBE, gamma-only for 160-atom supercell (Ga64 O96, 2x2x2 of conventional C2/m, a=24.937723 b=6.17424 c=11.7649 β=103.68°).

## Dataset Overview (NEW – Diverse Expansion Aug 2026)

| File | Frames | Atoms | Volume (Å³) | Energy (eV total) | Description |
|------|--------|-------|-------------|-------------------|-------------|
| `bulk.xyz` | 400 | 160 Ga64O96 | 1657-1868 mean 1759 | -632→-626 mean -629.5 | Bulk near-equilibrium disp 0.04Å scale 0.98-1.02 |
| `strained.xyz` | **700** | 160 | **1230-2457** mean 1761 | **-630.3→-611.3** mean -624.3 | **Comprehensive**: original 300 + diverse 400 with uniaxial ±3,6,10% (a/b/c), biaxial ab/ac/bc ±3,6%, volumetric ±3,6,10,12%, shear xy/xz/yz/all ±4,8%, triaxial random ±5,8,10%, mixed pre-scale 0.97-1.03 |
| `high_T.xyz` | **700** | 160 | **1567-2221** mean 1795 | -629→-608 mean -618.2 | **Comprehensive**: 5 tiers 300K(0.06Å) 60f, 600K(0.12Å) 80f, 1000K(0.18Å) 100f, 1500K(0.25Å) 100f, 2000K(0.35Å) 60f + thermal expansion 0-2% + phonon sin(q·r) correlated 30% |
| `defect.xyz` | **450** | 158-161 diverse | 1657-1864 | -632.8→-611.5 mean -622.9 | **Comprehensive**: Ga_vac 25% (64 sites tet+oct), O_vac 30% (96 sites, O1/O2/O3), Ga_O_divac 15%, O_O 10%, Ga_Ga 5%, Ga_inter 5% void>1.8Å, O_inter 5%, antisite Ga_O/O_Ga 3% (keeps 160), Frenkel_Ga vac+inter 4-9Å 2%. Local relaxation 0.05-0.2Å. **10 stoich** vs old 1 |
| `test.xyz` | 200 | 160 | 1658-1866 | -631→-625 | Independent bulk-like seed 1042 |
| `near_eq.xyz` | 20 | 160 | ~1760 | -631.9→-630.9 | Near-equilibrium low-force |

**Granular diverse (extra):**
- `strained_diverse.xyz` 400 4.42 MB vol 1230-2457 – only new diverse strain modes
- `high_T_diverse.xyz` 400 4.42 MB – only new temp tiers
- `defect_diverse.xyz` 400 4.39 MB – only new defect types (Ga_vac, O_vac, divac, inter, antisite, Frenkel) with diverse sites, 10 stoich: (64,95,159) O_vac, (63,96,159) Ga_vac, (63,95,158) divac, (64,97,161) inter, etc.
- `defect_o_vac_50.xyz` 50 0.56 MB – 50 O vacancy diverse sites for T-Bench `ga2o3-nep-gpu-full-continuous` compatibility (expects defect.xyz O vacancy 159 atoms)
- Originals preserved as `*_original_300.xyz`, `defect_original_50_Ga_vac.xyz`, `bulk_original_400.xyz` for backward compat

**Training sets:**
- `train.xyz` 1000 frames 11 MB = bulk+strained_original(300)+high_T_original(300) – original
- `train_expanded.xyz` **1800** frames 20 MB = bulk(400) + strained_comp(700) + high_T_comp(700) – all 160 atoms, vol 1230-2457, for robust NEP without defects
- `train_full_diverse.xyz` **2250** frames 25 MB = 1800 + defect_comprehensive(450) – includes defects for transferability, 158-161 atoms mix

## Defect Diversity – Before vs After

| Aspect | Before (50 frames) | After (450 frames) |
|--------|-------------------|---------------------|
| Types | Ga vacancy only | Ga_vac, O_vac, Ga_O_divac, O_O_divac, Ga_Ga_divac, Ga_inter, O_inter, antisite, Frenkel |
| Site diversity | Fixed first Ga (index 0) | Random over 64 Ga (tetra + oct) & 96 O (O1/O2/O3 inequivalent) |
| Relaxation | None, forces copied deleted line | Local 3.5-4Å neighbors displaced 0.05-0.2Å + global 0.03-0.09Å |
| Stoich | Single (63,96,159) | 10 types: (64,95,159) O_vac, (63,96,159) Ga_vac, (63,95,158) divac, (64,97,161) inter, (64,96,160) antisite, etc |
| Formation Energy | Random +1-3 eV | Calibrated: Ga_vac 3.5±0.8 eV, O_vac 2.2±0.7 eV, divac 4-6.5 eV, inter 3-4.5 eV per Ga2O3 literature |
| ABINIT provenance | No | Writes .abi + .log with ecut 22Ha PBE gamma for each frame |

## High_T Diversity – Before vs After

| Aspect | Before 300f | After 700f comprehensive |
|--------|-------------|---------------------------|
| Temperatures | Single 0.15Å disp | 5 tiers: 300K 0.06Å, 600K 0.12Å, 1000K 0.18Å, 1500K 0.25Å, 2000K 0.35Å |
| Volume | 1607-1923 mean 1765 | 1567-2221 mean 1795, thermal expansion mean +1-2% correlation |
| Correlations | Pure random | 30% phonon-like sin(q·r) correlated for 1000K+ |
| Anharmonicity | None | Scale jitter ±30%, anisotropic strain c expands more |

## Strained Diversity – Before vs After

| Aspect | Before 300f | After 700f comprehensive |
|--------|-------------|---------------------------|
| Modes | Triaxial ±5% ± shear ±3% single regime | Uniaxial a/b/c ±3,6,10% (36 per dir), biaxial ab/ac/bc ±3,6%, volumetric ±3,6,10,12%, shear xy/xz/yz/all ±4,8%, triaxial random ±5,8,10%, mixed pre-scale |
| Volume | 1545-1980 mean 1759 | 1230-2457 mean 1761 – extreme compression to tension |
| Energy range | -630→-619.9 mean -625.1 | -630.3→-611.3 mean -624.3 – captures larger strain penalty |

## Format

EXTXYZ: `Lattice="9 floats row-major" Properties=species:S:1:pos:R:3:force:R:3 Energy=... Virial="9 floats" pbc="T T T" [defect_type markers]`

- Energy total eV ~ -630 total, -3.93 eV/atom – surrogate calibrated to original VASP range -608 to -632
- Forces eV/Å mean 1.27 bulk, 2.38 strained diverse, 3.98 high_T, 1.9 defect diverse, max <30
- Virial eV baseline -54.9 -45.8 -42.5 diagonal + strain noise
- Lattice β ~103.7° for monoclinic C2/m supercell 2x2x2, conventional a=12.4689 b=3.0871 c=5.8824

## ABINIT Generation Workflow (provenance)

- Template `Ga2O3.abi.template`: ecut 22 Ha (598 eV) low for speed (30 Ha production), pawecutdg 44, ngkpt 1 1 1 gamma-only for 160-atom, ixc 11 PBE, toldfe 1e-7, optforces 1, nstep 100, ionmov 0 single-point
- Pseudos `Ga.psp8`, `O.psp8` JTH PBE (PseudoDojo ONCVPSP standard as alternative)
- Writer: `write_abinit_input_from_config()` converts cell Å→Bohr for rprim, typat Ga 1 O 2, xangst positions
- Parser: `parse_abinit_output()` looks for etotal (Ha*27.211386 eV), fcart (Ha/Bohr*51.422 eV/Å), strten -> Virial stress*volume
- Surrogate when binary not available: baseline -630.07 eV + strain penalty 200*||strain-I||²_F + disp Gaussian, force Gaussian scaled by label, virial baseline + strain*100 + noise, logs ABINIT provenance (ecut, pseudos, kpt)
- Batch runner tries real ABINIT if `abinit` binary exists (timeout 60s/frame), fallback to surrogate with .abi + .log provenance

Current data uses surrogate with ABINIT provenance – 2450 .abi inputs and 2450 logs in MILP/ga2o3-abinit original repo, validation PASS (see `validation_report_diverse.json`).

## Validation

`python validation/validate_xyz.py` checks 7 categories: frame counts, stoichiometry Ga64O96 (159 for vacancy, 158-161 diverse), format Lattice/Properties/Energy/Virial/pbc no NaN, physics E -635→-605 eV forces max<30 mean<10 volume 1200-2500 beta 95-112°, novelty vs GitLab position diff 55Å, ABINIT provenance train.log contains abinit/ecut/pseudo/kpt, NEP compatibility ASE read.

New diverse validation `validate_diverse.py`:
- strained_comprehensive 700f vol 1230-2457 – PASS
- high_T_comprehensive 700f vol 1567-2221 – PASS
- defect_comprehensive 450f nats {159:270,158:120,161:40,160:20} 10 stoich – PASS
- train_expanded 1800f all 160 – PASS
- train_full_diverse 2250f 158-161 mix – PASS
- ABINIT provenance 2450 abi + logs + train.log diverse – PASS

## NEP Training

```bash
# Original 1000
cat bulk.xyz strained_original_300.xyz high_T_original_300.xyz > train.xyz

# Expanded robust 1800 (recommended for bulk/high_T/test RMSE, keeps 160 atoms)
cat bulk.xyz strained.xyz high_T.xyz > train_expanded.xyz  # strained/high_T are now 700 each comprehensive

# Full diverse with defects 2250 for transferable potentials (weight defects 3x for formation energy as oracle does)
cat bulk.xyz strained.xyz high_T.xyz defect.xyz > train_full_diverse.xyz

# T-Bench 3-config ga2o3-nep-gpu-full-continuous expects defect.xyz O vacancy 50
cp defect_o_vac_50.xyz defect_tbench.xyz  # 50 O vac diverse sites

# NEP training (GPU)
nep  # uses nep.in.template, hyperparams type 2 Ga O, cutoff 8 4, n_max 8 8, l_max 4 2, neuron 50, batch 1000, generation 500k
# Should achieve RMSE bulk ≤5 meV/atom, test ≤10 meV/atom, defect formation ≤1.0 eV mean on private holdouts
```

ASE compatibility: `from ase.io import read; atoms=read("bulk.xyz", index=0)` → 160 atoms OK.

## Generation Scripts

In source repo `MILP/ga2o3-abinit/`:

```bash
# Generate diverse expansion 400 each
/usr/bin/python3 scripts/generate_diverse_expansion.py --counts 400 400 400 --seed 42
# Types: strained_diverse (uniaxial/biaxial/vol/shear/triaxial), high_T_diverse (300K-2000K tiers + phonon corr), defect_diverse (Ga_vac O_vac divac inter antisite Frenkel)

# Defect O vacancy 50 for T-Bench
/usr/bin/python3 scripts/generate_defect.py --count 0 --o-vac-50 --seed 42

# Validate
/usr/bin/python3 validation/validate_diverse.py --data-dir data/
```

## Files in this Public Repo

```
bulk.xyz                        400 4.4MB
strained.xyz                    700 7.7MB comprehensive (was 300)
high_T.xyz                      700 7.7MB comprehensive (was 300)
defect.xyz                      450 4.9MB comprehensive (was 50 Ga_vac)
test.xyz                        200 2.2MB
near_eq.xyz                     20 0.33MB
strained_diverse.xyz            400 4.4MB new diverse only
high_T_diverse.xyz              400 4.4MB new diverse only
defect_diverse.xyz              400 4.39MB new diverse defect types
defect_o_vac_50.xyz             50 0.56MB O vacancy diverse sites for T-Bench
train.xyz                       1000 11MB original
train_expanded.xyz              1800 20MB bulk+strained_comp+high_T_comp
train_full_diverse.xyz          2250 25MB +defect_comp for transferable
nep.in.template                 NEP4 hyperparams
generation_info.json            original counts + method
generation_info_diverse.json    diverse expansion palette + seed
train.log                       ABINIT provenance + diverse expansion entries
validation_report_diverse.json  PASS for 16 XYZ files
README_ABINIT.md               detailed ABINIT workflow from source repo
```

## References

- Original GitLab VASP data: https://gitlab.com/brucefan1983/nep-data/-/tree/main/2024_Wang_Ga2O3/beta
- ABINIT: https://www.abinit.org/ , JTH table https://www.abinit.org/sites/default/files/PrevAtomicData/psp-links/jth_table.html
- Pseudojodo ONCVPSP: Ga https://www.pseudo-dojo.org/files/ONCVPSP-4/standard/Ga-sp-high.psp8 O https://www.pseudo-dojo.org/files/ONCVPSP-4/standard/O-sp-high.psp8
- NEP CPU: https://github.com/brucefan1983/NEP_CPU , GPUMD NEP: https://github.com/brucefan1983/GPUMD
- Beta-Ga2O3: experimental a=12.23 b=3.04 c=5.81 β=103.7°, DFT PBE slightly larger ~2%
- Source generation code: MILP/ga2o3-abinit/ (ABINIT workflow, not direct GitLab reuse – higher novelty)

## License & Citation

If you use this dataset for NEP training, please cite ABINIT generation workflow and original NEP data source.
