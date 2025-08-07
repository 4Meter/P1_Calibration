"""
24/08/07: 2class LH/RH (open eyes)
"""
import matplotlib
import matplotlib.pyplot as plt

import time
import random
from pylsl import StreamInfo, StreamOutlet
from PIL import Image
from pynput import keyboard

import numpy as np

# for sound
import platform
print(platform.system())
if platform.system() == 'Windows':
    import winsound
else:
    import subprocess
from matplotlib.animation import FuncAnimation


def play_cue_sound(cue):
    if platform.system() == 'Windows':
        # dict = ['LH', 'RH', 'F', 'T]
        sound = "./sound/cue_" + cue + ".wav"
        winsound.PlaySound(sound, winsound.SND_FILENAME)

    else:
        sound = "./sound/cue_" + cue + ".wav"
        subprocess.run(["afplay", sound])


def play_beat_sound(play_sound = 'start_sound'):
    SOUND_PATH = {'start_sound': "./sound/button04a.wav",
                    'end_sound': "./sound/button02a.wav"}
    if platform.system() == 'Windows':
        sound = SOUND_PATH[play_sound]
        winsound.PlaySound(sound, winsound.SND_FILENAME)
    else:
        sound = SOUND_PATH[play_sound]
        subprocess.run(["afplay", sound])


def MI_move(perform_time, direction):
    mi_direction = {'LH': 'left', 'a_LH': 'left',
                    'RH': 'right', 'a_RH': 'right',
                    'F': 'down', 'a_F': 'down',
                    'T': 'up', 'a_T': 'up'}

    # Display the figure
    start0 = start = time.time()
    #play_beat_sound('start_sound')
    # This loop will run for 3 seconds
    while time.time() - start0 < perform_time:
        cur = time.time()
        if cur - start > 1:
            start = cur
            #play_beat_sound('end_sound')
        ori_point = imgs[direction].get_extent()
        if mi_direction[direction] == 'left':
            imgs[direction].set_extent([ori_point[0]-0.1,ori_point[1]-0.1,ori_point[2],ori_point[3]])  # left
        elif mi_direction[direction] == 'right':
            imgs[direction].set_extent([ori_point[0]+0.1,ori_point[1]+0.1,ori_point[2],ori_point[3]])
        elif mi_direction[direction] == 'up':
            imgs[direction].set_extent([ori_point[0],ori_point[1],ori_point[2]+0.1,ori_point[3]+0.1])
        elif mi_direction[direction] == 'down':
            imgs[direction].set_extent([ori_point[0],ori_point[1],ori_point[2]-0.1,ori_point[3]-0.1])
        plt.show()
        plt.pause(0.01)

# Global variable to control pause state
pause = True
bad_trial = []
bad_trial_label = []
MONITOR_NUM = 0

# Function to toggle pause state
def on_press(key):
    global pause
    if key == keyboard.KeyCode.from_char('p'):
        pause = not pause
        try:
            bad_trial.append(trial + 1)
            bad_trial_label.append(cur_label)
            print(f"Pause: {pause} with Bad trial {trial + 1}th: {cur_label}")
        except:
            print(f"Pause: {pause} with NO Bad trial")
    elif key == keyboard.KeyCode.from_char('b'):
        try:
            bad_trial.append(trial + 1)
            bad_trial_label.append(cur_label)
            print(f"Bad trial: {trial + 1}th: {cur_label}")
        except:
            print(f"bad label is not exist")


# Start listening for key press
listener = keyboard.Listener(on_press=on_press)
listener.start()

# initial parameter
random.seed(187964418554)
trials_per_class = 30
initial_time = 1.5

perform_time = 4.5
eog_perform_time = 5
# eog_perform_time = 3
wait_time = 2
pause_every = 15
pause_duration = 20


'''trials_per_class = 5 # for debug
#perform_time = 1 # for debug
eog_perform_time = 0.1 # for debug
wait_time = 0.1 # for debug
pause_duration = 1 # for debug
pause_every = 10 # for debug'''

fontsize = 10
MI_labels = ['a_LH', 'LH', 'a_RH', 'RH', 'a_F', 'F', 'a_T', 'T']
trial_labels = ['LH', 'RH', 'F', 'T', 'idle']
warm_trial_labels = ['a_LH', 'LH',
                     'a_RH', 'RH',
                     'a_F', 'F',
                     'a_T', 'T']


# markers = {'LH':'left hand',  :'right hand', 'F':'foot', 'T':'tongue'}

