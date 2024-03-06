# -*- coding: utf-8 -*-

# Import relevant modules
from psychopy import prefs
prefs.hardware['audioLib'] = ['ptb']
prefs.hardware['audioLatencyMode'] = 1
import psychtoolbox as ptb
from psychopy import visual, monitors, tools, core, gui, event, sound
import pandas as pd
import copy
import datetime
import numpy as np
from pathlib import Path
from titta import Titta
import noise_helpers as helpers
import parameters as params
from scipy.io.wavfile import write
import os

# Change directory to current dir
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


# %% Class fixation marker
class FixMarker:
    '''
    Generates the best fixation target according to Thaler et al. (2013)
    '''
    def __init__(self, win, outer_diameter=0.5, inner_diameter=0.1,
                 outer_color = 'blue', inner_color = 'red',units = 'deg'):
        '''
        Class to generate a stimulus dot with
        units are derived from the window
        '''

        # Set propertis of dot
        outer_dot = visual.Circle(win,fillColor = outer_color, radius = outer_diameter/2,
                                  units = units)
        inner_dot = visual.Circle(win,fillColor = inner_color, radius = inner_diameter/2,
                                  units = units)

        self.outer_dot = outer_dot
        self.inner_dot = inner_dot


    def set_size(self, size):
        ''' Sets the size of the stimulus as scaled by 'size'
        That is, if size == 1, the size is not altered.
        '''
        self.outer_dot.radius = size / 2

    def set_pos(self, pos):
        '''
        sets position of dot
        pos = [x,y]
        '''
        self.outer_dot.pos = pos
        self.inner_dot.pos = pos

    def get_pos(self):
        '''
        get position of dot
        '''
        pos = self.outer_dot.pos

        return pos

    def get_size(self):
        '''
        get size of dot
        '''

        return self.outer_dot.size


    def draw(self):
        '''
        draws the dot
        '''
        self.outer_dot.draw()
        self.inner_dot.draw()

########################################
########################################

