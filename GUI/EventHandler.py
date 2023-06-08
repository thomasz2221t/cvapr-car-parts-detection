import PySimpleGUI as sg
from PIL import Image, ImageTk

from Layout import Layout, NTAB
from PathHandler import get_folder_name_from_path, is_directory, get_file_name, get_list_of_files_in_dir,\
                        combine_path_with_project_root, combine_path_with_gui_root, get_path_from_user, \
                        get_newest_folder_in_dir
from PathHandler import SRC_IMAGES_FOLDER, RES_IMAGES_FOLDER

from DetectionHandler import DetectionHandler

def remove_empty(l:list) -> list:
    """ Removes empty strings and None values from list. """
    return [x for x in l if (x != '' and x != None)]

def resize_image(img:Image.Image, size: tuple) -> Image.Image:
    """ Resizes image to given size. """
    return img.resize(size, Image.ANTIALIAS)

class EventHandler:
    """ Class handling events from GUI. Only run() method should be called from outside of this class.
        Available events: 
        - 'Select model' button
        - 'Select images' button
        - 'Select folder' checkbox
        - 'Detect' button
        - 'Precision' slider
        - 'Show next image' button
        - 'Show previous image' button
    """

    def __init__(self, _layout:Layout) -> None:
        self.layout    : Layout    = _layout                 # My class handling layout
        self.sg_layout : list      = _layout.get_sg_layout() # PySimpleGUI layout
        self.window    : sg.Window = None                    # PySimpleGUI Window object

        self.flag_select_folder   : bool  = False # Flag for remembering if show open folder (true) or file (false) dialog
        self.flag_images_detected : bool  = False # Flag for remembering if images were detected
        self.modelpath            : str   = None  # Provided by user to .pt file with pretrain headers
        self.imagelist            : list  = []    # List of paths to image(s) selected by user
        self.source_path          : str   = None  # Path to image or folder with images selected by user
        self.output_images        : list  = []    # List of paths to output images
        self.current_img_index    : int   = -1    # Index of currently displayed image
        self.precision_value      : float = self.layout.DEFAULT_PRECISION_VALUE # For remembering precision value set by user

    def __create_window(self)->None:
        """ Creates window with layout passed as class constructor's argument. """
        self.window = sg.Window('Car parts detection', self.sg_layout, finalize=True, resizable=False, element_justification='center', return_keyboard_events=True)
        self.window.Size = Layout.WINDOW_SIZE

    def __set_image_view(self, image_path:str)->None:
        """ Displays image from given path in window. """
        img = resize_image(Image.open(image_path), self.layout.get_image_field_size(self.window))
        self.layout.update_image_data(self.window, imgdata=ImageTk.PhotoImage(img))

    def __log_status(self, *_msgs)->None:
        """ Prints given messages to status field. """
        for _msg in _msgs: self.layout.update_status(self.window, msg=f'>>> {_msg}')
        self.window.refresh()

    def __is_all_data_is_set(self) -> bool:
        """ Checks if all data needed to start detection (model image(s) paths) is set. """
        return bool(self.modelpath) and bool(self.source_path)

    def __try_unlock_detect_btn(self)->None:
        """ Enables detect button if all data needed to start detection is set. """
        if self.__is_all_data_is_set():
            self.layout.set_enabled(self.window, key=self.layout.KEY_DETECT_BTN, _enabled=True) 

    def __handle_select_model_btn(self, event_val:any)->None:
        """ Handles event from clicking "select model" button. """
        self.modelpath = event_val
        self.__log_status(f'Selected model: {self.modelpath}')
        self.layout.update_label(self.window, key=self.layout.KEY_SELECTED_PT_LABEL, value=self.modelpath)
        self.__try_unlock_detect_btn()

    def __handle_select_img_btn(self)->None:
        """ Handles event from clicking "select image" button. Sets source_path and imagelist. """
        file_types = None if self.flag_select_folder else self.layout.SELECT_IMAGES_FILTER
        initial_folder = combine_path_with_project_root(SRC_IMAGES_FOLDER)
        self.source_path = get_path_from_user('Select image(s) or folder with them', file_types, initial_folder)
        self.source_path = remove_empty(self.source_path)
        if len(self.source_path) == 0:
            self.source_path = None
            return
        # Note! Method was prepared to handle multiple images, but decided to use only one path of image or folder. ( get_path_from_user(multiple=True) asks for multiple files. )
        #       If you want to use multiple images (but not whole folder), you need to change this method, __handle_detect_btn() and probably detect.py script.)
        self.source_path = self.source_path[0]
        if is_directory(self.source_path):
            self.imagelist = get_list_of_files_in_dir(self.source_path)
        else:
            self.imagelist = [self.source_path]
        msg =  f'Image folder: ' + f'"/{get_folder_name_from_path(self.source_path)}" [{len(self.imagelist)} image(s)]'  
        self.__log_status(f'Selected images: {NTAB}- {(NTAB+"- ").join([get_file_name(path) for path in self.imagelist])}')
        self.layout.update_label(self.window, key=self.layout.KEY_SELECTED_IMG_LABEL, value=msg)

        self.flag_images_detected = False
        self.current_img_index = 0
        self.__handle_img_switch(self.current_img_index)
        self.__try_unlock_detect_btn()
        if len(self.imagelist) > 1:
            self.layout.set_enabled(self.window, key=self.layout.KEY_NEXT_BTN, _enabled=True)
            self.layout.set_enabled(self.window, key=self.layout.KEY_SWITCHT_IMAGES_LABEL, _enabled=True)

    def __handle_precission_slider(self, event_val:any):
        """ Handles event from changing precision slider. Sets precision_value."""
        self.precision_value = float(event_val)

    def __handle_select_folder_box(self, event_val:any):
        """ Handles event from clicking "select folder" checkbox. Sets flag_select_folder."""
        self.flag_select_folder = bool(event_val)

    def __handle_detect_btn(self):
        """ Handles event from clicking "detect" button. Runs detection from DetectHandler class. 
        Sets output_images and displays first image if detection was successful. """
        resultfolder = combine_path_with_gui_root(RES_IMAGES_FOLDER)
        #detectFile = combine_path_with_project_root(SRC_DETECT_SCRIPT) # deprecated
        self.output_images = []
        self.flag_images_detected = False

        try:
            def logfromdetect(s:str)->None: self.__log_status(s)
            DetectionHandler().detect(print=logfromdetect, weights=self.modelpath, conf_thres=self.precision_value, source=self.source_path)
            #code = os.system(f'python {detectFile} --weights {self.modelpath} --conf {self.precision_value} --source {self.source_path}')
            #if code != 0: raise Exception(f'Process return error code: {code}')
        except Exception as e:
            self.__log_status(f'[Error] Exception occured while running detection:{NTAB}{e}')    
            return

        result_path = get_newest_folder_in_dir(resultfolder)
        try: self.output_images = get_list_of_files_in_dir(result_path)
        except Exception as e: self.__log_status(f'[Error] Cannot access files in given result folder:{NTAB}{e}')
        
        if len(self.output_images) == 0:
            self.__log_status(f'[Error] No output images found in result folder {resultfolder}')
        else:
            self.flag_images_detected = True
            if self.current_img_index == -1: self.current_img_index = 0
            self.__handle_img_switch(self.current_img_index)
        self.__log_status(f'Result images fetched from {result_path} folder.')


    def __handle_img_switch(self, index:int):
        """ Handles event from clicking "next" or "prev" button. Sets current_img_index and displays image. """
        self.current_img_index = index
        if self.current_img_index == -1: return
        img_to_show = self.output_images[self.current_img_index] if self.flag_images_detected else self.imagelist[self.current_img_index]
        self.__set_image_view(img_to_show)
        self.layout.update_label(self.window, key=self.layout.KEY_SWITCHT_IMAGES_LABEL, 
                                 value=f'Image {self.current_img_index+1:02d}/{(len(self.output_images) if self.flag_images_detected else len(self.imagelist)):02d}')

    def __handle_prev_btn(self):
        """ Handles event from clicking "prev" button. Calls __handle_img_switch() and sets enabled state of "prev" and "next" buttons. """
        self.__handle_img_switch(self.current_img_index - 1)
        enabled = False if (self.current_img_index <= 0) else True
        self.layout.set_enabled(self.window, key=self.layout.KEY_PREV_BTN, _enabled=enabled)
        if self.current_img_index == len(self.imagelist)-2:
            self.layout.set_enabled(self.window, key=self.layout.KEY_NEXT_BTN, _enabled=True)
        
    def __handle_next_btn(self):
        """ Handles event from clicking "next" button. Calls __handle_img_switch() and sets enabled state of "prev" and "next" buttons. """
        self.__handle_img_switch(self.current_img_index + 1)
        enabled = False if (self.current_img_index >= len(self.imagelist)-1) else True
        self.layout.set_enabled(self.window, key=self.layout.KEY_NEXT_BTN, _enabled=enabled)
        if self.current_img_index == 1:
            self.layout.set_enabled(self.window, key=self.layout.KEY_PREV_BTN, _enabled=True)

    def __run(self):
        """ Runs main loop of GUI. Initializes window and handles defined events. Not to be called directly. 
        None of called handlers raise their own exceptions - everything should be handled here and logged in status bar.  """
        self.__create_window()
        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break
            if event == Layout.KEY_SELECT_PT_BTN:
                self.__handle_select_model_btn(values[event])
            elif event == Layout.KEY_SELECT_IMG_BTN:
                self.__handle_select_img_btn()
            elif event == Layout.KEY_PRECISSION_SLIDER:
                self.__handle_precission_slider(values[event])
            elif event == Layout.KEY_SELECT_FOLDER_BOX:
                self.__handle_select_folder_box(values[event])
            elif event == Layout.KEY_DETECT_BTN:
                self.__handle_detect_btn()
            elif event == Layout.KEY_PREV_BTN:
                self.__handle_prev_btn()
            elif event == Layout.KEY_NEXT_BTN:
                self.__handle_next_btn()
            else: 
                pass

    def run(self):
        """ Runs GUI. In __run() method, initializes window and handles defined events. Raises Exception if any error occured."""
        try:
            self.__run()
        except Exception as e:
            raise Exception(f'Exception occured while running GUI: {e}')
        finally:
            self.window.close()    