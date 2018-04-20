import os

from GUI.Demo import main

if __name__ == '__main__':
    os.chdir("GUI")
    try:
        main()
    except:
        import pdb
        pdb.pm()