# %% Task MSG
def MGS(noise_condition, n_trials, training=False):
    # Show instruction
    text.text = "Titta på punkten i mitten tills den försvinner. Flytta sedan ögonen till positionen där andra punkten dök upp.\
        \n\n(Tryck på mellanslagstangenten för att börja)"

    '''
    look at the central fixation target while a peripheral stimulus was switched on, and they
    had to remember the location of this peripheral stimulus,
    wait for the extinction of the central fixation target, and
    only after the fixation target was switched off, make a saccade directed toward the remembered stimulus location.
    '''

    # text.draw()
    # win.flip()
    # event.waitKeys()
    core.wait(1)

    n_correct_trials = 0
    performance.text = f'{n_correct_trials}/{n_trials}'

    if training:
        # Always train without noise
        noise_condition = 'silence'
        win.mouseVisible = True
        mouse.setPos((0, 0)) # Center of screen
    else:
        mouse.setPos((50, 50)) # set outside of the screen
        win.mouseVisible = False

    #Play noise a bit prior to real exp starts
    if 'auditory' in noise_condition:
        auditory_noise.play()
        core.wait(1)
    elif 'visual' in noise_condition:
        for i in range(int(monitor_refresh_rate)):
            visual_noise[np.mod(i, params.mask_duration)].draw()
            win.flip()
    else:
        core.wait(1)

    for trial in range(n_trials):

        # Trial message
        temp = noise_condition.split('_')
        if len(temp) > 1:
            # e.g, MSG_visual_25_0
            msg = '_'.join(['MGS', temp[0], str(temp[1]), str(trial)])
        else:
            # e.g., MSG_auditory_0_1
            msg = '_'.join(['MGS', noise_condition, str(0), str(trial)])

        # Decide direction and amplitude of target
        rho, theta = (amplitude[np.random.randint(len(amplitude))],
                      direction[np.random.randint(len(direction))])
        x, y = tools.coordinatetools.pol2cart(theta, rho)
        target.pos = (x, y)

        if training:
            position_msg = f'{x:.2f}_{y:.2f}_TRAINING'
        else:
            position_msg = f'{x:.2f}_{y:.2f}'

        # Compute location of target in Tobii coordinate system
        # xy = helpers.deg2tobii(np.expand_dims(np.array([x, y]), axis=0), mon)[0]
        # print(x, y, xy)

        # Present fixation cross in center of the screen for random period
        wait_dur = np.random.rand() * (central_fixation_duration[1] \
                                     - central_fixation_duration[0]) \
                                     + central_fixation_duration[0]
        # if train:
        #     wait_dur = 100

        for i in range(int(wait_dur * monitor_refresh_rate)):
            fixation_point.draw()
            if 'visual' in noise_condition:
                visual_noise[np.mod(i, params.mask_duration)].draw()
            if training:
                performance.draw()
            win.flip()
            now = str(ptb.GetSecs())
            if i == 0:
                tracker.send_message('_'.join(['start_fixation_point', msg, position_msg]))
                tracker.send_message('_'.join(['onset', msg, position_msg])) # Sent to parse trials

                # e.g, 22225_MSG_visual_25_0_0.73_-0.73_start_fixation_point
                trial_messages.append('_'.join([now, msg, position_msg, 'start_fixation_point']))

            # if train and event.getKeys():
            #     break

        tracker.send_message('_'.join(['end_fixation_point', msg, position_msg]))
        trial_messages.append('_'.join([now, msg, position_msg, 'end_fixation_point']))

        # if train:
        #     flash_duration_frames = 10 * monitor_refresh_rate

        # Flash peripheral target
        for i in range(flash_duration_frames):
            fixation_point.draw()
            target.draw()
            if 'visual' in noise_condition:
                visual_noise[np.mod(i, params.mask_duration)].draw()
            if training:
                performance.draw()
            win.flip()
            now = str(ptb.GetSecs())

            if i == 0:
                t0 = tracker.get_system_time_stamp()
                tracker.send_message('_'.join(['start_flash', msg, position_msg]))
                trial_messages.append('_'.join([now, msg, position_msg, 'start_flash']))

            # if train and event.getKeys():
            #     break

        tracker.send_message('_'.join(['end_flash', msg, position_msg]))
        trial_messages.append('_'.join([now, msg, position_msg, 'end_flash']))

        # Memory delay (offset of fixation point is triggered to launch saccade)
        memory_delay_frames = int(np.random.rand() * (memory_delay[1] \
                                     - memory_delay[0]) \
                                     + memory_delay[0] * monitor_refresh_rate)

        # if train:
        #     memory_delay_frames = 100 * monitor_refresh_rate

        for i in range(memory_delay_frames):
            fixation_point.draw()
            if 'visual' in noise_condition:
                visual_noise[np.mod(i, params.mask_duration)].draw()
            if training:
                performance.draw()
            win.flip()
            now = str(ptb.GetSecs())

            if i == 0:
                tracker.send_message('_'.join(['start_memory_delay', msg, position_msg]))
                trial_messages.append('_'.join([now, msg, position_msg, 'start_memory_delay']))

            # if train and event.getKeys():
            #     break

        tracker.send_message('_'.join(['end_memory_delay', msg, position_msg]))
        trial_messages.append('_'.join([now, msg, position_msg, 'end_memory_delay']))

        # Wait for the participant to respond (empty screen is shown [just with noise])
        for i in range(int(wait_response_duration * monitor_refresh_rate)):
            if 'visual' in noise_condition:
                visual_noise[np.mod(i, params.mask_duration)].draw()
            if training:
                performance.draw()
            win.flip()
            now = str(ptb.GetSecs())

            if i == 0:
                t1 = tracker.get_system_time_stamp()
                tracker.send_message('_'.join(['start_saccade_window', msg, position_msg]))
                trial_messages.append('_'.join([now, msg, position_msg, 'start_saccade_window']))

        tracker.send_message('_'.join(['end_saccade_window', msg, position_msg]))
        trial_messages.append('_'.join([now, msg, position_msg, 'end_saccade_window']))
        tracker.send_message('_'.join(['offset', msg, position_msg])) # Sent to parse trial offset

        t2 = tracker.get_system_time_stamp()

        # Finally show true target position
        if show_target_after_trial:
            for i in range(int(monitor_refresh_rate * target_duration_feedback)):
                target.draw()
                if 'visual' in noise_condition:
                    visual_noise[np.mod(i, params.mask_duration)].draw()
                if training:
                    performance.draw()
                win.flip()

        if training:

            # Present feedback
            samples = tracker.buffer.consume_time_range('gaze', t0, t1)
            xy_left = helpers.tobii2deg(np.c_[samples['left_gaze_point_on_display_area_x'],
                                              samples['left_gaze_point_on_display_area_y']], mon)
            xy_right = helpers.tobii2deg(np.c_[samples['right_gaze_point_on_display_area_x'],
                                              samples['right_gaze_point_on_display_area_y']], mon)

            # Were all the samples in this time window (target onset to fixation point offset) in the center of the screen
            # (should be for a successful trial) 80% of samples should be in this window
            # Tobii coordinate system [0, 1], center is at [0.5, 0.5]]
            prop_samples_L = np.sum(((0.0 - window_size) < xy_left[:, 0]) & \
               ((0.0 + window_size) > xy_left[:, 0]) & \
               ((0.0 - window_size) < xy_left[:, 1]) & \
               ((0.0 + window_size) > xy_left[:, 1])) / len(xy_left[:, 0])
            prop_samples_R = np.sum(((0.0 - window_size) < xy_right[:, 0]) & \
               ((0.0 + window_size) > xy_right[:, 0]) & \
               ((0.0 - window_size) < xy_right[:, 1]) & \
               ((0.0 + window_size) > xy_right[:, 1])) / len(xy_right[:, 0])

            # if the best eye has more than 80% of data in the center.
            # print(prop_samples_L, prop_samples_R)
            if np.logical_or((prop_samples_L > 0.8), (prop_samples_R > 0.8)):
                success0 = True
            else:
                success0 = False

            # Get samples from the other time window (fixation point offset -> trial offset)
            samples = tracker.buffer.consume_time_range('gaze', t1, t2)
            xy_left = helpers.tobii2deg(np.c_[samples['left_gaze_point_on_display_area_x'],
                                              samples['left_gaze_point_on_display_area_y']], mon)
            xy_right = helpers.tobii2deg(np.c_[samples['right_gaze_point_on_display_area_x'],
                                              samples['right_gaze_point_on_display_area_y']], mon)

            prop_samples_L = np.sum(((x - window_size) < xy_left[:, 0]) & \
               ((x + window_size) > xy_left[:, 0]) & \
               ((y - window_size) < xy_left[:, 1]) & \
               ((y + window_size) > xy_left[:, 1])) / len(xy_left[:, 0])
            prop_samples_R = np.sum(((x - window_size) < xy_right[:, 0]) & \
               ((x + window_size) > xy_right[:, 0]) & \
               ((y - window_size) < xy_right[:, 1]) & \
               ((y + window_size) > xy_right[:, 1])) / len(xy_right[:, 0])

            # if the best eye has more than 5% of data in the target area
            if np.logical_or((prop_samples_L > 0.05), (prop_samples_R > 0.05)):
                success1 = True
            else:
                success1 = False

            # print(success0, success1)
            success = success0 & success1
            n_correct_trials += int(success)


            performance.text = f'{n_correct_trials}/{n_trials}'

            # # Show performance for 1 s
            # for fi in range(monitor_refresh_rate):
            #     performance.draw()
            #     if 'visual' in noise_condition:
            #         visual_noise[np.mod(i, params.mask_duration)].draw()
            #     win.flip()

        # interrupt?
        keys = event.getKeys()
        if 'escape' in keys:
            win.close()
            core.quit()

    win.flip()
    if 'auditory' in noise_condition:
        auditory_noise.stop()

    return n_correct_trials

