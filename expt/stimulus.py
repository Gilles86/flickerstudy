class Rim(ImageBased):

    def __init__(self, win,
                 inner_radius,
                 outer_radius,
                 n_bars,
                 pos,
                 *args,
                 **kwargs):

        self.inner_radius = inner_radius
        self.outer_radius = outer_radius
        self.n_bars = n_bars

        super(Rim, self).__init__(win,
                                  size=outer_radius*2+1,
                                  pos=pos,
                                  *args,
                                  **kwargs)

    def _get_array(self):
        x = np.linspace(-self.outer_radius,
                        self.outer_radius,
                        int(2*self.outer_radius+1))

        y = np.linspace(-self.outer_radius,
                        self.outer_radius,
                        int(2*self.outer_radius+1))

        xv, yv = np.meshgrid(x, y)

        rim = np.round(np.arctan2(xv, yv) / np.pi * self.n_bars/2) % 2 * 2 - 1


        rad = xv**2+yv**2
        mask = (rad > self.inner_radius**2) & (rad < self.outer_radius**2)
        mask = mask.astype(float)

        mask = mask * 2 - 1

        return rim, mask


