# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 20:31:05 2020

@author: Marcus
"""
import numpy as np

test = True

Fs = 60  # screen refresh rate
mask_duration = Fs  # Duration of noise mask in frames
visualNoiseSize = 1024*2  # Dimension in pixels of visual noise.

MY_MONITOR = 'testMonitor'  # needs to exists in PsychoPy monitor center
FULLSCREEN = True
SCREEN_RES = [1920, 1080]
SCREEN_WIDTH = 52.7  # cm
VIEWING_DIST = 63  # distance from eye to center of screen (cm)

noise_level = 0.5  # Opacity of noise mask

#  Positions of words in non-word table (in deg)
# width = 15
# height = 8
# x = np.linspace(-width, width, 8)
# y = np.linspace(-height, height, 6)
width = 0.8
height = 0.7
x = np.linspace(-width, width, 8)
y = np.linspace(-height, height, 6)

#  Text size (in deg)
letter_height = 1
letter_height_table = 0.05  # in norm units
letter_color = 'white'

if test:

    #  Parameters for word recall
    duration_word = 0.2#3
    duration_cross = 0.1#2

    nonword_reading_stim_duration = 1 #45

    # Time noise is presented before the onset of stimulus
    stim_noise_prep_duration = 0.1

    # Spanboard
    stim_duration = 0.1#2.250  # Seconds the dot is shown
    inter_trial_duration = 0.1#0.750
    inter_stimulus_interval = 0.1#3.000
else:
    #  Parameters for word recall
    duration_word = 3
    duration_cross = 2

    nonword_reading_stim_duration = 45

    # Time noise is presented before the onset of stimulus
    stim_noise_prep_duration = 0.1

    # Spanboard
    stim_duration = 2.250  # Seconds the dot is shown
    inter_trial_duration = 0.750
    inter_stimulus_interval = 3.000