try:
    import os, sys
    import PySimpleGUI as sg

    from Layout import Layout
    from EventHandler import EventHandler
except ImportError as ie:
    input(f'Import error: {ie}\nPress any key to exit...')
    exit(1)




def main():
    layout = Layout()
    event_handler = EventHandler(layout)
    event_handler.run()


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f'Programm will close due to exception: {e}')