import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.figure import Figure
from matplotlib.patheffects import withStroke
from matplotlib import pyplot as plt


class Protractor(Figure):
    STYLE_COMMON = 1
    STYLE_SIMPLE = 0

    def __init__(self, angle, figsize, dpi, constrained_layout=True, style=1):
        super().__init__(figsize, dpi, constrained_layout=constrained_layout)
        self.figsize = figsize
        self.dpi = dpi
        self.angle = angle
        self.style = style
        self.lp = [0.96, 0.93, 0.2, 0] if self.style else [0.96, 0.96, 0.93, 0.93]
        self.ax = self.add_subplot(projection="polar")

    def draw_protractor(self):
        self.init_ax(self.ax)
        self.draw_scales()

        if self.style == Protractor.STYLE_COMMON:
            self.draw_semi_circle()
            self.draw_text()

    def init_ax(self, ax):
        ax.clear()
        ax.set_thetamin(0)
        ax.set_thetamax(360)
        ax.set_xticklabels([])
        ax.set_yticklabels([])
        ax.set_rlim(0, 1)
        ax.grid(False)
        ax.set_frame_on(False)  # 删除外边框

    def draw_scales(self):
        scales = np.zeros((self.angle + 1, 2, 2))
        angles = np.linspace(0, np.deg2rad(self.angle), self.angle + 1)
        scales[:, :, 0] = np.stack((angles, angles), axis=1)
        scales[:, 0, 1] = self.lp[0]
        scales[::5, 0, 1] = self.lp[1]
        scales[::10, 0, 1] = self.lp[2]
        scales[::90, 0, 1] = self.lp[3]
        scales[:, 1, 1] = 1

        scales_coll = LineCollection(scales, linewidths=[3, 1.5, 1.5, 1.5, 1.5], color="k", linestyles="solid")
        zero_line = LineCollection([[[0, 0.9], [0, 1]], [[np.pi, 0.9], [np.pi, 1]]], linewidths=[3], color="r",
                                   linestyles="solid")
        self.ax.add_collection(scales_coll)
        self.ax.add_collection(zero_line)
        if self.style == Protractor.STYLE_SIMPLE:
            self.ax.plot(0, 0, color="red", marker='o', markersize=3)

    def draw_semi_circle(self):
        for r in [0.815, 0.7, 0.2]:
            semi = np.linspace(0, np.deg2rad(self.angle) if r != 0.999 else np.deg2rad(360), 1000)
            rs = np.full_like(semi, fill_value=r)
            self.ax.plot(semi, rs, linewidth=2, c="k")

    def draw_text(self, c="blue"):
        text_kw = dict(rotation_mode='anchor',
                       va='top', ha='center', clip_on=False,
                       path_effects=[withStroke(linewidth=12, foreground='white')])

        for i in range(0, self.angle + 1, 10):
            theta = np.deg2rad(i)
            if theta == np.pi / 2:
                self.ax.text(theta, 0.85, i, fontsize=40, **text_kw)
                continue
            elif theta == np.pi * 1.5:
                self.ax.text(theta, 0.85, 90, rotation=i - 90, fontsize=40, **text_kw)
                continue

            self.ax.text(theta, 0.89, ((180 - i) % 180 if i not in (0, 360) else 180), rotation=i - 90, fontsize=22,
                         **text_kw)
            self.ax.text(theta, 0.79, (i % 180 if i != 180 else 180), rotation=i - 90, fontsize=18,
                         color=c, **text_kw)

    def change_style(self):
        self.style = not self.style
        self.lp = [0.96, 0.93, 0.2, 0] if self.style else [0.96, 0.96, 0.93, 0.93]

    def get_mask(self, angle):
        mask = plt.figure(figsize=self.figsize, dpi=self.dpi, constrained_layout=True)
        ax = mask.add_subplot(projection="polar")
        self.init_ax(ax)
        if angle == 180:
            theta = np.linspace(np.deg2rad(-4), np.deg2rad(184), 1000)
            chords = np.full_like(theta, 1)
            ax.plot(theta, chords, color="k", antialiased=True, rasterized=True)
            ax.fill(theta, chords, color="k", antialiased=True, rasterized=True)
        else:
            ax.plot(0, 0, marker="o", markersize=mask.get_figwidth() * mask.get_dpi(), c="k",
                    antialiased=True, rasterized=True)
        return mask
