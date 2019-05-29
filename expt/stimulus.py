import numpy as np
import psychopy
from psychopy.visual import Line, GratingStim, TextStim, RadialStim, ElementArrayStim
from psychopy.visual.filters import makeMask
from psychopy.tools.unittools import radians
from psychopy.tools.attributetools import setAttribute, attributeSetter

class ImageBased(object):

    def __init__(self,
                 win,
                 size,
                 pos,
                 ori=0,
                 contrast=1,
                 hide=False,
                 mask=None,
                 *args,
                 **kwargs):

        self.win = win

        self._array, self._mask = self._get_array(size)

        if mask is None:
            mask = self._mask 

        self._stim = psychopy.visual.ImageStim(
            self.win,
            self._array,
            size=size,
            pos=pos,
            mask=mask,
            ori=ori,
            *args,
            **kwargs)

        self.contrast = contrast

        self.hide = hide
        self.autoLog = False

    def draw(self):
        if not self.hide:
            self._stim.draw()

    def _get_array(self):
        pass

    @attributeSetter
    def opacity(self, opacity):
        self._stim.opacity = opacity

    @property
    def contrast(self):
        return self._stim.contrast

    @contrast.setter
    def contrast(self, value):
        self._stim.contrast = value

    @property
    def ori(self):
        return self._stim.ori

    @ori.setter
    def ori(self, value):
        self._stim.ori = value

    def setOri(self, value):
        self.ori = value

    @property
    def pos(self):
        return self._stim.pos

    @ori.setter
    def pos(self, value):
        self._stim.pos = value

    def setPos(self, value):
        self.pos = value


    @property
    def size(self):
        return self._stim.size

    @size.setter
    def size(self, value):
        self._stim.size = value


class FlickerStimulus(ImageBased):

    def __init__(self, win, size, pos=(0, 0),
                 falloff_ratio=.9,
                 resolution=1024, *args, **kwargs):

        self.resolution = resolution
        self.falloff_ratio = falloff_ratio

        super(FlickerStimulus, self).__init__(win, size=size, pos=pos, mask='raisedCos', texRes=1024, *args, **kwargs)

    def _get_array(self, size):
        x = np.linspace(-size / 2.,
                        size / 2.,
                        self.resolution)

        y = np.linspace(-size / 2.,
                        size / 2.,
                        self.resolution)

        xv, yv = np.meshgrid(x, y)

        im = np.ones_like(xv)

        rad = np.sqrt(xv**2+yv**2)

        mask = (rad < size / 2.)
        mask = mask.astype(float)
        mask = mask * 2 - 1

        return im, mask



class FixationPoint(object):

    def __init__(self,
                 win,
                 pos,
                 size,
                 color=(1,-1,-1)):

        self.screen = win
        self._pos = pos
        self.fixation_stim = GratingStim(win,
                                          sf=0,
                                          color=color,
                                          mask='raisedCos',
                                          maskParams={'fringeWidth':.2*size},
                                          texRes=512,
                                          pos=pos,
                                          size=size)

        self.fixation_stim2 = GratingStim(win,
                                          sf=0,
                                          color=[0., 0., 0.],
                                          mask='raisedCos',
                                          maskParams={'fringeWidth':.4*size},
                                          texRes=512,
                                          pos=pos,
                                          size=2.*size)
    def draw(self):
        #self.fixation_stim2.draw()
        self.fixation_stim.draw()

    @property
    def pos(self):
        return self.pos

    @pos.setter
    def pos(self, value):
        self.fixation_stim.pos = value
        self.fixation_stim2.pos = value
        self._pos = value

    def setPos(self, value):
        self.pos = value

    @property
    def size(self):
        return self.pos

    @size.setter
    def size(self, value):
        self.fixation_stim.size = value
        self.fixation_stim2.size = value
        self._pos = value

    def setSize(self, value):
        self.size = value