# %% Task PF
def PF(noise_condition):
    '''
    In the ocular fixation task, the child was instructed to
    look at a fixation cross at the center of a computer
    screen for two minutes without looking away
    (no distractors; Gould et al., 2001).
    The number of saccades exiting an Area of
    Interest (AOI) covering the fixation cross
    plus ~2 visual degrees (Munoz et al., 2003)
    served as the dependent variable
    '''
    text.text = "Titta på punkten i mitten hela tiden den visas \
        \n\n(Tryck på mellanslagstangenten för att börja)"

    # text.draw()
    # win.flip()
    # event.waitKeys()
    core.wait(1)
    '''
    Falck-Ytter, T., Pettersson, E., Bölte, S., D'Onofrio, B., Lichtenstein, P., & Kennedy, D. P. (2020). Difficulties maintaining prolonged fixation and attention-deficit/hyperactivity symptoms share genetic influences in childhood. Psychiatry Research, 293, 113384.'''

    #Play noise a bit prior to real exp starts
    if 'auditory' in noise_condition:
        auditory_noise.play()
        core.wait(1)
    if 'visual' in noise_condition:
        for i in range(int(monitor_refresh_rate)):
            visual_noise[np.mod(i, params.mask_duration)].draw()
            win.flip()

    for trial in range(1):

        # Trial message
        temp = noise_condition.split('_')
        if len(temp) > 1:
            # e.g, FIX_visual_25_0
            msg = '_'.join(['FIX', temp[0], str(temp[1]), str(trial)])
        else:
            msg = '_'.join(['FIX', noise_condition, str(0), str(trial)])

        # Look at the dot for a prolonged period of time
        target.pos = (0, 0)
        for i in range(int(long_fixation_duration * monitor_refresh_rate)):
            fixation_point.draw()
            if 'visual' in noise_condition:
                visual_noise[np.mod(i, params.mask_duration)].draw()
            win.flip()
            now = str(ptb.GetSecs())

            if i == 0:
                tracker.send_message('_'.join(['onset', msg]))
                trial_messages.append('_'.join([now, msg, '0_0', 'start']))

            # interrupt?
            keys = event.getKeys()
            if 'escape' in keys:
                win.close()
                core.quit()

        tracker.send_message('_'.join(['offset', msg]))
        trial_messages.append('_'.join([now, msg, '0_0', 'end']))


    win.flip()
    if 'auditory' in noise_condition:
        auditory_noise.stop()

