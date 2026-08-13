"""
Test consistency of bulk, test, and Ga vacancy defect configs
TDD RED test – should FAIL for old defect_original_50_Ga_vac, PASS for new defect_Ga_vac_*
This test reproduces the high MLIP error due to inconsistent setup
"""
import re
import pathlib
import numpy as np
from pathlib import Path

PUBLIC = Path('/tmp/ga2o3-nep-data-public')
LOCAL = Path('/Users/luzi/Meta/MILP/ga2o3-abinit/data')

def load_frames(path):
    with open(path, errors='ignore') as f:
        lines=f.readlines()
    frames=[]
    i=0
    while i < len(lines):
        if not lines[i].strip():
            i+=1
            continue
        try:
            nat=int(lines[i].strip().split()[0])
        except:
            i+=1
            continue
        if i+1>=len(lines):
            break
        comment=lines[i+1]
        em=re.search(r'Energy=([-\d\.Ee\+]+)',comment)
        energy=float(em.group(1)) if em else None
        lm=re.search(r'Lattice="([^"]+)"',comment)
        lat=[float(x) for x in lm.group(1).split()] if lm else None
        atom_lines=lines[i+2:i+2+nat]
        pos=[]
        forces=[]
        species=[]
        for l in atom_lines:
            parts=l.split()
            if len(parts)<7: continue
            species.append(parts[0])
            pos.append([float(parts[1]),float(parts[2]),float(parts[3])])
            forces.append([float(parts[4]),float(parts[5]),float(parts[6])])
        frames.append({
            'nat':nat,
            'energy':energy,
            'lattice':np.array(lat).reshape(3,3) if lat else None,
            'species':species,
            'positions':np.array(pos),
            'forces':np.array(forces),
            'comment':comment
        })
        i+=2+nat
    return frames

def test_bulk_test_consistent_setup():
    """Bulk and test should be generated with same setup: similar energy vol, forces slightly higher for test but within tolerance"""
    bulk=load_frames(PUBLIC/'bulk_original_400.xyz')
    test=load_frames(PUBLIC/'test.xyz')
    assert len(bulk)==400, f"bulk frames {len(bulk)} !=400"
    assert len(test)==200, f"test frames {len(test)} !=200"
    bulk_mean=np.mean([f['energy'] for f in bulk])
    test_mean=np.mean([f['energy'] for f in test])
    # test mean within 1 eV of bulk (same reference)
    assert abs(bulk_mean-test_mean) < 1.0, f"bulk mean {bulk_mean} vs test mean {test_mean} diff >1 eV, inconsistent setup"
    # volume mean similar
    bulk_vol=np.mean([np.linalg.det(f['lattice']) for f in bulk])
    test_vol=np.mean([np.linalg.det(f['lattice']) for f in test])
    assert abs(bulk_vol-test_vol) < 20, f"vol diff {bulk_vol} vs {test_vol} >20, inconsistent"
    # forces mean similar
    bulk_f=np.mean([np.mean(np.linalg.norm(f['forces'],axis=1)) for f in bulk])
    test_f=np.mean([np.mean(np.linalg.norm(f['forces'],axis=1)) for f in test])
    assert abs(bulk_f-test_f) < 0.5, f"force mean diff bulk {bulk_f} test {test_f} >0.5"

def test_old_defect_inconsistent_energy_formation():
    """Old defect should have NEGATIVE formation (bug) – this test FAILS for new data (expected) and should PASS for old data showing bug"""
    bulk=load_frames(PUBLIC/'bulk_original_400.xyz')
    def_old=load_frames(PUBLIC/'defect_original_50_Ga_vac.xyz')
    bulk_mean=np.mean([f['energy'] for f in bulk])
    expected_159=159/160*bulk_mean
    def_old_mean=np.mean([f['energy'] for f in def_old])
    formation=def_old_mean-expected_159
    # Old defect has formation -2.07 eV (negative, unphysical) – this is the BUG
    # For new Ga vac, formation should be +2 to +7 eV positive
    # This test checks for NEGATIVE formation to reproduce bug – will FAIL for fixed data
    assert formation < 0, f"Old defect formation {formation:.2f} should be negative (bug reproduction), if positive, bug is fixed"

def test_old_defect_positions_no_relaxation():
    """Old defect positions exactly match bulk subset within 1e-3 A -> no relaxation, inconsistent"""
    bulk=load_frames(PUBLIC/'bulk_original_400.xyz')
    def_old=load_frames(PUBLIC/'defect_original_50_Ga_vac.xyz')
    # Find closest bulk frame by volume for first defect
    d0=def_old[0]
    b_closest=min(bulk,key=lambda f: abs(np.linalg.det(f['lattice'])-np.linalg.det(d0['lattice'])))
    matches=0
    tol=1e-3
    for dp in d0['positions'][:20]:
        dists=np.linalg.norm(b_closest['positions']-dp,axis=1)
        if np.min(dists)<tol:
            matches+=1
    # Old defect should have 20/20 matches (no relaxation) – bug
    assert matches==20, f"Expected old defect to have 20/20 exact matches (no relaxation) bug, got {matches}/20 – bug already fixed?"

