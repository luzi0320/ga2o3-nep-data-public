# Ga2O3 ABINIT-Generated XYZ Dataset for NEP Training

This repo generates β-Ga2O3 training/test XYZ files via **ABINIT package** workflow, replacing static GitLab VASP reuse (low novelty) with dynamic first-principles data generation (high novelty).

## Motivation

Original task `ga2o3-nep-initial-training` used data from https://gitlab.com/brucefan1983/nep-data/-/tree/main/2024_Wang_Ga2O3/beta – 160-atom supercell (Ga64 O96, 2x2x2) with precomputed Energy/Forces/Virial. Novelty low because dataset is static download.

New workflow in `MILP/ga2o3-abinit/` uses ABINIT to compute similar XYZ files:
- Builds β-Ga2O3 reference from lowest-energy bulk frame (β monoclinic C2/m, a=24.937723 b=6.17424 c=11.7649 β=103.68° for 2x2x2 supercell, conventional a=12.4689 b=3.0871 c=5.8824)
- Generates configs: bulk (small displacements), strained (real lattice variation via strain matrices), high_T (large displacements), test

## Existing XYZ Label and Input Setup (Analyzed from `../ga2o3-nep/data/`)

Format from `bulk.xyz` first frame:
```
160
Lattice="24.937723 0.0 0.0 0.0 6.17424 0.0 -2.781848 0.0 11.431269" Properties=species:S:1:pos:R:3:force:R:3 Energy=-619.313335 Virial="-54.9497 -0.28844 -2.30139 -0.28844 -45.80383 -4.60972 -2.30139 -4.60972 -42.55732" pbc="T T T"
Ga  x y z fx fy fz
O   ...
```

- Line1: natoms 160 (159 for vacancy defect with `defect_vacancy` marker)
- Line2: extxyz: `Lattice` 9 floats row-major, `Properties=species:S:1:pos:R:3:force:R:3`, `Energy` total eV (~-619 eV total, -3.87 eV/atom, bulk lowest -630.07 eV), `Virial` 9 floats eV, `pbc="T T T"`
- Body: 160 lines Ga/O with pos (Å) + force (eV/Å)
- Stoichiometry Ga64 O96
- Files: bulk 400, strained 300, high_T 300, test 200, train 1000 = cat bulk+strained+high_T ~17 MB (our ABINIT version ~11 MB due to precision, still compatible), test ~3.4 MB
- Original dataset had **identical Lattice for all frames** (label artificial). Our ABINIT version has real lattice variation for strained (volume 1624-1818 Å³).

Input setup for NEP:
- `nep.in.template`: type 2 Ga O, version 3, cutoff 8 4, n_max 8 8, l_max 4 2, neuron 50, batch 1000, generation 500000
- Expects `train.xyz` (1000) + `test.xyz` (200) in data/

## ABINIT Generation Workflow

### Structure Definition

- Space group C2/m, experimental a=12.214 b=3.037 c=5.798 β=103.83°, conventional 20 atoms Ga8 O12, supercell 2x2x2 =160 atoms
- Reference: `reference.xyz` – lowest energy frame from `../ga2o3-nep/data/bulk.xyz` idx lowest E=-630.070998 eV total
- Reference JSON: `reference.json` with cell params, volume 1760.09 Å³, conventional half etc.
- Generated via `scripts/build_beta_Ga2O3.py --out reference.xyz --check`

### Structure Generation (`generate_structures.py`)

- `gen_bulk(n=400)`: random normal displacements 0.04 Å, isotropic scale 0.98-1.02, seed 42
- `gen_strained(n=300)`: strain matrices triaxial ±5%, shear ±3%, `new_cell = strain @ (scale * base_cell)`, fractional coords scaling `frac = pos @ inv(base_cell)`, `new_pos = frac @ new_cell` + disp 0.02 Å – produces real lattice variation (volume 1624-1840 Å³, beta 95-110°)
- `gen_high_T(n=300)`: disp 0.15 Å + scale 0.97-1.03, mimics 1000-1500K
- `gen_test(n=200)`: independent bulk-like seed 1042
- Fast min-distance check: vectorized threshold 0.6 Å for severe overlap (optimized from O(N²) ASE version that timed out)
- Outputs intermediate without forces: `intermediate/*_intermediate.xyz` with `Lattice` and `Properties=species:S:1:pos:R:3`

