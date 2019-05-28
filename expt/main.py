import argparse
from datetime import datetime
from exptools2.core import Session
from exptools2.core import Trial
from psychopy.visual import TextStim
from exptools2 import utils
import os.path as op
import numpy as np
from stimulus import Rim, FlickerStimulus, FixationPoint

class FlickerTrial(Trial):
    """ Simple trial with text (trial x) and fixation. """
    def __init__(self, session, trial_nr, phase_durations, frequency=15., **kwargs):
        super().__init__(session, trial_nr, phase_durations, **kwargs)

        self.cycle_length_seconds = 1./frequency
        self.cycle_length_frames = self.cycle_length_seconds * self.session.actual_framerate

    def draw(self):
        """ Draws stimuli """

        #self.session.rim.draw()
        
        contrast = self.session.nr_frames % self.cycle_length_frames
        contrast /= self.cycle_length_frames
        contrast *= np.pi * 2
        contrast = np.sin(contrast)

        self.session.flicker_stimulus.contrast = contrast
        self.session.flicker_stimulus.draw()
        self.session.fixation_stimulus.draw()

        if self.session.clock.getTime() > self.session.fixation_switch_onsets[0]:
            self.session.change_fixation_color()



class FlickerSession(Session):
    """ Simple session with x trials. """

    def __init__(self, output_str, output_dir=None, settings_file=None):
        """ Initializes TestSession object. """

        super().__init__(output_str, output_dir=None, settings_file=settings_file)
        self.durations = self.settings['flicker_experiment']['durations']
        self.frequencies = self.settings['flicker_experiment']['frequencies']

        if len(self.frequencies) != len(self.durations):
            raise Exception('Length of frequencies and durations-settings should be equal!')

        self.n_trials = len(self.durations)

        mean_color_duration = self.settings['flicker_experiment']['mean_color_duration']
        total_duration = np.sum(self.durations)

        self.fixation_switch_onsets = np.random.exponential(mean_color_duration,
                                                            int(total_duration/mean_color_duration * 10))
        self.fixation_switch_onsets = list(np.cumsum(self.fixation_switch_onsets))

        self.rim = Rim(self.win,
                       self.settings['flicker_experiment']['rim_size'],
                       self.settings['flicker_experiment']['rim_size'] * \
                       self.settings['flicker_experiment']['rim_outer_ratio'],
                       self.settings['flicker_experiment']['rim_nbars'],
                       (0, 0),)

        self.flicker_stimulus = FlickerStimulus(self.win,
                                                self.settings['flicker_experiment']['rim_size'])
        self.fixation_stimulus = FixationPoint(self.win,
                                               (0, 0),
                                               self.settings['flicker_experiment']['fixation_size'])
        
                                               
    def create_trials(self,
                      timing='seconds'):
        self.trials = []

        for trial_nr, duration, frequency in zip(range(self.n_trials),
                                                 self.durations,
                                                 self.frequencies):


            self.trials.append(
                FlickerTrial(session=self,
                             trial_nr=trial_nr,
                             phase_durations=(duration,),
                             frequency=frequency,
                             verbose=True,
                             timing=timing)
            )


    def change_fixation_color(self):
        if (self.fixation_stimulus.fixation_stim.color == [1., -1., -1.]).all():
            self.fixation_stimulus.fixation_stim.color = (-1., 1., -1.)
            color = 'green'
        else:
            self.fixation_stimulus.fixation_stim.color = (1., -1., -1.)
            color = 'red'

        idx = self.global_log.shape[0]
        self.global_log.loc[idx, 'color'] = color
        self.global_log.loc[idx, 'event_type'] = 'color change'
        self.global_log.loc[idx, 'nr_frames'] = 0
        self.global_log.loc[idx, 'phase'] = 0
        self.global_log.loc[idx, 'trial_nr'] = self.global_log.iloc[-1]['trial_nr']
        self.global_log.loc[idx, 'onset'] =self.clock.getTime()
        self.fixation_switch_onsets.pop(0)
        print(self.fixation_switch_onsets)


    def run(self):
        """ Runs experiment. """
        self.start_experiment(wait_n_triggers=1)
        for trial in self.trials:
            trial.run()            

        self.close()


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('subject')
    parser.add_argument('--settings',
                        default='settings.yml')

    args = parser.parse_args()
    now = datetime.now()
    date_str = now.strftime('%Y.%m.%d.%H.%M.%S')
    session = FlickerSession(f'sub-{args.subject}.{date_str}', settings_file=args.settings)
    session.create_trials()
    session.run()
    session.quit()
