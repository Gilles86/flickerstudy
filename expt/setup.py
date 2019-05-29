from psychopy import event
import argparse
from datetime import datetime
from exptools2.core import Session
from exptools2.core import Trial
from psychopy.visual import TextStim
import os.path as op
import numpy as np
from stimulus import FlickerStimulus, FixationPoint
from psychopy import logging

class PositioningTrial(Trial):
    """ Simple trial with text (trial x) and fixation. """
    def __init__(self, session, trial_nr, phase_durations=(1e9,), **kwargs):
        super().__init__(session, trial_nr, phase_durations, **kwargs)

        self.keys = self.session.settings['flicker_experiment']['keys']

        self.position = self.session.settings['flicker_experiment']['position']
        self.size = self.session.settings['flicker_experiment']['size']

        self.current_topic = 'position_x'

    def draw(self):
        """ Draws stimuli """

        #self.session.rim.draw()
        self.session.flicker_stimulus.draw()
        self.session.fixation_stimulus.draw()
        self.session.info.draw()

    def get_events(self):
        events = event.getKeys(timeStamped=self.session.clock)

        if events:
            if 'q' in [ev[0] for ev in events]:  # specific key in settings?
                self.session.close()
                self.session.quit()

            for key, t in events:

                if key == self.session.mri_trigger:
                    event_type = 'pulse'
                else:
                    event_type = 'response'

                idx = self.session.global_log.shape[0]
                self.session.global_log.loc[idx, 'trial_nr'] = self.trial_nr
                self.session.global_log.loc[idx, 'onset'] = t
                self.session.global_log.loc[idx, 'event_type'] = event_type
                self.session.global_log.loc[idx, 'phase'] = self.phase
                self.session.global_log.loc[idx, 'response'] = key

                for param, val in self.parameters.items():
                    self.session.global_log.loc[idx, param] = val

                if self.eyetracker_on:  # send msg to eyetracker
                    msg = f'start_type-{event_type}_trial-{self.trial_nr}_phase-{self.phase}_key-{key}_time-{t}'
                    self.session.tracker.sendMessage(msg)

                #self.trial_log['response_key'][self.phase].append(key)
                #self.trial_log['response_onset'][self.phase].append(t)
                #self.trial_log['response_time'][self.phase].append(t - self.start_trial)

                if key != self.session.mri_trigger:
                    self.last_resp = key
                    self.last_resp_onset = t
        for e in events:
            if e[0] in self.keys:
                ix = self.keys.index(e[0])

                if ix == 0:
                    if self.current_topic == 'position_x':
                        self.position[0] -= 0.1
                    elif self.current_topic == 'position_y':
                        self.position[1] -= 0.1
                    elif self.current_topic == 'size':
                        self.size -= 0.1
                elif ix == 1:
                    if self.current_topic == 'position_x':
                        self.position[0] += 0.1
                    elif self.current_topic == 'position_y':
                        self.position[1] += 0.1
                    elif self.current_topic == 'size':
                        self.size += 0.1
                elif ix == 2:
                    if self.current_topic == 'position_x':
                        self.current_topic = 'position_y'
                    elif self.current_topic == 'position_y':
                        self.current_topic = 'size'
                    elif self.current_topic == 'size':
                        self.current_topic = 'position_x'
        
        if self.current_topic == 'position_x':
            self.session.info.text = 'x: {:0.2f}'.format(self.position[0])
        elif self.current_topic == 'position_y':
            self.session.info.text = 'y: {:0.2f}'.format(self.position[1])
        elif self.current_topic == 'size':
            self.session.info.text = 'size: {:0.2f}'.format(self.size)


        if self.current_topic.startswith('position'):
            self.session.info.pos = self.position
            self.session.flicker_stimulus.pos = self.position
            self.session.fixation_stimulus.pos = self.position
        elif self.current_topic == 'size':
            self.session.flicker_stimulus.size = self.size
            self.session.fixation_stimulus.size = self.size * self.session.settings['flicker_experiment']['fixation_size_prop']
            self.session.info.height = self.size / 15.




class SetupSession(Session):
    """ Simple session with x trials. """

    def __init__(self, output_str, output_dir=None, settings_file=None):
        """ Initializes TestSession object. """

        super().__init__(output_str, output_dir=None, settings_file=settings_file)
        self.flicker_stimulus = FlickerStimulus(self.win,
                                                size=self.settings['flicker_experiment']['size'],
                                                pos=self.settings['flicker_experiment']['position'])
        self.fixation_stimulus = FixationPoint(self.win,
                                               size=self.settings['flicker_experiment']['fixation_size_prop'] * \
                                               self.settings['flicker_experiment']['size'],
                                               pos=self.settings['flicker_experiment']['position'])

        self.info = TextStim(self.win,
                             color=(0, 0, 0),
                             text='{}'.format(self.settings['flicker_experiment']['position'][0]))

        self.trial = PositioningTrial(self, 1)
        
        print('SIZE FLICKER {}'.format(self.flicker_stimulus.size))
        

    def run(self):
        """ Runs experiment. """
        self.start_experiment()
        self.trial.run()
        self.close()


    def close(self):
        logging.warn("final parameters:\nX-position: {}\nY-position: {}\nSize: {}".format(
        self.trial.position[0],
        self.trial.position[1],
        self.trial.size))
        super().close()



if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--subject',
                        default='01')
    parser.add_argument('--settings',
                        default='settings.yml')

    args = parser.parse_args()
    now = datetime.now()
    date_str = now.strftime('%Y.%m.%d.%H.%M.%S')
    session = SetupSession(f'CALIBRATE_sub-{args.subject}.{date_str}', settings_file=args.settings)
    session.run()
    session.quit()
