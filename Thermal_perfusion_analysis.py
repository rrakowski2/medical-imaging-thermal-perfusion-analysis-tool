#!/usr/bin/env python3

"""
===========================
Script to process (semi-automatically) thermal perfusion maps 
by Rafal Nov 2024
===========================

"""


# Create compute environment
import os
import re
import cv2
import sys
import math
import os.path
import warnings
import colorama
import termcolor
import itertools
import statistics
import numpy as np
import pandas as pd
from termcolor import colored
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.pyplot import imshow
from matplotlib.widgets import Slider
from matplotlib.backend_bases import MouseButton
warnings.filterwarnings("ignore")
os.system('color')
colorama.init()


# Declare default parameters or pass them as arguments when the script is imported as a module
max_freq_number = 1000
max_rois_number = 10
histogram_bin_no = 20
default_rois_no = 4


# HELPER CLASSES:

# Move ROI to another position and pick pixels coordinates class
class Move_ROI():
    def __init__(self, region, images, regions,  side):
        # Plot image with ROI 
        global orientation


        # Print image
        self.fig, self.ax = plt.subplots()
        self.ax.clear()
        self.ax.set_title('Image selector')
        self.ax.set_xlabel('Pixel no.')
        self.ax.set_ylabel('Pixel no.')
        self.ax.imshow(images[0][:,:], cmap='gray')


        # Introduce patch
        self.rect = patches.Rectangle((0, 0), 0, 0, linewidth=1, edgecolor='r', facecolor='none') 
        self.ax.add_artist(self.rect)
        self.ax.set_title(f'Click to move ROI no.{region + 1}')


        # Get a preferred corner of a square ROI to bind to
        orientation = orientation_input_tester()
        if orientation == 0 or orientation > 4:
            while orientation == 0 or orientation> 4:
                print('\nInvalid input! ') 
                orientation = orientation_input_tester()
        self.bound = orientation
        self.region = region
        if self.region != 0:
            # Pick dummy coord. of a ROI
            dummy = x
            dummy = y


        # Prompt user to indicate a ROI
        print(f'\nClick on image to select ROI no.{region + 1}')
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)


    # Get pixel coordinates when clicked at
    def on_click(self, event):
        global x, y, bound
        # On a click
        if event.button is MouseButton.LEFT:
            x = round(event.xdata)
            y = round(event.ydata)
            print("Roi's centre coord x & y = ", x, '&', y, 'pix')
            if self.bound == 1:
                pass
            elif self.bound == 2:
                x = x - roi_box_side
                y = y
            elif self.bound == 3:
                x = x - roi_box_side
                y = y - roi_box_side
            elif self.bound == 4:
                x = x
                y = y - roi_box_side
            bound = self.bound
            self.rect.set_bounds(x, y, roi_box_side, roi_box_side)
            self.fig.canvas.draw()
    def show(self):
        plt.show()


# Zoom in/out a selected ROI class
class Scale_ROI(object):
    def __init__(self, region, images):
        global w, h, xx, yy


        # Print image frame
        self.region = region
        self.fig, self.ax = plt.subplots()
        self.ax.clear()
        self.ax.set_title('Image selector')
        self.ax.set_xlabel('Pixel no.')
        self.ax.set_ylabel('Pixel no.')
        self.ax.imshow(images[0][:,:], cmap='gray')


        # Compute ROI coordinates corrected by a selected corner (bound to a pixel) 
        w = h = roi_box_side
        if bound == 1:
            xx = x
            yy = y
        elif bound == 2:
            xx = x - w + roi_box_side
            yy = y
        elif bound == 3:
            xx = x - w + roi_box_side
            yy = y - h + roi_box_side
        elif bound == 4:
            xx = x
            yy = y - h + roi_box_side
        self.rect = patches.Rectangle((x, y), roi_box_side, roi_box_side, linewidth=1, edgecolor='r', facecolor='none') 
        self.ax.add_artist(self.rect)
        self.ax.set_title(f'input digit key to scale ROI no.{region + 1}')
        self.fig.canvas.mpl_connect('key_press_event', self.on_press)


    # Get pixel coordinates and ROIS' box sizes
    def on_press(self, event):
        global w, h, xx, yy
        w = h = roi_box_side * int(event.key)/5
        xx = x
        yy = y
        if bound == 1:
            xx = x
            yy = y
        elif bound == 2:
            xx = x - w + roi_box_side
            yy = y
        elif bound == 3:
            xx = x - w + roi_box_side
            yy = y - h + roi_box_side
        elif bound == 4:
            xx = x
            yy = y - h + roi_box_side
        self.rect.set_bounds(xx, yy, w, h)
        self. fig.canvas.draw()    
    def show(self):
        plt.show()
        