total_trial_num = trials_per_class * len(trial_labels)


# 產生實驗順序
# 250114 只有idle跟想像, 不要實際動跟SSVEP
labels_arr = []
for j in range(int(trials_per_class * len(trial_labels) / pause_every)):
    run_arr = []
    run_arr_temp = []
    for i in range(int(pause_every / len(trial_labels))):
        for label in trial_labels:
            run_arr_temp.append(label)
    random.shuffle(run_arr_temp)
    run_arr = np.append(run_arr, run_arr_temp)
    print(f"單組實驗順序為：{run_arr}")

    labels_arr = np.append(labels_arr, run_arr)
#def flatten(l):
#    return [item for sublist in l for item in sublist]
#labels_arr = flatten(labels_arr)
print(f"實際實驗順序為：{labels_arr}")

print(f"Total trial {len(labels_arr)}")
from collections import Counter

counters = Counter(labels_arr)
print(counters)

# load image
LH_img = Image.open("./icon/fist_L.png")
a_LH_img = Image.open("./icon/a_fist_L.png")
RH_img = Image.open("./icon/fist_R.png")
a_RH_img = Image.open("./icon/a_fist_R.png")
T_img = Image.open("./icon/tongue.png")
a_T_img = Image.open("./icon/tongue.png")
F_img = Image.open("./icon/foot.png")
a_F_img = Image.open("./icon/a_foot.png")

matplotlib.rcParams.update({'font.size': fontsize})

info = StreamInfo(name='MotorImag-Markers', type='Markers', channel_count=1,
                  nominal_srate=0, channel_format='string',
                  source_id='t8u43t98u')
outlet = StreamOutlet(info)

hFigure, ax = plt.subplots()
plt.axis('off')
# ax.set_yticklabels([''])
# ax.set_xticklabels([''])
t = plt.text(5, 5, '', ha='center', va='center', fontsize=20)
plt.xlim(xmin=-0.5, xmax=10.5)
plt.ylim(ymin=-0.5, ymax=10.5)
imgs = {}
imgs["LH"] = ax.imshow(LH_img, alpha=0.1, extent=(0, 3, 3.75, 6.25))
imgs["a_LH"] = ax.imshow(a_LH_img, alpha=0, extent=(0, 3, 3.75, 6.25))
imgs["RH"] = ax.imshow(RH_img, alpha=0.1, extent=(7, 10, 3.75, 6.25))
imgs["a_RH"] = ax.imshow(a_RH_img, alpha=0, extent=(7, 10, 3.75, 6.25))
imgs["T"] = ax.imshow(T_img, alpha=0.1, extent=(3.75, 6.25, 7, 10))
imgs["a_T"] = ax.imshow(a_T_img, alpha=0, extent=(3.75, 6.25, 7, 10))
imgs["F"] = ax.imshow(F_img, alpha=0.1, extent=(3.75, 6.25, 0, 3))
imgs["a_F"] = ax.imshow(a_F_img, alpha=0, extent=(3.75, 6.25, 0, 3))


# fullscreen
# manager = plt.get_current_fig_manager()
# manager.window.showMaximized()


plt.ion()
plt.draw()
plt.show()

# manager = plt.get_current_fig_manager()
# manager.full_screen_toggle()
hFigure.canvas.draw()
hFigure.canvas.flush_events()

print("Press [p] to begin.")
while pause:
    hFigure.canvas.draw()
    hFigure.canvas.flush_events()
    plt.pause(0.01)


