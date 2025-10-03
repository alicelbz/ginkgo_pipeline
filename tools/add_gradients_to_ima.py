#!/usr/bin/env python3
import argparse, os

def read_bvec(path):
    rows = [list(map(float, ln.split())) for ln in open(path) if ln.strip()]
    if len(rows) >= 3 and all(len(r) == len(rows[0]) for r in rows[:3]):
        # standard .bvec format: 3 rows (x,y,z)
        return [list(v) for v in zip(*rows[:3])]
    # fallback: one vector per line
    return [list(map(float, ln.split())) for ln in open(path) if ln.strip()]

def read_bval(path, n):
    vals = [float(x) for x in open(path).read().split()]
    if len(vals) == 1:        # single value -> replicate
        vals = [vals[0]] * n
    return vals

def write_minfs(ima_path, attrs):
    base, ext = os.path.splitext(ima_path)         # /.../DWI_b0500 , .ima
    body = "attributes = " + repr(attrs) + "\n"
    for p in (base + ".dim.minf", base + ".minf", ima_path + ".minf"):
        with open(p, "w") as f:
            f.write(body)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ima",  required=True)
    ap.add_argument("--bvec", required=True)
    ap.add_argument("--bval", required=False)
    ap.add_argument("--shell_bvalue", type=float, default=None,
                    help="Force this shell b for all volumes if --bval not provided")
    args = ap.parse_args()

    grads = read_bvec(args.bvec)
    n = len(grads)
    if args.bval:
        bvals = read_bval(args.bval, n)
    elif args.shell_bvalue is not None:
        bvals = [args.shell_bvalue] * n
    else:
        raise SystemExit("No b-values provided. Use --bval or --shell_bvalue")

    # legacy block expected by DwiTensorField
    legacy = {
        "b-value": bvals[0] if n else 0.0,
        "gradient-characteristics": {"type": "unknown"},
        "homogeneous-transform3d":  [1,0,0,0,  0,1,0,0,  0,0,1,0,  0,0,0,1],
        "motion-rotation3ds":       [[0,0,0]] * n,
        "orientation-count":        n,
        "orientations":             grads,
    }
    attrs = {
        "diffusion_gradient_orientations": grads,
        "diffusion_b_values":              bvals,
        "diffusion_sensitization_parameters": legacy,
        "diffusion_sensitization_type":   "spherical_single-shell_custom",
    }
    write_minfs(args.ima, attrs)
    print(f"[add_gradients_to_ima] wrote {os.path.splitext(args.ima)[0]}.dim.minf (N={n})")

if __name__ == "__main__":
    main()