# HELPER FUNCTIONS:

# Test input validity of frequency number option
def frequency_input_tester(max_freq_number=1000):
    while 'n' not in locals():
        try:
            prompt = input(colored(f'\nInput integer number n to select every nth image from the tiff_stack: ', 'yellow')) #'light_yellow')) # print(colored('Hello, World!', 'red'))
            n = abs(int(prompt))
        except (ValueError, ZeroDivisionError):
            pass
        else:
            if prompt == '':
                print('\nInvalid input! ') 
                frequency_input_tester(max_freq_number)
    return n


# Test input validity of ROIs' number option
def rois_no_input_tester(max_rois_number=10):
    while 'rois_number' not in locals():
        try:
            prompt = input(f"\nInput:\n      1 - TO SET no. of ROIs (default is 4)\n      2 - TO SELECT ONE EXTRA ROI \n      OTHER INTEGER - FOR ARBITRARY NUMBER OF ROIs (min. 3) \n      0 - TO SKIP OPTIONS & EXIT\nYour selection? ")
            rois_number = abs(int(prompt))
        except ValueError:
            pass
        else:
            if prompt == '':
                rois_no_input_tester(max_rois_number)
    return rois_number


# Test input validity of frequency number option
def orientation_input_tester():
    while 'corner' not in locals():
        try:
            prompt = input(colored(f"\nInput:\n1 to bind to upper-left corner of ROI's\n2 for upper-right\n3 for lower-right\n4 for lower-left corner\nYour selection?  ", 'green')) #light_blue'))
            corner = abs(int(prompt))
        except ValueError:
            pass
        else:
            if prompt == '':
                print('\nInvalid input! ') 
                frequency_input_tester()
    return corner


# Test input validity for default parameter option
def initial_input_tester():
    while 'param' not in locals():
        try:
            prompt = input((f"\nInput 1 through 4 to update corresponding default parameter or 0 to proceed with defaults: "))
            param = abs(int(prompt))
        except ValueError:
            pass
        else:
            if prompt == '' or not isinstance(param, int):
                print('\nInvalid input! ') 
                initial_input_tester()         
    return param


# Test input validity for updating default params option
def no_input_tester(option):
    while 'prompt' not in locals():
        try:
            if option == 1:
                prompt = input(f"\nInput max frequency number: ")
            elif option == 2:
                prompt = input(f"\nInput default ROIs number: ")
            elif option == 3:
                prompt = input(f"\nInput max Rois number: ")
            elif option == 4:
                prompt = input(f"\nInput number of histogram bins: ")
            number = abs(int(prompt))
        except ValueError:
            pass
        else:
            if prompt == '':
                no_input_tester(option)
    return number


# Test generating output folder to store DataFrame to a csv file
def test_for_output():
        global path_out, iteration, file
        try:
            os.makedirs(path_out, exist_ok=False)
            print("Output directory '%s' created" % path_out)
            output = True
        except OSError as error:
            if (not os.path.exists(os.path.join(os.getcwd(), f'{file}_{iteration}'))):
                path_out = os.path.join(os.getcwd(), f'{file}_{iteration}')
                os.makedirs(path_out, exist_ok=False)
                file_next = os.path.basename(path_out)
                print("\nNext output folder '%s' was created" % file_next)
                output = True
            else:
                iteration += 1
                output = False
        return output


# Print the dafault parameters at start
print(colored(f'\nDefault parameters are:\n1) Maximum frequency = {max_freq_number}\n2) Default ROIs no. = {default_rois_no}\n3) Maximum ROIs no. = {max_rois_number}\n4) Hist. bins = {histogram_bin_no}\n', 'cyan'))


# Prompt to update default parameters when required
update_init = False
init_param = True
while init_param:
    init_param = initial_input_tester()
    if init_param in [1, 2, 3, 4]:
        update_init = True
    if init_param > 4:
        while init_param > 4:
            print('\nInvalid input! ') 
            init_param = initial_input_tester()
    if init_param == 1:
        max_freq_number = no_input_tester(1)
    elif init_param == 2:
        default_rois_no = no_input_tester(2)
    elif init_param == 3:
        max_rois_number = no_input_tester(3)
    elif init_param == 4:
        histogram_bin_no = no_input_tester(4)


# Show updated default parameters 
if update_init:
    print(colored(f'\nUpdated default parameters are:\n1) Maximum frequency = {max_freq_number}\n2) Default ROIs no. = {default_rois_no}\n3) Maximum ROIs no. = {max_rois_number}\n4) Hist. bins = {histogram_bin_no}\n', 'cyan'))