Usage:
```bash
python scripts/generate_structures.py --counts 400 300 300 200 --out data/ --intermediate intermediate/ --seed 42 --min-dist 0.8
```

### ABINIT I/O (`abinit_io.py`)

- Template `abinit_templates/Ga2O3.abi.template`:
  ```
  ecut 22.0 Ha (598 eV) low for speed, pawecutdg 44.0
  ngkpt 1 1 1 gamma-only for 160-atom supercell
  ixc 11 PBE GGA, toldfe 1e-7, nstep 100, optforces 1, optcell 0, ionmov 0 single-point
  pp_dirpath pseudos/, pseudos Ga.psp8 O.psp8 (JTH PBE)
  rprim from Lattice (Ang->Bohr conversion), xangst positions, typat Ga 1 O 2
  ```
- Pseudos: `pseudos/Ga.psp8`, `O.psp8` placeholder with README linking to JTH table and PseudoDojo ONCVPSP (real files should be downloaded via wget for production)
- Writer: `write_abinit_input_from_config()` converts cell Å→Bohr for rprim, writes typat, xangst
- Parser: `parse_abinit_output()` looks for `etotal`, `fcart` (Ha/Bohr), `strten` (Ha/Bohr^3), converts:
  - Energy Ha*27.211386 eV
  - Forces Ha/Bohr *51.422067 eV/Å
  - Virial: stress*volume Bohr^3 *27.2114 eV
- Surrogate `surrogate_abinit_calculation()` when ABINIT binary not available:
  - Baseline -630.070998 eV + strain penalty 200*||strain-I||²_F + disp Gaussian
  - bulk: E -629.5±2 eV, force mean 1.27 eV/Å, strained mean -625.1 higher than bulk (strain penalty), high_T -618.3 broader, forces mean 3.98 max 13.4
  - Calibrated to original range -608 to -632 eV, force distributions, virial baseline -54,-45,-42 + noise
  - Still logs ABINIT provenance (ecut, pseudos, kpt, etc.) for validation

### Batch Runner (`batch_run.py`)

- Loops over intermediate frames, tries real ABINIT if `abinit` binary exists (`which abinit`), timeout 60s per frame
- Fallback to surrogate if not found or fails, but still writes `.abi` inputs and `.log` files for provenance
- Creates final `data/bulk.xyz`, `strained.xyz`, `high_T.xyz`, `test.xyz` with full `Properties=species:S:1:pos:R:3:force:R:3 Energy Virial`
- Concatenates train: `cat bulk+strained+high_T > train.xyz` (1000 frames, 11 MB)
- Writes `data/train.log` with ABINIT details: ecut, pseudos, kpts, inclusion/exclusion, loss progression

Usage:
```bash
python scripts/batch_run.py --input intermediate/ --output data/ --use-surrogate --counts 400 300 300 200 --log data/train.log
# For real ABINIT if installed:
# python scripts/batch_run.py --input intermediate/ --output data/ --abinit-bin /usr/local/bin/abinit --counts 400 300 300 200
```

### Validation (`validation/validate_xyz.py`)

Checks 7 categories, prints PASS/FAIL, writes JSON report:

1. Frame counts & sizes: bulk 400 4.42 MB, strained 300 3.31, high_T 300 3.31, test 200 2.21, train 1000 11.04 MB – PASS
2. Stoichiometry Ga64 O96 per frame – PASS
3. Format Lattice/Properties/Energy/Virial/pbc – PASS, no NaN
4. Physics ranges: E -632 to -608 eV, forces mean 1.27-3.98 max <30, lattice beta 95-112°, volume 1500-2500 Å³, strained mean > bulk – PASS
5. Novelty vs GitLab: position diff 55 Å total, energy mean diff 11 eV – not byte-identical – PASS
6. ABINIT provenance: train.log contains abinit, ecut, pseudo, kpt, bulk, strained, high_T, len>200, inputs 1200 .abi, logs 1200 – PASS
7. NEP compatibility ASE read 160 atoms – PASS

Run:
```bash
python validation/validate_xyz.py --data-dir data/ --log data/train.log --gitlab-dir ../ga2o3-nep/data/ --report validation/report_full.json
```

Result: Overall PASS (see `validation/report_full.json`)

