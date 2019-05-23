from exptools2.core import Session
from exptools2.core import Trial
from psychopy.visual import TextStim
from exptools2 import utils
import os.path as op
import numpy as np


class FlickerTrial(Trial):
    """ Simple trial with text (trial x) and fixation. """
    def __init__(self, session, trial_nr, phase_durations, frequency=15., **kwargs):
        super().__init__(session, trial_nr, phase_durations, **kwargs)
        self.txt = TextStim(self.session.win)

        self.cycle_length_seconds = 1./frequency
        self.cycle_length_frames = self.cycle_length_seconds * self.session.actual_framerate

    def draw(self):
        """ Draws stimuli """
        
        print(self.cycle_length_frames)
        contrast = self.session.nr_frames % self.cycle_length_frames
        contrast /= self.cycle_length_frames
        contrast *= np.pi * 2
        contrast = np.sin(contrast)
        #self.txt.text = contrast
        self.txt.contrast = contrast
        self.txt.draw()
        


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

    def run(self):
        """ Runs experiment. """
        self.start_experiment()
        for trial in self.trials:
            trial.run()            

        self.close()


if __name__ == '__main__':

    settings = op.join(op.dirname(__file__), 'settings.yml')
    session = FlickerSession('sub-01', settings_file=settings)
    session.create_trials()
    session.run()
    session.quit()