# %%
def pause():
    text.text = 'Ta en paus!'
    event.clearEvents()

    i = 0
    while True:
        text.draw()
        win.flip()
        if i == 0:
            core.wait(1)
            pause_instructions.play()
            i += 1

        # Break if 'c button is pressed'
        keys = event.getKeys()
        if keys:
            if keys[0] == 'c':
                break

    win.flip()
###############################################################################
###############################################################################
# %% EXP parameters
dummy_mode = False

# size fixation window # in degrees (whole window = window_size * 2)
window_size = 3

eyes = ['left', 'right']
dimensions = ['x', 'y']

# Parameters MGS
amplitude = np.array([10, 10])
direction  = np.arange(0, 360, 45)[1::2] # [ 45, 135, 225, 315]
central_fixation_duration = [2, 3.5] # Caldani
flash_duration = 0.300 # Caldani
memory_delay = [2, 3.5] # Time from
wait_response_duration = 1

n_trials = 30 # 30
n_trials_practise = 5 # 5
show_target_after_trial = True # At the end of each trial, show flashed target again,
                     # and instruct participants to fixate it (to calibrate)
target_duration_feedback = 1

# Parameters long fixation
long_fixation_duration = 60 #60 # sec

noise_conditions = ['silence', 'auditory', 'visual_25', 'visual_50']

fs_audio = 48000
trial_messages = []

duration_auditory_noise = 5 * 60 # in seconds
sound_file = Path.cwd() / "white_noise.wav"

# Pause instructions
pause_instructions = sound.Sound("paus.wav")


# %%
myDlg = gui.Dlg(title="MS exp")
myDlg.addField('Participant ID:')

ok_data = myDlg.show()  # show dialog and wait for OK or Cancel
if myDlg.OK:  # if ok_data is not None
    print(ok_data)
else:
    print('user cancelled')
    core.quit()


pid = myDlg.data[0]

# %%  Monitor/geometry
MY_MONITOR = 'testMonitor'  # needs to exists in PsychoPy monitor center
FULLSCREEN = True
SCREEN_RES = [1920, 1080]
SCREEN_WIDTH = 52.7  # cm
VIEWING_DIST = 63  # distance from eye to center of screen (cm)

monitor_refresh_rate = 60  # frames per second (fps)
mon = monitors.Monitor(MY_MONITOR)  # Defined in defaults file
mon.setWidth(SCREEN_WIDTH)          # Width of screen (cm)
mon.setDistance(VIEWING_DIST)       # Distance eye / monitor (cm)
mon.setSizePix(SCREEN_RES)

flash_duration_frames = int(monitor_refresh_rate * flash_duration)

# %%  ET settings
et_name = 'Tobii Pro Spectrum'

# Change any of the default dettings?e
settings = Titta.get_defaults(et_name)
settings.FILENAME = pid  + '_' + datetime.datetime.now().strftime("%H_%M_%S")
settings.N_CAL_TARGETS = 5
settings.DEBUG = False
settings.SAMPLING_RATE = 600