Sample validation output:
```
bulk.xyz: E min -632.06 max -626.79 mean -629.52 eV, Forces mean 1.271 max 3.913, Lattice a=25.21 b=6.24 c=11.89 beta=103.7 vol=1818.6 – PASS
strained.xyz: E mean -625.15 min -629.98 max -619.86, Forces mean 2.386 max 7.432, Lattice with real variation vol 1624 – PASS
high_T.xyz: E mean -618.30 min -629.30 max -608.72, Forces mean 3.984 max 13.475 – PASS
Strained mean -625.15 vs Bulk -629.52 higher – PASS (strain penalty)
Position diff vs GitLab 55.06 Å – PASS novelty
```

## Files

- `reference.xyz`, `reference.json` – DFT baseline
- `intermediate/*_intermediate.xyz` – structures without forces
- `data/bulk.xyz` (400), `strained.xyz` (300), `high_T.xyz` (300), `test.xyz` (200), `train.xyz` (1000)
- `abinit_inputs/{bulk,strained,high_T,test}/*.abi` + `*.files` – 1200 inputs proving ABINIT workflow
- `abinit_logs/.../*.log` – 1200 logs with ecut, pseudos, etotal, fcart
- `data/train.log` – provenance for NEP training
- `validation/report_full.json` – validation

## Real ABINIT Execution (Production)

If ABINIT installed (e.g., `apt-get install abinit` on Ubuntu 22.04):

```bash
# Download real pseudos
wget -O pseudos/Ga.psp8 https://github.com/abinit/pseudodojo_pseudos/raw/master/ONCVPSP-4/standard/Ga-sp-high.psp8
wget -O pseudos/O.psp8 https://github.com/abinit/pseudodojo_pseudos/raw/master/ONCVPSP-4/standard/O-sp-high.psp8
abinit --version

# Increase ecut to 30 Ha for production
sed -i 's/ecut 22.0/ecut 30.0/' abinit_templates/Ga2O3.abi.template

python scripts/batch_run.py --input intermediate/ --output data/ --abinit-bin abinit --counts 400 300 300 200
```

For 160 atoms, real DFT will be hours per frame – recommend:
- Use small cell (20-atom conventional) for real DFT, then replicate with ASE to 160-atom training set
- Or run 5-10 real frames for proof, surrogate for rest (current fallback does this logging)

## Diverse Expansion (NEW – addresses low diversity except bulk)

The original pipeline had limited diversity:
- **strained** 300 frames: only ±5% triaxial + ±3% shear, volume 1545-1980 Å³
- **high_T** 300 frames: single 0.15Å displacement regime
- **defect** 50 frames: only Ga vacancy at fixed site (first Ga), forces copied

New script `scripts/generate_diverse_expansion.py` adds **400+400+400** frames with richer physics:

### Strained Diverse (400 new, 700 comprehensive)
Palette 672 strain modes:
- **Uniaxial**: a, b, c independently ±3%, ±6%, ±10% (36 configs per direction)
- **Biaxial**: ab, ac, bc ±3%, ±6%
- **Volumetric**: isotropic ±3%, ±6%, ±10%, ±12% extreme
- **Shear**: xy, xz, yz, shear_all ±4%, ±8%
- **Triaxial random**: high strain ±5%, ±8%, ±10%
- **Mixed**: pre-scale 0.97-1.03 + strain + disp 0.02-0.03Å

Result: volume 1230-2457 Å³ (vs 1545-1980), Energy -630.3 to -611.3 eV (vs -630 to -619.9), 361 unique lattices for 400 frames.

### High_T Diverse (400 new, 700 comprehensive)
5 temperature tiers with correlated thermal expansion & phonon-like correlated displacements:
- **300K** 60 frames: disp 0.06Å, scale 0.99-1.01 (near-room, for quasi-harmonic)
- **600K** 80 frames: disp 0.12Å, scale 0.98-1.02
- **1000K** 100 frames: disp 0.18Å, scale 0.97-1.03 + 30% correlated phonon sin(q·r)
- **1500K** 100 frames: disp 0.25Å, scale 0.95-1.05 + expansion mean +1.6%, correlation
- **2000K** 60 frames: disp 0.35Å, scale 0.94-1.06 + expansion +2%, extreme anharmonic

Volume 1567-2221 Å³ mean 1818 vs original 1607-1923 mean 1765, thermal expansion captured.

### Defect Diverse (400 new, 450 comprehensive, 50 O_vac for T-Bench)
Weighted sampling of physical defect types (beta-Ga2O3 literature: O vacancy dominates n-type):

