import glob, os, shutil
from spynoza.filtering.nodes import savgol_filter
from spynoza.conversion.nodes import percent_signal_change
import nibabel as nb
import numpy as np

TR = 1.6
polyorder=3
deriv=0
window_length=201

base_dir = '/home/shared/2018/visual/seq_test/prf_lyon/derivatives'
wildcard = 'fmriprep/sub-01/func/sub-01_task-prf_dir-*-preproc_bold.nii.gz'

nii_files = glob.glob(os.path.join(base_dir, wildcard))

# create parallel folder structure for post-preprocessing
os.makedirs(os.path.split(os.path.join(base_dir, wildcard))[0].replace('fmriprep', 'pp'))

for niif in nii_files:
    print('filtering the data')
    sg_nii = savgol_filter(in_file=niif, polyorder=polyorder, deriv=deriv, window_length=window_length, tr=TR)
    print('percent-signal change converting the data')
    psc_nii = percent_signal_change(in_file=sg_nii, func='median')

    print('moving the data')
    shutil.move(sg_nii, sg_nii.replace('fmriprep', 'pp'))
    shutil.move(psc_nii, psc_nii.replace('fmriprep', 'pp'))

# just going to average the T1w space data for now.
average_wildcard = 'pp/sub-01/func/sub-01_task-prf_dir-*T1w_desc-preproc_bold_sg_psc.nii.gz'
to_be_averaged = glob.glob(os.path.join(base_dir, average_wildcard))

# set up the data
to_be_medianed_data = np.zeros([len(to_be_averaged)] + list(nb.load(to_be_averaged[0]).shape))

# load the data
for i,tba in enumerate(to_be_averaged):
    to_be_medianed_data[i] = nb.load(tba).get_data()

median_data = np.median(to_be_medianed_data, axis=0)

# create output image
nii_img_median_data = nb.Nifti1Image(median_data, 
    affine=nb.load(to_be_averaged[0]).affine,
    header=nb.load(to_be_averaged[0]).header)

# save
nii_img_median_data.to_filename(os.path.join(os.path.split(to_be_averaged[0])[0], 'sub-01_task-prf_acq-median_T1w_desc-preproc_bold.nii.gz'))
