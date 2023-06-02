from Layout import Layout, NTAB
import PySimpleGUI as sg
from datetime import datetime

from PathHandler import get_folder_name_from_path, is_directory, get_file_name, get_list_of_files_in_dir, combine_path_with_root, get_path_from_user
from PathHandler import SRC_IMAGES_FOLDER

def remove_empty(l:list) -> list:
    return [x for x in l if (x != '' or x != None)]

class EventHandler:

    def __init__(self, _layout:Layout) -> None:
        self.layout = _layout
        self.sg_layout = _layout.get_sg_layout()
        self.window = None

        self.modelpath : str  = None
        self.imagelist : list = []
        self.flag_select_folder : bool = False

    def __create_window(self):
        self.window = sg.Window('Car parts detection', self.sg_layout, finalize=True, resizable=False, element_justification='center', return_keyboard_events=True)
        self.window.Size = Layout.WINDOW_SIZE

    def __log_status(self, _msg:str):
        self.layout.update_status(self.window, msg=f'>>> {_msg}')

    def __handle_select_model_btn(self, event_val:any):
        self.modelpath = event_val
        self.__log_status(f'Selected model: {self.modelpath}')
        self.layout.update_label(self.window, key=self.layout.KEY_SELECTED_MODEL_LABEL, value=self.modelpath)

    def __handle_select_img_btn(self):
        file_types = None if self.flag_select_folder else self.layout.SELECT_IMAGES_FILTER
        initial_folder = combine_path_with_root(SRC_IMAGES_FOLDER)
        self.imagelist = get_path_from_user('Select image(s) or folder with them', file_types, initial_folder) 
        self.imagelist = remove_empty(self.imagelist)
        if len(self.imagelist) == 0:
            return
        if is_directory(self.imagelist[0]):
            self.imagelist = get_list_of_files_in_dir(self.imagelist[0])
        msg =  f'Image folder: ' + f'"/{get_folder_name_from_path(self.imagelist[0])}" [{len(self.imagelist)} image(s)]'  
        self.__log_status(f'Selected images: {NTAB}- {(NTAB+"- ").join([get_file_name(path) for path in self.imagelist])}')
        self.layout.update_label(self.window, key=self.layout.KEY_SELECTED_IMG_LABEL, value=msg)

    def __handle_precission_slider(self, event_val:any):
        pass

    def __handle_select_folder_box(self, event_val:any):
        self.flag_select_folder = bool(event_val)

    def __handle_detect_btn(self, event_val:any):
        pass

    def __handle_prev_btn(self, event_val:any):
        pass

    def __handle_next_btn(self, event_val:any):
        pass


    def __run(self):
        self.__create_window()
        while True:
            event, values = self.window.read()
            if event == sg.WIN_CLOSED:
                break
            if event == Layout.KEY_SELECT_MODEL_BTN:
                self.__handle_select_model_btn(values[event])
            elif event == Layout.KEY_SELECT_IMG_BTN:
                self.__handle_select_img_btn()
            elif event == Layout.KEY_PRECISSION_SLIDER:
                pass
            elif event == Layout.KEY_SELECT_FOLDER_BOX:
                self.__handle_select_folder_box(values[event])
            elif event == Layout.KEY_DETECT_BTN:
                pass
            elif event == Layout.KEY_PREV_BTN:
                pass
            elif event == Layout.KEY_NEXT_BTN:
                pass
            else: 
                pass

    def run(self):
        try:
            self.__run()
        except Exception as e:
            raise Exception(f'Exception occured while running GUI: {e}')
        finally:
            self.window.close()    