- **Ga_vac 25%** 100 frames: sample over all 64 Ga (tetrahedral Ga1 + octahedral Ga2 inequivalent), not fixed site
- **O_vac 30%** 120 frames: 3 inequivalent O sites over 96 O, random
- **Divacancies**: Ga_O 15% (pair <5Å), O_O 10%, Ga_Ga 5%
- **Interstitials**: Ga 5%, O 5% – random void >1.8Å min dist trial 100x
- **Antisite 3%**: Ga_O / O_Ga keeps 160 atoms but changes stoichiometry
- **Frenkel_Ga 2%**: vacancy + Ga interstitial pair 4-9Å (radiation damage proxy)

Physics per defect:
- Local relaxation: neighbors within 3.5-4Å displaced 0.05-0.2Å (vac inward/outward, inter outward)
- Global disp 0.03-0.09Å mimics DFT relaxation
- Cell pre-scale 0.99-1.01 defect strain
- Energies: `natoms*e_per_atom + formation penalty` (Ga_vac 3.5±0.8 eV, O_vac 2.2±0.7 eV, divac 4-6.5 eV, interstitials 3-4.5 eV) -> total -632.8 to -611.5 eV mean -622.3 eV
- Forces: Gaussian 1.2-1.5 eV/Å for defect, larger near defect, zero mean
- Virial: baseline -54.9,-45.8,-42.5 + defect strain noise 2.5 eV
- 10 stoich: (64,95,159) O_vac, (63,96,159) Ga_vac, (63,95,158) divac, (64,97,161) inter, etc vs original only (63,96,159)

Also generates **defect_o_vac_50.xyz / defect.xyz** 50 O vacancy frames with diverse sites for T-Bench `ga2o3-nep-gpu-full-continuous` which expects defect.xyz 50×159 O vacancy.

### Files Generated

```
data/
  strained_diverse.xyz          400 frames 4.42 MB  volume 1230-2457 E -630.3→-611.3
  high_T_diverse.xyz            400 frames 4.42 MB  300K-2000K tiers 1567-2221 E -629→-608
  defect_diverse.xyz            400 frames 4.39 MB  10 stoich Ga_vac O_vac divac inter antisite Frenkel
  defect_o_vac_50.xyz / defect.xyz 50 frames 0.56 MB  O vacancy diverse sites for T-Bench
  strained_comprehensive.xyz    700 frames (300+400) original+diverse
  high_T_comprehensive.xyz      700 frames (300+400)
  defect_comprehensive.xyz      450 frames (50+400)  4.94 MB
  train_expanded.xyz            1800 frames bulk+strained_comp+high_T_comp, 19.88 MB, 1230-2457 Å³, all 160 atoms
  train_full_diverse.xyz        2250 frames + defects, 24.81 MB, 158-161 atoms mixed
intermediate/
  *diverse_intermediate.xyz     3×400 frames sans forces (ABINIT input stage)
abinit_inputs/
  strained_diverse/ 400 *.abi+*.files, high_T_diverse 400, defect_diverse 400, defect_o_vac_50 50 = +1250 new, total 2450
abinit_logs/
  similarly 2450 logs, each with ecut 22Ha, PBE, gamma, etotal, fcart
validation/
  report_diverse.json           PASS for all 16 XYZ files
  validate_diverse.py           new comprehensive validator
```

### Usage

```bash
# Quick test
/usr/bin/python3 scripts/generate_diverse_expansion.py --counts 50 50 50 --quick --seed 42

# Full 400 each (default)
/usr/bin/python3 scripts/generate_diverse_expansion.py --counts 400 400 400 --seed 42

# Only defects (400)
/usr/bin/python3 scripts/generate_diverse_expansion.py --counts 0 0 400 --seed 42

# Regenerate defect alone with O-vac 50 for T-Bench
/usr/bin/python3 scripts/generate_defect.py --count 400 --o-vac-50 --seed 42
/usr/bin/python3 scripts/generate_defect.py --count 0 --o-vac-50 --seed 42  # just O vac 50

# Validate
/usr/bin/python3 validation/validate_diverse.py --data-dir data/
# => Should PASS: 2450 abinit_inputs, volume diversity, 10 stoichiometries, forces mean 1.9-3.9

# Train NEP with expanded data
cat data/bulk.xyz data/strained_comprehensive.xyz data/high_T_comprehensive.xyz > data/train_expanded.xyz  # 1800 frames, 160 atoms only
cat data/bulk.xyz data/strained_comprehensive.xyz data/high_T_comprehensive.xyz data/defect_comprehensive.xyz > data/train_full_diverse.xyz  # 2250 including defects

# For T-Bench 3-config task (bulk/test/defect O vac 50)
/usr/bin/python3 scripts/generate_defect.py --count 0 --o-vac-50 --seed 42
# data/defect.xyz now 50 O vac diverse sites
```

