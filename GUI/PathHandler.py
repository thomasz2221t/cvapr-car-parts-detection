import os, glob
import PySimpleGUI as sg
from tkinter.filedialog import askdirectory, askopenfilenames

# Defines
PRETRAIN_HEADERS_EXTENTION = '.pt'
PRETRAIN_HEADERS_PREFIX = 'exp'

SRC_MODELS_FOLDER = 'yolov7/runs/train/'
SRC_IMAGES_FOLDER = 'yolov7/YOLO-image-recognition-1/test/images/'
RES_IMAGES_FOLDER = 'yolov7/runs/detect/'

FOLDER_FLAG = 'folder'
FILE_FLAG = 'file'
FILE_SPLIT_CHAR = ';'


def get_project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def combine_path_with_root(path:str) -> str:
    return os.path.join(get_project_root(), path)

def get_folder_name_from_path(path:str) -> str:
    path = os.path.normpath(path)
    return os.path.basename(os.path.dirname(path))

def get_file_name(path:str) -> str: 
    return os.path.basename(os.path.normpath(path))

def get_list_of_files_in_dir(directory:str, extention:str='') -> list:
    if not os.path.isdir(directory): raise Exception(f'Directory {directory} does not exist')
    if extention != '' and extention[0] != '.': extention = '.' + extention
    return glob.glob(directory + '/*' + extention)

    

def is_directory(path:str) -> bool:
    return os.path.isdir(path)

def is_file(path:str) -> bool:
    return os.path.isfile(path)

def get_path_from_user(title:str, file_types:tuple=None, initial_folder:str=None) -> list:
    """ :return: path to file(s) or folder(s) selected by user. 
        :param: file_types - leave empty to select folders """
    if initial_folder is None: initial_folder = get_project_root()
    if file_types is None:
        return [askdirectory(title=title, initialdir=initial_folder)]
    return list(askopenfilenames(title=title, filetypes=file_types, initialdir=initial_folder))

# Returns newest folder in directory with prefix
def get_newest_folder_in_dir(directory:str, prefix:str='exp') -> str:    
    if not os.path.isdir(directory):
        raise Exception(f'Directory {directory} does not exist')
    folders = glob.glob(directory + '/*/')    
    folders = [f for f in folders if prefix in f]
    return max(folders, key=os.path.getctime)