def test_old_defect_forces_copied():
    """Old defect forces mean ≈ bulk mean (copied), should be higher for vacancy"""
    bulk=load_frames(PUBLIC/'bulk_original_400.xyz')
    def_old=load_frames(PUBLIC/'defect_original_50_Ga_vac.xyz')
    bulk_f=np.mean([np.mean(np.linalg.norm(f['forces'],axis=1)) for f in bulk])
    def_old_f=np.mean([np.mean(np.linalg.norm(f['forces'],axis=1)) for f in def_old])
    # Difference should be small (<0.05) for old buggy data (copied)
    assert abs(def_old_f-bulk_f) < 0.05, f"Old defect force mean {def_old_f:.3f} should be ≈ bulk {bulk_f:.3f} diff <0.05 indicating copying bug, got diff {abs(def_old_f-bulk_f):.3f}"

def test_new_Ga_vac_consistent_setup():
    """NEW Ga vac dedicated should be consistent: positive formation 2-7 eV, forces higher, local relaxation, tetra/oct markers, ABINIT provenance"""
    bulk=load_frames(PUBLIC/'bulk_original_400.xyz')
    def_new=load_frames(PUBLIC/'defect_Ga_vac_50.xyz')
    assert len(def_new)==50
    bulk_mean=np.mean([f['energy'] for f in bulk])
    expected_159=159/160*bulk_mean
    def_new_mean=np.mean([f['energy'] for f in def_new])
    formation=def_new_mean-expected_159
    # Formation should be positive 2-7 eV
    assert 2.0 < formation < 7.0, f"New Ga vac formation {formation:.2f} should be 2-7 eV positive, got {formation}"
    # Forces should be higher or at least similar but not identical, and header should have Ga_vac_type
    assert 'Ga_vac_type' in def_new[0]['comment'], "New Ga vac missing Ga_vac_type marker, inconsistent setup"
    assert 'Ga_coord' in def_new[0]['comment'], "Missing Ga_coord marker"
    # Check ABINIT provenance exists
    base=Path('/Users/luzi/Meta/MILP/ga2o3-abinit')
    inputs=list((base/'abinit_inputs/defect_Ga_vac_50').glob('*.abi'))
    logs=list((base/'abinit_logs/defect_Ga_vac_50').glob('*.log'))
    assert len(inputs)>=50, f"ABINIT inputs for Ga vac 50 missing {len(inputs)}"
    assert len(logs)>=50, f"ABINIT logs for Ga vac 50 missing {len(logs)}"
    # Positions should NOT exactly match bulk (relaxation)
    b_closest=min(bulk,key=lambda f: abs(np.linalg.det(f['lattice'])-np.linalg.det(def_new[0]['lattice'])))
    matches=0
    tol=1e-3
    for dp in def_new[0]['positions'][:20]:
        dists=np.linalg.norm(b_closest['positions']-dp,axis=1)
        if np.min(dists)<tol:
            matches+=1
    # Should NOT be 20/20 exact (should have relaxation breaking exact match)
    assert matches < 15, f"New Ga vac should have relaxation, expected <15 exact matches, got {matches}/20 – still copying?"

def test_Ga_vac_tetra_oct_classification():
    """Ga vac should have balanced tetra/oct classification 32 each in supercell, 25/25 in 50 file"""
    from collections import Counter
    # Check log files for tetra/oct
    base=Path('/Users/luzi/Meta/MILP/ga2o3-abinit/abinit_logs/defect_Ga_vac_50')
    logs=list(base.glob('*.log'))
    tetra=0
    octt=0
    for log in logs:
        text=log.read_text(errors='ignore')
        if 'Ga_tetra' in text:
            tetra+=1
        if 'Ga_oct' in text:
            octt+=1
    # Each log may contain both? Count files containing tetra vs oct
    # More accurate: count XYZ header markers
    def_new=load_frames(PUBLIC/'defect_Ga_vac_50.xyz')
    header_tetra=sum(1 for f in def_new if 'Ga_tetra' in f['comment'])
    header_oct=sum(1 for f in def_new if 'Ga_oct' in f['comment'])
    assert header_tetra==25 and header_oct==25, f"Ga vac 50 should be 25 tetra +25 oct balanced, got tetra {header_tetra} oct {header_oct}"

if __name__=='__main__':
    import sys
    print("Run with: /usr/bin/python3 -m pytest tests/test_consistency.py -v")

def test_old_defect_should_be_consistent_but_fails():
    """This is the RED test that SHOULD pass if defect is consistent with bulk/test setup – it will FAIL for old defect, demonstrating high MLIP error root cause. After fix (using new Ga vac), it should PASS."""
    bulk=load_frames(PUBLIC/'bulk_original_400.xyz')
    def_old=load_frames(PUBLIC/'defect_original_50_Ga_vac.xyz')
    bulk_mean=np.mean([f['energy'] for f in bulk])
    expected_159=159/160*bulk_mean
    def_old_mean=np.mean([f['energy'] for f in def_old])
    formation=def_old_mean-expected_159
    # Consistent defect should have formation 2-7 eV positive
    assert 2.0 < formation < 7.0, f"Defect formation {formation:.2f} should be 2-7 eV positive for consistent setup – OLD DATA FAILS with negative formation, causing high MLIP error"

