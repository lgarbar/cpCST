# !/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 11 16:25:50 2022

@author: jcloud
"""

import argparse
import subprocess
import time
import os
import signal
import time
import PySimpleGUI as sg
from argus_eyetracking_server import connect, record_data, save_data, show_eye_camera
from gui import argus_gui, check_eye_camera
import pygame
import threading

first_run = True
tasks = ['SESSION 1', 'passivepresent', 'passivesherlock', 'segpresent', 'segsherlock', 'cst', 'checkerboard',
         'recallsherlock', '**switch to windows**', 'SESSION 2 V2', 'ravlt1', 'recallpresent', 'recallsherlock',
         'flanker', 'checkerboard', 'ravlt2', 'mst1', 'mst2', 'mst3', 'breathhold', 'nasa', 'SESSION 2 V1',
         'recallpresent', 'recallsherlock', 'passivepresent', 'passivesherlock', 'segpresent', 'segsherlock', 'mst1',
         'mst2', 'mst3', 'nasa', 'TESTER', 'tracksanity', 'foraging']

os.system('sudo apt-get install python-parallel')
os.system('sudo rmmod lp')
os.system('sudo modprobe ppdev')
os.system('sudo chmod a+rw /dev/parport0')

date = time.localtime()
year = str(date[0])
month = str(date[1])
if len(month) == 1:
    month = '0' + month
day = str(date[2])
if len(day) == 1:
    day = '0' + day
date = year + month + day


def MainMenu(ID='', Visit='', Run='', EEG=False, Eyetracking=False, Video=False):
    global first_run
    pygame.init()
    layout = [
        [sg.Text('ID', font=('Verdana, 12')), sg.Input(ID, key='id', font=('Verdana, 12'))],
        [sg.Text('Visit', font=('Verdana, 12')), sg.Input(Visit, key='visit', font=('Verdana, 12'))],
        [sg.Text('Run', font=('Verdana, 12')), sg.Input(Run, key='run', font=('Verdana, 12'))],
        [sg.Checkbox('EEG?', key='eeg', default=EEG, font=('Verdana, 12')),
         sg.Checkbox('Eyetracking?', key='el', default=Eyetracking, font=('Verdana, 12')),
         sg.Checkbox('Video?', key='video', default=Video, font=('Verdana, 12'))],
        [sg.Combo(tasks, key='task', font=('Verdana, 12'))],
        [sg.Button('Launch', font=('Verdana, 12')), sg.Button('Close', font=('Verdana, 12'))]
    ]

    window = sg.Window('RS2 Stimuli Launcher - Main Menu', layout)

    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == 'Close':
            window.close()
            break
        if event == 'Launch':
            window.close()
            if len(values['id']) > 0 and len(values['visit']) > 0 and len(values['run']) > 0 and len(
                    values['task']) > 0:
                try:
                    x = int(values['run'])
                except:
                    sg.Popup('Please select an integer value for "RUN"')
                    continue

                task_output_dir = '/home/nkirs/Desktop/MOBI/Output/sub-{}/ses-{}/raw/'.format(values['id'],
                                                                                              values['visit'])
                raw_output_dir = '/home/nkirs/Desktop/MOBI/Output/sub-{}/ses-{}/raw/'.format(values['id'],
                                                                                             values['visit'])

                if not os.path.exists(task_output_dir):
                    os.makedirs(task_output_dir)
                if not os.path.exists(raw_output_dir):
                    os.makedirs(raw_output_dir)

                task_filename = os.path.join(task_output_dir,
                                             'sub-{}_ses-{}_task-{}_run-{}_events.csv'.format(values['id'],
                                                                                              values['visit'],
                                                                                              values['task'],
                                                                                              values['run']))
                raw_filename = os.path.join(raw_output_dir, 'sub-{}_ses-{}_task-{}_run-{}_{}.{}')
                if values['video']:
                    f = raw_filename.format(values['id'], values['visit'], values['task'], values['run'], 'video',
                                            'avi')
                    video = subprocess.Popen(
                        ['python', '/home/nkirs/Desktop/MOBI/Stimuli/webcam_video.py', '--filename', f])
                    sg.Popup('Wait until video window appears, then press OK')

                if values['el']:
                    if first_run:
                        sg.Popup('On the Eyetracking laptop, run server.py from the MOBI folder')
                        first_run = True
                    f = raw_filename.format(values['id'], values['visit'], values['task'], values['run'], 'eyetracking', 'edf')
                    connect(values['id'], values['visit'], values['task'], values['run'])
                    sg.Popup('Complete Argus calibration')
                    record_data()
                    sg.Popup('Record start time in MOBI checklist')
                
                else:
                   sg.Popup('Record start time in MOBI checklist') 

                if values['eeg'] and 'mst' not in values['task'] and 'cst' not in values['task']:
                    eeg = '--withEEG True&'
                elif 'mst1' in values['task']:
                    eeg = 'Phase1&'
                elif 'mst2' in values['task']:
                    eeg = 'Phase2&'
                elif 'mst3' in values['task']:
                    eeg = 'Phase3&'
                elif 'cst' in values['task']:
                    eeg = ''
                    if values['eeg']:
                        eeg += '--eeg '
                    eeg += '&'
                else:
                    eeg = '&'

                if 'mst' in values['task']:
                    task_process = 'python /home/nkirs/Desktop/MOBI/Stimuli/{} {}'
                    task_filename = task_filename.replace('.csv', '.txt')
                    task_process_practice = task_process.format('MST_practice.py', eeg)
                    task_process = 'python /home/nkirs/Desktop/MOBI/Stimuli/{} {} {}'
                    task_process = task_process.format('MST.py', task_filename, eeg)
                    print('run practice')
                    activity = subprocess.run(task_process_practice, shell=True, stdout=subprocess.PIPE)
                    print('run task')
                    activity2 = subprocess.run(task_process, shell=True, stdout=subprocess.PIPE)

                else:
                    if 'cst' in values['task']:
                        task_process = 'python /home/nkirs/Desktop/MOBI/Stimuli/{} --subid {} --visit {} --run {} {}'
                    else:
                        task_process = 'python /home/nkirs/Desktop/MOBI/Stimuli/{} --filename {} {}'
                    if values['task'] == 'recallpresent':
                        program = 'freerecall_present.py'
                    if values['task'] == 'recallsherlock':
                        program = 'freerecall_sherlock.py'
                    if values['task'] == 'ravlt1':
                        program = 'ravlt_pt1.py'
                    if values['task'] == 'ravlt2':
                        program = 'ravlt_pt2.py'
                    if values['task'] == 'nasa':
                        program = 'nasa_lean.py'
                    if values['task'] == 'passivesherlock':
                        program = 'sherlock.py'
                    if values['task'] == 'segsherlock':
                        program = 'sherlock_segmentation.py'
                    if values['task'] == 'passivepresent':
                        program = 'thepresent.py'
                    if values['task'] == 'segpresent':
                        program = 'thepresent_segmentation.py'
                    if values['task'] == 'flanker':
                        program = 'flanker.py'
                    if values['task'] == 'checkerboard':
                        program = 'checkerboard.py'
                    if values['task'] == 'rey0':
                        program = 'ipad_rey0.py'
                    if values['task'] == 'rey1':
                        program = 'ipad_rey1.py'
                    if values['task'] == 'trails':
                        program = 'ipad_trails.py'
                    if values['task'] == 'spirals':
                        program = 'ipad_spirals.py'
                    if values['task'] == 'writesamples':
                        program = 'ipad_writesamples.py'
                    if values['task'] == 'alphawrite':
                        program = 'ipad_alphawrite.py'
                    if values['task'] == 'tracksanity':
                        program = 'tracking_validation.py'
                    if values['task'] == 'breathhold':
                        program = 'breathhold_lsl.py'
                    if values['task'] == 'foraging':
                        program = 'foraging.py'
                    if values['task'] == 'cst':
                        program = 'run_cst_task.py'
                    if 'cst' in values['task']:
                        task_process = task_process.format(program, values['id'], values['visit'], values['run'], eeg)
                        print(task_process)
                    else:
                        task_process = task_process.format(program, task_filename, eeg)
                    activity = subprocess.run(task_process, shell=True, stdout=subprocess.PIPE)
                    if values['video']:
                        video.send_signal(signal.SIGINT)
                        video.wait()
                        
                sg.Popup('Record stop time in MOBI checklist')
                time.sleep(1)
                if values['el']:
                    save_data_async()
                time.sleep(5)
                MainMenu(values['id'], values['visit'], values['run'], values['eeg'], values['el'], values['video'])

            else:
                window.close()
                MainMenu()
                sg.Popup('Please enter all values')
                continue


def save_data_async():
    def save_data_with_retry():
        max_retries = 5
        retries = 0
        while retries < max_retries:
            try:
                save_data()
                print("Data saved successfully")
                break
            except Exception as e:
                print(f"Error while saving data: {e}")
                retries += 1
                time.sleep(1)  # Wait for 1 second before retrying

        if retries == max_retries:
            print("Failed to save data after multiple attempts")
    t = threading.Thread(target=save_data_with_retry)
    t.start()


if __name__ == "__main__":
    MainMenu()