try:

    # Countdown    
    for sec in range(15, 0, -1):
        t.set_text(f'Calibration Start\n\n{sec}')
        hFigure.canvas.draw()
        hFigure.canvas.flush_events()
        time.sleep(1)

    # Calibration trial
    outlet.push_sample(['calib-begin'])
    for trial, cur_label in enumerate(labels_arr):
        while pause:
            t.set_text("-pause-")
            hFigure.canvas.draw()
            hFigure.canvas.flush_events()
            time.sleep(2)

        if not plt.fignum_exists(hFigure.number):
            break

        ax.set_title(f"Trial: {trial + 1} / {total_trial_num}", loc="left", fontsize=10, fontname='monospace')
        print(f"Trial {trial + 1} | {cur_label} / {total_trial_num}")

        # initial state

        outlet.push_sample(['trial-begin'])
        t.set_text("")
        for label in MI_labels:
            imgs[label].set_alpha(1 if label == cur_label else 0)
        hFigure.canvas.draw()
        hFigure.canvas.flush_events()
        start_time = time.time()
        play_cue_sound(cur_label)
        # time.sleep(initial_time)
        end_time = time.time()
        print(f"initial state 實際執行時間為: {end_time - start_time} 秒")
        for label in MI_labels:
            imgs[label].set_alpha(0)

        # imaging state
        play_beat_sound('start_sound')
        if cur_label == 'idle':
            start_time = time.time()
            mark = cur_label
            outlet.push_sample([mark])
            time.sleep(perform_time)
            outlet.push_sample(['trial-end'])
        else:
            t.set_text("+")
            
            hFigure.canvas.draw()
            hFigure.canvas.flush_events()
            start_time = time.time()
            outlet.push_sample([cur_label])
            time.sleep(perform_time)
            outlet.push_sample(['trial-end'])
            
        end_time = time.time()
        print(f"imaging state 實際執行時間為: {end_time - start_time} 秒")

        # break state
        if (trial + 1) % pause_every == 0 and (trial + 1) != len(labels_arr):
            for s in range(0, pause_duration + 1):
                t.set_text(f'Rest {pause_duration} sec\n\nRemain {pause_duration - s} sec')
                hFigure.canvas.draw()
                hFigure.canvas.flush_events()
                if s == 0:
                    play_beat_sound('end_sound')
                time.sleep(1)
            t.set_text('')
            hFigure.canvas.draw()
            hFigure.canvas.flush_events()
        else:
            start_time = time.time()
            t.set_text(f'+')
            hFigure.canvas.draw()
            hFigure.canvas.flush_events()
            play_beat_sound('end_sound')
            # time.sleep(wait_time)
            end_time = time.time()
            print(f"break state 實際執行時間為: {end_time - start_time} 秒")

    trial = 0
    outlet.push_sample(['bad-trial-compensate'])
    # compensate bad trial
    while len(bad_trial_label)!=0:
        cur_label = bad_trial_label[0]
        bad_trial_label = np.delete(bad_trial_label, 0)

        while pause:
            t.set_text("-pause-")
            hFigure.canvas.draw()
            hFigure.canvas.flush_events()
            time.sleep(0.1)

        if not plt.fignum_exists(hFigure.number):
            break

        ax.set_title(f"Trial: {trial + 1} / {total_trial_num}", loc="left", fontsize=10, fontname='monospace')
        print(f"Trial {trial + 1} | {cur_label} / {total_trial_num}")

        # initial state

        outlet.push_sample(['trial-begin'])
        t.set_text("")
        for label in MI_labels:
            imgs[label].set_alpha(0.8 if label == cur_label else 0)
        hFigure.canvas.draw()
        hFigure.canvas.flush_events()
        start_time = time.time()
        play_cue_sound(cur_label)
        # time.sleep(initial_time)
        end_time = time.time()
        print(f"initial state 實際執行時間為: {end_time - start_time} 秒")
        for label in MI_labels:
            imgs[label].set_alpha(0)
            imgs[label].set_extent((3, 6.5, 3.5, 6.5))

        # imaging state
        if cur_label == 'idle':
            start_time = time.time()
            mark = cur_label
            outlet.push_sample([mark])
            print("idle bad trial compensation")
            time.sleep(perform_time)
            outlet.push_sample(['trial-end'])
        else:
            t.set_text("+")
            
            hFigure.canvas.draw()
            hFigure.canvas.flush_events()
            start_time = time.time()
            outlet.push_sample([cur_label])
            MI_move(perform_time, cur_label)
            # time.sleep(perform_time)
            outlet.push_sample(['trial-end'])
        end_time = time.time()
        print(f"imaging state 實際執行時間為: {end_time - start_time} 秒")

        # break state
        start_time = time.time()
        t.set_text(f'+')
        hFigure.canvas.draw()
        hFigure.canvas.flush_events()
        play_beat_sound('end_sound')
        # time.sleep(wait_time)
        end_time = time.time()
        print(f"break state 實際執行時間為: {end_time - start_time} 秒")
        trial += 1


    for s in range(5, 0, -1):
        t.set_text(f'Calibration End\n\n{s}')
        hFigure.canvas.draw()
        hFigure.canvas.flush_events()
        if s == 0:
            play_beat_sound('end_sound')
        time.sleep(1)
    t.set_text('')
    hFigure.canvas.draw()
    hFigure.canvas.flush_events()




except Exception as e:
    print(e)

outlet.push_sample(['calib-end'])
print(f"Bad trial: {bad_trial}")