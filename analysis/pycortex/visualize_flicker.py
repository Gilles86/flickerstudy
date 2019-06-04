import cortex
from nilearn import image
import os.path as op
import numpy as np

derivatives = '/data/flicker/derivatives'
subject = 'tk'
session = 'flicker1'

pc_subject = f'odc.{subject}'

freq = '/data/flicker/zooi/pars_mean.nii.gz'
log_freq = '/data/flicker/zooi/pars_mean_log.nii.gz'
r2 = '/data/flicker/zooi/pars_r2.nii.gz'
amplitude = '/data/flicker/zooi/pars_amplitude.nii.gz'
log_sd = '/data/flicker/zooi/pars_mean_log.nii.gz'

derivatives = '/data/odc/derivatives'
t1w = cortex.db.get_anat(pc_subject)

freq = image.resample_to_img(freq, t1w, interpolation='nearest')
log_freq = image.resample_to_img(log_freq, t1w, interpolation='nearest')
r2 = image.resample_to_img(r2, t1w, interpolation='nearest')
amplitude = image.resample_to_img(amplitude, t1w, interpolation='nearest')
log_sd = image.resample_to_img(log_sd, t1w, interpolation='nearest')
transform = cortex.xfm.Transform(np.identity(4), t1w)
transform.save(pc_subject, 'identity.t1w.v2', 'magnet')

r2 = r2.get_data().T
freq = freq.get_data().T

freq_log10 = np.log10(freq)

#freq[freq <1] = np.nan
#freq[freq > 60] = np.nan
#freq[r2 < .1] = np.nan

images = {}
images['frequency'] = cortex.Volume(freq, pc_subject, 'identity.t1w.v2', vmin=0.1, vmax=60)
images['r2'] = cortex.Volume(r2, pc_subject, 'identity.t1w.v2', vmin=0, vmax=0.7)
images['log_freq'] = cortex.Volume(log_freq.get_data().T, pc_subject, 'identity.t1w.v2', vmin=-1, vmax=5)
images['log10'] = cortex.Volume(freq_log10, pc_subject, 'identity.t1w.v2')
images['amplitude'] = cortex.Volume(amplitude.get_data().T, pc_subject, 'identity.t1w.v2')
images['log_sd'] = cortex.Volume(log_sd.get_data().T, pc_subject, 'identity.t1w.v2')

ds =  cortex.Dataset(**images)
cortex.webshow(images)