# Main loop to set ROIs, retrieve pixel values and populate DataFrame with these
def select_ROIs(images, extra_ROIs=0, first_image_val=0, rois_no=default_rois_no):
    # Set variables
    global df 
    global dicts_list
    global ROIs
    global final_Rois_list
    global roi_box_side_list
    global rois_list
    global slider_max 
    global image_number
    global images_subset
    global binding_id
    global corrections
    global total_regions 
    global default_rois_no
    global maxi_roi_no
    global multiple
    global columns
    columns = []
    image_no = 0
    side = ()

  
    # Iterate through all images in the tif stack (multipage-tiff-file video)
    for image in images:
        regions = []
        # In case of the first image
        if image_no == 0:
            # Iterate through setting all ROIs
            for region in range(rois_no):  
                move = Move_ROI(region, images, regions, side)
                move.show()
                scale = Scale_ROI(region, images)
                scale.show()
                regions.append((int(xx), int(yy)))   
                side = side + (int(w),) 
                print(f"Roi's width/height = {int(w)} pixels")


            # Show 1st image to add selected regions of interest (ROIs)
            fig, ax = plt.subplots()
            ax.imshow(images[image_no][:,:], cmap='gray', interpolation='none')
            ax.set_title('All selected ROIs')
            ax.set_xlabel('Pixel no.')
            ax.set_ylabel('Pixel no.')
   

            # Remove potential duplicate ROIs
            ROIs = []
            for el in regions:
                if el not in ROIs:
                    ROIs.append(el)


            # Count number of ROIs depending on the chosen menu case
            if extra_ROIs != 2:                                   
                total_regions = len(ROIs)
            else:
                total_regions = total_regions + len(ROIs)  
           

            # Initiate dictionaries to store ROIS' pixel values
            dict = {}
            dict1 = {}
            

            # Show selected regions for the 1st image frame
            counter = 1
            for roi in ROIs:
                rect = patches.Rectangle(roi, side[counter-1], side[counter-1], linewidth=1, edgecolor='r', facecolor='none')
                ax.add_patch(rect)


                # Get the bounding box of the rectangle
                bbox = rect.get_bbox()


                # Extract pixel values from the image frame within the rectangle/square ROI
                pixel_values = images[image_no][int(bbox.ymin):int(bbox.ymax), int(bbox.xmin):int(bbox.xmax)]


                # Update ROIs' list when adding one extra ROI
                if extra_ROIs != 2:                                
                    # Build a dictionary with ROIs as keys and pixel values as corresponding vaules for other than 'add one ROI' menu's options 
                    dict[f"ROI_no.{counter}"] = [i for i in(itertools.chain(*list(pixel_values)))]
                    counter += 1
                    

            # Build a list of all dictionaries for ROIs and region sizes
            if  extra_ROIs != 2:                                          
                if  first_image_val == 0 and multiple == False:
                    dicts_list.insert(image_no, dict) 
                    final_Rois_list.insert(image_no, ROIs) 
                    roi_box_side_list.insert(image_no, side) 
                elif first_image_val != 0 or multiple == True:
                     dicts_list[image_no] = dict
                     final_Rois_list[image_no + first_image_val] = ROIs
                     roi_box_side_list[image_no + first_image_val] = side 


            # Populate DataFrame for the first image frame when starting the processing 
            if first_image_val == 0 and multiple == False:
                rois_list.insert(0, len(ROIs))
                df = df._append(dict, ignore_index = True)


            # Update DataFrame for corrected ROIs starting from the first image frame
            elif first_image_val == 0 and multiple == True:
                # Add columns to DataFrame for lately added ROIs
                if  total_regions - max(rois_list) > 0: # and max(rois_list) != 1:                                          
                    for discrepancy in range(total_regions - max(rois_list)):
                        df[f'ROI_no.{discrepancy + 1 + max(rois_list)}'] = None

                # When added/updated multiple ROIs
                if extra_ROIs != 2:                            
                    rois_list[0] = total_regions
                    df.loc[image_no] = pd.Series(dicts_list[image_no])

                # When added/updated one extra ROI
                elif extra_ROIs == 2:                          
                    # Correct position of previous ROI
                    for previous in range(0, 1):
                        x_correct = 0
                        y_correct = 0

                        # Pick up pixel values for the corrected previously processed image frames
                        pix_values = images_set[previous][int(bbox.ymin) - y_correct : int(bbox.ymax) - y_correct, int(bbox.xmin) - x_correct : int(bbox.xmax) - x_correct]
                        
                        # Populate variables and dataframe with computed values
                        dict1 = df.to_dict('records')[previous]
                        dict1[f"ROI_no.{total_regions}"] =  [i for i in(itertools.chain(*list(pix_values)))]
                        dicts_list[previous] = dict1
                        rois_list[previous] = rois_list[previous] + 1
                        df.loc[previous] = pd.Series(dicts_list[previous])
                        temp = tuple(final_Rois_list[previous]) 
                        roi1 = (roi[0] - x_correct, roi[1] - y_correct)
                        temp = temp + ((roi1),)
                        final_Rois_list[previous] = list(temp)
                        temp2 = tuple(roi_box_side_list)
                        temp3 = temp2[previous] + (int(w),) 
                        roi_box_side_list[previous] = temp3


            # Update DataFrame for corrected ROIs starting from any arbitrary image  
            elif first_image_val != 0:

                # Add columns to DataFrame for added ROIs
                if  total_regions - max(rois_list) > 0: #and max(rois_list) != 1:                         
                    for discrepancy in range(total_regions - max(rois_list)):
                        df[f'ROI_no.{discrepancy + 1 + max(rois_list)}'] = None

                # Update all image frames for added one extra ROI starting from an arbitrary image
                if  multiple == True and extra_ROIs == 2:                         
                    last_correction = (0,0,0)
                    one_before_last_correction = (0,0,0)
                    y_correct = 0
                    x_correct = 0
                    count = 0
                    start = 0

                    # Add corrections to coordinates of previously processed image frames for just added one extra ROI to an arbitrary image in the stack
                    for correction in corrections:
                        if correction[0] != 0:                     
                            if last_correction[0] == correction[0]:
                                if one_before_last_correction[0] == 0:
                                    start = last_correction[0]
                                    stop = correction[0] + 1    #????
                                    x_correct = 0
                                    y_correct = 0
                                else:
                                    start = one_before_last_correction[0]
                                    x_correct = corrections[-1][1] - last_correction[1]
                                    y_correct = corrections[-1][2] - last_correction[2]
                            else:
                                start = last_correction[0]
                                x_correct = corrections[-1][1] - correction[1]
                                y_correct = corrections[-1][2] - correction[2]
                            if len(corrections) > 1:
                                if correction == corrections[-1] and corrections[0][0] != 0 and correction != corrections[1]:
                                    start = correction[0]         # added
                                    stop = correction[0] + 1   
                                    x_correct = 0
                                    y_correct = 0
                                elif corrections[0][0] == 0 and correction == corrections[1]:
                                    start = 0        # added
                                    stop = correction[0] + 1   
                                    x_correct = 0
                                    y_correct = 0
                                else:
                                    stop = correction[0]
                                    if one_before_last_correction[0] == 0 and correction == corrections[-1] and last_correction == corrections[0]:
                                        stop = correction[0] + 1         
                            else:
                                start = 0       
                                stop = correction[0] + 1  
                                x_correct =  0
                                y_correct =  0

                            # Correct position of previous ROIs   
                            for previous in range(start, stop):
                                # Pick up pixel values for the corrected previously processed images
                                pix_values = images_set[previous][int(bbox.ymin) - y_correct : int(bbox.ymax) - y_correct, int(bbox.xmin) - x_correct : int(bbox.xmax) - x_correct]
                                if ((int(bbox.ymin) - y_correct) <= 0 and (int(bbox.ymax) - y_correct) <= 0) or ((int(bbox.xmin) - x_correct) <= 0 and (int(bbox.xmax) - x_correct) <= 0) or any(len(sublist) == 0 for sublist in pix_values): #np.isnan(pix_values)
                                    pix_values = np.array([[0.0 for _ in range(pix_values.shape[0])] for _ in range(pix_values.shape[0])])
                                if ((int(bbox.ymin) - y_correct) >= 240 and (int(bbox.ymax) - y_correct) >= 240) or ((int(bbox.xmin) - x_correct) >= 320 and (int(bbox.xmax) - x_correct) >= 320) or any(len(sublist) == 0 for sublist in pix_values):
                                    pix_values = np.array([[0.0 for _ in range(pix_values.shape[0])] for _ in range(pix_values.shape[0])])
                              
                                # Update variables
                                dict1 = df.to_dict('records')[previous]
                                dict1[f"ROI_no.{total_regions}"] =  [i for i in(itertools.chain(*list(pix_values)))] # list(itertools.chain.from_iterable(pix_values))
                                dicts_list[previous] = dict1
                                rois_list[previous] = rois_list[previous] + 1
                                df.loc[previous] = pd.Series(dicts_list[previous])
                                temp = tuple(final_Rois_list[previous]) 
                                roi1 = (roi[0] - x_correct, roi[1] - y_correct)
                                temp = temp + ((roi1),)
                                final_Rois_list[previous] = list(temp)
                                temp2 = tuple(roi_box_side_list)
                                temp3 = temp2[previous] + (int(w),) 
                                roi_box_side_list[previous] = temp3
                                if count >= 1:
                                    one_before_last_correction = last_correction # last_corr_image  
                                last_correction = correction
                                count += 1
                        else:
                            count += 1

                # Update current image 'in correcting-ROIs loop' for added one extra ROI   
                else:
                    rois_list[first_image_val] = len(ROIs)
                    df.loc[first_image_val] = pd.Series(dict)
            plt.show()
            image_no += 1


        # In the case of the next image frames after the first one has been processed
        else:  
            dict2 = {}
            counter = 1
            for roi in ROIs:
                # Extract pixel values from the image within the rectangle/square
                pixels = images[image_no][int(roi[1]):int(roi[1] + side[counter-1]), int(roi[0]):int(roi[0] + side[counter-1])]
                temp2 = ()

                # Add one extra ROI
                if  multiple == True and extra_ROIs == 2:                 #  +++     rois_no == 1 and         #ADDED and multiple == True
                    temp = tuple(final_Rois_list[first_image_val + image_no]) 
                    temp = temp + ((roi),)
                    final_Rois_list[first_image_val + image_no] = list(temp)
                    temp2 = tuple(roi_box_side_list)
                    temp3 = temp2[image_no + first_image_val] + (int(w),) 
                    roi_box_side_list[image_no + first_image_val] = temp3
                else:
                    dict[f"ROI_no.{counter}"] = [i for i in (itertools.chain(*list(pixels)))] #[pixels]
                    counter += 1


            # Update variables in the case of choosing an option of multiple ROIs processing 
            if  extra_ROIs != 2:                                          
                if  first_image_val == 0 and multiple == False:
                    dicts_list.insert(image_no, dict) 
                    final_Rois_list.insert(image_no, ROIs) 
                    roi_box_side_list.insert(image_no, side)
                elif first_image_val != 0 or multiple == True:
                     dicts_list[image_no] = dict
                     final_Rois_list[image_no + first_image_val] = ROIs
                     roi_box_side_list[image_no + first_image_val] = side  
        
            
            # When starting current iteration from the first image of selected stack subset 
            if first_image_val == 0:
                # When starting from the absolute first image of the processed stack
                if multiple == False:
                    rois_list.insert(image_no, len(ROIs))
                    df = df._append(dict, ignore_index = True)

                # When starting from the absolute first image of the processed stack in subsequent iteration
                elif multiple == True:
                    # Multiple ROIs number case
                    if  extra_ROIs != 2:                                                   
                        rois_list[image_no] = total_regions
                        df.loc[image_no] = pd.Series(dicts_list[image_no])

                    # Adding single ROI case
                    else:
                        dict2 = df.to_dict('records')[image_no]   
                        dict2[f"ROI_no.{total_regions}"] =  [i for i in(itertools.chain(*list(pixels)))]   
                        dicts_list[image_no] = dict2
                        rois_list[image_no] = total_regions 
                        df.loc[image_no] = pd.Series(dicts_list[image_no])

            # When starting current iteration from other than first image of selected stack subset 
            elif first_image_val != 0:
                # When adding one extra ROI
                if  extra_ROIs == 2:                                                       
                    dict2 = df.to_dict('records')[image_no + first_image_val]   
                    dict2[f"ROI_no.{total_regions}"] =  [i for i in(itertools.chain(*list(pixels)))] 
                    dicts_list[image_no + first_image_val] = dict2
                    rois_list[image_no + first_image_val] = total_regions 
                    df.loc[image_no + first_image_val] = pd.Series(dicts_list[image_no + first_image_val])  
                
                # When setting multiple new ROIs
                else:
                    rois_list[image_no + first_image_val] = len(ROIs)
                    df.loc[image_no + first_image_val] = pd.Series(dict)
            plt.show()
            image_no += 1
      

    # SHOW ALL PROCESSED IMAGES including processed ROIs

    # Display all image frsames for inspection using a slider after ROIs' initial processing 
    fig, ax = plt.subplots()
    ax.imshow(images[0], cmap='gray')
    ax.set_title('Image selector')
    ax.set_xlabel('Pixel no.')
    ax.set_ylabel('Pixel no.')


    # Show ROIs
    meter = 0
    for roi in ROIs:
        rect = patches.Rectangle(roi, side[meter], side[meter], linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(rect)
        meter += 1


    # Create the slider to browse through image frames
    axcolor = 'lightgoldenrodyellow'
    ax_slider = plt.axes([0.2, 0.01, 0.65, 0.03], facecolor=axcolor)
    slider = Slider(ax_slider, 'Image no.', 0, slider_max, valinit=0, valfmt='%d')


    # Update function for the slider
    def update(val):
        # Update the image based on the slider value
        new_image = images[math.floor(val)]
        ax.imshow(new_image, cmap='gray')
        ax.set_title('Image selector')
        ax.set_xlabel('Pixel no.')
        ax.set_ylabel('Pixel no.')
        nonlocal image_val

        # Pick up a current image number in the stack at a window closing
        image_val = math.floor(val)
        fig.canvas.draw_idle
        
        # Show all selected ROIs in the current image frame
        meter = 0
        for roi in ROIs:
            rect = patches.Rectangle(roi, side[meter],  side[meter], linewidth=1, edgecolor='r', facecolor='none')
            ax.add_patch(rect)
            meter += 1
    slider.on_changed(update)
    plt.show()


    # Update: 1)'first_image_val' variable with an image number for lately corrected ROIs, and 2)'images_subset' variable storing image frames still left in the stack to further inspect and process
    if  'image_val' not in locals():
        image_val = 0
        image_number = image_val
    image_number = image_val
    first_image_val = first_image_val + image_number
    images_subset = images[image_number:]
    image_array = np.array(images_subset)
    slider_max = image_array.shape[0] - 1
    if list(dict.keys()) > columns:
        columns = dict.keys()


    # Compute relocation corrections to update ROIs' positions relative to images
    x_mass = y_mass = 0
    if 1: #extra_ROIs != 2: #rois_no != 1 or multiple == False:
        for roi in ROIs:
            x_mass += int(roi[0])
            y_mass += int(roi[1])
        x_mass = round(x_mass/len(ROIs))
        y_mass = round(y_mass/len(ROIs))
        corrections.append((first_image_val, x_mass, y_mass))   

        
    # Return first_image_val (with absolute image number in the stack for lately corrected  ROIs)
    multiple = True
    return first_image_val


# MAIN
if __name__ == "__main__":


    # Initiate variables
    global df
    df = pd.DataFrame()
    df_2 = pd.DataFrame()
    global rois_list
    rois_list = []
    global total_regions 
    global dicts_list
    global final_Rois_list
    global first_image_val
    dicts_list = []
    total_regions = 0
    corrections = []
    final_Rois_list = []
    roi_box_side_list = []
    roi_box_side = 10
    w = h = 10 
    multiple = False


    # Input name & location of an input tif stack
    while True: 
        try:
            # Specify the absolute path
            filename = input(colored(f'\nType a file name with .tif extension if it is in the aplication directory (or copy & paste absolute path directory from File Explorer) or hit enter to proceed with default FLIR0787.tif\n', 'red'))
            # Set default input file
            if filename == '':
                filename = 'FLIR0787.tif'

            # Make sure the file has .tif extension
            else:
                extension = os.path.splitext(filename)[1]
                assert  extension == ".tif"
        except:
            continue
        else:
            break


    # Specify the absolute path for the input file
    path = r'{}'.format(filename)  
    path = os.path.abspath(path)


    # Digest the multistack tiff file and extract a subset of images
    _, images_all = cv2.imreadmulti(path, [], cv2.IMREAD_UNCHANGED) 
    n = frequency_input_tester(max_freq_number)
    if n == 0 or n > max_freq_number:
        while n == 0 or n > max_freq_number:
            print('\nInvalid input! ') 
            n = frequency_input_tester(max_freq_number)
    images_set = (images_all[::n])
   

    # Select a subset of images for processing
    images = (images_all[::n])
    image_array = np.array(images)

    
    # Create a slider associated with image's consecutive number
    slider_max = image_array.shape[0] - 1

  
    # Iterate through the main loop to generate ROIs, pick their pixel values, and store them in the temporary variables and DataFrame
    first_image_val = select_ROIs(images)
    extra_ROIs = rois_no_input_tester(max_rois_number=10)
    if n == 0 or extra_ROIs > max_rois_number:
        while n == 0 or extra_ROIs > max_rois_number:
            print('\nInvalid input! ') 
            extra_ROIs = rois_no_input_tester(max_rois_number=10)


    # UI menu to select a number of ROIs to update when a feet's image significantly shifts 
    while True:
        # Select same as initial no. of ROIS to correct an image with shifted ROIs positions
        if extra_ROIs == 1:
            first_image_val = select_ROIs(images_subset, extra_ROIs, first_image_val)
            extra_ROIs = rois_no_input_tester(max_rois_number=10)
            if n == 0 or extra_ROIs > max_rois_number:
                while n == 0 or extra_ROIs > max_rois_number:
                    print('\nInvalid input! ') 
                    extra_ROIs = rois_no_input_tester(max_rois_number=10)

        # Select adding one extra ROI option
        elif extra_ROIs == 2:
            rois_no = 1
            first_image_val = select_ROIs(images_subset, extra_ROIs, first_image_val, rois_no)
            extra_ROIs = rois_no_input_tester(max_rois_number=10)
            if n == 0 or extra_ROIs > max_rois_number:
                while n == 0 or extra_ROIs > max_rois_number:
                    print('\nInvalid input! ') 
                    extra_ROIs = rois_no_input_tester(max_rois_number=10)

        # Select arbitrary no. of ROIS (>=3) 
        elif type(extra_ROIs) == int and extra_ROIs != 1 and extra_ROIs != 2 and extra_ROIs != 0:
            rois_no = extra_ROIs
            first_image_val = select_ROIs(images_subset, extra_ROIs, first_image_val, rois_no)
            extra_ROIs = rois_no_input_tester(max_rois_number=10)
            if n == 0 or extra_ROIs > max_rois_number:
                while n == 0 or extra_ROIs > max_rois_number:
                    print('\nInvalid input! ') 
                    extra_ROIs = rois_no_input_tester(max_rois_number=10)
        else:
            break


    # PLOT OUTCOME CHARTS

    # Display images plus computed charts against a slider selector
    image_array = np.array(images_set)
    slider_max = image_array.shape[0] 
    fig = plt.figure(constrained_layout=False, figsize=(14, 9))   # True??
    gs0 = fig.add_gridspec(1, 2)
    gs00 = gs0[0].subgridspec(max(rois_list), 1)
    gs01 = gs0[1].subgridspec(2, 1)
    ax1 = fig.add_subplot(gs01[0])


    # Set frame image's axes
    ax1.imshow(images_set[0], cmap='gray')
    ax1.set_title('Image selector')
    ax1.set_xlabel('Pixel no.')
    ax1.set_ylabel('Pixel no.')
    fig.add_axes(ax1)


    # Create a slider
    axcolor = 'lightgoldenrodyellow'
    ax_slider = fig.add_axes([0.2, 0.01, 0.65, 0.03], facecolor=axcolor)
    slider = Slider(ax_slider, 'Image no.', 0, slider_max, valinit=0, valfmt='%d')


    # Declare two charts for average pixel values and their histogram against an frame image
    ax3 = fig.add_subplot(gs01[1])
    ax2 = [fig.add_subplot(gs00[reg]) for reg in range(max(rois_list))]


    # Replace NaNs with zeros in DataFrame's cells lists
    maxi_box_side = 0
    for reg in range(max(rois_list)):
        for ele in range(slider_max):
            if (df.loc[ele, f'ROI_no.{reg + 1}']) != None and type(df.loc[ele, f'ROI_no.{reg + 1}']) != float:
                box_side = len(df.loc[ele, f'ROI_no.{reg + 1}'])
                if box_side > maxi_box_side:
                     maxi_box_side = box_side
        df[f'ROI_no.{reg + 1}'] =  df[f'ROI_no.{reg + 1}'].apply(lambda d: d if isinstance(d, list) else [float(k) for k in (maxi_box_side * [0])])
        box_side = 0
        maxi_box_side = 0
  

    # Calculate max of pixel values stored in DataFrame's cells Python lists
    for reg in range(max(rois_list)):
        df[f'ROI_no.{reg + 1}_max'] = df[f'ROI_no.{reg + 1}'].apply(max) 


    # Update images/charts according to the slider position (agains1t image number)
    markers = ['o', 'v', 's', 'p', 'P', 'X', '*'] 
    

    def update_image(val):
        # Update the image based on the slider value
        global image_no
        global im
        global final_Rois_list
        global roi_box_side_list
        new_image = images_set[math.floor(val)]
        ax1.clear()
        ax1.set_title('Image selector')
        ax1.set_xlabel('Pixel no.')
        ax1.set_ylabel('Pixel no.')
        # Show slider indicated image 
        ax1.imshow(new_image, cmap='gray')
        image_no = math.floor(val)


        # Draw all saved ROIs
        counter = 0
        for roi in final_Rois_list[image_no]:
            rect = patches.Rectangle(roi, roi_box_side_list[image_no][counter], roi_box_side_list[image_no][counter], linewidth=1, edgecolor='r', facecolor='none')
            ax1.add_patch(rect)
            if counter + 1 < len(final_Rois_list[image_no]):
                counter += 1


        # Plot aggregate (mean) of pixel values vs. frame image
        ax3.clear()
        ax3.set_title("Rois' Max values")
        for reg in range(max(rois_list)):
            ax3.plot( list(range(len(images_set))), list(df.loc[:, f'ROI_no.{reg + 1}_max' ]), marker = markers[reg] , linestyle='dashed',
        linewidth=1, markersize=2, label=f"ROI no.{reg + 1} max values") 
        ax3.set_xlabel('Image no.')
        ax3.set_ylabel('Max Temp [C]')
        ax3.legend()


        # Draw histograms vs. ROIs per frame image selected by the slider 
        bins = histogram_bin_no 
        for reg in range(max(rois_list)):
            ax2[reg].clear()
            if reg == 0:
                ax2[reg].set_title(f'Histogram for ROIs per image')
            ax2[reg].hist((list(df.loc[image_no, f'ROI_no.{reg + 1}' ])), bins=bins, alpha=1, rwidth=0.9, label=f'ROI_no.{reg + 1} per image {image_no}')
            if reg == max(rois_list) - 1:
                ax2[reg].set_xlabel('Temp bins')
            ax2[reg].set_ylabel('Occurences')
            ax2[reg].legend()
        fig.canvas.draw_idle()
        

    # Update window's charts for frame image indicated by slider
    slider.on_changed(update_image)
    plt.show()


    # STORING DATA TO DataFrame

    # Make the output directory to store DataFrame
    file_name_with_extension = os.path.basename(path)
    file = os.path.splitext(file_name_with_extension)[0]
    path_out = os.path.join(os.getcwd(), file) 
    output = False
    iteration = 2
    while output != True:
        output = test_for_output()


    # Save ROIs data to df DataFrame (stacked version)
    df.to_csv(f'{path_out}\df_stacked.csv', sep=',')
    df_copy = df.copy()


    # Populate horizontally unstacked df_2 DataFrame 
    for reg in range(max(rois_list)):
        maximal = 0
        for ele in range(slider_max):
            box_side_squared = len(df.loc[ele, f'ROI_no.{reg + 1}'])
            if box_side_squared > maximal:
                maximal = box_side_squared
        for ele in range(slider_max):
            df.iat[ele, int(f'{reg}')] = df.loc[ele, f'ROI_no.{reg + 1}'] + [float(k) for k in ((maximal - len(df.loc[ele, f'ROI_no.{reg + 1}'])) * [0])]
        # Create columns to store unstacked data
        unstacked = ['df1_' + f'ROI_no.{reg + 1}' + '_' + str(x + 1) for x in list(range(maximal))]   
        df[unstacked] = pd.DataFrame(df[f'ROI_no.{reg + 1}'].tolist(), index= df.index)   
    df_2 = df
    

     # Remove cols with averages
    to_remove_cols = list(df_2)[:(max(rois_list) * 2)]
    df2 = df_2.drop(to_remove_cols, axis=1)


    # Split df_2 into multiple frames storing 5k data points in a single frame
    quotient = len(list(df2))// 5000
    remainder = len(list(df2)) % 5000
    step = 0
    part = 1
    if quotient > 0:
        for i in range(quotient):
            df2_part = df2[list(df2)[step: step + 5000]].copy()
            #df2_part.to_csv(f'FLIR0787_df{part}_horiz_unstacked.csv', sep=',')
            step += 5000
            part += 1
    if remainder != 0:
        df2_part = df2[list(df2)[step: step + remainder]].copy()
        #df2_part.to_csv(f'FLIR0787_df{part}_horiz_unstacked.csv', sep=',')


    # SAVE ROIs TO A VERTICALLY UNSTACKED df_3 DataFrame AND .csv FILE

    # Remove cols with averages
    to_remove_cols = list(df_copy)[-max(rois_list):]
    df_copy = df_copy.drop(to_remove_cols, axis=1)


    # Prepare data to be vertically unstacked
    maximal = 0
    for reg in range(max(rois_list)):
        for ele in range(slider_max):
            box_side_squared = len(df_copy.loc[ele, f'ROI_no.{reg + 1}'])
            if box_side_squared > maximal:
                maximal = box_side_squared

    for reg in range(max(rois_list)):
        for ele in range(slider_max):
            df_copy.iat[ele, int(f'{reg}')] = df_copy.loc[ele, f'ROI_no.{reg + 1}'] + [float(k) for k in ((maximal - len(df_copy.loc[ele, f'ROI_no.{reg + 1}'])) * [0])]


    # Unstack df dataframe vertically into a df_3 frame
    df_3 = df_copy.apply(pd.Series.explode)
    

    # Split df_3 into multiple sub-frames storing max 5k data points in a single sub-frame
    quotient = len(df_3.iloc[:]) // 5000
    remainder = len(df_3.iloc[:]) % 5000
    step = 0
    part = 1
    if quotient > 0:
        for i in range(quotient):
            df3_part = df_3.iloc[step: step + 5000].copy()
            df3_part.to_csv(f'{path_out}\df{part}_vert_unstacked.csv', sep=',')
            step += 5000
            part += 1
    if remainder != 0:
        df3_part = df_3.iloc[step: step + remainder].copy()
        df3_part.to_csv(f'{path_out}\df{part}_vert_unstacked.csv', sep=',')


    # Optionally print to the console the last sub-frame of horizontally unstacked dataframe 
    #print("\nDataFrame after insertion:\n", df2_part,'\n') 
    #print(df.info())
    