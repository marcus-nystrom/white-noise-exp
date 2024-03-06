# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 11:23:40 2020

@author: Marcus

"""
# import psychtoolbox as ptb

from psychopy import prefs, core
prefs.hardware['audioLib'] = ['ptb']
prefs.hardware['audioLatencyMode'] = 1

# prefs.hardware['audioDevice'] = ['Microphone (Realtek(R) Audio)']

# prefs.hardware['audioLib'] = ['sounddevice']
# print(prefs.hardware)

from scipy.io.wavfile import write
from pathlib import Path

from psychopy import gui, event, visual, monitors, sound, logging
# from tasks import screen_specs
import noise_helpers as helpers
import parameters as params
import os, sys
import numpy as np

# Make sure you're in the correct path
path = os.path.abspath(os.path.dirname(__file__))
os.chdir(path)

sound_file = Path.cwd() / "white_noise.wav"

fs_audio = 48000
duration_auditory_noise = 5 * 60 # in seconds

# %% open a window and generate visual and auditory noise
screen_fs = 60

mon = monitors.Monitor(params.MY_MONITOR)  # Defined in defaults file
mon.setWidth(params.SCREEN_WIDTH)          # Width of screen (cm)
mon.setDistance(params.VIEWING_DIST)       # Distance eye / monitor (cm)
mon.setSizePix(params.SCREEN_RES)

# Create window and text element
win = visual.Window(monitor=mon, units='deg', screen=1, fullscr=False)
text = visual.TextStim(win, text='',
                       height=params.letter_height,
                       units='deg',
                       color=params.letter_color,
                       wrapWidth=20)
# visual_noise = make_noise(params.mask_duration,
#                           opacity=params.noise_level)

visual_noise = helpers.generate_visual_noise(win, params.mask_duration,
                          params.visualNoiseSize, params.noise_level)

noise_array = helpers.generate_auditory_noise(fs_audio * duration_auditory_noise)

# Ramp up noise slowly
x = np.linspace(-fs_audio, fs_audio, fs_audio)
z = 1/(1 + np.exp(-1/(fs_audio/4)*x))
noise_array[:fs_audio] = noise_array[:fs_audio] * np.c_[z,z]

# Create file with noise if it does not already exist
if not sound_file.is_file():
    max_amplitude = np.iinfo(np.int16).max
    noise_array = max_amplitude * noise_array
    write("white_noise.wav", fs_audio, noise_array.astype(np.int16))
auditory_noise = sound.Sound("white_noise.wav")

win.clearBuffer() # Clear buffer from drawings of noise

# %% Let the participants listen and see the noise
text.text = 'Du kommer att få göra olika uppgifter \
medan du lyssnar och ser på brus. Tryck på mellanslagstangenten \
för att höra hur bruset låter och ser ut'
text.draw()
win.flip()
event.waitKeys()

text.text = 'Så här låter bruset! Tryck på mellanslagstangenten för att gå vidare.'
text.draw()
win.flip()
auditory_noise.play()
event.waitKeys()
auditory_noise.stop()

text.text = 'Så här ser bruset ut. Tryck på mellanslagstangenten för att gå vidare.'

keypressed = False
j = 0
t = []
idx = np.random.randint(0, screen_fs, screen_fs)
while not keypressed:
    key = event.getKeys()
    if key:
        break

    # # text.draw()
    # noiseTexture = np.random.uniform(low=-1, high=1,
    #                                  size=(params.visualNoiseSize,
    #                                        params.visualNoiseSize))
    # visual_noise.tex = noiseTexture
    if np.mod(j, params.mask_duration) == 0:
        np.random.shuffle(idx)

    visual_noise[idx[np.mod(j, params.mask_duration)]].draw()
    # visual_noise.draw()

    win.flip()
    t.append(core.getTime())

    j += 1

print(win.getActualFrameRate())
win.flip()


win.close()