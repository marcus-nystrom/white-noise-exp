# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 12:46:57 2020

@author: Marcus
"""

import numpy as np
from psychopy import visual
from psychopy.tools.monitorunittools import cm2deg, deg2pix
import copy


# %%
def tobii2deg(pos, mon):
    ''' Converts Tobiis coordinate system [0, 1 to degrees.
    Note that the Tobii coordinate system start in the upper left corner
    and the PsychoPy coordinate system in the center
    Assumes pixels are square
    Args:   pos: N x 2 array with calibratio position in [0, 1]
            screen_height: height of screen in cm
    '''

    pos_temp = copy.deepcopy(pos) # To avoid that the called parameter is changed

    # Center
    pos_temp[:, 0] = pos_temp[:, 0] - 0.5
    pos_temp[:, 1] = (pos_temp[:, 1] - 0.5) * -1

    # Cenvert to psychopy coordinates (center)
    pos_temp[:, 0] = pos_temp[:, 0] * mon.getWidth()
    pos_temp[:, 1] = pos_temp[:, 1] * mon.getWidth() * (float(mon.getSizePix()[1]) / \
                                              float(mon.getSizePix()[0]))

    # Convert to deg.
    pos_deg = cm2deg(pos_temp, mon, correctFlat=False)
    return pos_deg

# %%
def generate_auditory_noise(n_samples):
    ''' Generate white noise from a uniform distribution

    Args:
        n_samples (int): length of noise array

    Returns:
        noise (N x 1 array).

    '''

    noise = np.random.uniform(low=-1, high=1, size=(n_samples, 2))

    return noise

# %%
def generate_visual_noise(win, mask_duration,
                          visualNoiseSize, noise_level= 0.5):
    ''' Returns noise textures:

    Args:
        mask_duration - duration fo noise mask in frames
        visualNoiseSize - size of mask in units of win
        noise_level - opacity of the noise (0 - 1), where 0 is no noise
        opacity - transparancy of noise mask
    '''
    visualNoise = []  # list of rendered frames
    for n in range(mask_duration):
        noiseTexture = np.random.uniform(low=-1, high=1,
                                         size=(visualNoiseSize,
                                               visualNoiseSize))
        visualNoise.append(visual.GratingStim(win=win, tex=noiseTexture,
                                              size=(visualNoiseSize,
                                                    visualNoiseSize),
                                              units='pix',
                                              opacity=noise_level,
                                              interpolate=False, mask=None))
        visualNoise[n].draw()

    return visualNoise


