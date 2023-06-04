import os
import PySimpleGUI as sg
from PIL import Image, ImageTk

from Layout import Layout, NTAB
from PathHandler import get_folder_name_from_path, is_directory, get_file_name, get_list_of_files_in_dir,\
                        combine_path_with_root, get_path_from_user
from PathHandler import SRC_IMAGES_FOLDER, SRC_DETECT_SCRIPT, RES_IMAGES_FOLDER

from DetectionHandler import DetectionHandler

def remove_empty(l:list) -> list:
    return [x for x in l if (x != '' and x != None)]


def resize_image(img:Image.Image, size: tuple) -> Image.Image:
    return img.resize(size, Image.ANTIALIAS)

class EventHandler:

    def __init__(self, _layout:Layout) -> None:
        self.layout = _layout
        self.sg_layout = _layout.get_sg_layout()
        self.window = None

        self.flag_select_folder : bool = False
        self.flag_images_detected = False
        self.modelpath : str  = None
        self.imagelist : list = []  # used outside "__handle_select_img_btn()" only if multiple images (not folder) selection allowed.
        self.source_path : str = None
        self.output_images : list = []
        self.current_img_index : int = -1
        self.precision_value : float = self.layout.DEFAULT_PRECISION_VALUE

    def __create_window(self):
        self.window = sg.Window('Car parts detection', self.sg_layout, finalize=True, resizable=False, element_justification='center', return_keyboard_events=True)
        self.window.Size = Layout.WINDOW_SIZE

    def __set_image_view(self, image_path:str):
        #try: self.layout.update_image_path(self.window, imgpath=image_path)
        #except: 
        img = resize_image(Image.open(image_path), self.layout.get_image_field_size(self.window))
        self.layout.update_image_data(self.window, imgdata=ImageTk.PhotoImage(img))

    def __log_status(self, *_msgs):
        for _msg in _msgs: self.layout.update_status(self.window, msg=f'>>> {_msg}')

    def __is_all_data_is_set(self) -> bool:
        return bool(self.modelpath) and bool(self.source_path)

    def __try_unlock_detect_btn(self):
        if self.__is_all_data_is_set():
            self.layout.set_enabled(self.window, key=self.layout.KEY_DETECT_BTN, _enabled=True) 

    def __handle_select_model_btn(self, event_val:any):
        self.modelpath = event_val
        self.__log_status(f'Selected model: {self.modelpath}')
        self.layout.update_label(self.window, key=self.layout.KEY_SELECTED_PT_LABEL, value=self.modelpath)
        self.__try_unlock_detect_btn()

    def __handle_select_img_btn(self):
        file_types = None if self.flag_select_folder else self.layout.SELECT_IMAGES_FILTER
        initial_folder = combine_path_with_root(SRC_IMAGES_FOLDER)
        self.source_path = get_path_from_user('Select image(s) or folder with them', file_types, initial_folder)
        self.source_path = remove_empty(self.source_path)
        if len(self.source_path) == 0:
            self.source_path = None
            return
        # Note! Method was prepared to handle multiple images, but decided to use only one path of image or folder. ( get_path_from_user(multiple=True) asks for multiple files. )
        #       If you want to use multiple images, you need to change this method, __handle_detect_btn() and probably detect.py script.)
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
        self.__set_image_view(self.imagelist[0])
        self.__try_unlock_detect_btn()
        if len(self.imagelist) > 1:
            self.layout.set_enabled(self.window, key=self.layout.KEY_NEXT_BTN, _enabled=True)
            self.layout.set_enabled(self.window, key=self.layout.KEY_SWITCHT_IMAGES_LABEL, _enabled=True)

    def __handle_precission_slider(self, event_val:any):
        self.precision_value = float(event_val)

    def __handle_select_folder_box(self, event_val:any):
        self.flag_select_folder = bool(event_val)

    def __handle_detect_btn(self):
        resultfolder = combine_path_with_root(RES_IMAGES_FOLDER)
        detectFile = combine_path_with_root(SRC_DETECT_SCRIPT)
        self.output_images = []
        self.current_img_index = -1
        self.flag_images_detected = False

        try:
            def logfromdetect(s:str)->None: self.__log_status(s)
            self.__log_status(f'Running detection...')
            DetectionHandler().detect(print=logfromdetect, weights=self.modelpath, conf_thres=self.precision_value, source=self.source_path)
            #code = os.system(f'python {detectFile} --weights {self.modelpath} --conf {self.precision_value} --source {self.source_path}')
            #if code != 0: raise Exception(f'Process return error code: {code}')
        except Exception as e:
            self.__log_status(f'[Error] Exception occured while running detection:{NTAB}{e}')    
            return

        self.current_img_index = 0
        self.output_images = get_list_of_files_in_dir(resultfolder)
        if len(self.output_images) == 0:
            self.__log_status(f'[Error] No output images found in result folder {resultfolder}')
        else:
            self.flag_images_detected = True
            self.__set_image_view(self.output_images[self.current_img_index])


    def __handle_img_switch(self, index:int):
        self.current_img_index = index
        if self.current_img_index == -1: return
        img_to_show = self.output_images[self.current_img_index] if self.flag_images_detected else self.imagelist[self.current_img_index]
        self.__set_image_view(img_to_show)

    def __handle_prev_btn(self):
        self.__handle_img_switch(self.current_img_index - 1)
        enabled = False if (self.current_img_index <= 0) else True
        self.layout.set_enabled(self.window, key=self.layout.KEY_PREV_BTN, _enabled=enabled)
        if self.current_img_index == len(self.imagelist)-2:
            self.layout.set_enabled(self.window, key=self.layout.KEY_NEXT_BTN, _enabled=True)
        
    def __handle_next_btn(self):
        self.__handle_img_switch(self.current_img_index + 1)
        enabled = False if (self.current_img_index >= len(self.imagelist)-1) else True
        self.layout.set_enabled(self.window, key=self.layout.KEY_NEXT_BTN, _enabled=enabled)
        if self.current_img_index == 1:
            self.layout.set_enabled(self.window, key=self.layout.KEY_PREV_BTN, _enabled=True)

    def __run(self):
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
        try:
            self.__run()
        except Exception as e:
            raise Exception(f'Exception occured while running GUI: {e}')
        finally:
            self.window.close()    