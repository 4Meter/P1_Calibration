import matplotlib
import matplotlib.pyplot as plt

import time
import random
from pylsl import StreamInfo, StreamOutlet
from PIL import Image
from pynput import keyboard

# for SSVEP
import pygame
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


def SSVEP(perform_time, FREQ=0, marker=None):
    class Button():

        def __init__(self, name, color, rect, time, target_f):
            self.name = name
            self.color = color
            self.rect = rect
            self.target_f = target_f
            self.delay = 1000 / target_f
            self.time = time + self.delay
            self.show = False
            self.show_portion = 0.5
            self.time_buffer = []
            self.maxBuffer = 16

        def draw(self, screen):
            if self.show:
                pygame.draw.rect(screen, self.color, self.rect)
                pygame.draw.rect(screen, (0, 0, 0), self.rect, 5)

        def update(self, current_time):
            if current_time >= self.time:
                if self.show:
                    # show
                    self.time = current_time + self.delay * self.show_portion
                else:
                    # no-show
                    self.time = current_time + self.delay * (1 - self.show_portion)
                self.show = not self.show
                if self.show:
                    self.time_buffer.append(current_time)
                    if (len(self.time_buffer) > self.maxBuffer):
                        dif = np.diff(self.time_buffer)
                        actual_f = 1000 / np.mean(dif)
                        if actual_f - self.target_f > 0.05:
                            self.delay += 0.5
                        elif actual_f - self.target_f < 0.05:
                            self.delay -= 0.5
                        self.time_buffer.clear()

        # print the average time interval per blink of the button
        def observe(self):
            if (len(self.time_buffer) > 1):
                dif = np.diff(self.time_buffer)
                actual_f = 1000 / np.mean(dif)
                print(
                    f" {self.name} | Sample: {len(self.time_buffer):2d} | Actual Frequency: {actual_f:.5f} Hz | Delay: {self.delay:.5f} ms    \r",
                    end="\b")

    if FREQ == 0:
        mark = "idle"
        start0 = start = time.time()
        play_beat_sound('start_sound')
        if marker:
            marker.push_sample([mark])
        # This loop will run for 3 seconds
        while time.time() - start0 < perform_time:
            cur = time.time()
            if cur - start > 1:
                #play_beat_sound('end_sound')
                start = cur

    else:
        pygame.init()

        # UI Settings
        screen = pygame.display.set_mode((800, 800), display=MONITOR_NUM)
        current_time = pygame.time.get_ticks()
        button = Button(
            name='ssvep',
            color=(0, 0, 0),
            rect=(200, 200, 400, 400),
            time=current_time,
            target_f=FREQ,  # target frequency
        )

        start_time = time.time()
        cur_time = time.time()
        play_beat_sound('start_sound')

        if marker:
            mark = "SSVEP_" + str(FREQ)
            marker.push_sample([mark])

        while (cur_time - start_time <= perform_time):
            # clock.tick(fps)

            current_time = pygame.time.get_ticks()
            button.update(current_time)

            # --- draws ---
            screen.fill((255, 255, 255))
            button.draw(screen)
            button.observe()  # Uncomment to observe actual frequency of button
            pygame.display.update()
            cur_time = time.time()

        pygame.quit()



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
trials_per_class = 20
initial_time = 1.5

perform_time = 4
# eog_perform_time = 3
wait_time = 2
pause_every = 20
pause_duration = 10

fontsize = 10
SSVEP_fqs = [0, 6.0, 7.2, 8.4]

SSVEP_list = np.repeat(SSVEP_fqs, trials_per_class)

random.shuffle(SSVEP_list)

total_trial_num = len(SSVEP_list)
print(f"實際實驗順序為：{SSVEP_list}")
print(f"Total trial {total_trial_num}")


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
    outlet.push_sample(['SESSION-begin'])

    for sec in range(5, 0, -1):
        t.set_text(f'Calibration Start\n\n{sec}')
        hFigure.canvas.draw()
        hFigure.canvas.flush_events()
        time.sleep(1)

    # Calibration trial
    outlet.push_sample(['calib-begin'])
    print("Calibration Start")
    t.set_text(f'+')
    hFigure.canvas.draw()
    hFigure.canvas.flush_events()
    
    for trial, fq in enumerate(SSVEP_list):
        while pause:
            t.set_text("-pause-")
            hFigure.canvas.draw()
            hFigure.canvas.flush_events()
            time.sleep(2)

        if not plt.fignum_exists(hFigure.number):
            break

        ax.set_title(f"Trial: {trial + 1} / {total_trial_num}", loc="left", fontsize=10, fontname='monospace')
        print(f"Trial {trial + 1} / {total_trial_num} | freq: {fq} Hz")

        # initial state

        outlet.push_sample(['trial-begin'])
        t.set_text("")
        start_time = time.time()
        play_beat_sound('start_sound')
        end_time = time.time()
        time.sleep(initial_time-(end_time - start_time))
        end_time = time.time()
        print(f"initial state 實際執行時間為: {end_time - start_time} 秒")

        # performing state
        start_time = time.time()
        # mark = cur_label + "_" + str(SSVEP_list[SSVEP_IDX])
        # outlet.push_sample([mark])
        print(f"freq is {fq} Hz")
        SSVEP(perform_time, fq, marker=outlet)
        outlet.push_sample(['trial-end'])
            
        end_time = time.time()
        print(f"imaging state 實際執行時間為: {end_time - start_time} 秒")

        # break state
        if (trial + 1) % pause_every == 0 and (trial + 1) != total_trial_num:
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
            
            end_time = time.time()
            time.sleep(wait_time-(end_time - start_time))
            end_time = time.time()
            print(f"break state 實際執行時間為: {end_time - start_time} 秒")



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


