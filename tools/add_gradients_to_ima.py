#!/usr/bin/env python3
import argparse, os, math

def read_bvec(path):
    with open(path, "r") as f:
        lines = [l.strip() for l in f if l.strip()]
    # Allow 3xN or Nx3 formats
    vals = []
    if len(lines) == 3:
        rows = [list(map(float, l.split())) for l in lines]
        N = len(rows[0])
        for i in range(N):
            vals.append([rows[0][i], rows[1][i], rows[2][i]])
    else:
        for l in lines:
            toks = l.split()
            if len(toks) >= 3:
                vals.append(list(map(float, toks[:3])))
    return vals

def read_bval(path):
    try:
        with open(path, "r") as f:
            nums = [float(x) for x in f.read().strip().split()]
        return nums
    except Exception:
        return []

def normalize(v):
    x,y,z = v
    n = math.sqrt(x*x + y*y + z*z)
    if n == 0: return [0.0,0.0,0.0]
    return [x/n, y/n, z/n]

def write_minf(minf_path, orientations, bvals):
    # Compute a representative shell b-value (mode of non-zero)
    nz = [b for b in bvals if b > 1e-3]
    if nz:
        # mode-ish: pick the most frequent rounded value
        from collections import Counter
        c = Counter([round(b,0) for b in nz])
        b_shell = float(c.most_common(1)[0][0])
    else:
        b_shell = 0.0

    # Normalize orientations (DWI code often expects unit vectors)
    ori = [normalize(v) for v in orientations]

    # Build optional motion list (zeros) to match orientation count
    zeros = ", ".join("[ 0, 0, 0 ]" for _ in ori)
    ori_txt = ", ".join(f"[ {v[0]:.6g}, {v[1]:.6g}, {v[2]:.6g} ]" for v in ori)

    text = f"""attributes = {{
    'diffusion_gradient_orientations' : [ {ori_txt} ],
    'diffusion_sensitization_parameters' : {{
        'b-value' : {b_shell:.6g},
        'gradient-characteristics' : {{
            'type' : 'unknown'
        }},
        'homogeneous-transform3d' : [ 1, 0, 0, 0,
                                      0, 1, 0, 0,
                                      0, 0, 1, 0,
                                      0, 0, 0, 1 ],
        'motion-rotation3ds' : [ {zeros} ],
        'orientation-count' : {len(ori)},
        'orientations' : [ {ori_txt} ]
    }},
    'diffusion_sensitization_type' : 'spherical_single-shell_custom'
}}
"""
    with open(minf_path, "w") as f:
        f.write(text)

def main():
    ap = argparse.ArgumentParser(description="Inject gradients into GIS .ima.minf")
    ap.add_argument("--ima",  required=True, help="Path to DWI shell .ima")
    ap.add_argument("--bvec", required=True, help="Path to corresponding .bvec")
    ap.add_argument("--bval", required=False, help="Path to corresponding .bval (better output if provided)")
    args = ap.parse_args()

    bvecs = read_bvec(args.bvec)
    bvals = read_bval(args.bval) if args.bval else [0.0]*len(bvecs)

    if len(bvals) != len(bvecs):
        # pad/trim to match (some exporters store only shell nonzero in bval)
        if len(bvals) < len(bvecs):
            bvals = (bvals + [0.0]*len(bvecs))[:len(bvecs)]
        else:
            bvals = bvals[:len(bvecs)]

    minf_path = args.ima + ".minf"
    write_minf(minf_path, bvecs, bvals)
    print(f"[add_gradients_to_ima] wrote {minf_path}  (N={len(bvecs)})")

if __name__ == "__main__":
    main()
