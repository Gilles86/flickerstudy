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
        self.size = size

        self._array, self._mask = self._get_array()

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

class Rim(ImageBased):

    def __init__(self, win,
                 inner_radius,
                 outer_radius,
                 n_bars,
                 pos,
                 resolution=1000,
                 *args,
                 **kwargs):

        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.n_bars = n_bars
        self.resolution = resolution

        super(Rim, self).__init__(win,
                                  size=outer_radius*2,
                                  pos=pos,
                                  *args,
                                  **kwargs)

    def _get_array(self):
        x = np.linspace(-self.outer_radius,
                        self.outer_radius,
                        self.resolution)

        y = np.linspace(-self.outer_radius,
                        self.outer_radius,
                        self.resolution)

        xv, yv = np.meshgrid(x, y)

        rim = np.round(np.arctan2(xv, yv) / np.pi * self.n_bars/2) % 2 * 2 - 1


        rad = xv**2+yv**2
        mask = (rad > self.inner_radius**2) & (rad < self.outer_radius**2)
        mask = mask.astype(float)

        mask = mask * 2 - 1

        return rim, mask


class FlickerStimulus(ImageBased):

    def __init__(self, win, size, pos=(0, 0),
                 falloff_ratio=.9,
                 resolution=1024, *args, **kwargs):

        self.size = size
        self.resolution = resolution
        self.falloff_ratio = falloff_ratio

        super(FlickerStimulus, self).__init__(win, size=size * 2, pos=pos, mask='raisedCos', texRes=1024, *args, **kwargs)

    def _get_array(self):
        x = np.linspace(-self.size,
                        self.size,
                        self.resolution)

        y = np.linspace(-self.size,
                        self.size,
                        self.resolution)

        xv, yv = np.meshgrid(x, y)

        im = np.ones_like(xv)

        rad = np.sqrt(xv**2+yv**2)

        #falloff_min = self.falloff_ratio * self.size
        #falloff_size = (1 - self.falloff_ratio) * self.size

        #falloff_region = (np.cos((rad[rad > falloff_min] - falloff_min) \
            #/ falloff_size * np.pi) + 1) / 2

        #im[rad > falloff_min] = falloff_region
        #print(im)

        mask = (rad < self.size)
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
