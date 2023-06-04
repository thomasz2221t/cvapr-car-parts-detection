import glob
from os.path import isdir, isfile, join, normpath, basename, dirname, abspath, getmtime
from tkinter.filedialog import askdirectory, askopenfilenames, askopenfilename

# Defines
PRETRAIN_HEADERS_EXTENTION  = '.pt'
PRETRAIN_HEADERS_PREFIX     = 'exp'

SRC_PT_HEADERS_FOLDER   = 'yolov7/runs/train/'                              # Default to folder with pretrain headers
SRC_IMAGES_FOLDER       = 'yolov7/YOLO-image-recognition-1/test/images/'    # Default to folder with images to detect
RES_IMAGES_FOLDER       = 'runs/detect/'

def get_file_abspath(__file:str) -> str:
    return abspath(__file)

def get_gui_root() -> str:
    return dirname(get_file_abspath(__file__))

def get_project_root() -> str:
    return dirname(get_gui_root())

def combine_path_with_gui_root(path:str) -> str:
    return normpath(join(get_gui_root(), path))

def combine_path_with_project_root(path:str) -> str:
    return normpath(join(get_project_root(), path))

def get_folder_name_from_path(path:str) -> str:
    return basename(dirname(normpath(path)))

def get_file_name(path:str) -> str: 
    return basename(normpath(path))

def get_list_of_files_in_dir(directory:str, extention:str='') -> list:
    if not isdir(directory): raise Exception(f'Directory {directory} does not exist')
    if extention != '' and extention[0] != '.': extention = '.' + extention
    return glob.glob(directory + '/*' + extention)

def is_directory(path:str) -> bool:
    return isdir(path)

def is_file(path:str) -> bool:
    return isfile(path)

def get_path_from_user(title:str, file_types:tuple=None, initial_folder:str=None, multiple_files=False) -> list:
    """ :return: path to file(s) or folder(s) selected by user. :param: file_types - leave empty to select folders """
    if initial_folder is None: 
        initial_folder = get_project_root()
    if   file_types is None: return [askdirectory(title=title, initialdir=initial_folder)]
    elif multiple_files:     return askopenfilenames(title=title, filetypes=file_types, initialdir=initial_folder) #already list type
    else:                    return [askopenfilename(title=title, filetypes=file_types, initialdir=initial_folder)]

# Returns newest folder in directory with prefix
def get_newest_folder_in_dir(directory:str, prefix:str=PRETRAIN_HEADERS_PREFIX) -> str:    
    if not isdir(directory):
        raise Exception(f'Directory {directory} does not exist')
    return max(glob.glob(directory+f'/{prefix}*'), key=getmtime)