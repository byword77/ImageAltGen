# -*- coding: utf-8 -*-
import sys
import traceback

def run(bk):
    try:
        from main_window import launch_gui
        return launch_gui(bk)
    except Exception as e:
        print("Error in ImageAltGen plugin:", str(e))
        traceback.print_exc()
        return -1

def main():
    print("This plugin must be run as a Sigil edit plugin.")
    return -1

if __name__ == "__main__":
    sys.exit(main())