# %% Connect to eye tracker and calibrate
tracker = Titta.Connect(settings)
if dummy_mode:
    tracker.set_dummy_mode()
tracker.init()

# Window set-up (this color will be used for calibration)
win = visual.Window(monitor=mon, fullscr=FULLSCREEN,
                    screen=1, size=SCREEN_RES, units='deg')

fixation_point = FixMarker(win, outer_diameter=1.0, inner_diameter=0.2)
# fixation_cross = visual.TextStim(win, text='+', height=1)
target = visual.Circle(win, fillColor = 'white', radius = 0.5)

text = visual.TextStim(win, text='', height=1, color='white')
performance = visual.TextStim(win, text=f'0/{n_trials_practise}', height=0.1, color='white',
                              units='norm', pos=(-0.8, 0.8))

# Check screen refresh rate
measured_rate = win.getActualFrameRate()
assert ((measured_rate < (monitor_refresh_rate  + 1)) & \
        (measured_rate > (monitor_refresh_rate  - 1))),\
        f"Screen refresh rate should be {monitor_refresh_rate}, \
        but is {measured_rate}"

# %% Generate noise

text.text = 'Skapar brus. Vänta!'
text.draw()
win.flip()

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

visual_noise_25 = helpers.generate_visual_noise(win, params.mask_duration,
                          params.visualNoiseSize, 0.25)

visual_noise_50 = helpers.generate_visual_noise(win, params.mask_duration,
                          params.visualNoiseSize, 0.50)

# %% ET setup

#  Calibratse
tracker.calibrate(win)
win.flip()

mouse = event.Mouse(win)


# %% RUN tasks
# np.random.shuffle(tasks) # MGS always first
np.random.shuffle(noise_conditions)

mouse.setPos((50, 50)) # set outside of the screen
# mouse.setVisible(False)

if not dummy_mode:
    win.mouseVisible = False


# %%Run MGS for the first two noise conditions
tracker.start_recording(gaze=True)

noise_conditions_msg = copy.deepcopy(noise_conditions)
for j, noise_condition in enumerate(noise_conditions_msg[:2]):

    # Adjust visual noise level
    if '_25' in noise_condition:
        visual_noise = visual_noise_25
    if '_50' in noise_condition:
        visual_noise = visual_noise_50

    # Practice until ready (only first noise condition)
    if j == 0:
        while True:
            n_correct_trials = MGS(noise_condition, n_trials_practise, training=True)
            text.text = f'{n_correct_trials}/{n_trials_practise} correct. More training (y/n)'
            text.draw()
            win.flip()
            k = event.waitKeys(keyList=['y', 'n'])
            win.flip()

            if 'n' in k:
                break

    # Run experimental trials of MSG
    MGS(noise_condition, n_trials)

tracker.stop_recording(gaze=True)

# %% Pause
pause()

# %% Run PF (four conditions)
tracker.start_recording(gaze=True)

np.random.shuffle(noise_conditions)
for j, noise_condition in enumerate(noise_conditions):

    # Adjust visual noise level
    if '_25' in noise_condition:
        visual_noise = visual_noise_25
    if '_50' in noise_condition:
        visual_noise = visual_noise_50

    PF(noise_condition)

tracker.stop_recording(gaze=True)

# %% Pause
pause()

# %%Run MGS for the last two noise conditions
tracker.start_recording(gaze=True)

for j, noise_condition in enumerate(noise_conditions_msg[2:]):

    # Adjust visual noise level
    if '_25' in noise_condition:
        visual_noise = visual_noise_25
    if '_50' in noise_condition:
        visual_noise = visual_noise_50

    # Run experimental trials of MSG
    MGS(noise_condition, n_trials)

tracker.stop_recording(gaze=True)
# %%

# Close window and save data
text.text = 'Nu är det slut! Ta av dig hörlurarna men sitt kvar på din plats.'
text.draw()
win.flip()
core.wait(10)

win.close()

tracker.save_data(append_version=False)

# Save trial messages to dataframe
df = pd.DataFrame(trial_messages, columns=['all'])
df1 = df['all'].str.split("_", n = 7, expand = True)

# e.g., ['MSG', 'visual', 25, 3, 0.73, -0.73, 'start_saccade_window']
df1.columns = ['time', 'task', 'noise_condition', 'noise_level', 'trial',
               'target_x', 'target_y', 'event']

df1.to_csv(settings.FILENAME + '.tsv', sep='\t')

