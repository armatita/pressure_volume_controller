"""
MIT License

Copyright (c) 2021 Pedro Correia

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


# Python libraries
import sys
import os
import platform
import time
from packaging import version

# Local libraries
import src.ui as ui

# Qt
from PyQt5 import QtWidgets


_version: version = version.parse("0.1.0")
_name: str        = "CPV mini"
_temp: str        = ".CPVmini"


def update(incoming_version:version)->bool:
    """
    Returns True or False depending on this version of the software
    needing an update.
    """
    return incoming_version > _version

def prepare_for_start(user_folder:str, print_to_file:bool=True) -> None:
    """
    Prepares the software for launch namely by printing the inital report
    plus setting up the system to write log to file or console.
    """
    logfile = os.path.join(user_folder, "log.txt")

    # NOTE: removing log file if too big.
    if os.path.exists(logfile):
        statinfo = os.stat(logfile)
        if statinfo.st_size > 1024*1024*10:
            os.remove(logfile)

    # NOTE: making sure the log is written to file if requested.
    if print_to_file:
        sys.stdout = open(logfile, "a")
        sys.stderr = sys.stdout

def create_user_folder(print_to_file:bool=True)->str:
    """
    Creates an user folder if one does not yet exist. Returns the
    string with the path to this folder.
    """
    # NOTE: creating a user folder in the system user folder.
    folder = os. path. expanduser("~")
    user_folder = os.path.join(folder, _temp)
    if not os.path.exists(user_folder):
        os.mkdir(user_folder)
    
    # NOTE: preparing the software to either write to console or log file.
    prepare_for_start(user_folder, print_to_file)

    # NOTE: returning the generated user folder.
    return user_folder

def initial_report(user_folder: str) -> None:
    """
    Prints a new report to either console or log file with initialization data
    (platform, version, name, user folder, etc.).
    """
    print("\n")
    intro = "+++++++++++++++++++++++++ " + _name + " +++++++++++++++++++++++++"
    print(intro)
    print("+ PLATFORM:    ", platform.system())
    print("+ TIME:        ", time.asctime())
    print("+ VERSION:     ", _version)
    print("+ USER FOLDER: ", user_folder)
    print("+"*len(intro))
    print("\n")


if __name__ == "__main__":
    # NOTE: Unique QApplication instance
    app = QtWidgets.QApplication(sys.argv)

    # NOTE: Creating an User folder where all preferences, configurations,
    #       and logs are stored.
    user_folder = create_user_folder(print_to_file=False)

    # NOTE: initial report.
    initial_report(user_folder)

    # NOTE: Main Window
    window = ui.MiniMainWindow(_name, str(_version), user_folder)

    # NOTE: Event Loop
    app.exec_()