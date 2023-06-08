try:
    from os import path, sys
    parentdir = path.dirname(path.dirname(path.abspath(__file__)))
    yolodir = path.join(parentdir, 'yolov7')
    sys.path.extend([parentdir, yolodir]) # to allow import modules from parent dir
    print('\nAdded dir\'s to sys.path:\n    '+'\n    '.join(sys.path[-2:]))
    print('\nImporting modules...\n')
    from Layout import Layout
    from EventHandler import EventHandler
except ImportError as ie:
    input(f'Import error: {ie}\nPress any key to exit...')
    exit(1)

def main():
    print('\nStarting GUI...')
    layout = Layout()
    event_handler = EventHandler(layout)
    event_handler.run()
    print('Goodbye!')

if __name__ == '__main__':
    try: main()
    except Exception as e:
        print(f'Programm will close due to exception: {e}')