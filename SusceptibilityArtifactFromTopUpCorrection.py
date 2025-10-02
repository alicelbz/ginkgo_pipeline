# SusceptibilityArtifactFromTopUpCorrection.py
import os, json
from core.command.CommandFactory import *
from CopyFileDirectoryRm import *

FSL_PREFIX = os.environ.get("FSL_PREFIX", "").strip()
def _fsl(cmd):
    # run FSL command either on host or via container prefix
    full = f"{FSL_PREFIX} {cmd}" if FSL_PREFIX else cmd
    print(full); _fsl(full)

def _safe_load_json(p):
    try:
        with open(p, "r") as f:
            return json.load(f)
    except Exception:
        return {}

def _vec_from_pe(phase_dir):
    """
    BIDS PhaseEncodingDirection → topup PE vector.
    'i'/'i-' → (±1,0,0), 'j'/'j-' → (0,±1,0), 'k'/'k-' → (0,0,±1)
    """
    if not phase_dir:
        raise ValueError("PhaseEncodingDirection manquante")
    axis = phase_dir[0]
    sign = -1 if phase_dir.endswith('-') else 1
    if axis == 'i': return ( 1*sign, 0, 0)
    if axis == 'j': return ( 0, 1*sign, 0)
    if axis == 'k': return ( 0, 0, 1*sign)
    raise ValueError(f"PhaseEncodingDirection inconnue: {phase_dir}")

def runTopUpCorrection(
    subjectDirectoryNiftiConversion,   # ex: .../data_in/sub-PR08/ses-20250723
    outputDirectory,                   # ex: .../results/sub-PR08/ses-.../01-DistortionCorrection
    verbose
):
    """
    Utilise deux EPI b0 opposés (AP/PA) placés dans:
      <session>/fmap/AP.nii.gz + AP.json  (PhaseEncodingDirection p.ex. 'j-')
      <session>/fmap/PA.nii.gz + PA.json  (PhaseEncodingDirection p.ex. 'j')

    Corrige le 4D DWI:
      <session>/dwi/dwi.nii.gz  ->  <output>/dwi_dc.nii.gz
    """

    if verbose:
        print("SUSCEPTIBILITY ARTIFACT CORRECTION FROM TOPUP")
        print("-------------------------------------------------------------")

    os.makedirs(outputDirectory, exist_ok=True)

    fmap_dir = os.path.join(subjectDirectoryNiftiConversion, "fmap")
    dwi_dir  = os.path.join(subjectDirectoryNiftiConversion, "dwi")
    ap_nii   = os.path.join(fmap_dir, "AP.nii.gz")
    pa_nii   = os.path.join(fmap_dir, "PA.nii.gz")
    ap_json  = os.path.join(fmap_dir, "AP.json")
    pa_json  = os.path.join(fmap_dir, "PA.json")
    dwi_4d   = os.path.join(dwi_dir, "dwi.nii.gz")
    dwi_json = os.path.join(dwi_dir, "dwi.json")  # si disponible

    # Garde-fous
    if not (os.path.isfile(ap_nii) and os.path.isfile(pa_nii)
            and os.path.isfile(ap_json) and os.path.isfile(pa_json)):
        print(f"[WARN] AP/PA introuvables dans {fmap_dir}; topup ignoré.")
        return

    if not os.path.isfile(dwi_4d):
        print(f"[WARN] DWI 4D introuvable: {dwi_4d}; topup ignoré.")
        return

    # Charger metadonnées
    ap = _safe_load_json(ap_json)
    pa = _safe_load_json(pa_json)
    ap_dir = ap.get("PhaseEncodingDirection")
    pa_dir = pa.get("PhaseEncodingDirection")
    ap_trt = float(ap.get("TotalReadoutTime", 0))
    pa_trt = float(pa.get("TotalReadoutTime", 0))

    if verbose:
        print(f"AP: dir={ap_dir}  TRt={ap_trt}")
        print(f"PA: dir={pa_dir}  TRt={pa_trt}")

    # Construire acqparams (ordre = AP puis PA)
    pe_ap = _vec_from_pe(ap_dir)
    pe_pa = _vec_from_pe(pa_dir)
    acqparams = os.path.join(outputDirectory, "top_up_acquisition_parameters.txt")
    with open(acqparams, "w") as fp:
        fp.write(f"{pe_ap[0]} {pe_ap[1]} {pe_ap[2]} {ap_trt:.6f}\n")
        fp.write(f"{pe_pa[0]} {pe_pa[1]} {pe_pa[2]} {pa_trt:.6f}\n")

    # Merge AP/PA (ordre cohérent avec acqparams)
    merged = os.path.join(outputDirectory, "topup_references")
    cmd_merge = f"fslmerge -t {merged} {ap_nii} {pa_nii}"
    print(cmd_merge); _fsl(cmd_merge)

    # topup
    topup_base = os.path.join(outputDirectory, "top_up_transformation")
    cmd_topup = (
        f"topup --imain={merged} "
        f"--datain={acqparams} "
        f"--config=b02b0.cnf --out={topup_base} -v"
    )
    print(cmd_topup); _fsl(cmd_topup)

    # Choix de inindex selon la polarité du DWI principal
    dwi_dir_flag = None
    dj = _safe_load_json(dwi_json) if os.path.isfile(dwi_json) else {}
    dwi_dir_flag = dj.get("PhaseEncodingDirection")
    # Si le DWI a même PE que AP.json → inindex=1 ; s'il a la PE de PA.json → inindex=2
    # Sinon, par défaut: 1
    if dwi_dir_flag == ap_dir:
        inindex = 1
    elif dwi_dir_flag == pa_dir:
        inindex = 2
    else:
        inindex = 1
        if verbose:
            print(f"[INFO] DWI PhaseEncodingDirection={dwi_dir_flag} inconnu/absent; inindex=1 par défaut.")

    # Appliquer au 4D DWI
    corrected = os.path.join(outputDirectory, "dwi_dc.nii.gz")  # <- nom attendu par la nouvelle pipeline
    cmd_apply = (
        f"applytopup --imain={dwi_4d} "
        f"--datain={acqparams} --inindex={inindex} "
        f"--topup={topup_base} --method=jac --interp=spline "
        f"--out={corrected} --verbose"
    )
    print(cmd_apply); _fsl(cmd_apply)

    # (Optionnel) conversion GIS immédiate — pas nécessaire car on convertira par shell après eddy+split.
    # Je la laisse pour compat, mais OK de la commenter si tu préfères.
    try:
        corrected_gis = os.path.join(outputDirectory, "dwi_dc.ima")
        CommandFactory().executeCommand({
            "algorithm": "Nifti2GisConverter",
            "parameters": {
                "fileNameIn": str(corrected),
                "fileNameOut": str(corrected_gis),
                "outputFormat": "gis",
                "ascii": False,
                "verbose": verbose,
            },
            "verbose": verbose,
        })
        removeMinf(corrected_gis)
    except Exception as e:
        # Ne bloque pas la pipeline si conversion GIS immédiate échoue.
        print(f"[WARN] Nifti2GisConverter a échoué (optionnel): {e}")

    if verbose:
        print("-------------------------------------------------------------")
