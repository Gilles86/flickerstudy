import os.path as op
import pandas as pd
import glob
from bids import BIDSLayout
import pandas as pd
import yaml
import numpy as np
from nistats.first_level_model import FirstLevelModel
import os

derivatives = '/derivatives'
sourcedata = '/sourcedata/ds-flicker'
subject = 'tk'
session = 'flicker1'
acquisition = '0p93'

layout_s = BIDSLayout(sourcedata, validate=False)
layout_d = BIDSLayout(derivatives, validate=False)

#behavior_fns = op.join(sourcedata, f'sub-{subject}', f'ses-{session}',
                       #'behavior', '*.tsv')
#print(glob.glob(behavior_fns))

events = layout_s.get(subject=subject,
                      session=session,
                      acquisition=acquisition,
                      return_type='file',
                      suffix='events')
settings = layout_s.get(subject=subject,
                      session=session,
                      acquisition=acquisition,
                      suffix='expsettings',
                      return_type='file')

data = layout_d.get(subject=subject,
                    session=session,
                    acquisition=acquisition,
                    suffix='preproc',
                    return_type='file')

confounds = layout_d.get(subject=subject,
                    session=session,
                    acquisition=acquisition,
                    suffix='confounds',
                    return_type='file')
compcorr = layout_d.get(subject=subject,
                    session=session,
                    acquisition=acquisition,
                    suffix='compcor',
                    return_type='file')
mask = layout_d.get(subject=subject,
                    session=session,
                    acquisition=acquisition,
                    suffix='mask',
                    return_type='file')

assert len(mask) == 1, 'No mask found'

mask = mask[0]
df = pd.DataFrame({'events':events,
                   'settings':settings,
                   'data':data,
                   'confounds':confounds,
                   'compcorr':compcorr})

results_dir = os.path.join(derivatives, 
                           'modelfitting', 
                           'glm8',
                           'sub-{}'.format('subject'))
results_dir = os.path.join(results_dir, 'ses-{}'.format('session'))
results_dir = op.join(results_dir, 'func')

os.makedirs(results_dir, exist_ok=True)

models = []

for run, row in df.iterrows():
    run += 1
    events = pd.read_table(row.events)

    first_tr = events.loc[events.event_type == 'pulse'].iloc[0].onset
    events['onset'] -= first_tr
    button_presses = events[events.event_type == 'response'][['event_type', 'onset']]
    button_presses['duration'] = 0.1

    with open(row.settings) as f:
        settings = yaml.load(f)

    flickers = pd.DataFrame({'event_type':'flicker',
                             'duration':settings['flicker_experiment']['durations'] *
                             settings['flicker_experiment']['repeats'],
                             'frequency':settings['flicker_experiment']['frequencies'] *
                             settings['flicker_experiment']['repeats'],
                             'duration':np.cumsum(settings['flicker_experiment']['durations'] *
                             settings['flicker_experiment']['repeats'])})

    flickers['event_type'] = flickers['frequency'].apply(lambda x: 'on' if x != 0 else 'off')

    confounds = pd.concat((pd.read_table(row.confounds),
                           pd.read_table(row.compcorr)),
                           axis=1).fillna(method='bfill')

    t_r = events[events['event_type'] == 'pulse'].onset.diff().mean()


    model = FirstLevelModel(t_r=t_r,
                            signal_scaling=False,
                            subject_label=int(run),
                            mask=mask)

    paradigm = pd.concat((button_presses, flickers), axis=0, ignore_index=True)
    paradigm['trial_type'] = paradigm['event_type']
    paradigm = paradigm[paradigm.trial_type != 'off']

    model.fit(row['data'], paradigm, confounds=confounds)

    response = model.compute_contrast('response', output_type='z_score')
    response.to_filename(os.path.join(results_dir,
                                        'sub-{subject}_ses-{session}_task-flicker_run-{run:02d}_response_right_zmap.nii.gz'.format(**locals())))

    onoff = model.compute_contrast('on', output_type='z_score')
    onoff.to_filename(os.path.join(results_dir,
                                        'sub-{subject}_ses-{session}_task-flicker_run-{run:02d}_on_off_zmap.nii.gz'.format(**locals())))

    models.append(model)

model = FirstLevelModel()
