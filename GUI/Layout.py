import PySimpleGUI as sg
from PathHandler import combine_path_with_project_root
from PathHandler import SRC_PT_HEADERS_FOLDER

TAB = '       ' 
NTAB = '\n' + TAB

class Layout:

    KEY_SELECT_PT_BTN = '-select_model_btn-'
    KEY_SELECT_IMG_BTN = '-select_img_btn-'
    KEY_PRECISSION_SLIDER = '-precission_slider-'
    KEY_DETECT_BTN = '-detect-'
    KEY_IMAGE = '-image-'
    KEY_TXT_STATUS = '-txt_status-'
    KEY_PREV_BTN = '-prev-'
    KEY_NEXT_BTN = '-next-'
    KEY_SELECTED_PT_LABEL = '-selected_model_label-'
    KEY_SELECTED_IMG_LABEL = '-selected_img_label-'
    KEY_SWITCHT_IMAGES_LABEL = '-switch_images_label-'
    KEY_SELECT_FOLDER_BOX = '-select_folder_box-'

    DEFAULT_PRECISION_VALUE = 0.2
    WINDOW_SIZE = (800, 700)
    
    SELECT_IMAGES_FILTER = (("JPEG (*.jpg)", "*.jpg"), ("PNG (*.png)", "*.png"), ("BMP (*.bmp)", "*.bmp"), ("All files (*.*)", "*.*"))
    SELECT_PT_FILTER = (("Pytorch model (*.pt)", "*.pt"), ("All files (*.*)", "*.*"))

    __IMAGE_FRAME_SIZE = (525, 400)
    __MENU_FRAME_SIZE = (WINDOW_SIZE[0] - __IMAGE_FRAME_SIZE[0], __IMAGE_FRAME_SIZE[1])

    __MAX_STATUS_CHARS = 2147483647          # INT32 max value  
    __MAX_MENU_TEXT_LENGTH_MAGIC_NUMBER = 31 # TODO: find a better way to calculate this

    def __init__(self, _theme='Dark') -> None:
        self.status_length = 0 
        self.initial_pt_headers_path = combine_path_with_project_root(SRC_PT_HEADERS_FOLDER)
        
        sg.theme(_theme)
        self.sg_layout = self.__create_layout()
        
    
    def __create_layout(self)->list['list[sg.Element]']:
        """Creates PySimpleGUI layout representation for application"""
        left_frame_content = [
            [sg.Image(source='', filename='No image selected', key=self.KEY_IMAGE, expand_x=True, expand_y=True)]]
        right_frame_content = [
            [sg.Text()],
            [sg.FileBrowse('Select pretrained model',key=self.KEY_SELECT_PT_BTN, file_types=self.SELECT_PT_FILTER, initial_folder=self.initial_pt_headers_path, size=(20,1), enable_events=True, visible=True)],
            [sg.Text('[No model selected]', key=self.KEY_SELECTED_PT_LABEL)],
            [sg.Text()],
            [sg.Button('Select images', key=self.KEY_SELECT_IMG_BTN, size=(20,1), enable_events=True, visible=True)],
            [sg.Text('[No images selected]', key=self.KEY_SELECTED_IMG_LABEL)],
            [sg.Stretch(), sg.Checkbox('Select Folder', key=self.KEY_SELECT_FOLDER_BOX, enable_events=True, pad=((0,3),(10, 0)))],
            [sg.HorizontalSeparator(pad=((0,0),(5, 0)))],
            [sg.VStretch()],
            [sg.Slider(range=(0, 1), orientation='h', resolution=.1, default_value=self.DEFAULT_PRECISION_VALUE, size=(15, 15), key=self.KEY_PRECISSION_SLIDER)],
            [sg.Text('Set detection precission', pad=((0,0),(0, 10)))],
            [sg.Button('Detect car parts', key=self.KEY_DETECT_BTN, size=(20,1), enable_events=True, visible=True, disabled=True)],
            [sg.VStretch()],
            [sg.HorizontalSeparator(pad=((0,0),(0, 5)))],
            [sg.Text('Switch images', key=self.KEY_SWITCHT_IMAGES_LABEL, pad=((0,0),(0, 10)), text_color='grey')],
            [sg.Button("<- Previous", key=self.KEY_PREV_BTN, disabled=True, enable_events=True, size=(10,1), pad=((10,0),(0,15))), sg.Push(), sg.Button("Next ->", key=self.KEY_NEXT_BTN, enable_events=True, size=(10,1), pad=((0,10),(0,15)), disabled=True)]
        ]
        bottom_frame_content = [[sg.Multiline(f'>>> Welcome to car parts detection{NTAB}Select model and images to start.', key=self.KEY_TXT_STATUS, size=(40, 2), autoscroll=True, no_scrollbar=False, expand_x=True, expand_y=True, disabled=True)]]
        
        left_frame = sg.Frame('Image', left_frame_content,size=self.__IMAGE_FRAME_SIZE, element_justification='center', expand_x=True, expand_y=True, relief=sg.RELIEF_SUNKEN)
        right_frame = sg.Frame('Menu', right_frame_content,size=self.__MENU_FRAME_SIZE, element_justification='center', expand_x=True, expand_y=True, relief=sg.RELIEF_SUNKEN)
        bottom_frame = sg.Frame('Status', bottom_frame_content, element_justification='left', expand_x=True, expand_y=True, relief=sg.RELIEF_SUNKEN)

        return  [ [left_frame, right_frame],
                  [bottom_frame]
                ]

    def __trim_path_begining(self, path:str)->str:
        """ Returns path that can fit into Menu frame. If path is too long,
          it's trimmed form nearest to MAX_MENU_TEXT_LENGTH_MAGIC_NUMBER '/' character and '...' is added at the begining 
          If no '/' character is found, path is trimmed from the end. """ 
        path = path.replace('\\', '/')  
        if(len(path) > self.__MAX_MENU_TEXT_LENGTH_MAGIC_NUMBER):
            nearest_slash_index = path.find('/', len(path)-self.__MAX_MENU_TEXT_LENGTH_MAGIC_NUMBER, len(path)-1 )
            if(nearest_slash_index != -1): return '...' + path[nearest_slash_index:] 
            else: return '...'  + path[:len(path)-self.__MAX_MENU_TEXT_LENGTH_MAGIC_NUMBER] 
    
    #----------------------------------------------------------------------------------------------------------
        ## PUBLIC METHODS ##
    #----------------------------------------------------------------------------------------------------------

    def update_status(self, window:sg.Window, msg:str)->None:
        """Updates status text box with new message. If message is too long, status text box is cleared."""
        self.status_length += 1
        if self.status_length > self.__MAX_STATUS_CHARS: # clear status if it's too long
            window[self.KEY_TXT_STATUS].update(">>> Cleared status due to it's length.")
            self.status_length = 0
        window[self.KEY_TXT_STATUS].update('\n'+msg, append=True)

    def set_visibility(self, window:sg.Window, key:str, _visible:bool)->None:
        """Sets visibility of element with given key"""
        window[key].update(visible=_visible)

    def set_enabled(self, window:sg.Window, key:str, _enabled:bool)->None:
        """Sets enabled state of element with given key. Special case for KEY_SWITCHT_IMAGES_LABEL 
            - it's text color is changed: disabled - grey, enabled - default"""
        if(key==self.KEY_SWITCHT_IMAGES_LABEL): # special case for this label
            if (_enabled):  window[key].update(text_color=sg.theme_text_color())
            else:           window[key].update(text_color='grey') 
        else:
            window[key].update(disabled=(not _enabled))

    def update_image_path(self, window: sg.Window, imgpath:str)->None:
        """Sets image path for image field and updates image field with new image."""
        window[self.KEY_IMAGE].update(source=imgpath)

    def update_image_data(self, window: sg.Window, imgdata)->None:
        """ Sets image data for image field and updates image field with new image."""
        window[self.KEY_IMAGE].update(data=imgdata)

    def update_label(self, window:sg.Window, key:str, value:str)->None:
        """Updates label with given key. If key is KEY_SELECTED_PT_LABEL, path is trimmed to fit into Menu frame."""
        if(key==self.KEY_SELECTED_PT_LABEL):
            value = self.__trim_path_begining(value)
        window[key].update(value)

    def get_image_field_size(self, window:sg.Window)->tuple:
        """Returns size of image field."""
        return window[self.KEY_IMAGE].get_size()
    
    def get_sg_layout(self)->list['list[sg.Element]']:
        """Returns created PysimpleGUI layout."""
        return self.sg_layout