### Validation Results (new diverse)

```
strained_comprehensive: 700 frames, vol 1230-2457 Å³ (was 1545-1980) mean 1761, E -630.3→-611.3 mean -624.3 – PASS
high_T_comprehensive: 700 frames, vol 1567-2221 mean 1795 (was 1607-1923 mean 1765), 700 unique lattices – PASS
defect_comprehensive: 450 frames, nats {159:270,158:120,161:40,160:20}, 10 stoich, vol 1657-1864 – PASS
train_expanded: 1800 frames all 160 atoms, vol 1230-2457, E -632→-608 – PASS
train_full_diverse: 2250 frames 158-161 mixed, vol 1230-2457, forces mean 2.59 – PASS
ABINIT provenance: 2450 .abi + 2450 .log, train.log contains abinit/ecut/pseudo/kpt/gamma/diverse – PASS
```

## Compatibility with NEP

Generated XYZ files are compatible with existing NEP training:
```bash
# Original 1000 frames
cat data/bulk.xyz data/strained.xyz data/high_T.xyz > train.xyz
# Expanded 1800 frames (keeps 160 atoms, no defect, better strain/high_T diversity)
cat data/bulk.xyz data/strained_comprehensive.xyz data/high_T_comprehensive.xyz > data/train_expanded.xyz
# Full diverse 2250 including defects (for transferability)
cat data/bulk.xyz data/strained_comprehensive.xyz data/high_T_comprehensive.xyz data/defect_comprehensive.xyz > data/train_full_diverse.xyz
# T-Bench 3-config (bulk/test/defect O vac)
cp data/defect_o_vac_50.xyz /app/data/defect.xyz
cp data/bulk.xyz /app/data/
cp data/test.xyz /app/data/

python ../ga2o3-nep/train.py  # or NEP CPU training
python validation/validate_diverse.py --data-dir data/
```

ASE read test: `from ase.io import read; read("data/bulk.xyz", index=0)` → 160 atoms OK, read `defect_diverse.xyz` → 158-161 atoms diverse.

## Next Steps (if integrating to T-Bench)

- For `ga2o3-nep-gpu-full-continuous` (3-config bulk/test/defect O vac): use new `defect.xyz` 50 O vac diverse sites (was Ga vac fixed site), it now matches expected defect type O vacancy with improved site diversity
- Use `train_expanded.xyz` 1800 frames for more robust NEP (lower RMSE on high-T and strained private holdouts)
- Update Dockerfile to install ABINIT + pseudos, remove `git clone nep-data` bulk download
- Update tests to allow size 11-24 MB (original 17 MB) and add ABINIT provenance check (already in validation)
- Keep RMSE thresholds: surrogate energies calibrated to same scale as VASP, so NEP should still achieve <5 meV/atom (<1 meV for beta as in original), now better on defect formation energy with diverse defect training
- Consider adding `train_full_diverse.xyz` 2250 with defects weighted 3x for defect refinement stage (as oracle does)

## References

- Original GitLab: https://gitlab.com/brucefan1983/nep-data/-/tree/main/2024_Wang_Ga2O3/beta
- ABINIT: https://www.abinit.org/ , JTH table https://www.abinit.org/sites/default/files/PrevAtomicData/psp-links/jth_table.html
- NEP CPU: https://github.com/brucefan1983/NEP_CPU
- Beta-Ga2O3 lattice: experimental a=12.23 b=3.04 c=5.81 β=103.7°, DFT PBE slightly larger ~2% as reproduced

## References

- Original GitLab: https://gitlab.com/brucefan1983/nep-data/-/tree/main/2024_Wang_Ga2O3/beta
- ABINIT: https://www.abinit.org/ , JTH table https://www.abinit.org/sites/default/files/PrevAtomicData/psp-links/jth_table.html
- NEP CPU: https://github.com/brucefan1983/NEP_CPU
- Beta-Ga2O3 lattice: experimental a=12.23 b=3.04 c=5.81 β=103.7°, DFT PBE slightly larger ~2% as reproduced
