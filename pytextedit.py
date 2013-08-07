# -*- coding: utf-8 -*-

###############################################################################
"""

pytextedit
Version 0.4
Written by Adam Chesak.

pytextedit is a simple text editor written in Python with Tkinter for the GUI.

Please read the README and LICENSE files.

"""
###############################################################################


# META VARIABLES ##############################################################
# Define variables with information about pytextedit.
# These are used in the About dialog.

# This is the current version.
gbl_meta_version = "0.4"
# This is the date it was last updated.
gbl_meta_lastupdated = "1 May, 2013"


###############################################################################


# IMPORTS #####################################################################
# Import any modules needed.

# Try to import Tkinter in Python 3, then fall back to Python 2 if needed.
# Use this variable to remember the version of Python being used.
gbl_py_version = 3
try:
    # Try importing for Python 3.
    # Import tkinter for the GUI.
    from tkinter import *
    # Import the various dialogs needed.
    from tkinter.messagebox import showinfo, showerror, showwarning, askyesno
    from tkinter.filedialog import Open, SaveAs, askdirectory, askopenfilename
    from tkinter.simpledialog import askstring, askinteger, askfloat
    from tkinter.colorchooser import askcolor
except ImportError:
    # Fall back to Python 2.
    gbl_py_version = 2
    # Import Tkinter for the GUI.
    from Tkinter import *
    # Import the various dialogs needed.
    from tkMessageBox import showinfo, showerror, showwarning, askyesno
    from tkFileDialog import Open, SaveAs, askdirectory, askopenfilename
    from tkSimpleDialog import askstring, askinteger, askfloat
    from tkColorChooser import askcolor
# Import codecs for reading/writing with unicode support, if needed.
# This is only required for Python 2.
if gbl_py_version == 2:
    import codecs
# Import os and shutil for various things.
import os
import shutil
# Import os.path for splitting file paths.
import os.path
# Import sys for sys.exit().
import sys
# Import webbrowser for opening files in the user's web browser
import webbrowser
# Import time and datetime for getting the date and time.
import time
import datetime
# Import urlopen for opening a file from a URL.
# Try importing Python 3 module, then fall back to Python 2 if needed.
try:
    # Try importing for Python 3.
    from urllib.request import urlopen
    from urllib.parse import urlencode, quote, unquote
except ImportError:
    # Fall back to Python 2.
    from urllib import urlopen, urlencode
    from urllib2 import quote, unquote
# Import re for replacing strings using regular expressions.
import re
# Import platform for finding the users's operating system.
import platform
# Import subprocess for starting other processes.
import subprocess
# Import glob for getting lists of files.
import glob
# Import stat for getting statistics about files.
import stat
# Import smtplib for sending email.
import smtplib
# Import ftplib for sending files over FTP.
import ftplib
# Import socket for the collaborative editing.
import socket


###############################################################################


# IMPORT OPTIONS ##############################################################
# Get the options from the config files.


# Check if the file exists first.
if not os.path.isfile("resources/config/config"):
    print("The configuration file (\"resources/config/config\") is missing. Please replace the needed file and try again.")
    sys.exit()

try:
    # Open the config file.
    config_file = open("resources/config/config", "r")
    # Load the configs.
    CONFIG = {}
    for i in config_file.readlines():
        # Remove any extra spacing.
        if i.endswith("\n"):
            i = i[:-1]
        # Split on the first equals sign.
        split_pos = i.find("=")
        config_components = [i[:split_pos], i[split_pos + 1:]]
        CONFIG[config_components[0]] = config_components[1]
except IOError:
    print("Error reading the configuration file.")
    sys.exit()

# Change any configs, as needed.
# NOTE: these are due to how the configuration was handled previously,
# with the configs being stored in a Python source file. These no longer
# fit with how it's done now, and should be changed.
CONFIG["font_size"] = int(CONFIG["font_size"])
CONFIG["indent"] = int(CONFIG["indent"])
CONFIG["spaces_tab"] = int(CONFIG["spaces_tab"])

if CONFIG["tearoff"] == "enabled":
    CONFIG["tearoff"] = True
else:
    CONFIG["tearoff"] = False

if CONFIG["toolbar"] == "show":
    CONFIG["toolbar"] = True
else:
    CONFIG["toolbar"] = False

if CONFIG["line_numbers"] == "show":
    CONFIG["line_numbers"] = True
else:
    CONFIG["line_numbers"] = False

if CONFIG["status_bar"] == "show":
    CONFIG["status_bar"] = True
else:
    CONFIG["status_bar"] = False

if CONFIG["case_insensitive"] == "insensitive":
    CONFIG["case_insensitive"] = True
else:
    CONFIG["case_insensitive"] = False

if CONFIG["regex"] == "yes":
    CONFIG["regex"] = True
else:
    CONFIG["regex"] = False

if CONFIG["prompt_encode"] == "yes":
    CONFIG["prompt_encode"] = True
else:
    CONFIG["prompt_encode"] = False


###############################################################################


# SETUP CODE ##################################################################
# Configure settings, load lists, etc. before the GUI is created.

try:
    # Read the last file name, lock state, and encoding.
    last_file_file = open("resources/lastopen", "r")
    # Get the file name.
    last_file = last_file_file.readline().rstrip()
    # Get the lock state
    last_lock = last_file_file.readline().rstrip()
    # Finally, get the encoding.
    last_encode = last_file_file.readline().rstrip()
    last_file_file.close()
except IOError:
    print("Error reading data file \"lastopen\".")
    sys.exit()

try:
    # Read the list of favorite files.
    gbl_favorites_file = open("resources/favorites", "r")
    gbl_favorites = gbl_favorites_file.readlines()
    gbl_favorites_file.close()
    # Strip line endings.
    for fav in range(0, len(gbl_favorites)):
        if gbl_favorites[fav].endswith("\n"):
            gbl_favorites[fav] = gbl_favorites[fav].rstrip()
except IOError:
    print("Error reading data file \"favorites\".")
    sys.exit()

try:
    # Read the list of recently opened files.
    gbl_recent_open_file = open("resources/recentopen", "r")
    gbl_recent_open = gbl_recent_open_file.readlines()
    gbl_recent_open_file.close()
    # Strip line endings.
    for ro in range(0, len(gbl_recent_open)):
        if gbl_recent_open[ro].endswith("\n"):
            gbl_recent_open[ro] = gbl_recent_open[ro].rstrip()
except IOError:
    print("Error reading data file \"recentopen\".")
    sys.exit()

try:
    # Get the last-used window size and position.
    gbl_winsize_file = open("resources/winsize", "r")
    gbl_winsize = gbl_winsize_file.read().rstrip()
    gbl_winsize_file.close()
except IOError:
    print("Error reading data file \"winsize\".")
    sys.exit()

try:
    # Get the cursor mode.
    gbl_curmode_file = open("resources/curmode", "r")
    gbl_overwrite = gbl_curmode_file.read().rstrip()
    # Insert mode:
    if gbl_overwrite == "INS":
        gbl_overwrite = False
    # Overwrite mode:
    else:
        gbl_overwrite = True
    gbl_curmode_file.close()
except IOError:
    print("Error reading data file \"curmode\".")
    sys.exit()

try:
    # Get the saved notes.
    gbl_notes_file = open("resources/notes", "r")
    gbl_notes = gbl_notes_file.read()
    gbl_notes_file.close()
except IOError:
    print("Error reading data file \"notes\".")
    sys.exit()

try:
    # Get the macro bindings.
    gbl_bind_file = open("resources/macrobind", "r")
    gbl_mac_bindings = gbl_bind_file.readlines()
    gbl_bind_file.close()
    # Strip line endings.
    for mb in range(0, len(gbl_mac_bindings)):
        if gbl_mac_bindings[mb].endswith("\n"):
            gbl_mac_bindings[mb] = gbl_mac_bindings[mb].rstrip()
except IOError:
    print("Error reading data file \"macrobind\".")
    sys.exit()

try:
    # Get the folders list.
    folders_file = open("resources/folders", "r")
    gbl_folders = folders_file.readlines()
    folders_file.close()
    # Strip line endings.
    for i in range(0, len(gbl_folders)):
        if gbl_folders[i].endswith("\n"):
            gbl_folders[i] = gbl_folders[i].rstrip()
except IOError:
    print("Error reading data file \"folders\".")
    sys.exit()

try:
    # Get the Find history.
    find_file = open("resources/findhistory", "r")
    gbl_find_history = find_file.readlines()
    find_file.close()
    # Parse the history.
    for i in range(0, len(gbl_find_history)):
        gbl_find_history[i] = gbl_find_history[i].rstrip()
except IOError:
    print("Error reading data file \"findhistory\".")
    sys.exit()

try:
    # Get the Replace history.
    replace_file = open("resources/replacehistory", "r")
    gbl_replace_history = replace_file.readlines()
    replace_file.close()
    # Parse the history.
    for i in range(0, len(gbl_replace_history)):
        gbl_replace_history[i] = gbl_replace_history[i].rstrip()
        gbl_replace_history[i] = gbl_replace_history[i].split(" - ")
except IOError:
    print("Error reading data file \"replacehistory\".")
    sys.exit()

try:
    # Get the filetypes list.
    filetypes_file = open("resources/filetypes", "r")
    filetypes_data = filetypes_file.readlines()
    filetypes_file.close()
    # Get the filetypes.
    gbl_file_types = []
    for i in filetypes_data:
        # Strip line endings, if needed.
        if i.endswith("\n"):
            i = i[:-1]
        # Separate the components and format them in a way
        # the Tk dialogs can use.
        split_pos = i.find("=")
        filetypes_components = [i[:split_pos], i[split_pos + 1:]]
        gbl_file_types.append(tuple(filetypes_components))
except IOError:
    print("Error reading data file \"filetypes\".")
    sys.exit()

try:
    # See if this is the first time running pytextedit.
    firstopen_file = open("resources/firstopen", "r")
    gbl_first = firstopen_file.read().rstrip()
    firstopen_file.close()
except IOError:
    print("Error reading data file \"firstopen\".")
    sys.exit()

# Remember the current directory.
gbl_directory = os.getcwd()

# Configure the initial directory.
if CONFIG["init_dir"] == "$HOME":
    # The HOME variable doesn't work on Windows. Default to "C:" instead.
    if platform.system() == "Windows":
        CONFIG["init_dir"] = "C:"
    # This works on Linux, and probably on OSX as well.
    else:
        CONFIG["init_dir"] = os.environ["HOME"]
    # Switch to specified directory.
    os.chdir(CONFIG["init_dir"])

# Configure the default Unicode encoding.
if CONFIG["def_encode"] == "DEFAULT":
    CONFIG["def_encode"] = sys.getdefaultencoding()

# Configure the path separator. Use a backspace on Windows, and a 
# forward space on other systems.
if platform.system() == "Windows":
    gbl_path_sep = "\\"
else:
    gbl_path_sep = "/"


###############################################################################


# GLOBAL VARIABLES ############################################################
# Define variables needed for storing values between functions.

# Used for checking if file has been modified since last save.
gbl_saved_data = ""
# Used to store the file name, with the entire path.
gbl_file_name = ""
# Used to store the short version (without the path) of the file name.
gbl_file_name_short = ""
# Used to store the Save dialog, for remembering the last directory.
gbl_save_dlg = None
# Used to store the Open dialog, for remembering the last directory.
gbl_open_dlg = None
# Used for marking if the file has changed since the last save.
gbl_text_modified = False
# Used for marking the file as locked.
gbl_file_locked = False
# Used for storing bookmarks.
gbl_bookmarks = []
# Used to store the last-used encoding.
gbl_last_encode = None
# Used to store various values from dialogs.
gbl_dlg_open_url = "http://"
gbl_dlg_qopen = CONFIG["init_dir"] + "/"
gbl_dlg_move_sel = 1.0
gbl_last_find = ""
gbl_dlg_replace1 = ""
gbl_dlg_replace2 = ""
gbl_dlg_paste = ""
gbl_dlg_run_cmd = ""
gbl_dlg_pb_name = ""
gbl_dlg_pb_type = ""
gbl_dlg_pb_exp = ""
gbl_dlg_ph_type = ""
# Used for storing the name of the current panel in the Options dialog.
opt_panel = "font"
# Used for storing all the open documents.
gbl_mdi = [["name", "short name", "locked", "modified", "cursor position", "selection start", "selection end", "text"]]
# Used for storing the current document index.
gbl_mdi_current = 0
# Used for storing macro variables.
gbl_mac_vars = {}
# Used for the history for the file browser.
gbl_history = [CONFIG["init_dir"]]
gbl_history_pos = 0


###############################################################################


# TEXT BOX CLASSES ############################################################
# Define the classes used for the text box.


# This is the basic class for the text box, without line numbers.
class Textbox(object):
    def __init__(self, master):
        # Create the frame for the widgets.
        self.frame = Frame(master, relief = SUNKEN)
        self.frame.pack(side = TOP, expand = 1, fill = BOTH)
        # Create the scrollbars.
        self.scroll_v = Scrollbar(self.frame, bg = CONFIG["ui_bg"])
        self.scroll_v.pack(fill = Y, side = RIGHT)
        self.scroll_h = Scrollbar(self.frame, orient = "horizontal", bg = CONFIG["ui_bg"])
        self.scroll_h.pack(side = BOTTOM, fill = X)
        # Create the main text box.
        self.text_box = Text(self.frame, wrap = CONFIG["wrap"], bg = CONFIG["bg"], fg = CONFIG["fg"], undo = 1, autoseparators = 1, exportselection = 1, font = (CONFIG["font_name"], CONFIG["font_size"], CONFIG["font_style"]), relief = SUNKEN, selectbackground = CONFIG["sel_bg"], selectforeground = CONFIG["sel_fg"])
        self.text_box.pack(side = LEFT, fill = BOTH, expand = 1)
        # Set the tags.
        self.text_box.tag_config("current_line", background = CONFIG["highlight_color"])
        self.text_box.tag_lower("current_line")
        # Set up scrolling.
        self.text_box.config(yscrollcommand = self.scroll_v.set, xscrollcommand = self.scroll_h.set)
        self.scroll_v.config(command = self.text_box.yview)
        self.scroll_h.config(command = self.text_box.xview)
    

# This is the class for the text box that includes the line numbers.
class TextboxLN(object):
    def __init__(self, master):
        self.lineNumbers = ""
        # How often should the text box be updated? (In milliseconds.)
        self.UPDATE_PERIOD = 100
        # Create the frame for the widgets.
        self.frame = Frame(master, relief = SUNKEN)
        self.frame.pack(side = TOP, expand = 1, fill = BOTH)
        # Create the scrollbars.
        self.scroll_v = Scrollbar(self.frame, bg = CONFIG["ui_bg"])
        self.scroll_v.pack(fill = Y, side = RIGHT)
        self.scroll_h = Scrollbar(self.frame, orient = "horizontal", bg = CONFIG["ui_bg"])
        self.scroll_h.pack(side = BOTTOM, fill = X)
        # Create the line numbers.
        self.line_text = Text(self.frame, width = 4, highlightthickness = 0, takefocus = 0, exportselection = 0, bd = 0, background = CONFIG["ui_bg"], foreground = CONFIG["ui_fg"], state = DISABLED, font = (CONFIG["font_name"], CONFIG["font_size"], CONFIG["font_style"]))
        self.line_text.pack(side = LEFT, fill = Y)
        # Create the main text box.
        self.text_box = Text(self.frame, wrap = CONFIG["wrap"], bd = 0, bg = CONFIG["bg"], fg = CONFIG["fg"], undo = 1, autoseparators = 1,  exportselection = 1,font = (CONFIG["font_name"], CONFIG["font_size"], "normal"), relief = SUNKEN, selectbackground = CONFIG["sel_bg"], selectforeground = CONFIG["sel_fg"])
        self.text_box.pack(side = LEFT, fill = BOTH, expand = 1)
        # Set the tags.
        self.text_box.tag_config("current_line", background = CONFIG["highlight_color"])
        self.text_box.tag_lower("current_line")
        # Set up scrolling.
        self.text_box.config(yscrollcommand = self.scroll_v.set, xscrollcommand = self.scroll_h.set)
        self.scroll_v.config(command = self.text_box.yview)
        self.scroll_h.config(command = self.text_box.xview)
        # Start the function to update line numbers.
        self.update_line_numbers()
   
    def get_line_numbers(self):
        """Gets the line numbers."""
        x = 0
        line = "0"
        col = ""
        ln = ""
        # Assume each line is at least 6 pixels high.
        step = 6
        # Loop for each line.
        for i in range(0, self.text_box.winfo_height(), step):
            ll, cc = self.text_box.index("@0,%d" % i).split(".")
            if line == ll:
                if col != cc:
                    col = cc
                    ln += "\n"
            else:
                line, col = ll, cc
                ln += ("    %s\n" % line)[-5:]
        return ln

    def update_line_numbers(self):
        """Updates the line numbers."""
        tt = self.line_text
        ln = self.get_line_numbers()
        if self.lineNumbers != ln:
            self.lineNumbers = ln
            tt.config(state = NORMAL)
            tt.delete("1.0", "end")
            tt.insert("1.0", self.lineNumbers)
            tt.config(state = DISABLED)
        # Call this function again after specified period.
        self.text_box.after(self.UPDATE_PERIOD, self.update_line_numbers)


###############################################################################


# FUNCTIONS ###################################################################
# Define the (many) functions used.


def file_new():
    """Clears text box and resets variables."""
    global gbl_file_locked
    global gbl_file_name
    global gbl_file_name_short
    global gbl_last_encode
    global gbl_saved_data
    # Check for unsaved changes.
    if gbl_text_modified:
        # Ask the user for confirmation.
        open_confirm = askyesno("Confirm Open", "Are you sure you want to open a new file?\n\nUnsaved changes in the current file will not be kept if a new file is opened.")
        if not open_confirm:
            return internal_return_focus()
    # Unlock the text box.
    gbl_file_locked = False
    tkvar_lock.set(False)
    text_box.text_box.config(state = NORMAL)
    # Forget the last file name.
    gbl_file_name = ""
    gbl_file_name_short = ""
    # Forget the last encoding.
    gbl_last_encode = None
    # Mark the text as having no changes.
    internal_text_modified(False)
    # Clear saved data.
    gbl_saved_data = ""
    # Clear the undo/redo stack.
    text_box.text_box.edit_reset()
    # Reset the title and clear the text box.
    update_title()
    text_box.text_box.delete(1.0, "end-1c")
    # Update the status bar.
    update_status_file("No File", "None")
    # Return focus to the text box.
    return internal_return_focus()


def file_open(to_open = None, mod_chk = True, insert = False):
    """ Opens and displays the file specified by the user. """
    global gbl_file_locked
    global gbl_last_encode
    global gbl_open_dlg
    global gbl_file_name
    global gbl_file_name_short
    global gbl_saved_data
    # If we are inserting text, and the file is locked, this cannot be done.
    if insert == True and gbl_file_locked:
        showerror("Insert", "The file is in read only mode. Enable write mode to insert.")
        return internal_return_focus()
    # Check for unsaved changes, if needed.
    if mod_chk:
        if gbl_text_modified and insert == False:
            open_con = askyesno("Confirm Open", "Are you sure you want to open a new file?\n\nUnsaved changes in the current file will not be kept if a new file is opened.")
            if not open_con:
                return internal_return_focus()
    # Get the name of the file to open.
    if to_open:
        file_in = to_open
    else:
        if not gbl_open_dlg:
            gbl_open_dlg = Open(initialdir = CONFIG["init_dir"], filetypes = gbl_file_types)
        file_in = gbl_open_dlg.show()
        if not file_in:
            return internal_return_focus()
    # If the file doesn't exist, don't do anything.
    if not os.path.isfile(file_in):
        showerror("Open", "File doesn't exist.")
        return internal_return_focus()
    # Open the file.
    text = None
    t_file = None
    # If this is running in python 2, change the open function so unicode can be used.
    if gbl_py_version == 2:
        open = codecs.open
    # Try the config-specified default encoding.
    if text == None and not CONFIG["prompt_encode"]:
        try:
            t_file = open(file_in, "r", encoding = CONFIG["def_encode"])
            text = t_file.read()
            gbl_last_encode = CONFIG["def_encode"]
        except IOError:
            showerror("Open", "File could not be opened.")
            return internal_return_focus()
        except UnicodeError:
            pass
    # Ask the user for the encoding.
    if text == None and CONFIG["prompt_encode"]:
        try:
            encode = askstring("Open", "Enter encoding:", initialvalue = (sys.getdefaultencoding() or ""))
            if encode:
                t_file = open(file_in, "r", encoding = encode)
                text = t_file.read()
                gbl_last_encode = encode
        except IOError:
            showerror("Open", "File could not be opened.")
            return internal_return_focus()
        except UnicodeError:
            pass
    # Use the system's default encoding.
    if text == None:
        try:
            t_file = open(file_in, "r", encoding = sys.getdefaultencoding())
            text = t_file.read()
            gbl_last_encode = sys.getdefaultencoding()
        except IOError:
            showerror("Open", "File could not be opened.")
            return internal_return_focus()
        except UnicodeError:
            pass
    # If all else fails, try opening the file in binary mode.
    if text == None:
        try:
            t_file = open(file_in, "rb")
            text = t_file.read().replace(b'\r\n', b'\n')
            gbl_last_encode = "binary"
        except IOError:
            showerror("Open", "File could not be opened.")
            return internal_return_focus()
        except UnicodeError:
            pass
    # If none of the encodings worked, then the file cannot be opened.
    if text == None:
        showerror("Open", "Could not open or decode file.")
        return internal_return_focus()
    else:
        # Close the file.
        t_file.close()
    # If the text is being inserted into the current document:
    if insert == True:
        # Insert the text.
        text_box.text_box.insert("insert", text)
        # Mark text as having changes.
        internal_text_modified(True)
    # If the file is being opened as a new file:
    else:
        # Reset the file lock.
        text_box.text_box.config(state = NORMAL)
        gbl_file_locked = False
        # Insert the text.
        text_box.text_box.delete(1.0, "end-1c")
        text_box.text_box.insert(1.0, text)
        # Split the file name.
        file_name1, file_name2 = os.path.split(file_in)
        # Remember the file name.
        gbl_file_name = file_in
        gbl_file_name_short = file_name2
        # Mark the text as having no change.
        internal_text_modified(False)
        # Set the saved data.
        gbl_saved_data = text
        # Add the file to the Recently Opened list.
        gbl_recent_open.append(file_in)
        file_recent_open_update(initial = False, new = file_in)
        # Clear the undo/redo stack.
        text_box.text_box.edit_reset()
        # Set the insert cursor to the first position in the text box.
        text_box.text_box.mark_set("insert", 1.0)
        # Update the status bar..
        update_status_file(gbl_file_name_short, gbl_last_encode)
    # Update the title.
    update_title()
    # Return focus to the text box.
    return internal_return_focus()


def file_quick_open():
    """Opens a file."""
    global gbl_dlg_qopen
    # Ask the user for the file name.
    file_in = askstring("Quick Open", "Enter file:", initialvalue = gbl_dlg_qopen)
    if not file_in:
        return internal_return_focus()
    # Try to open the file.
    file_open(to_open = file_in)
    # Save the file name.
    gbl_dlg_qopen = file_in
    # Return focus to the text box.
    return internal_return_focus()


def file_open_url(url = None):
    """Opens a file specified by URL."""
    global gbl_text_modified
    global gbl_dlg_open_url
    global gbl_file_locked
    global gbl_file_name
    global gbl_file_name_short
    global gbl_saved_data
    # Check for unsaved changes.
    if gbl_text_modified:
        open_con = askyesno("Confirm Open from URL", "Are you sure you want to open a new file?\n\nUnsaved changes in the current file will not be kept if a new file is opened.")
        if not open_con:
            return internal_return_focus()
    # Get the URL to open.
    file_name = url or askstring("Open from URL", "Enter URL: ", initialvalue = gbl_dlg_open_url)
    if not file_name:
        return internal_return_focus()
    try:
        # Open the file and read the text.
        file_in = urlopen(file_name)
        data = file_in.readlines()
        file_in.close()
        # Work around any problems with binary mode.
        insert_data = ""
        for line in data:
            insert_data += line.decode() + "\n"
    except IOError:
        showerror("Open from URL", "Could not open file.")
    except UnicodeError:
        showerror("Open from URL", "Could not decode file.")
    # Unlock the text box.
    gbl_file_locked = False
    text_box.text_box.config(state = NORMAL)
    # Insert the text.
    text_box.text_box.delete(1.0, "end-1c")
    text_box.text_box.insert(1.0, insert_data)
    # Forget the last filename
    gbl_file_name = ""
    gbl_file_name_short = ""
    # Remember the URL.
    gbl_dlg_open_url = file_name
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    # Update the status bar..
    update_status_file("No File", "None")
    # Clear the saved data.
    gbl_saved_data = ""
    # Clear the undo/redo stack.
    text_box.text_box.edit_reset()
    text_box.text_box.mark_set("insert", 1.0)
    # Return focus to the text box.
    return internal_return_focus()


def file_open_sel():
    """Opens the filename specified by the user's current selection."""
    # If no text is selected, this cannot be done.
    if not text_box.text_box.tag_ranges("sel"):
        showerror("Open from Selection", "No text selected.")
        return internal_return_focus()
    # Get the selected text.
    file_in = text_box.text_box.get("sel.first", "sel.last")
    # Try to open the file.
    file_open(to_open = file_in)
    # Return focus to the text box.
    return internal_return_focus()


def file_open_encoding(to_open = None, encoding = None):
    """ Opens and displays the file specified by the user. """
    global gbl_file_locked
    global gbl_last_encode
    global gbl_open_dlg
    global gbl_file_name
    global gbl_file_name_short
    global gbl_saved_data
    # Check for unsaved changes.
    if gbl_text_modified:
        open_con = askyesno("Confirm Open", "Are you sure you want to open a new file?\n\nUnsaved changes in the current file will not be kept if a new file is opened.")
        if not open_con:
            return internal_return_focus()
    # Get the encoding.
    if not encoding:
        encoding = askstring("Open", "Enter encoding: ")
        if not encoding:
            return internal_return_focus()
    # Get the name of the file to open.
    if to_open:
        file_in = to_open
    else:
        if not gbl_open_dlg:
            gbl_open_dlg = Open(initialdir = CONFIG["init_dir"], filetypes = gbl_file_types)
        file_in = gbl_open_dlg.show()
        if not file_in:
            return internal_return_focus()
    # If the file doesn't exist, don't do anything.
    if not os.path.isfile(file_in):
        showerror("Open", "File doesn't exist.")
        return internal_return_focus()
    # Open the file.
    text = None
    t_file = None
    # If this is running in python 2, change the open function so unicode can be used.
    if gbl_py_version == 2:
        open = codecs.open
    # Try the specified encoding.
    try:
        t_file = open(file_in, "r", encoding = encoding)
        text = t_file.read()
        gbl_last_encode = encoding
    except IOError:
        showerror("Open", "File could not be opened.")
        return internal_return_focus()
    except UnicodeError:
        pass
    # If the encoding didn't work, this file cannot be opened.
    if text == None:
        showerror("Open", "Could not open or decode file with encoding \"%s\"." % encoding)
        return internal_return_focus()
    else:
        # Close the file.
        t_file.close()
    # Reset the file lock.
    text_box.text_box.config(state = NORMAL)
    gbl_file_locked = False
    # Insert the text.
    text_box.text_box.delete(1.0, "end-1c")
    text_box.text_box.insert(1.0, text)
    # Split the file name.
    file_name1, file_name2 = os.path.split(file_in)
    # Remember the file name.
    gbl_file_name = file_in
    gbl_file_name_short = file_name2
    # Mark the text as having no change.
    internal_text_modified(False)
    # Set the saved data.
    gbl_saved_data = text
    # Add the file to the Recently Opened list.
    gbl_recent_open.append(file_in)
    file_recent_open_update(initial = False, new = file_in)
    # Clear the undo/redo stack.
    text_box.text_box.edit_reset()
    # Set the insert cursor to the first position in the text box.
    text_box.text_box.mark_set("insert", 1.0)
    # Update the status bar..
    update_status_file(gbl_file_name_short, gbl_last_encode)
    # Update the title.
    update_title()
    # Return focus to the text box.
    return internal_return_focus()


def file_save_encoding(encoding = None):
    """Saves current text in text box."""
    global gbl_file_name
    global gbl_last_encode
    global gbl_save_dlg
    global gbl_saved_data
    global gbl_file_name_short
    # Get the encoding.
    if not encoding:
        encoding = askstring("Save", "Enter encoding: ")
        if not encoding:
            return internal_return_focus()
    # Get the file name.
    if not gbl_save_dlg:
        gbl_save_dlg = SaveAs(initialdir = CONFIG["init_dir"], filetypes = gbl_file_types)
    file_out = gbl_save_dlg.show()
    if not file_out:
        return internal_return_focus()
    gbl_file_name = file_out
    # Get the text in the text box.
    file_data = text_box.text_box.get(1.0, "end-1c")
    # If this is running in python 2, change the open function so unicode can be used.
    if gbl_py_version == 2:
        open = codecs.open
    last_encode = None
    # Try to save using the specified encoding.
    try:
        file_data.encode(encoding)
        last_encode = encoding
    except IOError:
        showerror("Save", "File could not be saved.")
        return internal_return_focus()
    except UnicodeError:
        pass
    # If the encoding didn't work, this file cannot be saved.
    if not last_encode:
        showerror("Save", "Could not save or encode file with encoding \"%s\"." % encoding)
        return internal_return_focus()
    else:
        gbl_last_encode = encoding
    # Save the file.
    filef = open(gbl_file_name, "w", encoding = last_encode)
    filef.write(file_data)
    filef.close()
    # Store the text for use in reverting later.
    gbl_saved_data = file_data
    # Mark the text as having no changes.
    internal_text_modified(False)
    text_box.text_box.edit_separator()
    # Update the title.
    file_name1, file_name2 = os.path.split(gbl_file_name)
    gbl_file_name_short = file_name2
    # Update the list of recently opened files.
    gbl_recent_open.append(gbl_file_name)
    file_recent_open_update(initial = False, new = gbl_file_name)
    # Update the title.
    update_title()
    # Update the status bar..
    update_status_file(gbl_file_name_short, gbl_last_encode)
    # Return focus to the text box.
    return internal_return_focus()


def file_reload_encoding(encoding = None):
    """Reloads the current file."""
    # If no file is open, this cannot be done.
    if gbl_file_name == "":
        showerror("Reload", "No file to reload.")
        return internal_return_focus()
    # Get the encoding.
    if not encoding:
        encoding = askstring("Reload", "Enter encoding: ")
        if not encoding:
            return internal_return_focus()
    # Ask the user to confirm the reload.
    if gbl_text_modified:
        reload_con = askyesno("Reload", "Are you sure you want reload the file?\n\nUnsaved changes will not be kept if the file is reloaded.")
        if not reload_con:
            return internal_return_focus()
    # Try to open the file.
    file_open_encoding(to_open = gbl_file_name, encoding = encoding)
    # Return focus to the text box.
    return internal_return_focus()


def file_reload():
    """Reloads the current file."""
    # If no file is open, this cannot be done.
    if gbl_file_name == "":
        showerror("Reload", "No file to reload.")
        return internal_return_focus()
    # Ask the user to confirm the reload.
    if gbl_text_modified:
        reload_con = askyesno("Reload", "Are you sure you want reload the file?\n\nUnsaved changes will not be kept if the file is reloaded.")
        if not reload_con:
            return internal_return_focus()
    # Try to open the file.
    file_open(to_open = gbl_file_name, mod_chk = False)
    # Return focus to the text box.
    return internal_return_focus()


def file_recent_open_clear():
    """Clears the list of recently opened files."""
    global gbl_recent_open
    # Clear the list.
    gbl_recent_open = []
    # Clear the menu.
    file_recent_open_menu.delete("2", "end")
    # Return focus to the text box.
    return internal_return_focus()


def file_recent_open_update(initial = True, new = None):
    """Updates the list of recently opened files."""
    # If this is the first time:
    if initial:
        # Add each item to the menu.
        for i in gbl_recent_open:
            file_recent_open_menu.add_command(label = i, image = img_blank, compound = LEFT, command = lambda i=i: file_open(to_open = i))
    else:
        # Add the new item.
        file_recent_open_menu.add_command(label = new, image = img_blank, compound = LEFT, command = lambda new=new: file_open(to_open = new))


def file_favorites():
    """Shows a list of "favorite" files."""
    # If there are no favorites, don't show the dialog.
    if len(gbl_favorites) == 0:
        showinfo("Favorites", "There are no favorites.\n\nFavorites can be added from \"Options -> Edit Favorites...\".")
        return internal_return_focus()
    # Define the internal function to manage double-clicks.
    def file_favorites_open_click():
        """Manages double-click events for the favorites list."""
        # Get the active list item.
        file_in = fav_list.get("active")
        if not file_in:
            return
        # Remember the current file name.
        old_name = gbl_file_name
        # Try to open the file.
        file_open(to_open = file_in)
        # Close the window only if the file has changed.
        if old_name != gbl_file_name:
            fav_win.destroy()
        # Return focus to the text box.
        return internal_return_focus()
    # Create the GUI.
    fav_win = Toplevel()
    fav_win.title("Favorites")
    fav_win.transient(root)
    fav_win.grab_set()
    # Create the frame for the listbox and scrollbar
    fav_frm = Frame(fav_win)
    fav_frm.pack(expand = YES, fill = BOTH, side = TOP)
    # Create the listbox and scrollbar.
    fav_list = Listbox(fav_frm, bg = CONFIG["bg"], fg = CONFIG["fg"], relief = SUNKEN, width = 50)
    fav_scroll = Scrollbar(fav_frm)
    fav_scroll.config(command = fav_list.yview)
    fav_list.config(yscrollcommand = fav_scroll.set)
    fav_scroll.pack(side = RIGHT, fill = Y)
    fav_list.pack(side = LEFT, expand = YES, fill = BOTH)
    # Populate the listbox.
    for i in gbl_favorites:
        fav_list.insert("end", str(i))
    # Give the listbox focus.
    fav_list.focus()
    # Bind the events.
    fav_list.bind("<Double-1>", lambda event: file_favorites_open_click())
    fav_list.bind("<Return>", lambda event: file_favorites_open_click())
    fav_list.bind("<Escape>", lambda event: fav_win.destroy())


def file_save(mode = "save", filename = None):
    """Saves current text in text box."""
    global gbl_file_name
    global gbl_last_encode
    global gbl_save_dlg
    global gbl_saved_data
    global gbl_file_name_short
    # Determine which title to use.
    title = "Save"
    if mode == "saveas":
        title = "Save As"
    file_changed = False
    # If given a filename:
    if filename != None:
        gbl_file_name = filename
        file_changed = True
    # If the file has not been saved, or if this is Save As, show the save dialog.
    elif gbl_file_name == "" or mode == "saveas":
        file_changed = True
        if not gbl_save_dlg:
            gbl_save_dlg = SaveAs(initialdir = CONFIG["init_dir"], filetypes = gbl_file_types)
        file_out = gbl_save_dlg.show()
        if not file_out:
            return internal_return_focus()
        gbl_file_name = file_out
    # Get the text in the text box.
    file_data = text_box.text_box.get(1.0, "end-1c")
    # If this is running in python 2, change the open function so unicode can be used.
    if gbl_py_version == 2:
        open = codecs.open
    last_encode = None
    # Try to save using the last-used encoding.
    if gbl_last_encode != None and mode == "save":
        try:
            file_data.encode(gbl_last_encode)
            last_encode = gbl_last_encode
        except IOError:
            showerror("Save", "File could not be saved.")
            return internal_return_focus()
        except UnicodeError:
            pass
    # Try to use the encoding specified by the config file.
    if not last_encode and not CONFIG["prompt_encode"]:
        try:
            file_data.encode(CONFIG["def_encode"])
            last_encode = CONFIG["def_encode"]
        except IOError:
            showerror("Save", "File could not be saved.")
            return internal_return_focus()
        except UnicodeError:
            pass
    # Ask the user for the encoding.
    if not last_encode and CONFIG["prompt_encode"]:
        try:
            encode = askstring(title, "Enter encoding:", initialvalue = (gbl_last_encode or sys.getdefaultencoding() or ""))
            if encode:
                file_data.encode(encode)
                last_encode = encode
        except IOError:
            showerror("Save", "File could not be saved.")
            return internal_return_focus()
        except UnicodeError:
            pass
    # Lastly, try using the system's default encoding.
    if not last_encode:
        try:
            file_data.encode(sys.getdefaultencoding())
            last_encode = sys.getdefaultencoding()
        except IOError:
            showerror("Save", "File could not be saved.")
            return internal_return_focus()
        except UnicodeError:
            pass
    # If none of the possible encodings worked, the file cannot be saved.
    if not last_encode:
        showerror("Save", "Could not save or encode file.")
        return internal_return_focus()
    else:
        gbl_last_encode = last_encode
    # Save the file.
    filef = open(gbl_file_name, "w", encoding = last_encode)
    filef.write(file_data)
    filef.close()
    # Store the text for use in reverting later.
    gbl_saved_data = file_data
    # Mark the text as having no changes.
    internal_text_modified(False)
    text_box.text_box.edit_separator()
    # If the file has changed:
    if file_changed:
        # Update the title.
        file_name1, file_name2 = os.path.split(gbl_file_name)
        gbl_file_name_short = file_name2
        # Update the list of recently opened files.
        gbl_recent_open.append(gbl_file_name)
        file_recent_open_update(initial = False, new = gbl_file_name)
    # Update the title.
    update_title()
    # Update the status bar..
    update_status_file(gbl_file_name_short, gbl_last_encode)
    # Return focus to the text box.
    return internal_return_focus()


def file_save_copy(filename = None):
    """Saves a copy of the current file."""
    global gbl_save_dlg
    # If the file has not been saved, this cannot be done.
    if not gbl_file_name:
        showerror("Save Copy", "File has not yet been saved, so no copy can be created.")
        return internal_return_focus()
    # If the file has unsaved changes, this cannot be done.
    if gbl_text_modified:
        showerror("Save Copy", "File has unsaved changes. Please save and try again.")
        return internal_return_focus()
    # Remember the current filename.
    curr_file = gbl_file_name
    # Get the filename.
    if not filename:
        # Show the save dialog.
        if not gbl_save_dlg:
            gbl_save_dlg = SaveAs(initialdir = CONFIG["init_dir"], filetypes = gbl_file_types)
        file_out = gbl_save_dlg.show()
        if not file_out:
            return internal_return_focus()
    else:
        file_out = filename
    # Save a copy.
    file_save(filename = file_out)
    # Reopen the old file.
    file_open(to_open = curr_file)
    # Tell the user the file has been saved.
    showinfo("Save Copy", "Copy has been saved.")
    # Return focus to the text box.
    text_box.text_box.mark_set("insert", "1.0")
    return internal_return_focus()


def file_revert_save():
    """Reverts to the last save."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showerror("Revert to Last Save", "The file is in read only mode. Enable write mode to revert.")
        return internal_return_focus()
    # If the file has not been saved, this cannot be done.
    if not gbl_file_name:
        showerror("Revert to Last Save", "File has not yet been saved.")
        return internal_return_focus()
    # If the last save is the same as the current text, there no reason to do this.
    if gbl_saved_data == text_box.text_box.get(1.0, "end-1c"):
        showinfo("Revert to Last Save", "Last save is the same as current text.")
        return internal_return_focus()
    # Ask the user to confirm the revert.
    revert_con = askyesno("Revert to Last Save", "Are you sure you want to revert?")
    if not revert_con:
        return internal_return_focus()
    # Delete the current text and insert the older text.
    text_box.text_box.delete(1.0, "end-1c")
    text_box.text_box.insert(1.0, gbl_saved_data)
    # Mark the text as having no changes.
    internal_text_modified(False)
    # Update the title.
    update_title()
    text_box.text_box.edit_reset()
    # Return focus to the text box.
    text_box.text_box.mark_set("insert", "1.0")
    return internal_return_focus()


def file_open_binary(to_open = None):
    """ Opens and displays the file specified by the user in binary mode. """
    global gbl_file_locked
    global gbl_last_encode
    global gbl_open_dlg
    global gbl_file_name
    global gbl_file_name_short
    global gbl_saved_data
    # Check for unsaved changes.
    if gbl_text_modified:
        open_con = askyesno("Confirm Open", "Are you sure you want to open a new file?\n\nUnsaved changes in the current file will not be kept if a new file is opened.")
        if not open_con:
            return internal_return_focus()
    # Get the name of the file to open.
    if to_open:
        file_in = to_open
    else:
        if not gbl_open_dlg:
            gbl_open_dlg = Open(initialdir = CONFIG["init_dir"], filetypes = gbl_file_types)
        file_in = gbl_open_dlg.show()
        if not file_in:
            return internal_return_focus()
    # If the file doesn't exist, don't do anything.
    if not os.path.isfile(file_in):
        showerror("Open", "File doesn't exist.")
        return internal_return_focus()
    # Open the file.
    text = None
    t_file = None
    # If this is running in python 2, change the open function so unicode can be used.
    if gbl_py_version == 2:
        open = codecs.open
    # Try opening in binary mode.
    try:
        t_file = open(file_in, "rb")
        text = t_file.read().replace(b'\r\n', b'\n')
        gbl_last_encode = "binary"
    except IOError:
        showerror("Open", "File could not be opened.")
        return internal_return_focus()
    except UnicodeError:
        pass
    # If binary mode didn't work, this file cannot be opened.
    if text == None:
        showerror("Open", "Could not open file in binary mode.")
        return internal_return_focus()
    else:
        # Close the file.
        t_file.close()
    # Reset the file lock.
    text_box.text_box.config(state = NORMAL)
    gbl_file_locked = False
    # Insert the text.
    text_box.text_box.delete(1.0, "end-1c")
    text_box.text_box.insert(1.0, text)
    # Split the file name.
    file_name1, file_name2 = os.path.split(file_in)
    # Remember the file name.
    gbl_file_name = file_in
    gbl_file_name_short = file_name2
    # Mark the text as having no change.
    internal_text_modified(False)
    # Set the saved data.
    gbl_saved_data = text
    # Add the file to the Recently Opened list.
    gbl_recent_open.append(file_in)
    file_recent_open_update(initial = False, new = file_in)
    # Clear the undo/redo stack.
    text_box.text_box.edit_reset()
    # Set the insert cursor to the first position in the text box.
    text_box.text_box.mark_set("insert", 1.0)
    # Update the status bar..
    update_status_file(gbl_file_name_short, gbl_last_encode)
    # Update the title.
    update_title()
    # Return focus to the text box.
    return internal_return_focus()


def file_reload_binary():
    """Reloads the current file in binary mode."""
    # If no file is open, this cannot be done.
    if gbl_file_name == "":
        showerror("Reload", "No file to reload.")
        return internal_return_focus()
    # Ask the user to confirm the reload.
    if gbl_text_modified:
        reload_con = askyesno("Reload", "Are you sure you want reload the file?\n\nUnsaved changes will not be kept if the file is reloaded.")
        if not reload_con:
            return internal_return_focus()
    # Try to open the file.
    file_open_binary(to_open = gbl_file_name)
    # Return focus to the text box.
    return internal_return_focus()



def file_save_binary():
    """Saves current text in text box in binary mode."""
    global gbl_file_name
    global gbl_last_encode
    global gbl_save_dlg
    global gbl_saved_data
    global gbl_file_name_short
    # Show the save dialog.
    if not gbl_save_dlg:
        gbl_save_dlg = SaveAs(initialdir = CONFIG["init_dir"], filetypes = gbl_file_types)
    file_out = gbl_save_dlg.show()
    if not file_out:
        return internal_return_focus()
    gbl_file_name = file_out
    # Get the text in the text box.
    file_data = text_box.text_box.get(1.0, "end-1c")
    # If this is running in python 2, change the open function so unicode can be used.
    if gbl_py_version == 2:
        open = codecs.open
    last_encode = None
    # Save the file in binary mode.
    try:
        filef = open(gbl_file_name, "wb")
        filef.write(file_data)
        filef.close()
        last_encode = "binary"
    except IOError:
        showerror("Save", "File could not be saved.")
        return internal_return_focus()
    except UnicodeError:
        pass
    # If binary mode didn't work, this file cannot be opened.
    if not last_encode:
        showerror("Save", "Could not save file in binary mode.")
        return internal_return_focus()
    else:
        gbl_last_encode = last_encode
    # Store the text for use in reverting later.
    gbl_saved_data = file_data
    # Mark the text as having no changes.
    internal_text_modified(False)
    text_box.text_box.edit_separator()
    # Update the title.
    file_name1, file_name2 = os.path.split(gbl_file_name)
    gbl_file_name_short = file_name2
    # Update the list of recently opened files.
    gbl_recent_open.append(gbl_file_name)
    file_recent_open_update(initial = False, new = gbl_file_name)
    # Update the title.
    update_title()
    # Update the status bar..
    update_status_file(gbl_file_name_short, gbl_last_encode)
    # Return focus to the text box.
    return internal_return_focus()


def file_delete():
    """Deletes the current file."""
    # If no file is open, this cannot be done.
    if not gbl_file_name:
        showerror("Delete", "No file to delete.")
        return internal_return_focus()
    # Ask the user to confirm the delete.
    del_conf = askyesno("Delete", "Are you sure you want to delete the current file?")
    if not del_conf:
        return internal_return_focus()
    # Delete the file.
    os.remove(gbl_file_name)
    # Open a new file.
    file_new()


def file_rename(filename = None):
    """Renames the current file."""
    global gbl_save_dlg
    # If no file is open, this cannot be done.
    if not gbl_file_name:
        showerror("Rename", "No file to rename.")
        return internal_return_focus()
    # Ask the user to confirm the rename.
    ren_conf = askyesno("Rename", "Are you sure you want to rename the current file?")
    if not ren_conf:
        return internal_return_focus()
    # If the file has unsaved changes, ask the user if they want to proceed.
    if gbl_text_modified:
        ren_conf = askyesno("Rename", "File has unsaved changes. Proceed?")
        if not ren_conf:
            return internal_return_focus()
    # Select the new file.
    if not filename:
        if not gbl_save_dlg:
            gbl_save_dlg = SaveAs(initialdir = CONFIG["init_dir"], filetypes = gbl_file_types, title = "Rename")
        new_file = gbl_save_dlg.show()
        if not new_file:
            return internal_return_focus()
    else:
        new_file = filename
    # Rename the file.
    os.rename(gbl_file_name, new_file)
    # Open the renamed file.
    file_open(new_file)


def file_browse():
    """Shows a file browser."""
    if CONFIG["tearoff"] == "enabled":
        CONFIG["tearoff"] = True
    else:
        CONFIG["tearoff"] = False
    # Define internal functions
    def file_browse_chdir(directory = ""):
        """Changes the directory."""
        global gbl_history_pos
        global gbl_history
        # Get the directory.
        if directory == "":
            directory = browse_ent.get()
        # Switch to the directory.
        try:
            os.chdir(directory)
        except:
            showerror("Browse", "Could not switch to directory \"%s\"." % directory)
            return
        # Update the history.
        if len(gbl_history) - 1 == gbl_history_pos or len(gbl_history) == 0:
            # Increment the position.
            gbl_history_pos += 1
            # Add directory to history.
            gbl_history.append(os.getcwd())
        elif len(gbl_history) - 1 != gbl_history_pos:
            # Get the history up to the current point.
            new_history = gbl_history[:gbl_history_pos + 1]
            # Clear the history.
            gbl_history[:] = []
            # Insert the sliced history.
            gbl_history = new_history[:]
            # Increment the position.
            gbl_history_pos = len(gbl_history)
            # Add directory to history.
            gbl_history.append(os.getcwd())
        # Show the list of files and directories.
        file_browse_list()
        # Update the directory entry.
        if CONFIG["browser_toolbar"] == "show":
            browse_ent.delete(0, END)
            browse_ent.insert(0, os.getcwd())
    def file_browse_list():
        """Shows a list of the files."""
        # Get the list of files.
        file_list = glob.glob("*")
        # If no files were found, delete all the current list items.
        if file_list == None:
            list_box.delete(0, END)
            return
        # Separate directories from files.
        dir_list = []
        files_list = []
        # Loop though list to find directories and files.
        for i in file_list:
            if os.path.isdir(i):
                dir_list.append(i)
            else:
                files_list.append(i)
        # Alphabetically sort the lists.
        if CONFIG["browser_sort"] == "yes":
            dir_list.sort()
            file_list.sort()
        # Delete the current list items,
        list_box.delete(0, END)
        # Directories above files:
        if CONFIG["browser_folders"] == "folders above":
            # Insert the directories.
            for i in dir_list:
                list_box.insert(END, i)
            # Insert the files.
            for i in files_list:
                list_box.insert(END, i)
        # Files above directories:
        elif CONFIG["browser_folders"] == "folders below":
            # Insert the files.
            for i in files_list:
                list_box.insert(END, i)
            # Insert the directories.
            for i in dir_list:
                list_box.insert(END, i)
        # Update the title.
        if CONFIG["browser_title"] == "current directory":
            fold_win.title(os.getcwd())
        elif CONFIG["browser_title"] == "command name":
            fold_win.title("File Browser")
    def file_browse_double_click():
        """Manages double-clicks on the list box."""
        # Get the selected list item.
        active = list_box.get("active")
        # If nothing is selected, nothing can be done.
        if not active:
            return
        # If the selected item is a directory, open it.
        if os.path.isdir(active):
            file_browse_handle_dir(active)
        # If the selected item is a file, show info about it.
        else:
            file_browse_handle_file(active)
    def file_browse_handle_file(active):
        """Opens the file."""
        # Open the file.
        file_open(os.getcwd() + gbl_path_sep + active)
    def file_browse_handle_dir(active):
        """Switches to a new directory."""
        # Get the new directory.
        newdir = os.getcwd() + gbl_path_sep + active
        # Switch to the directory.
        file_browse_chdir(newdir)
    def file_browse_back():
        """Goes back in the history."""
        global gbl_history_pos
        # If the current directory is the first item, this cannot be done.
        if gbl_history_pos == 0:
            return
        # Go back one.
        gbl_history_pos -= 1
        os.chdir(gbl_history[gbl_history_pos])
        # Update the directory entry.
        if CONFIG["browser_toolbar"] == "show":
            browse_ent.delete(0, END)
            browse_ent.insert(0, gbl_history[gbl_history_pos])
        # Show the list of files and directories.
        file_browse_list()
    def file_browse_up():
        """Move up a directory."""
        # Get the current directory.
        cwd = os.getcwd()
        # Get the next higher directory.
        newdir = os.path.split(os.path.abspath(cwd))[0]
        # Go to the next directory.
        file_browse_chdir(newdir)
    def file_browse_mkdir():
        """Create a new directory."""
        # Prompt the user for the directory
        newdir = askstring("Create Directory", "Enter directory: ")
        if not newdir:
            return
        # If this directory already exists, this cannot be done.
        if os.path.isdir(newdir):
            showerror("Create Directory", "There is already a directory called \"%s\"." % newname)
            return
        # Make the new directory.
        try:
            os.mkdir(newdir)
            file_browse_chdir(newdir)
        except:
            showerror("Create Directory", "Could not create directory \"%s\"." % newdir)
    def file_browse_mkfile():
        """Creates a new file."""
        # Prompt the user for the filename.
        newfile = askstring("Create New File", "Enter filename: ")
        if not newfile:
            return
        # If this file already exists, this cannot be done.
        if os.path.isfile(newfile):
            showerror("Create New File", "There is already a file called \"%s\"." % newfile)
            return
        # Make the new file.
        try:
            new = open(newfile, "w")
            new.close()
        except:
            showerror("Create New File", "Could not create file \"%s\"." % newfile)
        # Refresh the listing.
        file_browse_list()
    def file_browse_rename():
        """Renames a file or directory."""
        # Get the item to rename.
        active = list_box.get("active")
        if not active:
            return
        # Prompt the user for the new name.
        newname = askstring("Rename", "Enter new name for \"%s\":" % active)
        if not newname:
            return
        # If the new name is already used, this cannot be done.
        if os.path.isfile(active) and os.path.isfile(newname):
            showerror("Rename", "There is already a file called \"%s\"." % newname)
            return
        if os.path.isdir(active) and os.path.isdir(newname):
            showerror("Rename", "There is already a directory called \"%s\"." % newname)
            return
        # Rename the item.
        try:
            os.rename(active, newname)
        except:
            showerror("Rename", "Could not rename file \"%s\" to \"%s\"." % (active, newname))
        # Refresh the listing.
        file_browse_list()
    def file_browse_del():
        """Deletes a file or directory."""
        # Get the item to delete.
        active = list_box.get("active")
        if not active:
            return
        # If the item is a file:
        if not os.path.isdir(active):
            # Ask the user for confirmation.
            conf = askyesno("Delete", "Are you sure you want to delete the file \"%s\"?" % active)
            if conf:
                try:
                    os.remove(active)
                except:
                    showerror("Delete", "Could not delete file \"%s\"." % active)
        # If the item is a folder:
        else:
            # Ask the user for confirmation.
            conf = askyesno("Delete", "Are you sure you want to delete the folder \"%s\" and any contents?" % active)
            if conf:
                try:
                    shutil.rmtree(active)
                except:
                    showerror("Delete", "Could not delete directory \"%s\"." % active)
        # Refresh the listing.
        file_browse_list()
    def file_browse_goto(go = None):
        """Go to a different directory."""
        # Prompt the user for the directory.
        newdir = go or askstring("Go to", "Enter directory: ")
        if not newdir:
            return
        # Go to the new directory.
        file_browse_chdir(os.path.expanduser(newdir))
    def file_browse_info():
        """Shows info about a file or folder."""
        # Get the item.
        active = list_box.get("active")
        if not active:
            return
        # Get the info.
        fstats = os.stat(active)
        type_ = "file"
        if os.path.isdir(active):
            type_ = "directory"
        elif os.path.islink(active):
            type_ = "link"
        size = fstats[stat.ST_SIZE]
        mod = time.ctime(fstats[stat.ST_MTIME])
        acc = time.ctime(fstats[stat.ST_ATIME])
        create = time.ctime(fstats[stat.ST_CTIME])
        user = fstats.st_uid
        group = fstats.st_gid
        # Show a dialog with the information.
        dlg_text = "Name: %s\nType: %s\nSize: %d bytes\n\nLast Modified: %s\nLast Accessed: %s\nCreated: %s\n\nOwner ID: %s\nGroup ID: %s" % (active, type_, size, mod, acc, create, user, group)
        showinfo("Info", dlg_text)
    def file_browse_edit_folders():
        """Edits the "folders" file."""
        def file_browse_edit_folders_add():
            """Adds an item to the listbox."""
            # Ask user for the directory
            direct = askdirectory(title = "Choose Directory", initialdir = CONFIG["init_dir"])
            if not direct:
                return
            # Insert the directory at the end of the listbox.
            fold_list.insert("end", direct)
        def file_browse_edit_folders_remove():
            """Removes an item from the listbox."""
            fold_list.delete(fold_list.curselection())
        def file_browse_edit_folders_save():
            """Saves the list to the file."""
            # Get all the items.
            items = []
            # Loop through the listbox until all the items are in the array.
            items_current = 0
            while True:
                item = fold_list.get(items_current)
                if item == "":
                    break
                items.append(item)
                items_current += 1
            # Delete all the items in the folders list, and add the new ones.
            del gbl_folders[:]
            gbl_folders[:] = items
            # Join the list items.
            items_str = "\n".join(gbl_folders)
            # Remember the current directory.
            file_dir = os.getcwd()
            # Switch to the pytextedit main directory.
            os.chdir(gbl_directory)
            # Open the folders file, write the new string, and close the file.
            try:
                fav_file = open("resources/folders", "w")
                fav_file.write(items_str)
                fav_file.close()
            except:
                showerror("Edit Folders", "Error saving data file \"folders\".")
            # Switch back to the original directory.
            os.chdir(file_dir)
            # Show a dialog telling the user that the favorites have been saved.
            showinfo("Edit Folders", "Folders saved.")
        # Create the GUI.
        fold2_win = Toplevel()
        fold2_win.title("Edit Folders")
        fold2_win.transient(fold_win)
        fold2_win.grab_set()
        # Create the frame for the listbox and scrollbar.
        fold_frm = Frame(fold2_win)
        fold_frm.pack(expand = YES, fill = BOTH, side = TOP)
        # Create the listbox and scrollbar.
        fold_list = Listbox(fold_frm, bg = CONFIG["bg"], fg = CONFIG["fg"], relief = SUNKEN, width = 60)
        fold_scroll = Scrollbar(fold_frm)
        fold_scroll.config(command = fold_list.yview)
        fold_list.config(yscrollcommand = fold_scroll.set)
        fold_scroll.pack(side = RIGHT, fill = Y)
        fold_list.pack(side = LEFT, expand = YES, fill = BOTH)
        # Populate the listbox.
        for i in gbl_folders:
            fold_list.insert("end", str(i))
        # Create the frame for the buttons.
        fold_frm2 = Frame(fold2_win)
        fold_frm2.pack(expand = NO, fill = X, side = TOP)
        # Create the Add button.
        fold_add_btn = Button(fold_frm2, text = "Add", width = 20, command = file_browse_edit_folders_add)
        fold_add_btn.pack(side = LEFT)
        # Create the Remove button.
        fold_rmv_btn = Button(fold_frm2, text = "Remove", width = 20, command = file_browse_edit_folders_remove)
        fold_rmv_btn.pack(side = LEFT)
        # Create the Save button.
        fold_sav_btn = Button(fold_frm2, text = "Save", width = 20, command = file_browse_edit_folders_save)
        fold_sav_btn.pack(side = LEFT)
    # Create the GUI.
    fold_win = Toplevel()
    if CONFIG["browser_title"] == "current directory":
        fold_win.title(os.getcwd())
    elif CONFIG["browser_title"] == "command name":
        fold_win.title("File Browser")
    # Create the frame for all the widgets.
    app = Frame(fold_win, bg = CONFIG["ui_bg"])
    app.pack(expand = 1, fill = BOTH)
    if CONFIG["browser_toolbar"] == "show":
        # Create the frame for the toolbar.
        browse_frm1 = Frame(app, bg = CONFIG["ui_bg"])
        browse_frm1.pack(side = TOP, fill = X)
        # Only images on buttons.
        if CONFIG["browser_btns"] == "images only":
            # Create the Back button.
            back_btn = Button(browse_frm1, image = img_fold_back, command = file_browse_back, relief = FLAT, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0)
            back_btn.pack(side = LEFT)
            # Create the Up button.
            up_btn = Button(browse_frm1, image = img_fold_up, command = file_browse_up, relief = FLAT, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0)
            up_btn.pack(side = LEFT)
        # Only text on buttons.
        if CONFIG["browser_btns"] == "text only":
            # Create the Back button.
            back_btn = Button(browse_frm1, text = "Back", command = file_browse_back, relief = FLAT, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0)
            back_btn.pack(side = LEFT)
            # Create the Up button.
            up_btn = Button(browse_frm1, text = "Up", command = file_browse_up, relief = FLAT, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0)
            up_btn.pack(side = LEFT)
        # Text and images on buttons.
        if CONFIG["browser_btns"] == "text and images":
            # Create the Back button.
            back_btn = Button(browse_frm1, image = img_fold_back, compound = CONFIG["browser_compound"], text = "Back", command = file_browse_back, relief = FLAT, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0)
            back_btn.pack(side = LEFT)
            # Create the Up button.
            up_btn = Button(browse_frm1, image = img_fold_up, compound = CONFIG["browser_compound"], text = "Up", command = file_browse_up, relief = FLAT, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0)
            up_btn.pack(side = LEFT)
        # Create the entry for the directory.
        browse_ent = Entry(browse_frm1, bg = CONFIG["bg"], fg = CONFIG["fg"], relief = FLAT)
        browse_ent.pack(side = LEFT, fill = X, expand = 1)
    # Create the frame for the listbox and scrollbar.
    browse_frm2 = Frame(app, bg = CONFIG["ui_bg"])
    browse_frm2.pack(side = TOP, fill = BOTH, expand = 1)
    # Create the listbox and scrollbar.
    list_box = Listbox(browse_frm2, bg = CONFIG["bg"], fg = CONFIG["fg"])
    browse_scroll = Scrollbar(browse_frm2, bg = CONFIG["ui_bg"])
    browse_scroll.config(command = list_box.yview)
    list_box.config(yscrollcommand = browse_scroll.set)
    browse_scroll.pack(side = RIGHT, fill = Y)
    list_box.pack(side = LEFT, expand = YES, fill = BOTH)
    # Create the menus.
    if CONFIG["browser_menubar"] == "show":
        menu = Menu(fold_win)
        fold_win.config(menu = menu)
        if CONFIG["browser_menu_file"] == "show":
            # Create the File menu.
            file_menu = Menu(menu, tearoff = CONFIG["tearoff"])
            menu.add_cascade(label = "File", menu = file_menu, underline = 0)
            file_menu.add_command(label = "Create Directory...", image = img_browse_newdir, compound = LEFT, underline = 0, accelerator = "Ctrl+N", command = file_browse_mkdir)
            file_menu.add_command(label = "Create New File...", image = img_browse_newdoc, compound = LEFT, underline = 7, accelerator = "Shift+Crtl+N", command = file_browse_mkfile)
            file_menu.add_separator()
            file_menu.add_command(label = "Rename...", image = img_blank, compound = LEFT, underline = 0, accelerator = "F2", command = file_browse_rename)
            file_menu.add_command(label = "Delete", image = img_browse_delete, compound = LEFT, underline = 0, accelerator = "F3, Delete", command = file_browse_del)
            file_menu.add_separator()
            file_menu.add_command(label = "Info...", image = img_browse_about, compound = LEFT, underline = 0, accelerator = "Alt+Return", command = file_browse_info)
            file_menu.add_separator()
            file_menu.add_command(label = "Go to...", image = img_blank, compound = LEFT, underline = 0, accelerator = "Ctrl+O", command = file_browse_goto)
            file_menu.add_command(label = "Refresh", image = img_browse_refresh, compound = LEFT, underline = 0, accelerator = "F5", command = lambda: file_browse_chdir(os.getcwd()))
            file_menu.add_separator()
            file_menu.add_command(label = "Exit", image = img_browse_exit, compound = LEFT, underline = 1, accelerator = "Ctrl+Q", command = sys.exit)
        if CONFIG["browser_menu_folders"] == "show":
            # Create the Folders menu.
            folders_menu = Menu(menu, tearoff = CONFIG["tearoff"])
            menu.add_cascade(label = "Folders", menu = folders_menu, underline = 2)
            for i in gbl_folders:
                folders_menu.add_command(label = i, image = img_blank, compound = LEFT, command = lambda i=i: file_browse_goto(i))
            folders_menu.add_separator()
            folders_menu.add_command(label = "Edit Folders...", image = img_browse_folder, compound = LEFT, underline = 0, accelerator = "Ctrl+E", command = file_browse_edit_folders)
    # Create the context menu.
    context_menu = Menu(fold_win, tearoff = False)
    # This command is needed because of a bug where the context menu won't close, I will try to fix it later.
    context_menu.add_command(label = "Close Menu", image = img_blank, compound = LEFT, underline = 6)
    context_menu.add_separator()
    context_menu.add_command(label = "Create Directory...", image = img_browse_newdir, compound = LEFT, underline = 0, accelerator = "Ctrl+N", command = file_browse_mkdir)
    context_menu.add_command(label = "Create New File...", image = img_browse_newdoc, compound = LEFT, underline = 7, accelerator = "Shift+Crtl+N", command = file_browse_mkfile)
    context_menu.add_separator()
    context_menu.add_command(label = "Open", image = img_blank, compound = LEFT, underline = 0, accelerator = "Return", command = file_browse_double_click)
    context_menu.add_command(label = "Info...", image = img_browse_about, compound = LEFT, underline = 0, accelerator = "Alt+Return", command = file_browse_info)
    context_menu.add_separator()
    context_menu.add_command(label = "Rename...", image = img_blank, compound = LEFT, underline = 0, accelerator = "F2", command = file_browse_rename)
    context_menu.add_command(label = "Delete...", image = img_browse_delete, compound = LEFT, underline = 0, accelerator = "F3, Delete", command = file_browse_del)
    # Define the function to show the context menu.
    def show_context_menu(event):
        """Shows the context menu."""
        try:
            context_menu.tk_popup(event.x_root, event.y_root, 0)
        finally:
            context_menu.grab_release()
    # Bind the right-click event to show the context menu.
    if CONFIG["browser_menu_context"] == "show":
        # OS X:
        if (root.tk.call("tk", "windowingsystem") == "aqua"):
            list_box.bind("<Button-2>", show_context_menu)
            list_box.bind("<Control-1>", show_context_menu)
        # Other systems:
        else:
            list_box.bind("<Button-3>", show_context_menu)
            list_box.bind("<Control-Button-1>", show_context_menu)
    # Bind the events.
    list_box.bind("<Double-1>", lambda event: file_browse_double_click())
    list_box.bind("<Return>", lambda event: file_browse_double_click())
    fold_win.bind("<Escape>", lambda event: fold_win.destroy())
    list_box.bind("<Alt-Left>", lambda event: file_browse_back())
    list_box.bind("<Alt-Up>", lambda event: file_browse_up())
    list_box.bind("<BackSpace>", lambda event: file_browse_back())
    if CONFIG["browser_toolbar"] == "show":
        browse_ent.bind("<Return>", lambda event: file_browse_chdir())
    # Bind the menu events.
    list_box.bind("<Alt-Return>", lambda event: file_browse_info())
    list_box.bind("<Control-Key-n>", lambda event: file_browse_mkdir())
    list_box.bind("<Shift-Control-Key-N>", lambda event: file_browse_mkfile())
    list_box.bind("<F2>", lambda event: file_browse_rename())
    list_box.bind("<F3>", lambda event: file_browse_del())
    list_box.bind("<Delete>", lambda event: file_browse_del())
    list_box.bind("<Control-Key-o>", lambda event: file_browse_goto())
    list_box.bind("<Control-Key-q>", lambda event: fold_win.close())
    list_box.bind("<Control-Key-e>", lambda event: file_browse_edit_folders())
    # Pre-fill the directory entry.
    if CONFIG["browser_toolbar"] == "show":
        browse_ent.insert(0, os.getcwd())
    # Show a list of the files and directories.
    file_browse_list()
    # Give the listbox focus.
    list_box.focus()


def file_print():
    """Prints the current file."""
    # If the file has not been saved, this cannot be done.
    if not gbl_file_name:
        showerror("Print", "File must be saved to do this.")
        return internal_return_focus()
    # All this really does is call an external program.
    # TODO: find a cross-platform, Python-only solution for printing.
    # For Windows:
    if platform.system() == "Windows":
        subprocess.call(["notepad", "/P", gbl_file_name])
    # For other systems:
    else:
        subprocess.call(["lpr", gbl_file_name])
    # Tell the user the file is printing.
    showinfo("Print", "File is finished printing.")
    # Return focus to the text box.
    return internal_return_focus()


def file_exit():
    """Closes the application, with confirmation."""
    # Define the internal functions.
    def file_exit_save():
        """Internal function for "Save" button."""
        file_save()
        # If the user cancelled the save, don't exit.
        if gbl_text_modified:
            # Close the window.
            exit_win.destroy()
            # Return focus to the text box.
            return internal_return_focus()
        # Exit the application.
        file_exit_exit()
    def file_exit_exit():
        """Internal function for "Exit" button."""
        # Get the current directory.
        ro_dir = os.getcwd()
        # Switch to the main pytextedit directory.
        os.chdir(gbl_directory)
        # Save the list of recently opened files.
        ro_str = "\n".join(gbl_recent_open)
        if len(gbl_recent_open) == 0:
            ro_str = ""
        try:
            ro_file = open("resources/recentopen", "w")
            ro_file.write(ro_str)
            ro_file.close()
        except IOError:
            showerror("Exit", "Error saving data file \"recentopen\". Continuing...")
        # Save the window size, if desired.
        if CONFIG["save_winsize"] == "yes":
            try:
                ws_file = open("resources/winsize", "w")
                ws_file.write(root.winfo_geometry())
                ws_file.close()
            except IOError:
                showerror("Exit", "Error saving data file \"winsize\". Continuing...")
        # Save the cursor mode, if desired.
        if CONFIG["save_curmode"] == "yes":
            try:
                cm_file = open("resources/curmode", "w")
                if gbl_overwrite == True:
                    cm_file.write("OVER")
                else:
                    cm_file.write("INS")
                cm_file.close()
            except IOError:
                showerror("Exit", "Error saving data file \"curmode\". Continuing...")
        # Save the filename, lock state, and encoding.
        try:
            lo_file = open("resources/lastopen", "w")
            if gbl_file_name != "":
                lo_file.write(gbl_file_name + "\n")
            else:
                lo_file.write("[{NEW}{FILE}]\n")
            if gbl_file_locked:
                lo_file.write("true\n")
            else:
                lo_file.write("false\n")
            lo_file.write(str(gbl_last_encode))
            lo_file.close()
        except IOError:
            showerror("Exit", "Error saving data file \"lastopen\". Continuing...")
        # Save the notes.
        try:
            n_file = open("resources/notes", "w")
            n_file.write(gbl_notes)
            n_file.close()
        except IOError:
            showerror("Exit", "Error saving data file \"notes\". Continuing...")
        # Save the Find history.
        try:
            find_file = open("resources/findhistory", "w")
            find_file.write("\n".join(gbl_find_history))
            find_file.close()
        except IOError:
            showerror("Exit", "Error saving data file \"findhistory\". Continuing...")
        # Save the Replace history.
        try:
            replace_file = open("resources/replacehistory", "w")
            for i in range(0, len(gbl_replace_history)):
                gbl_replace_history[i] = gbl_replace_history[i][0] + " - " + gbl_replace_history[i][1]
            replace_file.write("\n".join(gbl_replace_history))
            replace_file.close()
        except IOError:
            showerror("Exit", "Error saving data file \"replacehistory\". Continuing...")
        # Remember that the application has been run.
        try:
            fir_file = open("resources/firstopen", "w")
            fir_file.write("no")
            fir_file.close()
        except IOError:
            showerror("Exit", "Error saving data file \"firstopen\". Continuing...")
        # Save the macro bindings.
        try:
            mac_file = open("resources/macrobind", "w")
            if gbl_mac_bindings[0]:
                mac_file.write(gbl_mac_bindings[0])
            mac_file.write("\n")
            if gbl_mac_bindings[1]:
                mac_file.write(gbl_mac_bindings[1])
            mac_file.write("\n")
            if gbl_mac_bindings[2]:
                mac_file.write(gbl_mac_bindings[2])
            mac_file.write("\n")
            if gbl_mac_bindings[3]:
                mac_file.write(gbl_mac_bindings[3])
            mac_file.write("\n")
            if gbl_mac_bindings[4]:
                mac_file.write(gbl_mac_bindings[4])
            mac_file.write("\n")
            if gbl_mac_bindings[5]:
                mac_file.write(gbl_mac_bindings[5])
            mac_file.write("\n")
            if gbl_mac_bindings[6]:
                mac_file.write(gbl_mac_bindings[6])
            mac_file.write("\n")
            if gbl_mac_bindings[7]:
                mac_file.write(gbl_mac_bindings[7])
            mac_file.write("\n")
            if gbl_mac_bindings[8]:
                mac_file.write(gbl_mac_bindings[8])
            mac_file.write("\n")
            if gbl_mac_bindings[9]:
                mac_file.write(gbl_mac_bindings[9])
            mac_file.write("\n")
            mac_file.close()
        except IOError:
            showerror("Exit", "Error saving data file \"macrobind\". Continuing...")
        # switch back to original directory
        os.chdir(ro_dir)
        # Exit the application.
        sys.exit()
    # If the file has no unsaved changes, quit without confirmation.
    unsaved = 0
    for i in gbl_mdi:
        if i != None and i[3]:
            unsaved += 1
   # if gbl_text_modified and not i[3]:
    #    unsaved += 1
    if (not unsaved and not gbl_text_modified) or CONFIG["check_modified"] == "no":
        file_exit_exit()
    # Create the GUI.
    exit_win = Toplevel()
    exit_win.title("Exit")
    exit_win.transient(root)
    exit_win.grab_set()
    # Create the frame for the label.
    exit_frame1 = Frame(exit_win)
    exit_frame1.pack(side = TOP)
    # Create the label.
    if unsaved == 1:
        text = "There is 1 document with unsaved changes. Are you sure you want to close the application?"
    else:
        text = "There are %d documents with unsaved changes. Are you sure you want to close the application?" % unsaved
    exit_lbl = Label(exit_frame1, text = text)
    exit_lbl.pack(side = TOP, padx = 5, pady = 5)
    # Create the frame for the buttons.
    exit_frame2 = Frame(exit_win)
    exit_frame2.pack(side = TOP)
    # Create the Save button.
    exit_save_btn = Button(exit_frame2, text = "Save", width = 5, default = ACTIVE, command = file_exit_save)
    exit_save_btn.pack(side = LEFT)
    # Create the Exit button.
    exit_exit_btn = Button(exit_frame2, text = "Exit", width = 5, command = file_exit_exit)
    exit_exit_btn.pack(side = LEFT)
    # Create the Cancel button.
    exit_cancel_btn = Button(exit_frame2, text = "Cancel", width = 5, command = exit_win.destroy)
    exit_cancel_btn.pack(side = LEFT)
    # Bind the events.
    exit_win.bind("<Escape>", lambda event: exit_win.destroy())


def edit_undo():
    """Undos edit, if any."""
    # If the file is locked, this cannot be done.
    global gbl_file_locked
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    try:
        # Undo the last change.
        text_box.text_box.edit_undo()
        # Mark the text as having changes.
        internal_text_modified(True)
        # Update the title.
        update_title()
    except TclError:
        # Fail silently. This error would occur if there was nothing to undo.
        pass
    # Return focus to the text box.
    return internal_return_focus()


def edit_redo():
    """Redos edit, if any."""
    # If the file is locked, this cannot be done.
    global gbl_file_locked
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    try:
        # Redo the last undo.
        text_box.text_box.edit_redo()
        # Mark the text as having changes.
        internal_text_modified(True)
        # Update the title.
        update_title()
    except TclError:
        # Fail silently. This error would occur if there was nothing to redo.
        pass
    # Return focus to the text box.
    return internal_return_focus()


def edit_copy():
    """Copies selected text to clipboard, if any."""
    # If no text is selected, this cannot be done.
    if not text_box.text_box.tag_ranges("sel") and CONFIG["cut_copy_line"] == "no":
        return internal_return_focus()
    # Copy the line, if the user wants that.
    elif CONFIG["cut_copy_line"] == "yes":
        # Select the current line.
        line = text_box.text_box.index("insert").split(".")[0]
        text_box.text_box.tag_add("sel", "%s.0" % line, "%s.end" % line)
    # Get the selected text.
    text = text_box.text_box.get("sel.first", "sel.last")
    # Add the text to the clipboard.
    text_box.text_box.clipboard_clear()
    text_box.text_box.clipboard_append(text)
    # Return focus to the text box.
    return internal_return_focus()


def edit_cut():
    """Cuts selected text to clipboard, if any."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    # If no text is selected, this cannot be done.
    if not text_box.text_box.tag_ranges("sel") and CONFIG["cut_copy_line"] == "no":
        return internal_return_focus()
    # Cut the line, if the user wants that.
    elif CONFIG["cut_copy_line"] == "yes":
        # Select the current line.
        line = text_box.text_box.index("insert").split(".")[0]
        text_box.text_box.tag_add("sel", "%s.0" % line, "%s.end" % line)
    # First copy the text.
    edit_copy()
    # Then delete the selected text.
    text_box.text_box.edit_separator()
    text_box.text_box.delete("sel.first", "sel.last")
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def edit_paste():
    """Pastes clipboard contents, if any."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    try:
        text_box.text_box.edit_separator()
        # Get the text in the clipboard.
        text = text_box.text_box.selection_get(selection = "CLIPBOARD")
        # Delete the selected text, if there is any.
        if text_box.text_box.tag_ranges("sel"):
            text_box.text_box.delete("sel.first", "sel.last")
        # Insert the text.
        text_box.text_box.insert("insert", text)
        text_box.text_box.see("insert")
        # Mark the text as having changes.
        internal_text_modified(True)
        # Update the title.
        update_title()
        text_box.text_box.edit_separator()
    except TclError:
        # Fail silently.
        pass
    # Return focus to the text box.
    return internal_return_focus()


def edit_paste_overwrite():
    """Pastes clipboard contents, if any, replacing any existing text."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    try:
        text_box.text_box.edit_separator()
        # Get the text in the clipboard.
        text = text_box.text_box.selection_get(selection = "CLIPBOARD")
        # Delete all of the current text.
        text_box.text_box.delete("1.0", "end")
        # Insert the new text.
        text_box.text_box.insert("insert", text)
        text_box.text_box.see("insert")
        # Mark the text as having changes.
        internal_text_modified(True)
        # Update the title.
        update_title()
        text_box.text_box.edit_separator()
    except TclError:
        # Fail silently.
        pass
    # Return focus to the text box.
    return internal_return_focus()


def edit_paste_indent():
    """Pastes clipboard contents, if any, and indent the lines as well.."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    try:
        text_box.text_box.edit_separator()
        # Get the text in the clipboard.
        text = text_box.text_box.selection_get(selection = "CLIPBOARD")
        # Indent the text.
        text = "%s%s" % ((" " * CONFIG["indent"]), text.replace("\n", "\n%s" % (" " * CONFIG["indent"])))
        # Delete the selected text, if there is any.
        if text_box.text_box.tag_ranges("sel"):
            text_box.text_box.delete("sel.first", "sel.last")
        # Insert the text.
        text_box.text_box.insert("insert", text)
        text_box.text_box.see("insert")
        # Mark the text as having changes.
        internal_text_modified(True)
        # Update the title.
        update_title()
        text_box.text_box.edit_separator()
    except TclError:
        # Fail silently.
        pass
    # Return focus to the text box.
    return internal_return_focus()


def edit_copy_clipboard(copy):
    """Copies stuff to the clipboard."""
    # If the file has not been saved, this cannot be done.
    if not gbl_file_name:
        showerror("Copy to Clipboard", "File has not yet been saved.")
        return internal_return_focus()
    text_box.text_box.clipboard_clear()
    # Copy the full file path.
    if copy == "path" and gbl_file_name:
        text_box.text_box.clipboard_append(gbl_file_name)
    # Copy the file name.
    elif copy == "file" and gbl_file_name:
        text_box.text_box.clipboard_append(gbl_file_name_short)
    # Copy the directory.
    elif copy == "dir" and gbl_file_name:
        text_box.text_box.clipboard_append(os.path.split(gbl_file_name)[0])
    # Return focus to the text box.
    return internal_return_focus()


def edit_clear_clipboard():
    """Clears the clipboard."""
    # Clear the clipboard.
    text_box.text_box.clipboard_clear()
    # Return focus to the text box.
    return internal_return_focus()


def edit_change_case(case):
    """Changes the case of the selected text."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    # If no text is selected, this cannot be done.
    if not text_box.text_box.tag_ranges("sel"):
        showerror("Change Case", "No text selected.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # Get the selected text.
    text = text_box.text_box.get("sel.first", "sel.last")
    # Change the case of the text.
    if case == "lower":
        text = text.lower()
    elif case == "upper":
        text = text.upper()
    elif case == "cap":
        text = text.title()
    elif case == "rev":
        text = text.swapcase()
    # Delete the old text, then insert the new text.
    text_box.text_box.delete("sel.first", "sel.last")
    text_box.text_box.insert("insert", text)
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def edit_line_join():
    """Joins the selected lines."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    # If no text is selected, this cannot be done.
    if not text_box.text_box.tag_ranges("sel"):
        showerror("Join Lines", "No text selected.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # Get the selected text.
    lines = text_box.text_box.get("sel.first", "sel.last")
    # Join the lines.
    n_lines = lines.replace("\n", CONFIG["join_sep"])
    # Delete the old text, and insert the new text.
    text_box.text_box.delete("sel.first", "sel.last")
    text_box.text_box.insert("insert", n_lines)
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def edit_line_copy():
    """Copies the current line to clipboard."""
    # Get the current line.
    line = text_box.text_box.index("insert").split(".")[0]
    # Select the current line.
    text_box.text_box.tag_remove("sel", "1.0", "end")
    text_box.text_box.tag_add("sel", line + ".0", line + ".end")
    # Copy the line.
    edit_copy()
    # Remove the selection.
    text_box.text_box.tag_remove("sel", "1.0", "end")
    # Return focus to the text box.
    return internal_return_focus()


def edit_line_cut():
    """Cuts the current line to clipboard."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    # Get the current line.
    line = text_box.text_box.index("insert").split(".")[0]
    # Select the current line.
    text_box.text_box.tag_remove("sel", "1.0", "end")
    text_box.text_box.tag_add("sel", line + ".0", line + ".end")
    # Cut the line.
    edit_cut()
    # Remove the selection.
    text_box.text_box.tag_remove("sel", "1.0", "end")
    # Return focus to the text box.
    return internal_return_focus()


def edit_line_reverse():
    """Reverses the words on the current line."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # Get the current line.
    line = text_box.text_box.index("insert").split(".")[0]
    text = text_box.text_box.get(line + ".0", line + ".end")
    # Split the text.
    text_list = text.split(CONFIG["reverse_sep"])
    # Then reverse it.
    text_list.reverse()
    # Finally, join the text back together.
    text = CONFIG["reverse_sep"].join(text_list)
    # Delete the old text, and insert the new text.
    text_box.text_box.delete(line + ".0", line + ".end")
    text_box.text_box.insert("insert", text)
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def edit_line_duplicate():
    """Duplicates the current line."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # Get the current line.
    line, pos = text_box.text_box.index("insert").split(".")
    text = text_box.text_box.get("%s.0" % line, "%s.end" % line)
    # Insert the line again (duplicate it).
    text_box.text_box.insert("%s.end" % line, "\n%s" % text)
    # Move cursor, if set to insert above.
    if CONFIG["duplicate_line"] == "above":
        text_box.text_box.mark_set("insert", "%d.%s" % (int(line) + 1, pos))
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def edit_line_delete():
    """Deletes the current line."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # Get the current line.
    line = text_box.text_box.index("insert").split(".")[0]
    # Delete the line.
    text_box.text_box.delete(line + ".0", line + ".end")
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def edit_normalize():
    """Normalizes the spacing."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # Get the selected text.
    text = text_box.text_box.get("sel.first", "sel.last")
    # Normalize the string. Relace multiple occurrences of whitespace
    # with a single space.
    text = re.sub(r"\s+", " ", text.strip())
    # Delete the old text and insert the new.
    text_box.text_box.delete("sel.first", "sel.last")
    text_box.text_box.insert("insert", text)
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def edit_lock(mode = "ignore"):
    """Toggles read-only mode."""
    global gbl_file_locked
    if tkvar_lock.get() == False or mode == False:
        # Allow writing.
        text_box.text_box.config(state = NORMAL)
        # Set file as unlocked.
        gbl_file_locked = False
        # Update the title.
        update_title()
    elif mode == True:
        # Disallow writing.
        text_box.text_box.config(state = DISABLED)
        # Set file as locked.
        gbl_file_locked = True
        # Update the title.
        update_title()
    else:
        # Disallow writing.
        text_box.text_box.config(state = DISABLED)
        # Set file as locked.
        gbl_file_locked = True
        # Update the title.
        update_title()


def edit_select_all():
    """Selects all text in text box."""
    # Remove the current selection.
    text_box.text_box.tag_remove("sel", "1.0", "end")
    # Add the new selection.
    text_box.text_box.tag_add("sel", "1.0", "end-1c")
    # Return focus to the text box.
    return internal_return_focus()


def edit_deselect_all():
    """Deselects all text in text box."""
    # Remove the current selection.
    text_box.text_box.tag_remove("sel", "1.0", "end")
    # Return focus to the text box.
    return internal_return_focus()


def edit_select_from(start = None, end = None):
    """Selects text specified by user."""
    try:
        # Get the current position.
        current_pos = text_box.text_box.index("insert")
        # Get the start and end positions.
        pos1 = start or askfloat("Select From", "Start position: ", initialvalue = current_pos)
        if not pos1:
            return internal_return_focus()
        pos2 = end or askfloat("Select From", "End position: ", initialvalue = current_pos)
        if not pos2:
            return internal_return_focus()
        # Replace values if needed.
        if pos1 == "LINESTART":
            line = text_box.text_box.index("insert").split(".")[0]
            pos1 = "%s.0" % line
        if pos2 == "LINEEND":
            line = text_box.text_box.index("insert").split(".")[0]
            pos2 = "%s.end" % line
        # Remove the current selection.
        text_box.text_box.tag_remove("sel", "1.0", "end")
        # Add the new selection.
        text_box.text_box.tag_add("sel", pos1, pos2)
        # Set cursor position to second position.
        text_box.text_box.mark_set("insert", pos2)
    except TclError:
        showerror("Select From", "Could not select text.")
    # Return focus to the text box.
    return internal_return_focus()


def edit_delete_selected():
    """Deletes the currently selected text."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    # If no text is selected, this cannot be done.
    if not text_box.text_box.tag_ranges("sel"):
        showerror("Delete Selected", "No text selected.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # Delete the current selection.
    text_box.text_box.delete("sel.first", "sel.last")
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def edit_delete_nonselected():
    """Deletes all the text that is currently not selected."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    # If no text is selected, this cannot be done.
    if not text_box.text_box.tag_ranges("sel"):
        showerror("Delete Nonselected", "No text selected.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # Delete the nonselected text.
    text_box.text_box.delete("1.0", "sel.first")
    text_box.text_box.delete("sel.last", "end-1c")
    # Remove the selection.
    text_box.text_box.tag_remove("sel", "1.0", "end-1c")
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def documents_new():
    """Opens a new document in the MDI."""
    global gbl_mdi_current
    global gbl_file_name
    global gbl_file_name_short
    global gbl_file_locked
    global gbl_text_modified
    # Get info about the current document.
    curr_cursor = text_box.text_box.index("insert")
    if text_box.text_box.tag_ranges("sel"):
        curr_sel_start = text_box.text_box.index("sel.first")
        curr_sel_end = text_box.text_box.index("sel.last")
    else:
        curr_sel_start = None
        curr_sel_end = None
    curr_text = text_box.text_box.get("1.0", "end-1c")
    # Store info about the current document.
    gbl_mdi[gbl_mdi_current] = [gbl_file_name, gbl_file_name_short, gbl_file_locked, gbl_text_modified, curr_cursor, curr_sel_start, curr_sel_end, curr_text]
    # Open a new document.
    gbl_mdi_current = len(gbl_mdi)
    gbl_mdi.append(["", "", False, False, "1.0", None, None, ""])
    # Reset all variables.
    gbl_file_name = ""
    gbl_file_name_short = ""
    gbl_file_locked = False
    gbl_text_modified = False
    # Reset the lock and text box.
    text_box.text_box.config(state = "normal")
    text_box.text_box.delete("1.0", "end")
    # Update the title and status bar.
    update_title()
    update_status()
    update_status_file(gbl_file_name_short, gbl_last_encode)
    # Update the documents list.
    update_documents_list()
    # Return focus to the text box.
    return internal_return_focus()


def documents_open(filename = None):
    """Opens a document in the MDI."""
    global gbl_open_dlg
    # Prompt for the filename.
    if not filename:
        if not gbl_open_dlg:
            gbl_open_dlg = Open(initialdir = CONFIG["init_dir"], filetypes = gbl_file_types)
        filename = gbl_open_dlg.show()
        if not filename:
            return internal_return_focus()
    # Open a new document in the MDI.
    documents_new()
    # Open a file.
    file_open(to_open = filename)
    # Save the info about the document.
    curr_text = text_box.text_box.get("1.0", "end-1c")
    gbl_mdi[gbl_mdi_current] = [gbl_file_name, gbl_file_name_short, gbl_file_locked, gbl_text_modified, "1.0", None, None, curr_text]
    # Update the documents list.
    update_documents_list()
    # Return focus to the text box.
    return internal_return_focus()


def documents_close():
    """Closes the current document in the MDI."""
    global gbl_mdi_current
    global gbl_file_name
    global gbl_file_name_short
    global gbl_file_locked
    global gbl_text_modified
    # Remember the current position
    curr_pos = gbl_mdi_current
    # If this is the only document, call file_exit().
    list_without_none = filter(lambda x: x != None, gbl_mdi)
    if len(list_without_none) == 1:
        file_exit()
    # Loop though the MDI to find the next document.
    list_pos = gbl_mdi_current - 1
    found_pos = None
    while found_pos == None:
        # If this is the first item, go to the last
        if list_pos < 0:
            list_pos = len(gbl_mdi) - 1
            continue
        # If we're back at the original document, stop the loop.
        if list_pos == gbl_mdi_current:
            break
        # If this is not None, stop the loop.
        if gbl_mdi[list_pos] != None:
            found_pos = list_pos
            break
        list_pos -= 1
    # Switch to the other document.
    gbl_file_name = gbl_mdi[found_pos][0]
    gbl_file_name_short = gbl_mdi[found_pos][1]
    gbl_file_locked = gbl_mdi[found_pos][2]
    gbl_text_modified = gbl_mdi[found_pos][3]
    text_box.text_box.config(state = "normal")
    text_box.text_box.delete("1.0", "end")
    text_box.text_box.insert("1.0", gbl_mdi[found_pos][7])
    if gbl_file_locked:
        text_box.text_box.config(state = "disabled")
    text_box.text_box.mark_set("insert", gbl_mdi[found_pos][4])
    text_box.text_box.tag_remove("sel", "1.0", "end")
    if gbl_mdi[found_pos][5] != None:
        text_box.text_box.tag_add("sel", gbl_mdi[found_pos][5], gbl_mdi[found_pos][6])
    gbl_mdi_current = found_pos
    # Update the title and status bar.
    update_title()
    update_status()
    update_status_file(gbl_file_name_short, gbl_last_encode)
    # Set the old document to None.
    gbl_mdi[curr_pos] = None
    # Update the documents list.
    update_documents_list()
    # Return focus to the text box.
    return internal_return_focus()


def documents_previous():
    """Switches to the previous document in the MDI."""
    global gbl_mdi_current
    global gbl_file_name
    global gbl_file_name_short
    global gbl_file_locked
    global gbl_text_modified
    # If this is the only document, this cannot be done.
    if len(gbl_mdi) == 1:
        return internal_return_focus()
    # Otherwise, loop though the list and find the next document.
    list_pos = gbl_mdi_current - 1
    found_pos = None
    while found_pos == None:
        # If this is the first item, go to the last
        if list_pos < 0:
            list_pos = len(gbl_mdi) - 1
            continue
        # If we're back at the original document, stop the loop.
        if list_pos == gbl_mdi_current:
            break
        # If this is not None, stop the loop.
        if gbl_mdi[list_pos] != None:
            found_pos = list_pos
            break
        list_pos -= 1
    # If no other document was found, this cannot be done.
    if found_pos == None:
        return internal_return_focus()
    # Get info about the current document.
    curr_cursor = text_box.text_box.index("insert")
    if text_box.text_box.tag_ranges("sel"):
        curr_sel_start = text_box.text_box.index("sel.first")
        curr_sel_end = text_box.text_box.index("sel.last")
    else:
        curr_sel_start = None
        curr_sel_end = None
    curr_text = text_box.text_box.get("1.0", "end-1c")
    # Save the info about the current document.
    gbl_mdi[gbl_mdi_current] = [gbl_file_name, gbl_file_name_short, gbl_file_locked, gbl_text_modified, curr_cursor, curr_sel_start, curr_sel_end, curr_text]
    # Switch to the other document.
    gbl_file_name = gbl_mdi[found_pos][0]
    gbl_file_name_short = gbl_mdi[found_pos][1]
    gbl_file_locked = gbl_mdi[found_pos][2]
    gbl_text_modified = gbl_mdi[found_pos][3]
    text_box.text_box.config(state = "normal")
    text_box.text_box.delete("1.0", "end")
    text_box.text_box.insert("1.0", gbl_mdi[found_pos][7])
    if gbl_file_locked:
        text_box.text_box.config(state = "disabled")
    text_box.text_box.mark_set("insert", gbl_mdi[found_pos][4])
    text_box.text_box.tag_remove("sel", "1.0", "end")
    if gbl_mdi[found_pos][5] != None:
        text_box.text_box.tag_add("sel", gbl_mdi[found_pos][5], gbl_mdi[found_pos][6])
    gbl_mdi_current = found_pos
    # Update the title and status bar.
    update_title()
    update_status()
    update_status_file(gbl_file_name_short, gbl_last_encode)
    # Update the documents list.
    update_documents_list()
    # Return focus to the text box.
    return internal_return_focus()


def documents_next():
    """Switches to the next document in the MDI."""
    global gbl_mdi_current
    global gbl_file_name
    global gbl_file_name_short
    global gbl_file_locked
    global gbl_text_modified
    # If this is the only document, this cannot be done.
    if len(gbl_mdi) == 1:
        return internal_return_focus()
    # Otherwise, loop though the list and find the next document.
    list_pos = gbl_mdi_current + 1
    found_pos = None
    while found_pos == None:
        # If this is the last item, go to the first.
        if list_pos == len(gbl_mdi):
            list_pos = 0
            continue
        # If we're back at the original document, stop the loop.
        if list_pos == gbl_mdi_current:
            break
        # If this is not None, stop the loop.
        if gbl_mdi[list_pos] != None:
            found_pos = list_pos
            break
        list_pos += 1
    # If no other document was found, this cannot be done.
    if found_pos == None:
        return internal_return_focus()
    # Get info about the current document.
    curr_cursor = text_box.text_box.index("insert")
    if text_box.text_box.tag_ranges("sel"):
        curr_sel_start = text_box.text_box.index("sel.first")
        curr_sel_end = text_box.text_box.index("sel.last")
    else:
        curr_sel_start = None
        curr_sel_end = None
    curr_text = text_box.text_box.get("1.0", "end-1c")
    # Save the info about the current document.
    gbl_mdi[gbl_mdi_current] = [gbl_file_name, gbl_file_name_short, gbl_file_locked, gbl_text_modified, curr_cursor, curr_sel_start, curr_sel_end, curr_text]
    # Switch to the other document.
    gbl_file_name = gbl_mdi[found_pos][0]
    gbl_file_name_short = gbl_mdi[found_pos][1]
    gbl_file_locked = gbl_mdi[found_pos][2]
    gbl_text_modified = gbl_mdi[found_pos][3]
    text_box.text_box.config(state = "normal")
    text_box.text_box.delete("1.0", "end")
    text_box.text_box.insert("1.0", gbl_mdi[found_pos][7])
    if gbl_file_locked:
        text_box.text_box.config(state = "disabled")
    text_box.text_box.mark_set("insert", gbl_mdi[found_pos][4])
    text_box.text_box.tag_remove("sel", "1.0", "end")
    if gbl_mdi[found_pos][5] != None:
        text_box.text_box.tag_add("sel", gbl_mdi[found_pos][5], gbl_mdi[found_pos][6])
    gbl_mdi_current = found_pos
    # Update the title and status bar.
    update_title()
    update_status()
    update_status_file(gbl_file_name_short, gbl_last_encode)
    # Update the documents list.
    update_documents_list()
    # Return focus to the text box.
    return internal_return_focus()


def documents_view():
    """Shows all documents in the MDI."""
    # Define the internal function for managing double clicks.
    def documents_view_click():
        """Switch to a new document."""
        global gbl_mdi_current
        global gbl_file_name
        global gbl_file_name_short
        global gbl_file_locked
        global gbl_text_modified
        # Get the index number of the document.
        item = doc_list.get("active")
        if not item:
            return internal_return_focus()
        found_pos = int(re.findall(r'\d+', item)[0])
        # Get info about the current document.
        curr_cursor = text_box.text_box.index("insert")
        if text_box.text_box.tag_ranges("sel"):
            curr_sel_start = text_box.text_box.index("sel.first")
            curr_sel_end = text_box.text_box.index("sel.last")
        else:
            curr_sel_start = None
            curr_sel_end = None
        curr_text = text_box.text_box.get("1.0", "end-1c")
        # Save the info about the current document.
        gbl_mdi[gbl_mdi_current] = [gbl_file_name, gbl_file_name_short, gbl_file_locked, gbl_text_modified, curr_cursor, curr_sel_start, curr_sel_end, curr_text]
        # Switch to the other document.
        gbl_file_name = gbl_mdi[found_pos][0]
        gbl_file_name_short = gbl_mdi[found_pos][1]
        gbl_file_locked = gbl_mdi[found_pos][2]
        gbl_text_modified = gbl_mdi[found_pos][3]
        text_box.text_box.config(state = "normal")
        text_box.text_box.delete("1.0", "end")
        text_box.text_box.insert("1.0", gbl_mdi[found_pos][7])
        if gbl_file_locked:
             text_box.text_box.config(state = "disabled")
        text_box.text_box.mark_set("insert", gbl_mdi[found_pos][4])
        text_box.text_box.tag_remove("sel", "1.0", "end")
        if gbl_mdi[found_pos][5] != None:
            text_box.text_box.tag_add("sel", gbl_mdi[found_pos][5], gbl_mdi[found_pos][6])
        gbl_mdi_current = found_pos
        # Update the title and status bar.
        update_title()
        update_status()
        update_status_file(gbl_file_name_short, gbl_last_encode)
        # Update the documents list.
        update_documents_list()
        # Close the window
        doc_win.destroy()
        # Return focus to the text box.
        return internal_return_focus()
    # Create the GUI.
    doc_win = Toplevel()
    doc_win.title("Documents")
    doc_win.transient(root)
    doc_win.grab_set()
    # Create the frame for the listbox and scrollbar
    doc_frm = Frame(doc_win)
    doc_frm.pack(expand = YES, fill = BOTH, side = TOP)
    # Create the listbox and scrollbar.
    doc_list = Listbox(doc_frm, bg = CONFIG["bg"], fg = CONFIG["fg"], relief = SUNKEN, width = 50)
    doc_scroll = Scrollbar(doc_frm)
    doc_scroll.config(command = doc_list.yview)
    doc_list.config(yscrollcommand = doc_scroll.set)
    doc_scroll.pack(side = RIGHT, fill = Y)
    doc_list.pack(side = LEFT, expand = YES, fill = BOTH)
    # Populate the listbox.
    for i in range(len(gbl_mdi)):
        if gbl_mdi[i] == None:
            continue
        filename = gbl_mdi[i][1]
        if filename == "":
            filename = "[unsaved file]"
        locked = gbl_mdi[i][2]
        if locked:
            locked = "[READ ONLY]"
        else:
            locked = ""
        modified = gbl_mdi[i][3]
        if modified:
            modified = "*"
        else:
            modified = ""
        doc_list.insert("end", "%d - %s%s %s" % (i, modified, filename, locked))
    # Give the listbox focus.
    doc_list.focus()
    # Bind the events.
    doc_list.bind("<Double-1>", lambda event: documents_view_click())
    doc_list.bind("<Return>", lambda event: documents_view_click())
    doc_list.bind("<Escape>", lambda event: doc_win.destroy())


def search_find(to_find = None, start = "insert", end = "end"):
    """Finds text specified by the user."""
    # Define function to find text.
    def search_find_internal():
        """Finds text."""
        global gbl_last_find
        # Get the string to find.
        find = find_ent.get()
        if not find:
            return internal_return_focus()
        # Save the state of the case checkbox.
        CONFIG["case_insensitive"] = find_case_iv.get()
        # Save the state of the regex checkbox.
        CONFIG["regex"] = find_regex_iv.get()
        # Remember the string.
        gbl_last_find = find
        # Force an update.
        text_box.text_box.update()
        # Search for the string.
        if not find_back_iv.get():
            found = text_box.text_box.search(find, start, end, nocase = find_case_iv.get(), regexp = CONFIG["regex"])
        else:
            found = text_box.text_box.search(find, start, "1.0", nocase = find_case_iv.get(), regexp = CONFIG["regex"], backwards = True)
        # If the string was not found:
        if not found:
            showinfo("Find", "The string \"" + find + "\" was not found.")
            # Close the window, if specified.
            if not find_open_iv.get():
                find_win.destroy()
        # If the string was found:
        else:
            # Remember the string, if specified.
            if CONFIG["find_history"] == "yes":
                gbl_find_history.append(find)
            # Close the window, if specified.
            if not find_open_iv.get():
                find_win.destroy()
            # Select the string.
            found1 = found + "+%dc" % len(find)
            text_box.text_box.tag_remove("sel", "1.0", "end")
            text_box.text_box.tag_add("sel", found, found1)
            if CONFIG["search_cursor_pos"] == "end":
                text_box.text_box.mark_set("insert", found1)
            else:
                text_box.text_box.mark_set("insert", found)
            text_box.text_box.see(found)
    # Create the GUI.
    find_win = Toplevel()
    find_win.title("Find")
    find_win.transient(root)
    find_win.wm_resizable(0, 0)
    if to_find == None:
       find_win.grab_set()
    # This variable is used by the case checkbox.
    find_case_iv = IntVar()
    find_case_iv.set(CONFIG["case_insensitive"])
    # This variable is used by the regex checkbox.
    find_regex_iv = IntVar()
    find_regex_iv.set(CONFIG["regex"])
    # This variable is used by the backwards checkbox.
    find_back_iv = IntVar()
    find_back_iv.set(False)
    # This variable is used by the dialog checkbox.
    find_open_iv = IntVar()
    if CONFIG["search_keep_dlg"] == "yes":
        find_open_iv.set(True)
    else:
        find_open_iv.set(False)
    # Create the frame for the label and entry.
    find_frame1 = Frame(find_win, padx = 5, pady = 5)
    find_frame1.pack(side = TOP)
    # Create the label and entry.
    find_lbl = Label(find_frame1, text = "String to find:")
    find_lbl.grid(row = 0, column = 0, sticky = W)
    find_ent = Entry(find_frame1)
    find_ent.grid(row = 0, column = 1)
    # Create the frame for the checkboxes.
    find_frame2 = Frame(find_win, padx = 5, pady = 5)
    find_frame2.pack(side = TOP)
    # Create the case checkbox.
    find_case_chkbox = Checkbutton(find_frame2, text = "Case insensitive", variable = find_case_iv)
    find_case_chkbox.grid(row = 0, column = 0, sticky = W)
    # Create the regex checkbox.
    find_regex_chkbox = Checkbutton(find_frame2, text = "Regex search", variable = find_regex_iv)
    find_regex_chkbox.grid(row = 1, column = 0, sticky = W)
    # Create the backwards checkbox.
    find_back_chkbox = Checkbutton(find_frame2, text = "Search backwards", variable = find_back_iv)
    find_back_chkbox.grid(row = 2, column = 0, sticky = W)
    # Create the keep dialog open checkbox.
    find_open_chkbox = Checkbutton(find_frame2, text = "Keep dialog open", variable = find_open_iv)
    find_open_chkbox.grid(row = 3, column = 0, sticky = W)
    # Create the frame for the buttons.
    find_frame3 = Frame(find_win)
    find_frame3.pack(side = TOP)
    # Create the Find button.
    find_ok_btn = Button(find_frame3, text = "Find", width = 10, default = ACTIVE, command = search_find_internal)
    find_ok_btn.pack(side = LEFT, padx = 5, pady = 5)
    # Create the Cancel button.
    find_cancel_btn = Button(find_frame3, text = "Cancel", width = 10, command = find_win.destroy)
    find_cancel_btn.pack(side = LEFT, padx = 5, pady = 5)
    # Pre-fill the entry.
    if to_find != None:
        find_ent.insert(0, to_find)
    else:
        find_ent.insert(0, gbl_last_find)
    # Auto focus on the entry,
    find_ent.focus()
    # Bind the events.
    find_win.bind("<Return>", lambda event: search_find_internal())
    find_win.bind("<Escape>", lambda event: find_win.destroy())


def search_find_selected():
    """Finds text specified by user."""
    # If no text is selected, this cannot be done.
    if not text_box.text_box.tag_ranges("sel"):
        showerror("Find Selected", "No text selected.")
        return internal_return_focus()
    # Find the selected string.
    search_find(to_find = text_box.text_box.get("sel.first", "sel.last"))


def search_find_in_selected(string = None):
    """Findss text specified by user."""
    # If no text is selected, this cannot be done.
    if not text_box.text_box.tag_ranges("sel"):
        showerror("Find in Selected", "No text selected.")
        return internal_return_focus()
    # Find string in the selected text.
    search_find(to_find = string, start = "sel.first", end = "sel.last")


def search_replace(to_replace1 = None, to_replace2 = None, start = 1.0, end = "end-1c", replace_all = 0, replace_sel = False):
    """Replaces text specified by user."""
    # Define the internal functions.
    def search_replace_internal():
        """Manages which is used."""
        if replace_all_iv.get() == 1:
            # Replace all occurences.
            search_replace_all_internal()
        else:
            # Replace only the first occurence.
            search_replace_single_internal()
    def search_replace_all_internal():
        """Replaces all."""
        global gbl_dlg_replace1
        global gbl_dlg_replace2
        # Get the strings.
        replace1 = replace1_ent.get()
        replace2 = replace2_ent.get()
        if not replace1:
            return internal_return_focus()
        # Save the insert cursor.
        insert = text_box.text_box.index("insert")
        # Get all the text.
        text = text_box.text_box.get(start, end)
        regexp = None
        # If the replace is case-insensitive:
        if replace_case_iv.get() == 1:
            regexp = re.compile(re.escape(replace1), re.IGNORECASE)
        # If the replace is case-sensitive:
        else:
            regexp = re.compile(re.escape(replace1))
        # Replace the text.
        text = regexp.sub(replace2, text)
        # Delete the old text.
        text_box.text_box.delete(start, end)
        # Insert the new text.
        if start == 0.0:
            text_box.text_box.insert(1.0, text)
        else:
            text_box.text_box.insert(insert, text)
        # Remember the entries and the checkbox.
        gbl_dlg_replace1 = replace1
        gbl_dlg_replace2 = replace2
        CONFIG["case_insensitive"] = replace_case_iv.get()
        # Remember the strings, if specified.
        if CONFIG["replace_history"] == "yes":
            gbl_replace_history.append([replace1, replace2])
        # Mark the text as having changes.
        internal_text_modified(True)
        # Update the title.
        update_title()
        text_box.text_box.edit_separator()
        text_box.text_box.mark_set("insert", insert)
        # Close the window, if specified.
        if not replace_open_iv.get():
            replace_win.destroy()
    def search_replace_single_internal():
        """Replaces single."""
        global gbl_dlg_replace1
        global gbl_dlg_replace2
        # Get the strings.
        replace1 = replace1_ent.get()
        replace2 = replace2_ent.get()
        if not replace1:
            return internal_return_focus()
        # Search for the string.
        if not replace_back_iv.get():
            start_pos = text_box.text_box.search(replace1, "insert", "end", nocase = replace_case_iv.get(), regexp = replace_regex_iv.get())
        else:
            start_pos = text_box.text_box.search(replace1, "insert", "1.0", nocase = replace_case_iv.get(), regexp = replace_regex_iv.get(), backwards = True)
        # If the string was not found:
        if not start_pos:
            showinfo("Replace", "Nothing to replace.")
            # Close the window, if specified.
            if not replace_open_iv.get():
                replace_win.destroy()
            return internal_return_focus()
        # Delete the string.
        end_pos = start_pos + "+" + str(len(replace1)) + "c"
        text_box.text_box.mark_set("insert", end_pos)
        text_box.text_box.delete(start_pos, end_pos)
        # And replace it with the other string.
        text_box.text_box.insert("insert", replace2)
        # Remember entries and checkbox.
        gbl_dlg_replace1 = replace1
        gbl_dlg_replace2 = replace2
        CONFIG["case_insensitive"] = replace_case_iv.get()
        CONFIG["regex"] = replace_regex_iv.get()
        # Remember the strings, if specified.
        if CONFIG["replace_history"] == "yes":
            gbl_replace_history.append([replace1, replace2])
        # Mark the text as having changes.
        internal_text_modified(True)
        # Update the title.
        update_title()
        text_box.text_box.edit_separator()
        # Close the window, if specified.
        if not replace_open_iv.get():
            replace_win.destroy()
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    # Create the GUI.
    replace_win = Toplevel()
    replace_win.title("Replace")
    replace_win.transient(root)
    replace_win.wm_resizable(0, 0)
    if to_replace1 == None:
        replace_win.grab_set()
    # These variables are used by the checkboxes.
    replace_case_iv = IntVar()
    replace_case_iv.set(CONFIG["case_insensitive"])
    replace_all_iv = IntVar()
    replace_all_iv.set(replace_all)
    replace_regex_iv = IntVar()
    replace_regex_iv.set(CONFIG["regex"])
    replace_back_iv = IntVar()
    replace_back_iv.set(False)
    replace_open_iv = IntVar()
    if CONFIG["search_keep_dlg"] == "yes":
        replace_open_iv.set(True)
    else:
        replace_open_iv.set(False)
    # Create the frame for labels and entries.
    replace_frame1 = Frame(replace_win, padx = 5, pady = 5)
    replace_frame1.pack(side = TOP)
    # Create the label and entry for the text to replace.
    replace1_lbl = Label(replace_frame1, text = "To replace:")
    replace1_lbl.grid(row = 0, column = 0, sticky = W)
    replace1_ent = Entry(replace_frame1)
    replace1_ent.grid(row = 0, column = 1)
    # Create the label and entry for the text to replace with.
    replace2_lbl = Label(replace_frame1, text = "Replace with:")
    replace2_lbl.grid(row = 1, column = 0, sticky = W)
    replace2_ent = Entry(replace_frame1)
    replace2_ent.grid(row = 1, column = 1)
    # Create the frame for the checkboxes.
    replace_frame2 = Frame(replace_win, padx = 5, pady = 5)
    replace_frame2.pack(side = TOP)
    # Create the checkbox for case sensitivity.
    replace_case_chkbox = Checkbutton(replace_frame2, text = "Case insensitive", variable = replace_case_iv)
    replace_case_chkbox.grid(row = 0, column = 0, sticky = W)
    # Create the checkbox for replacing all.
    replace_all_chkbox = Checkbutton(replace_frame2, text = "Replace all", variable = replace_all_iv)
    replace_all_chkbox.grid(row = 1, column = 0, sticky = W)
    # Create the checkbox for regex replace.
    replace_regex_chkbox = Checkbutton(replace_frame2, text = "Regex replace", variable = replace_regex_iv)
    replace_regex_chkbox.grid(row = 2, column = 0, sticky = W)
    # Create the checkbox for backwards replace.
    replace_back_chkbox = Checkbutton(replace_frame2, text = "Replace backwards", variable = replace_back_iv)
    replace_back_chkbox.grid(row = 3, column = 0, sticky = W)
    # Create the checkbox for keeping the dialog open.
    replace_back_chkbox = Checkbutton(replace_frame2, text = "Keep dialog open", variable = replace_open_iv)
    replace_back_chkbox.grid(row = 4, column = 0, sticky = W)
    # Create the frame for the buttons.
    replace_frame3 = Frame(replace_win)
    replace_frame3.pack(side = TOP)
    # Create the Replace button.
    replace_ok_btn = Button(replace_frame3, text = "Replace", width = 10, default = ACTIVE, command = search_replace_internal)
    replace_ok_btn.pack(side = LEFT, padx = 5, pady = 5)
    # Create the Cancel button.
    replace_cancel_btn = Button(replace_frame3, text = "Cancel", width = 10, command = replace_win.destroy)
    replace_cancel_btn.pack(side = LEFT, padx = 5, pady = 5)
    # Pre-fill the entries.
    if to_replace1 != None:
        replace1_ent.insert(0, to_replace1)
    else:
        replace1_ent.insert(0, gbl_dlg_replace1)
    if to_replace2 != None:
        replace2_ent.insert(0, to_replace2)
    else:
        replace2_ent.insert(0, gbl_dlg_replace2)
    # Auto focus on the entry.
    if replace_sel:
        replace2_ent.focus()
    else:
        replace1_ent.focus()
    # Bind the events.
    replace_win.bind("<Return>", lambda event: search_replace_internal())
    replace_win.bind("<Escape>", lambda event: replace_win.destroy())
    # Make sure nothing gets unintentionally deleted.
    return "break"


def search_replace_selected(to_replace = None):
    """Replaces text specified by user."""
    # If no text is selected, this cannot be done.
    if not text_box.text_box.tag_ranges("sel"):
        showerror("Replace Selected", "No text selected.")
        return internal_return_focus()
    # Replace.
    search_replace(to_replace1 = text_box.text_box.get("sel.first", "sel.last"), to_replace2 = to_replace, replace_all = 1, replace_sel = True)


def search_replace_in_selected(nto_replace1 = None, nto_replace2 = None):
    """Replaces text specified by user."""
    # If no text is selected, this cannot be done.
    if not text_box.text_box.tag_ranges("sel"):
        showerror("Replace in Selected", "No text selected.")
        return internal_return_focus()
    # Replace.
    search_replace(to_replace1 = nto_replace1, to_replace2 = nto_replace2, start = "sel.first", end = "sel.last", replace_all = 1)


def search_find_history():
    """Shows a list of the Find history."""
    # If there is no history, don't show the dialog.
    if len(gbl_find_history) == 0:
        showinfo("Find History", "There is no history to display.")
        return internal_return_focus()
    # Define the internal function to manage double-clicks.
    def search_find_history_click():
        """Manages double-click events for the history list."""
        # Get the active list item.
        item = fhist_list.get("active")
        if not item:
            return
        # Close the window.
        fhist_win.destroy()
        # Open the Find dialog.
        search_find(to_find = item)
    # Create the GUI.
    fhist_win = Toplevel()
    fhist_win.title("Find History")
    fhist_win.transient(root)
    fhist_win.grab_set()
    # Create the frame for the listbox and scrollbar
    fhist_frm = Frame(fhist_win)
    fhist_frm.pack(expand = YES, fill = BOTH, side = TOP)
    # Create the listbox and scrollbar.
    fhist_list = Listbox(fhist_frm, bg = CONFIG["bg"], fg = CONFIG["fg"], relief = SUNKEN, width = 50)
    fhist_scroll = Scrollbar(fhist_frm)
    fhist_scroll.config(command = fhist_list.yview)
    fhist_list.config(yscrollcommand = fhist_scroll.set)
    fhist_scroll.pack(side = RIGHT, fill = Y)
    fhist_list.pack(side = LEFT, expand = YES, fill = BOTH)
    history = gbl_find_history[:]
    # Reverse the list, if necessary.
    if CONFIG["search_history_order"] == "oldest last":
        history.reverse()
    # Populate the listbox.
    for i in history:
        fhist_list.insert("end", str(i))
    # Give the listbox focus.
    fhist_list.focus()
    # Bind the events.
    fhist_list.bind("<Double-1>", lambda event: search_find_history_click())
    fhist_list.bind("<Return>", lambda event: search_find_history_click())
    fhist_list.bind("<Escape>", lambda event: fhist_win.destroy())


def search_replace_history():
    """Shows a list of the Replace history."""
    # If there is no history, don't show the dialog.
    if len(gbl_replace_history) == 0:
        showinfo("Replace History", "There is no history to display.")
        return internal_return_focus()
    # Define the internal function to manage double-clicks.
    def search_replace_history_click():
        """Manages double-click events for the history list."""
        # Get the active list item.
        item = frep_list.get("active")
        if not item:
            return
        item = item.split(" - ")
        # Close the window.
        frep_win.destroy()
        # Open the Replace dialog.
        search_replace(to_replace1 = item[0], to_replace2 = item[1])
    # Create the GUI.
    frep_win = Toplevel()
    frep_win.title("Replace History")
    frep_win.transient(root)
    frep_win.grab_set()
    # Create the frame for the listbox and scrollbar
    frep_frm = Frame(frep_win)
    frep_frm.pack(expand = YES, fill = BOTH, side = TOP)
    # Create the listbox and scrollbar.
    frep_list = Listbox(frep_frm, bg = CONFIG["bg"], fg = CONFIG["fg"], relief = SUNKEN, width = 50)
    frep_scroll = Scrollbar(frep_frm)
    frep_scroll.config(command = frep_list.yview)
    frep_list.config(yscrollcommand = frep_scroll.set)
    frep_scroll.pack(side = RIGHT, fill = Y)
    frep_list.pack(side = LEFT, expand = YES, fill = BOTH)
    history = gbl_replace_history[:]
    # Reverse the list, if necessary.
    if CONFIG["search_history_order"] == "oldest last":
        history.reverse()
    # Populate the listbox.
    for i in history:
        frep_list.insert("end", str(i[0]) + " - " + str(i[1]))
    # Give the listbox focus.
    frep_list.focus()
    # Bind the events.
    frep_list.bind("<Double-1>", lambda event: search_replace_history_click())
    frep_list.bind("<Return>", lambda event: search_replace_history_click())
    frep_list.bind("<Escape>", lambda event: frep_win.destroy())


def search_goto(line2 = None):
    """Goes to line number specified by the user."""
    # Get the current line number.
    line = text_box.text_box.index("insert").split(".")[0]
    # Ask the user for the line number.
    line = line2 or askinteger("Goto", "Enter line number:", initialvalue = line)
    if not line:
        return internal_return_focus()
    # Force an update and give focus to the text box.
    text_box.text_box.update()
    text_box.text_box.focus()
    # Get the last line number.
    lines = int(text_box.text_box.index("end-1c").split(".")[0])
    # If the line is negative, go to that many lines from the end.
    if CONFIG["goto_negative"] == "from end":
        if line < 0:
            line = lines + line + 1
    # Or go that many from the beginning.
    elif CONFIG["goto_negative"] == "from beginning":
        line = -line
    # Or simply ignore it.
    elif CONFIG["goto_negative"] == "ignore":
        return internal_return_focus()
    # If the line is positive and less than the last line:
    if line > 0 and line <= lines:
        text_box.text_box.mark_set("insert", "%d.0" % line)
        text_box.text_box.tag_remove("sel", "1.0", "end")
        text_box.text_box.see("insert")
    # If line is invalid:
    else:
        showerror("Goto", "Illegal line number specified. Number must be positive and not greater then the number of lines of text.")
    # Return focus to the text box.
    return internal_return_focus()


def search_jump_top():
    """Scrolls the text box all the way to the top."""
    # Remove any selection.
    text_box.text_box.tag_remove("sel", "1.0", "end")
    # Set the cursor
    text_box.text_box.mark_set("insert", "1.0")
    text_box.text_box.see("insert")
    # See and return focus to text box.
    return internal_return_focus()


def search_jump_bottom():
    """Scrolls the text box all the way to the bottom."""
    # Remove any selection.
    text_box.text_box.tag_remove("sel", "1.0", "end")
    # Set the cursor.
    text_box.text_box.mark_set("insert", "end")
    text_box.text_box.see("insert")
    # See and return focus to text box.
    return internal_return_focus()


def search_jump_select_start():
    """Scrolls the text box to the start of the selected text."""
    # If no text is selected, this cannot be done.
    if not text_box.text_box.tag_ranges("sel"):
        showerror("Jump to Selection Start", "No text selected.")
        return internal_return_focus()
    # Set the cursor.
    text_box.text_box.mark_set("insert", "sel.first")
    text_box.text_box.see("insert")
    # See and return focus to text box.
    return internal_return_focus()


def search_jump_select_end():
    """Scrolls the text box to the end of the selected text."""
    # If no text is selected, this cannot be done.
    if not text_box.text_box.tag_ranges("sel"):
        showerror("Jump to Selection End", "No text selected.")
        return internal_return_focus()
    # Set the cursor.
    text_box.text_box.mark_set("insert", "sel.last")
    text_box.text_box.see("insert")
    # See and return focus to text box.
    return internal_return_focus()


def search_jump_line_start():
    """Moves the cursor to the start of the line."""
    # Remove any selection.
    text_box.text_box.tag_remove("sel", "1.0", "end")
    # Get the line.
    line = text_box.text_box.index("insert").split(".")[0]
    # Set the cursor.
    text_box.text_box.mark_set("insert", "%s.0" % line)
    text_box.text_box.see("insert")
    # See and return focus to text box.
    return internal_return_focus()


def search_jump_line_end():
    """Moves the cursor to the end of the line."""
    # Remove any selection.
    text_box.text_box.tag_remove("sel", "1.0", "end")
    # Get the line.
    line = text_box.text_box.index("insert").split(".")[0]
    # Set the cursor.
    text_box.text_box.mark_set("insert", "%s.end" % line)
    text_box.text_box.see("insert")
    # See and return focus to text box.
    return internal_return_focus()


def search_open_url():
    """Opens a website in the user's web browser."""
    # If no text is selected, this cannot be done.
    if not text_box.text_box.tag_ranges("sel"):
        showerror("Open URL in Web Browser", "No text selected.")
        return internal_return_focus()
    # Open the file in the user's web browser.
    webbrowser.open(text_box.text_box.get("sel.first", "sel.last"))
    # Return focus to the text box.
    return internal_return_focus()


def search_search_sel(site):
    """Searches for the selected text on the specified website."""
    # If no text is selected, this cannot be done.
    if not text_box.text_box.tag_ranges("sel"):
        showerror("Search Selected", "No text selected.")
        return internal_return_focus()
    # Get the selected text.
    sel = text_box.text_box.get("sel.first", "sel.last")
    # Encode the selected text.
    sel = quote(sel.encode("utf8"))
    # Open a web browser with the selected search and specified site.
    webbrowser.open(site + sel)
    # Return focus to the text box.
    return internal_return_focus()


def tools_bookmarks_add():
    """Adds a bookmark."""
    # Get the current line.
    line = int(text_box.text_box.index("insert").split(".")[0])
    # If the line has already been bookmarked, don't add it again.
    if line in gbl_bookmarks:
        showinfo("Bookmarks", "Bookmark already added on line %d." % line)
        # Return focus to the text box.
        return internal_return_focus()
    # Add line to bookmarks.
    gbl_bookmarks.append(line)
    # Notify user that the bookmark has been added.
    showinfo("Bookmarks", "Bookmark added on line %d." % line)
    # Return focus to the text box.
    return internal_return_focus()


def tools_bookmarks_view():
    """Shows a window with the bookmarks."""
    # If there are no bookmarks, don't show the dialog.
    if len(gbl_bookmarks) == 0:
        showinfo("View Bookmarks", "There are no bookmarks.\n\nBookmarks can be added from \"Tools -> Bookmarks -> Add Bookmark...\" or by pressing \"Ctrl+B\".")
        return internal_return_focus()
    # Define internal function.
    def tools_bookmarks_view_click():
        """Manages double-clicks on listbox."""
        # Get line number of bookmark.
        item = bm_list.get("active")
        if not item:
            return
        line_num = re.findall(r'\d+', item)[0]
        # Close the window.
        bm_win.destroy()
        # Go to the line.
        text_box.text_box.mark_set("insert", "%s.0" % line_num)
        # Return focus to the text box.
        return internal_return_focus()
    # Create the GUI.
    bm_win = Toplevel()
    bm_win.title("Bookmarks")
    bm_win.transient(root)
    bm_win.grab_set()
    # Create the frame for the listbox and scrollbar.
    bm_frm = Frame(bm_win)
    bm_frm.pack(expand = YES, fill = BOTH, side = TOP)
    # Create the listbox and scrollbar.
    bm_list = Listbox(bm_frm, bg = CONFIG["bg"], fg = CONFIG["fg"], relief = SUNKEN, width = 60)
    bm_scroll = Scrollbar(bm_frm)
    bm_scroll.config(command = bm_list.yview)
    bm_list.config(yscrollcommand = bm_scroll.set)
    bm_scroll.pack(side = RIGHT, fill = Y)
    bm_list.pack(side = LEFT, expand = YES, fill = BOTH)
    # Sort the bookmarks.
    gbl_bookmarks.sort()
    # Get the total number of lines in the text box.
    lines = int(text_box.text_box.index("end-1c").split(".")[0])
    # Populate the listbox.
    for i in gbl_bookmarks:
        # If this in a valid line number:
        if i <= lines:
            # Build each string.
            bm_text = "%d - " % i
            # Get the text of the line.
            line = text_box.text_box.get("%d.0" % i, "%d.end" % i)
            # If the line is less than 50 chars, insert the whole line.
            if len(line) < 50:
                bm_text += line
            # Otherwise cut it to 50 chars.
            else:
                bm_text += line[:50]
            # Insert string into listbox.
            bm_list.insert("end", bm_text)
    # Give focus to the listbox.
    bm_list.focus()
    # Bind the events.
    bm_list.bind("<Double-1>", lambda event: tools_bookmarks_view_click())
    bm_list.bind("<Return>", lambda event: tools_bookmarks_view_click())
    bm_list.bind("<Escape>", lambda event: bm_win.destroy())


def tools_bookmarks_clear():
    """Clears all bookmarks."""
    global gbl_bookmarks
    # If there are no bookmarks, this cannot be done.
    if len(gbl_bookmarks) == 0:
        showinfo("Bookmarks", "There are no bookmarks to clear.")
        return internal_return_focus()
    # Ask the user to confirm the clear.
    bm_conf = askyesno("Bookmarks", "Are you sure you want to clear all %d bookmarks?" % len(gbl_bookmarks))
    # Clear the bookmarks.
    if bm_conf:
        gbl_bookmarks[:] = []
    # Return focus to the text box.
    return internal_return_focus()


def tools_bookmarks_save():
    """Saves the current list of bookmarks."""
    # If there are no bookmarks, this cannot be done.
    if len(gbl_bookmarks) == 0:
        showinfo("Bookmarks", "There are no bookmarks to save.")
        return internal_return_focus()
    # Remember the current directory, and switch to the main application directory.
    curr_dir = os.getcwd()
    os.chdir(gbl_directory)
    # Prompt for the name.
    bm_name = askstring("Bookmarks", "Enter name to save under:")
    # If nothing was entered, don't do anything.
    if not bm_name:
        return internal_return_focus()
    # Get the file/directory separator.
    if platform.system() == "Windows":
        file_sep = "\\"
    else:
        file_sep = "/"
    # Split the string on this separator, and only use the last one.
    split_bm_name = bm_name.split(file_sep)
    bm_name = split_bm_name[-1]
    # Check if this file exists, and ask for cofirmation if it does.
    if os.path.isfile("resources/bookmarks/" + bm_name):
        bm_conf = askyesno("Bookmarks", "File already exists. Overwrite?")
        if not bm_conf:
            os.chdir(curr_dir)
            return internal_return_focus()
    # Convert the list of bookmarks to a string.
    bm_str = ""
    for i in gbl_bookmarks:
        bm_str += str(i) + "\n"
    bm_str = bm_str[:-1]
    # Save the bookmarks
    try:
        bm_file = open("resources/bookmarks/" + bm_name, "w")
        bm_file.write(bm_str)
        bm_file.close()
    except IOError:
        showerror("Bookmarks", "File could not be saved.")
    # Go back to the original directory.
    os.chdir(curr_dir)
    # Return focus to the text box.
    return internal_return_focus()


def tools_bookmarks_open():
    """Shows a window with the bookmark files."""
    # If there are no bookmark files, don't show the dialog.
    if len(gbl_favorites) == 0:
        showinfo("Open Bookmarks", "There are no bookmark files to open.")
        return internal_return_focus()
    # Remember the current directory, and switch to the resource directory.
    curr_dir = os.getcwd()
    os.chdir(gbl_directory + "/resources/bookmarks")
    # Get the list of files.
    bm_files = glob.glob("*")
    # Sort the list.
    bm_files.sort()
    # Go back to the originial directory.
    os.chdir(curr_dir)
    # Define internal function.
    def tools_bookmarks_open_click():
        """Manages double-clicks on the listbox."""
        global gbl_bookmarks
        # Remember the current directory, and switch to the resource directory.
        curr_dir = os.getcwd()
        os.chdir(gbl_directory + "/resources/bookmarks")
        # Get line number of bookmark.
        item = bm_list.get("active")
        if not item:
            return
        # Clear the current list of bookmarks.
        gbl_bookmarks[:] = []
        # Get the bookmarks from the file.
        try:
            bm_file = open(item, "r")
            bm_data = bm_file.read()
            bm_file.close()
        except IOError:
            showerror("Bookmarks", "Bookmark file could not be opened.")
            os.chdir(curr_dir)
            bm_win.destroy()
            return internal_return_focus()
        # Convert the string to a list.
        bm_data_list = bm_data.split("\n")
        # Convert the items to numbers.
        for i in range(0, len(bm_data_list)):
            bm_data_list[i] = int(bm_data_list[i])
        # Add the new bookmarks.
        gbl_bookmarks = bm_data_list
        # Close the window.
        bm_win.destroy()
        # Go back to the original directory.
        os.chdir(curr_dir)
        # Return focus to the text box.
        return internal_return_focus()
    # Create the GUI.
    bm_win = Toplevel()
    bm_win.title("Open Bookmarks")
    bm_win.transient(root)
    bm_win.grab_set()
    # Create the frame for the listbox and scrollbar.
    bm_frm = Frame(bm_win)
    bm_frm.pack(expand = YES, fill = BOTH, side = TOP)
    # Create the listbox and scrollbar.
    bm_list = Listbox(bm_frm, bg = CONFIG["bg"], fg = CONFIG["fg"], relief = SUNKEN, width = 60)
    bm_scroll = Scrollbar(bm_frm)
    bm_scroll.config(command = bm_list.yview)
    bm_list.config(yscrollcommand = bm_scroll.set)
    bm_scroll.pack(side = RIGHT, fill = Y)
    bm_list.pack(side = LEFT, expand = YES, fill = BOTH)
    # Populate the listbox.
    for i in bm_files:
        bm_list.insert("end", i)
    # Give focus to the listbox.
    bm_list.focus()
    # Bind the events.
    bm_list.bind("<Double-1>", lambda event: tools_bookmarks_open_click())
    bm_list.bind("<Return>", lambda event: tools_bookmarks_open_click())
    bm_list.bind("<Escape>", lambda event: bm_win.destroy())


def tools_macro_run():
    """Runs a macro."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    # Remember the current directory, and switch to the resource directory.
    curr_dir = os.getcwd()
    os.chdir(gbl_directory + "/resources/macros")
    # Get the list of files.
    mac_files = glob.glob("*")
    # Sort the list.
    mac_files.sort()
    # Switch back to the original directory.
    os.chdir(curr_dir)
    # If there are no macros, don't show the dialog.
    if len(mac_files) == 0:
        showinfo("Run Macros", "There are no macros to run.")
        return internal_return_focus()
    # Define internal function.
    def tools_macro_run_click():
        """Manages double-clicks on the listbox."""
        # Get the macro name.
        mac_name = mac_list.get("active")
        if not mac_name:
            return
        # Close the window.
        mac_win.destroy()
        # Pass the name to the function for executing.
        tools_macro_run_file(mac_name)
        # Return focus to the text box.
        return internal_return_focus()
    # Create the GUI.
    mac_win = Toplevel()
    mac_win.title("Run Macro")
    mac_win.transient(root)
    mac_win.grab_set()
    # Create the frame for the listbox and scrollbar.
    mac_frm = Frame(mac_win)
    mac_frm.pack(expand = YES, fill = BOTH, side = TOP)
    # Create the listbox and scrollbar.
    mac_list = Listbox(mac_frm, bg = CONFIG["bg"], fg = CONFIG["fg"], relief = SUNKEN, width = 60)
    mac_scroll = Scrollbar(mac_frm)
    mac_scroll.config(command = mac_list.yview)
    mac_list.config(yscrollcommand = mac_scroll.set)
    mac_scroll.pack(side = RIGHT, fill = Y)
    mac_list.pack(side = LEFT, expand = YES, fill = BOTH)
    # Populate the listbox.
    for i in mac_files:
        mac_list.insert("end", i)
    # Give focus to the listbox.
    mac_list.focus()
    # Bind the events.
    mac_list.bind("<Double-1>", lambda event: tools_macro_run_click())
    mac_list.bind("<Return>", lambda event: tools_macro_run_click())
    mac_list.bind("<Escape>", lambda event: mac_win.destroy())


def tools_macro_run_file(macro):
    """Runs a macro."""
    # Remember the current directory, and switch to main application directory.
    curr_dir = os.getcwd()
    os.chdir(gbl_directory)
    # Load the file.
    try:
        mac_file = open("resources/macros/" + macro, "r")
        mac_text = mac_file.read()
        mac_file.close()
    except IOError:
        showerror("Run Macro", "Macro file \"" + macro + "\" could not be read.")
        os.chdir(curr_dir)
        return internal_return_focus()
    # Switch back to the original directory.
    os.chdir(curr_dir)
    # Split the text into lines.
    mac_lines = mac_text.split("\n")
    mac_len = len(mac_lines)
    # If the first line is "!suppress_dlg", don't show the completion dialog.
    show_dlg = True
    if mac_lines[0] == "!suppress_dlg":
        show_dlg = False
        mac_lines = mac_lines[1:]
    # If the first line is "!more_dlg", show more information in the dialog.
    show_more = False
    if mac_lines[0] == "!more_dlg":
        show_more = True
        mac_lines = mac_lines[1:]
        start_time = datetime.datetime.now()
    # Parse each line.
    for i in range(0, len(mac_lines)):
        result = tools_macro_parse(i, mac_lines[i], macro)
        # If there was an error, stop execution.
        if result == False and CONFIG["macro_stop_error"] == "yes":
            break
    end_time = datetime.datetime.now()
    # Clear the variable list.
    gbl_mac_vars.clear()
    # Tell the user the macro has finished running.
    if show_dlg:
        more_dlg = ""
        if show_more:
            time_diff = (end_time - start_time).microseconds / 1000
            more_dlg = "\n\nTime start: %d\nTime end: %d\nTime difference: %dms\n\nLines: %d" % (start_time.microsecond, end_time.microsecond, time_diff, mac_len - 1)
        showinfo("Run Macro", "Macro \"" + macro + "\" has finished running." + more_dlg)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def tools_macro_parse(line, text, macro):
    """Parses and executes each line of the macro."""
    # If the line is an empty string or if it starts with a "#", ignore it.
    if text == "" or text.startswith(CONFIG["macro_comment_start"]):
        return True
    # If the line starts with "~ ", send it to Python's exec() statement/function.
    if text.startswith(CONFIG["macro_python_start"]) and CONFIG["macro_python"] == "yes":
        text = text[len(CONFIG["macro_python_start"]):]
        exec(text)
        return True
    # If the line starts with "$", it's declaring a variable.
    if text[0] == CONFIG["macro_variable_start"] and CONFIG["macro_variables"] == "yes":
        var_comp = text[1:].split(" = ")
        var_name = var_comp[0]
        var_val = " = ".join(var_comp[1:])
        gbl_mac_vars[var_name] = var_val
        return True
    # Otherwise if it contains a "$" elsewhere, it's using a variable.
    elif CONFIG["macro_variable_start"] in text and CONFIG["macro_variables"] == "yes":
        var_pos = -1
        first = True
        while True:
            if first:
                var_pos = text.find(CONFIG["macro_variable_start"])
                first = False
            else:
                var_pos = text.find(CONFIG["macro_variable_start"], var_pos)
            if var_pos == -1:
                break
            # If the previous character is a "\", the "$" isn't meant as a variable.
            if text[var_pos - 1] != "\\":
                var_end = text.find(" ", var_pos)
                var_end2 = text.find("\n", var_pos)
                if var_end2 < var_end:
                    var_end = var_end2
                var_name = text[var_pos:var_end]
                if var_end == -1:
                    var_name = text[var_pos:]
                if " " in var_name:
                    str_pos = var_name.find(" ")
                    var_name = var_name[:str_pos]
                text = text.replace(var_name, gbl_mac_vars[var_name[1:]])
            var_pos += 1
    # Split the macro into components on each space.
    mac_comp = text.split(" ")
    # Execute the line.
    try:
        # out string
        if mac_comp[0] == "out":
            print(" ".join(mac_comp[1:]))
        # show_info string
        if mac_comp[0] == "show_info":
            showinfo(macro, " ".join(mac_comp[1:]))
        # show_warn string
        if mac_comp[0] == "show_warn":
            showwarning(macro, " ".join(mac_comp[1:]))
        # show_err string
        if mac_comp[0] == "show_err":
            showerror(macro, " ".join(mac_comp[1:]))
        # set_insert location
        if mac_comp[0] == "set_insert":
            text_box.text_box.mark_set("insert", mac_comp[1])
        # insert location string
        elif mac_comp[0] == "insert":
            ins_str = " ".join(mac_comp[2:])
            text_box.text_box.insert(mac_comp[1], ins_str)
            internal_text_modified(True)
            update_title()
        # insert_nl location number
        elif mac_comp[0] == "insert_nl":
            text_box.text_box.insert(mac_comp[1], "\n" * int(mac_comp[2]))
            internal_text_modified(True)
            update_title()
        # delete location1 location2
        elif mac_comp[0] == "delete":
            text_box.text_box.delete(mac_comp[1], mac_comp[2])
            internal_text_modified(True)
            update_title()
        # new
        elif mac_comp[0] == "new":
            file_new()
        # open filename
        elif mac_comp[0] == "open":
            file_open(to_open = " ".join(mac_comp[1:]))
        # open_url url
        elif mac_comp[0] == "open_url":
            file_open_url(url = " ".join(mac_comp[1:]))
        # reload
        elif mac_comp[0] == "reload":
            file_reload()
        # save
        elif mac_comp[0] == "save":
            file_save()
        # save_as filename
        elif mac_comp[0] == "save_as":
            file_save(mode = "saveas", filename = " ".join(mac_comp[1:]))
        # save_copy filename
        elif mac_comp[0] == "save_copy":
            file_save_copy(filename = " ".join(mac_comp[1:]))
        # revert_save
        elif mac_comp[0] == "revert_save":
            file_revert_save()
        # open_binary filename
        elif mac_comp[0] == "open_binary":
            file_open_binary(to_open = " ".join(mac_comp[1:]))
        # reload_binary
        elif mac_comp[0] == "reload_binary":
            file_reload_binary()
        # save_binary
        elif mac_comp[0] == "save_binary":
            file_save_binary()
        # insert_file filename
        elif mac_comp[0] == "insert_file":
            file_open(to_open = " ".join(mac_comp[1:]), insert = True)
        # delete_file
        elif mac_comp[0] == "delete_file":
            file_delete()
        # rename filename
        elif mac_comp[0] == "rename":
            file_rename(filename = " ".join(mac_comp[1:]))
        # browse
        elif mac_comp[0] == "browse":
            file_browse()
        # print
        elif mac_comp[0] == "print":
            file_print()
        # exit
        elif mac_comp[0] == "exit":
            file_exit()
        # undo
        elif mac_comp[0] == "undo":
            edit_undo()
        # redo
        elif mac_comp[0] == "redo":
            edit_redo()
        # cut
        elif mac_comp[0] == "cut":
            edit_cut()
        # copy
        elif mac_comp[0] == "copy":
            edit_copy()
        # paste
        elif mac_comp[0] == "paste":
            edit_paste()
        # paste_overwrite
        elif mac_comp[0] == "paste_overwrite":
            edit_paste_overwrite()
        # paste_indent
        elif mac_comp[0] == "paste_indent":
            edit_paste_indent()
        # clear_clip
        elif mac_comp[0] == "clear_clip":
            edit_clear_clipboard()
        # copy_path
        elif mac_comp[0] == "copy_path":
            edit_copy_clipboard("path")
        # copy_file
        elif mac_comp[0] == "copy_file":
            edit_copy_clipboard("file")
        # copy_dir
        elif mac_comp[0] == "copy_dir":
            edit_copy_clipboard("dir")
        # lock
        elif mac_comp[0] == "lock":
            edit_lock(True)
        # unlock
        elif mac_comp[0] == "unlock":
            edit_lock(False)
        # case_lower
        elif mac_comp[0] == "case_lower":
            edit_change_case("lower")
        # case_upper
        elif mac_comp[0] == "case_upper":
            edit_change_case("upper")
        # case_cap
        elif mac_comp[0] == "case_cap":
            edit_change_case("cap")
        # case_rev
        elif mac_comp[0] == "case_rev":
            edit_change_case("rev")
        # join_lines
        elif mac_comp[0] == "join_lines":
            edit_line_join()
        # copy_line
        elif mac_comp[0] == "copy_line":
            edit_line_copy()
        # cut_line
        elif mac_comp[0] == "cut_line":
            edit_line_cut()
        # rev_line
        elif mac_comp[0] == "rev_line":
            edit_line_reverse()
        # dup_line
        elif mac_comp[0] == "dup_line":
            edit_line_duplicate()
        # del_line
        elif mac_comp[0] == "del_line":
            edit_line_delete()
        # normalize
        elif mac_comp[0] == "normalize":
            edit_normalize()
        # sel_all
        elif mac_comp[0] == "sel_all":
            edit_select_all()
        # desel_all
        elif mac_comp[0] == "desel_all":
            edit_deselect_all()
        # sel_from location1 location2
        elif mac_comp[0] == "sel_from":
            edit_select_from(start = mac_comp[1], end = mac_comp[2])
        # sel_before
        elif mac_comp[0] == "sel_before":
            edit_select_from(start = "1.0", end = "insert")
        # sel_after
        elif mac_comp[0] == "sel_after":
            edit_select_from(start = "insert", end = "end")
        # sel_line_before
        elif mac_comp[0] == "sel_line_before":
            edit_select_from(start = "LINESTART", end = "insert")
        # sel_line_after
        elif mac_comp[0] == "sel_line_after":
            edit_select_from(start = "insert", end = "LINEEND")
        # del_sel
        elif mac_comp[0] == "del_sel":
            edit_delete_selected()
        # del_nonsel
        elif mac_comp[0] == "del_nonsel":
            edit_delete_nonselected()
        # new_doc
        elif mac_comp[0] == "new_doc":
            documents_new()
        # open_doc filename
        elif mac_comp[0] == "open_doc":
            documents_open(filename = " ".join(mac_comp[1:]))
        # close_doc
        elif mac_comp[0] == "close_doc":
            documents_close()
        # prev_doc
        elif mac_comp[0] == "prev_doc":
            documents_previous()
        # next_doc
        elif mac_comp[0] == "next_doc":
            documents_next()
        # find string
        elif mac_comp[0] == "find":
            search_find(to_find = " ".join(mac_comp[1:]))
        # find_sel
        elif mac_comp[0] == "find_sel":
            search_find_selected()
        # find_in_sel string
        elif mac_comp[0] == "find_in_sel":
            search_find_in_selected(string = " ".join(mac_comp[1:]))
        # goto line
        elif mac_comp[0] == "goto":
            search_goto(line2 = mac_comp[1])
        # replace string1 ||| string2
        elif mac_comp[0] == "replace":
            new_comp = (" ".join(mac_comp[1:])).split(" ||| ")
            search_replace(to_replace1 = new_comp[0], to_replace2 = new_comp[1])
        # replace_sel string2
        elif mac_comp[0] == "replace_sel":
            search_replace_selected(to_replace = mac_comp[1])
        # replace_in_sel string1 ||| string2
        elif mac_comp[0] == "replace_in_sel":
            new_comp = (" ".join(mac_comp[1:])).split(" ||| ")
            search_replace_in_selected(nto_replace1 = new_comp[0], nto_replace2 = new_comp[1])
        # find_history
        elif mac_comp[0] == "find_history":
            search_find_history()
        # replace_history
        elif mac_comp[0] == "replace_history":
            search_replace_history()
        # jump_top
        elif mac_comp[0] == "jump_top":
            search_jump_top()
        # jump_bottom
        elif mac_comp[0] == "jump_bottom":
            search_jump_bottom()
        # jump_insert
        elif mac_comp[0] == "jump_insert":
            internal_return_focus()
        # jump_select_start
        elif mac_comp[0] == "jump_select_start":
            search_jump_select_start()
        # jump_select_end
        elif mac_comp[0] == "jump_select_end":
            search_jump_select_end()
        # jump_line_start
        elif mac_comp[0] == "jump_line_start":
            search_jump_line_start()
        # jump_line_end
        elif mac_comp[0] == "jump_line_end":
            search_jump_line_end()
        # open_url_wb
        elif mac_comp[0] == "open_url_wb":
            search_open_url()
        # search_site site
        elif mac_comp[0] == "search_site":
            site = mac_comp[1]
            if site == "google":
                site = "http://www.google.com/search?q="
            elif site == "duckduckgo":
                site = "http://www.duckduckgo.com/?q="
            elif site == "yahoo":
                site = "http://search.yahoo.com/search?p="
            elif site == "bing":
                site = "http://www.bing.com/search?q="
            elif site == "wikipedia":
                site = "http://www.wikipedia.org/wiki/"
            elif site == "wiktionary":
                site = "http://www.wiktionary.org/wiki/"
            elif site == "wikidata":
                site = "http://www.wikidata.org/wiki/"
            elif site == "wikisource":
                site = "http://www.wikisource.org/wiki/"
            elif site == "youtube":
                site = "http://www.youtube.com/results?search_query="
            elif site == "wolframalpha":
                site = "http://www.wolframalpha.com/input/?i="
            elif site == "aboutcom":
                site = "http://search.about.com/?q="
            elif site == "isgdshorten":
                site = "http://is.gd/create.php?format=simple&url="
            elif site == "isgdlookup":
                site = "http://is.gd/forward.php?shorturl="
            search_search_sel(site)
        # add_bookmark
        elif mac_comp[0] == "add_bookmark":
            tools_bookmarks_add()
        # view_bookmarks
        elif mac_comp[0] == "view_bookmarks":
            tools_bookmarks_view()
        # clear_bookmarks
        elif mac_comp[0] == "clear_bookmarks":
            tools_bookmarks_clear()
        # save_bookmarks
        elif mac_comp[0] == "save_bookmarks":
            tools_bookmarks_save()
        # open_bookmarks
        elif mac_comp[0] == "open_bookmarks":
            tools_bookmarks_open()
        # insert_time
        elif mac_comp[0] == "insert_time":
            tools_insert_time()
        # insert_time_words
        elif mac_comp[0] == "insert_time_words":
            tools_insert_time_words()
        # insert_date
        elif mac_comp[0] == "insert_date":
            tools_insert_date()
        # insert_color
        elif mac_comp[0] == "insert_color":
            tools_insert_color()
        # insert_line
        elif mac_comp[0] == "insert_line":
            tools_insert("line")
        # insert_pos
        elif mac_comp[0] == "insert_pos":
            tools_insert("position")
        # insert_path
        elif mac_comp[0] == "insert_path":
            tools_insert("fullpath")
        # insert_filename
        elif mac_comp[0] == "insert_filename":
            tools_insert("filename")
        # insert_dir
        elif mac_comp[0] == "insert_dir":
            tools_insert("directory")
        # indent
        elif mac_comp[0] == "indent":
            tools_indent()
        # unindent
        elif mac_comp[0] == "unindent":
            tools_unindent()
        # encode_url
        elif mac_comp[0] == "encode_url":
            tools_encode_url()
        # decode_url
        elif mac_comp[0] == "decode_url":
            tools_decode_url()
        # strip_leading
        elif mac_comp[0] == "strip_leading":
            tools_strip_leading()
        # strip_trailing
        elif mac_comp[0] == "strip_trailing":
            tools_strip_trailing()
        # replace_ts
        elif mac_comp[0] == "replace_ts":
            tools_spaces_tabs("t2s")
        # replace_st
        elif mac_comp[0] == "replace_st":
            tools_spaces_tabs("s2t")
        # notes
        elif mac_comp[0] == "notes":
            tools_notes()
        # tasks
        elif mac_comp[0] == "tasks":
            tools_tasks()
        # collab
        elif mac_comp[0] == "collab":
            tools_collab()
        # upload_pastbin
        elif mac_comp[0] == "upload_pastebin":
            tools_upload_pastebin()
        # download_pastebin
        elif mac_comp[0] == "download_pastebin":
            tools_download_pastebin()
        # upload_pastehtml
        elif mac_comp[0] == "upload_pastehtml":
            tools_upload_pastehtml()
        # send_email
        elif mac_comp[0] == "send_email":
            tools_send_email()
        # send_ftp
        elif mac_comp[0] == "send_ftp":
            tools_send_ftp()
        # statistics
        elif mac_comp[0] == "statistics":
            tools_statistics()
        # open_web
        elif mac_comp[0] == "open_web":
            code_open_browser()
        # run_python args
        elif mac_comp[0] == "run_python":
            code_run_code(CONFIG["python"], args = " ".join(mac_comp[1:]))
        # run_perl args
        elif mac_comp[0] == "run_perl":
            code_run_code(CONFIG["perl"], args = " ".join(mac_comp[1:]))
        # run_php args
        elif mac_comp[0] == "run_php":
            code_run_code(CONFIG["php"], args = " ".join(mac_comp[1:]))
        # compile_c args
        elif mac_comp[0] == "compile_c":
            code_run_code(CONFIG["c"], args = " ".join(mac_comp[1:]))
        # compile_cpp args
        elif mac_comp[0] == "compile_cpp":
            code_run_code(CONFIG["cpp"], args = " ".join(mac_comp[1:]))
        # compile_java args
        elif mac_comp[0] == "compile_java":
            code_run_code(CONFIG["java"], args = " ".join(mac_comp[1:]))
        # run_other args
        elif mac_comp[0] == "run_other":
            code_run_code(None, args = " ".join(mac_comp[1:]))
        # execute args
        elif mac_comp[0] == "execute":
            code_execute(args = " ".join(mac_comp[1:]))
        # escape
        elif mac_comp[0] == "escape":
            code_escape_sel()
        # remove_tags
        elif mac_comp[0] == "remove_tags":
            code_remove_tags()
        # options
        elif mac_comp[0] == "options":
            opt_options()
        # revert_default
        elif mac_comp[0] == "revert_options":
            opt_revert()
        # enlarge_font
        elif mac_comp[0] == "enlarge_font":
            opt_font_size(True)
        # shrink_font
        elif mac_comp[0] == "shrink_font":
            opt_font_size(False)
        # edit_favorites
        elif mac_comp[0] == "edit_favorites":
            opt_edit_favorites()
        # edit_filetypes
        elif mac_comp[0] == "edit_filetypes":
            opt_edit_filetypes()
        # clear_find
        elif mac_comp[0] == "clear_find":
            opt_clear_find_history()
        # clear_replace
        elif mac_comp[0] == "clear_replace":
            opt_clear_replace_history()
        # about
        elif mac_comp[0] == "about":
            help_about()
        # help
        elif mac_comp[0] == "help":
            help_help()
        # Throw error on unknown command, if the user wants that.
        else:
            if CONFIG["macro_unknown_error"] == "yes":
                showerror("Run Macro", "Error executing macro \"%s\":\n%d: %s" % (macro, line + 1, text))
                return False
        # Execution was successful.
        return True
    # If there was any error:
    except:
        showerror("Run Macro", "Error executing macro \"%s\":\n%d: %s" % (macro, line + 1, text))
        return False


def tools_macro_bindings():
    """Changes keybindings for macros."""
    # Define internal function.
    def tools_macro_bindings_apply():
        """Applies the new bindings."""
        # Get the entries.
        b1 = b1_ent.get()
        b2 = b2_ent.get()
        b3 = b3_ent.get()
        b4 = b4_ent.get()
        b5 = b5_ent.get()
        b6 = b6_ent.get()
        b7 = b7_ent.get()
        b8 = b8_ent.get()
        b9 = b9_ent.get()
        b0 = b0_ent.get()
        # Apply each one.
        if b1:
            text_box.text_box.bind("<Control-Key-1>", lambda event: tools_macro_run_file(b1))
            gbl_mac_bindings[0] = b1
        if b2:
            text_box.text_box.bind("<Control-Key-2>", lambda event: tools_macro_run_file(b2))
            gbl_mac_bindings[1] = b2
        if b3:
            text_box.text_box.bind("<Control-Key-3>", lambda event: tools_macro_run_file(b3))
            gbl_mac_bindings[2] = b3
        if b4:
            text_box.text_box.bind("<Control-Key-4>", lambda event: tools_macro_run_file(b4))
            gbl_mac_bindings[3] = b4
        if b5:
            text_box.text_box.bind("<Control-Key-5>", lambda event: tools_macro_run_file(b5))
            gbl_mac_bindings[4] = b5
        if b6:
            text_box.text_box.bind("<Control-Key-6>", lambda event: tools_macro_run_file(b6))
            gbl_mac_bindings[5] = b6
        if b7:
            text_box.text_box.bind("<Control-Key-7>", lambda event: tools_macro_run_file(b7))
            gbl_mac_bindings[6] = b7
        if b8:
            text_box.text_box.bind("<Control-Key-8>", lambda event: tools_macro_run_file(b8))
            gbl_mac_bindings[7] = b8
        if b9:
            text_box.text_box.bind("<Control-Key-9>", lambda event: tools_macro_run_file(b9))
            gbl_mac_bindings[8] = b9
        if b0:
            text_box.text_box.bind("<Control-Key-0>", lambda event: tools_macro_run_file(b0))
            gbl_mac_bindings[9] = b0
        # Tell the user bindings have been saved.
        showinfo("Change Macro Bindings", "Macro bindings have been applied.")
        # Close the window.
        b_win.destroy()
        # Return focus to the text box.
        return internal_return_focus()
    # Create the GUI.
    b_win = Toplevel()
    b_win.title("Change Macro Bindings")
    b_win.transient(root)
    b_win.grab_set()
    b_win.wm_resizable(0, 0)
    # Create the frame for the widgets.
    b_frm = Frame(b_win, padx = 5, pady = 5)
    b_frm.pack(side = TOP)
    # Create the labels.
    b1_lbl = Label(b_frm, text = "Ctrl+1: ")
    b1_lbl.grid(row = 0, column = 0)
    b2_lbl = Label(b_frm, text = "Ctrl+2: ")
    b2_lbl.grid(row = 1, column = 0)
    b3_lbl = Label(b_frm, text = "Ctrl+3: ")
    b3_lbl.grid(row = 2, column = 0)
    b4_lbl = Label(b_frm, text = "Ctrl+4: ")
    b4_lbl.grid(row = 3, column = 0)
    b5_lbl = Label(b_frm, text = "Ctrl+5: ")
    b5_lbl.grid(row = 4, column = 0)
    b6_lbl = Label(b_frm, text = "Ctrl+6: ")
    b6_lbl.grid(row = 5, column = 0)
    b7_lbl = Label(b_frm, text = "Ctrl+7: ")
    b7_lbl.grid(row = 6, column = 0)
    b8_lbl = Label(b_frm, text = "Ctrl+8: ")
    b8_lbl.grid(row = 7, column = 0)
    b9_lbl = Label(b_frm, text = "Ctrl+9: ")
    b9_lbl.grid(row = 8, column = 0)
    b0_lbl = Label(b_frm, text = "Ctrl+0: ")
    b0_lbl.grid(row = 9, column = 0)
    # Create the entries.
    b1_ent = Entry(b_frm)
    b1_ent.grid(row = 0, column = 1)
    b2_ent = Entry(b_frm)
    b2_ent.grid(row = 1, column = 1)
    b3_ent = Entry(b_frm)
    b3_ent.grid(row = 2, column = 1)
    b4_ent = Entry(b_frm)
    b4_ent.grid(row = 3, column = 1)
    b5_ent = Entry(b_frm)
    b5_ent.grid(row = 4, column = 1)
    b6_ent = Entry(b_frm)
    b6_ent.grid(row = 5, column = 1)
    b7_ent = Entry(b_frm)
    b7_ent.grid(row = 6, column = 1)
    b8_ent = Entry(b_frm)
    b8_ent.grid(row = 7, column = 1)
    b9_ent = Entry(b_frm)
    b9_ent.grid(row = 8, column = 1)
    b0_ent = Entry(b_frm)
    b0_ent.grid(row = 9, column = 1)
    # Create the frame for the buttons.
    b2_frm = Frame(b_win)
    b2_frm.pack(side = TOP)
    # Create the OK button.
    b_ok_btn = Button(b2_frm, text = "OK", width = 10, default = ACTIVE, command = tools_macro_bindings_apply)
    b_ok_btn.pack(side = LEFT, padx = 5, pady = 5)
    # Create the Cancel button.
    b_cancel_btn = Button(b2_frm, text = "Cancel", width = 10, command = b_win.destroy)
    b_cancel_btn.pack(side = LEFT, padx = 5, pady = 5)
    # Prefill the entries.
    if gbl_mac_bindings[0]:
        b1_ent.insert("0", gbl_mac_bindings[0])
    if gbl_mac_bindings[1]:
        b2_ent.insert("0", gbl_mac_bindings[1])
    if gbl_mac_bindings[2]:
        b3_ent.insert("0", gbl_mac_bindings[2])
    if gbl_mac_bindings[3]:
        b4_ent.insert("0", gbl_mac_bindings[3])
    if gbl_mac_bindings[4]:
        b5_ent.insert("0", gbl_mac_bindings[4])
    if gbl_mac_bindings[5]:
        b6_ent.insert("0", gbl_mac_bindings[5])
    if gbl_mac_bindings[6]:
        b7_ent.insert("0", gbl_mac_bindings[6])
    if gbl_mac_bindings[7]:
        b8_ent.insert("0", gbl_mac_bindings[7])
    if gbl_mac_bindings[8]:
        b9_ent.insert("0", gbl_mac_bindings[8])
    if gbl_mac_bindings[9]:
        b0_ent.insert("0", gbl_mac_bindings[9])
    # Bind events.
    b_win.bind("<Escape>", lambda event: b_win.destroy())
    # Give focus.
    b1_ent.focus()


def tools_run_command():
    """Runs a single macro command."""
    global gbl_dlg_run_cmd
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    # Get the command to run.
    command = askstring("Run Command", "Command: ", initialvalue = gbl_dlg_run_cmd)
    if not command:
        return internal_return_focus()
    gbl_dlg_run_cmd = command
    # Run Python statement, if the user wants that.
    if CONFIG["macro_run_command"] == "python statements":
        command = CONFIG["macro_python_start"] + command
    # Pass the command to the parser
    tools_macro_parse(0, command, "command")
    # Clear the variable list, in case one was created.
    gbl_mac_vars.clear()
    # Return focus to the text box.
    return internal_return_focus()


def tools_insert_date(dformat = None, mode = None):
    """Inserts the current date."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # Delete the currently selected text, if any.
    if text_box.text_box.tag_ranges("sel"):
        text_box.text_box.delete("sel.first", "sel.last")
    # Determine the date format.
    dformat = dformat or CONFIG["date"]
    if mode == "other":
        dformat = askstring("Insert Date", "Enter date format:")
        if not dformat:
            return internal_return_focus()
    # Get the date, and format it.
    date = time.strftime(dformat)
    # Insert the date.
    text_box.text_box.insert("insert", date)
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def tools_insert_color():
    """Inserts a color."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # Delete the currently selected text, if any.
    if text_box.text_box.tag_ranges("sel"):
        text_box.text_box.delete("sel.first", "sel.last")
    # Ask the user for the color.
    color = askcolor()[1]
    if not color:
        return internal_return_focus()
    # Insert the color.
    text_box.text_box.insert("insert", color)
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def tools_insert_time(tformat = None, mode = None):
    """Inserts the current time."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # Delete the currently selected text, if any.
    if text_box.text_box.tag_ranges("sel"):
        text_box.text_box.delete("sel.first", "sel.last")
    # Determine the format.
    tformat = tformat or CONFIG["time"]
    if mode == "other":
        tformat = askstring("Insert Time", "Enter time format:")
        if not tformat:
            return internal_return_focus()
    # Get the time, and format it.
    time2 = time.strftime(tformat)
    # Insert the time.
    text_box.text_box.insert("insert", time2)
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def tools_insert_time_words():
    """Inserts the current time, but in word form."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # Delete the currently selected text, if any.
    if text_box.text_box.tag_ranges("sel"):
        text_box.text_box.delete("sel.first", "sel.last")
    # Get the current time.
    now = datetime.datetime.now()
    hour = now.hour
    hour2 = hour
    minute = now.minute
    # Figure out if it's noon, midnight, or sometime in the morning, afternoon, or night.
    if hour == 12:
        time = "noon"
    elif hour == 0 or hour == 24:
        time = "midnight"
    elif hour >= 3 and hour < 12:
        time = "in the morning"
    elif hour > 12 and hour <= 21:
        time = "in the afternoon"
    elif hour > 21 or hour < 3:
        time = "at night"
    # If it is noon or midnight, just insert that.
    if time == "noon" or time == "midnight":
        text_box.text_box.insert("insert", time)
        return internal_return_focus()
    # Otherwise, convert the time to 12-hour format.
    if hour > 12:
        hour -= 12
    # If it is 30 minutes or less, give the time as the minutes past the hour.
    if minute <= 30:
        sep = "after"
    # Otherwise, give the time as the minutes until the next hour.
    else:
        sep = "until"
        minute = 60 - minute
        hour += 1
        hour2 += 1
        # Convert the time to 12-hour format again, if needed.
        if hour > 12:
            hour -= 12
        # If it is exactly on the hour, then just insert the hour and time of day.
        if minute == 0:
            text_box.text_box.insert("insert", "%d %s" % (hour, time))
            return internal_return_focus()
    # If the next/previous hour was midnight:
    if hour2 == 0 or hour2 == 24:
        text_box.text_box.insert("insert", "%d %s midnight" % (minute, sep))
    # If the next/previous hour was noon:
    elif hour2 == 12:
        text_box.text_box.insert("insert", "%d %s noon" % (minute, sep))
    # Otherwise:
    else:
        text_box.text_box.insert("insert", "%d %s %d %s" % (minute, sep, hour, time))
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def tools_insert(insert):
    """Inserts something."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # Delete the currently selected text, if any.
    if text_box.text_box.tag_ranges("sel"):
        text_box.text_box.delete("sel.first", "sel.last")
    # Insert the string.
    if insert == "line":
        text_box.text_box.insert("insert", text_box.text_box.index("insert").split(".")[0])
    elif insert == "position":
        text_box.text_box.insert("insert", text_box.text_box.index("insert").split(".")[1])
    elif insert == "fullpath" and gbl_file_name:
        text_box.text_box.insert("insert", gbl_file_name)
    elif insert == "filename" and gbl_file_name:
        text_box.text_box.insert("insert", gbl_file_name_short)
    elif insert == "directory" and gbl_file_name:
        text_box.text_box.insert("insert", os.path.split(gbl_file_name)[0])
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def tools_indent():
    """Indents the current line."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # If text is selected:
    if text_box.text_box.tag_ranges("sel"):
        # Get the selected text.
        text = text_box.text_box.get("sel.first", "sel.last")
        # Insert the indents.
        text = text.replace("\n", "\n" + (" " * CONFIG["indent"]))
        # If the selection starts on the first position, add an indent at the start.
        if text_box.text_box.index("sel.first").split(".")[1] == "0":
            text = (" " * CONFIG["indent"]) + text
        # Delete the selected text.
        text_box.text_box.delete("sel.first", "sel.last")
        # Insert the new text.
        text_box.text_box.insert("insert", text)
    # If no text is selected:
    else:
        # Get the line.
        line = text_box.text_box.index("insert").split(".")[0]
        # Insert the indent.
        text_box.text_box.insert(line + ".0", (" " * CONFIG["indent"]))
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def tools_unindent():
    """Unindents the current line."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # If text is selected:
    if text_box.text_box.tag_ranges("sel"):
        # Get the selected text.
        text = text_box.text_box.get("sel.first", "sel.last")
        # Split the text into each line.
        lines = text.split("\n")
        # Loop for each line:
        new_lines = []
        for i in lines:
            # Get the number of spaces.
            spaces = len(i) - len(i.lstrip())
            # Compute the negative indent amount.
            if spaces <= CONFIG["indent"]:
                i = i.lstrip()
            else:
                i = (" " * (spaces - CONFIG["indent"])) + i.lstrip()
            # Add line to list.
            new_lines.append(i)
        # Join the lines.
        new_text = "\n".join(new_lines)
        # Delete the selected text.
        text_box.text_box.delete("sel.first", "sel.last")
        # Insert the new text.
        text_box.text_box.insert("insert", new_text)
    # If no text is selected:
    else:
        # Get the line.
        line = text_box.text_box.index("insert").split(".")[0]
        # Get the line text.
        text = text_box.text_box.get(line + ".0", line + ".end")
        # Get the number of spaces.
        spaces = len(text) - len(text.lstrip())
        # Compute the negative indent amount.
        if spaces <= CONFIG["indent"]:
            text = text.lstrip()
        else:
            text = (" " * (spaces - CONFIG["indent"])) + text.lstrip()
        # Delete the old line and insert the new one.
        text_box.text_box.delete(line + ".0", line + ".end")
        text_box.text_box.insert(line + ".0", text)
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def tools_encode_url():
    """Encodes a URL."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    # If no text is selected, this cannot be done.
    if not text_box.text_box.tag_ranges("sel"):
        showerror("Encode URL", "No text selected.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # Get the selected text.
    text = text_box.text_box.get("sel.first", "sel.last")
    # Encode the text.
    text = quote(text.encode("utf8"))
    # Delete the old text and insert the new.
    text_box.text_box.delete("sel.first", "sel.last")
    text_box.text_box.insert("insert", text)
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def tools_decode_url():
    """Decodes a URL."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    # If no text is selected, this cannot be done.
    if not text_box.text_box.tag_ranges("sel"):
        showerror("Decode URL", "No text selected.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # Get the selected text.
    text = text_box.text_box.get("sel.first", "sel.last")
    # Decode the text.
    text = unquote(text.encode("utf8"))
    # Delete the old text and insert the new.
    text_box.text_box.delete("sel.first", "sel.last")
    text_box.text_box.insert("insert", text)
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def tools_strip_leading():
    """Strips leading space."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # If text is selected:
    if text_box.text_box.tag_ranges("sel"):
        # Get the text.
        text = text_box.text_box.get("sel.first", "sel.last")
        # Strip the space.
        text = text.lstrip()
        # Delete the old text and insert the new.
        text_box.text_box.delete("sel.first", "sel.last")
        text_box.text_box.insert("insert", text)
    # If no text is selected:
    else:
        # Get the current line.
        line = text_box.text_box.index("insert").split(".")[0]
        # Get the text.
        text = text_box.text_box.get("%s.0" % line, "%s.end" % line)
        # Strip the space.
        text = text.lstrip()
        # Delete the old text and insert the new.
        text_box.text_box.delete("%s.0" % line, "%s.end" % line)
        text_box.text_box.insert("insert", text)
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def tools_strip_trailing():
    """Strips trailing space."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # If text is selected:
    if text_box.text_box.tag_ranges("sel"):
        # Get the text.
        text = text_box.text_box.get("sel.first", "sel.last")
        # Strip the space.
        text = text.rstrip()
        # Delete the old text and insert the new.
        text_box.text_box.delete("sel.first", "sel.last")
        text_box.text_box.insert("insert", text)
    # If no text is selected:
    else:
        # Get the current line.
        line = text_box.text_box.index("insert").split(".")[0]
        # Get the text.
        text = text_box.text_box.get("%s.0" % line, "%s.end" % line)
        # Strip the space.
        text = text.rstrip()
        # Delete the old text and insert the new.
        text_box.text_box.delete("%s.0" % line, "%s.end" % line)
        text_box.text_box.insert("insert", text)
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def tools_spaces_tabs(mode):
    """Replaces spaces with tabs, or vice versa."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # Get the text.
    text = text_box.text_box.get(1.0, "end-1c")
    # Get the cursor position.
    cur_pos = text_box.text_box.index("insert")
    done = False
    # Replace tabs with spaces:
    if mode == "t2s" and text.index("\t") != -1:
        text = text.replace("\t", (" " * CONFIG["spaces_tab"]))
        done = True
    # Replace spaces with tabs:
    elif mode == "s2t" and text.index(" " * CONFIG["spaces_tab"]) != -1:
        text = text.replace((" " * CONFIG["spaces_tab"]), "\t")
        done = True
    # Insert the new text.
    if done:
        # Delete old text, insert new.
        text_box.text_box.delete(1.0, "end-1c")
        text_box.text_box.insert(1.0, text)
        # Reset cursor position.
        text_box.text_box.mark_set("insert", cur_pos)
        # Mark the text as having changes.
        internal_text_modified(True)
        # Update the title.
        update_title()
        text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def tools_tasks():
    """Shows a list of tasks (lines with TODO or FIXME)."""
    # Define internal function.
    def tools_tasks_click():
        """Manages double-clicks on listbox."""
        # Get line number of bookmark.
        item = task_list.get("active")
        if not item:
            return
        line_num = re.findall(r'\d+', item)[0]
        # Close the window.
        task_win.destroy()
        # Go to the line.
        text_box.text_box.mark_set("insert", "%s.0" % line_num)
        text_box.text_box.see("insert")
        # Return focus to the text box.
        return internal_return_focus()
    # Get all the lines.
    lines = text_box.text_box.get("1.0", "end-1c").split("\n")
    # Find which lines have TODO or FIXME.
    tasks = []
    for i in range(0, len(lines)):
        if lines[i].find("TODO") != -1 or lines[i].find("FIXME") != -1:
            tasks.append([i + 1, lines[i]])
    # If there are no tasks, don't show the dialog.
    if len(tasks) == 0:
        showinfo("Tasks", "There are no tasks.")
        return internal_return_focus()
    # Create the GUI.
    task_win = Toplevel()
    task_win.title("Tasks")
    task_win.transient(root)
    task_win.grab_set()
    # Create the frame for the listbox and scrollbar.
    task_frm = Frame(task_win)
    task_frm.pack(expand = YES, fill = BOTH, side = TOP)
    # Create the listbox and scrollbar.
    task_list = Listbox(task_frm, bg = CONFIG["bg"], fg = CONFIG["fg"], relief = SUNKEN, width = 60)
    task_scroll = Scrollbar(task_frm)
    task_scroll.config(command = task_list.yview)
    task_list.config(yscrollcommand = task_scroll.set)
    task_scroll.pack(side = RIGHT, fill = Y)
    task_list.pack(side = LEFT, expand = YES, fill = BOTH)
    # Populate the listbox.
    for j in tasks:
        line = j[1]
        # Limit line length to 50 chars.
        if len(line) > 50:
            line = line[:50]
        task_list.insert("end", "%d - %s" % (j[0], line))
    # Give focus to the listbox.
    task_list.focus()
    # Bind the events.
    task_list.bind("<Double-1>", lambda event: tools_tasks_click())
    task_list.bind("<Return>", lambda event: tools_tasks_click())
    task_list.bind("<Escape>", lambda event: task_win.destroy())


def tools_notes():
    """Edits and shows notes."""
    # Define the internal functions.
    def tools_notes_close():
        """Remembers the text in the textbox."""
        global gbl_notes
        # Get the text.
        notes = n_text.get("1.0", "end-1c")
        # Remember the text.
        gbl_notes = notes
        # Destroy the window.
        n_win.destroy()
    # Create the GUI.
    n_win = Toplevel()
    n_win.title("Notes")
    # Create the frame for the textbox and scrollbar.
    n_frm = Frame(n_win)
    n_frm.pack(expand = YES, fill = BOTH, side = TOP)
    # Create the listbox and scrollbar.
    n_text = Text(n_frm, bg = CONFIG["bg"], fg = CONFIG["fg"], relief = SUNKEN, width = 60, wrap = WORD)
    n_scroll = Scrollbar(n_frm)
    n_scroll.config(command = n_text.yview)
    n_text.config(yscrollcommand = n_scroll.set)
    n_scroll.pack(side = RIGHT, fill = Y)
    n_text.pack(side = LEFT, expand = YES, fill = BOTH)
    # Show the text.
    n_text.insert("1.0", gbl_notes)
    # Give focus to the textbox.
    n_text.mark_set("insert", "1.0")
    n_text.focus()
    # Register event for when the window is closed.
    n_win.protocol("WM_DELETE_WINDOW", tools_notes_close)
    # Bind the events.
    n_text.bind("<Escape>", lambda event: tools_notes_close())


def tools_collab():
    """Shows the collaborative editing dialog."""
    # Define the internal funtions.
    def tools_collab_connect():
        """Connects to the server."""
        def tools_collab_push():
            """Sends data to the server."""
            try:
                # Connect to the server.
                sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock_server.connect((server, port))
            except:
                showerror("Collaborative Editing", "Data could not be sent to server \"%s\" on port %d." % (server, port))
                return
            # Get the text.
            text = text_box.text_box.get("1.0", "end-1c")
            # Send the text.
            sock_server.send("w" + text)
            # Disconnect from the server.
            sock_server.close()
            # Tell the user the text has been sent.
            showinfo("Collaborative Editing", "Data has been sent to the server.")
        def tools_collab_pull():
            """Gets data from the server."""
            try:
                # Connect to the server.
                sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock_server.connect((server, port))
            except:
                showerror("Collaborative Editing", "Data could not be read from server \"%s\" on port %d." % (server, port))
                return
            # Request the data.
            sock_server.send("r")
            # Get the data.
            data = ""
            while True:
                data2 = sock_server.recv(1024)
                if not data2:
                    break
                else:
                    data += str(data2)
            # Remember the cursor position.
            cursor = text_box.text_box.index("insert")
            # Delete the current text.
            text_box.text_box.delete("1.0", "end")
            # Insert the new text.
            text_box.text_box.insert("1.0", data[1:])
            # Restore the cursor position.
            text_box.text_box.mark_set("insert", cursor)
            # Disconnect from the server.
            sock_server.close()
            # Mark the text as having changes.
            internal_text_modified(True)
            # Update the title.
            update_title()
            # Update the documents list.
            update_documents_list()
        # Get the server and port.
        server = ce_serv_ent.get()
        port = ce_port_ent.get()
        # The server name is necessary.
        if not server:
            showerror("Collaborative Editing", "The server name is required.")
            return
        # The port is necessary, and must be an integer.
        if not port:
            showerror("Collaborative Editing", "The port is required.")
            return
        else:
            try:
                port = int(port)
            except:
                showerror("Collaborative Editing", "The port must be an integer.")
                return
        try:
            # Connect to the server.
            sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock_server.connect((server, port))
            # Test the connection.
            sock_server.send("t")
            response = sock_server.recv(10)
            if response == "b":
                showerror("Collaborative Editing", "Connection refused: blacklisted on \"%s\" on port %d, but test failed." % (server, port))
                return
            elif response == "w":
                showerror("Collaborative Editing", "Connection refused: not whitelisted on \"%s\" on port %d, but test failed." % (server, port))
                return
            elif response != "success":
                showerror("Collaborative Editing", "Connected to server \"%s\" on port %d, but test failed." % (server, port))
                return
        except:
            showerror("Collaborative Editing", "Could not connect to server \"%s\" on port %d." % (server, port))
            return
        # Close the previous window.
        ce_win.destroy()
        # Create the GUI.
        ce2_win = Toplevel()
        ce2_win.title("Collaborative Editing")
        ce2_win.wm_resizable(0, 0)
        # Create the connection label.
        ce2_lbl = Label(ce2_win, text = "Connected to server \"%s\" on port %d." % (server, port))
        ce2_lbl.pack(side = TOP, padx = 5, pady = 5)
        # Create the frame for the buttons.
        ce2_frm = Frame(ce2_win)
        ce2_frm.pack(side = TOP)
        # Create the Push button.
        ce_push_btn = Button(ce2_frm, text = "Push", width = 10, command = tools_collab_push)
        ce_push_btn.pack(side = LEFT, padx = 5, pady = 5)
        # Create the Pull button.
        ce_pull_btn = Button(ce2_frm, text = "Pull", width = 10, command = tools_collab_pull)
        ce_pull_btn.pack(side = LEFT, padx = 5, pady = 5)
        # Create the Close button.
        ce_close_btn = Button(ce2_frm, text = "Close", width = 10, command = ce2_win.destroy)
        ce_close_btn.pack(side = LEFT, padx = 5, pady = 5)
    # Create the GUI.
    ce_win = Toplevel()
    ce_win.title("Collaborative Editing")
    ce_win.transient(root)
    ce_win.grab_set()
    ce_win.wm_resizable(0, 0)
    # Create the frame for everything but the buttons.
    ce_inf_frame = Frame(ce_win)
    ce_inf_frame.pack(side = TOP, expand = YES, fill = X)
    # Create the frame for the widgets.
    ce_frm = Frame(ce_inf_frame, padx = 5, pady = 5)
    ce_frm.pack(side = TOP, expand = YES, fill = X)
    # Create the name label, entry, and button.
    ce_serv_lbl = Label(ce_frm, text = "Server: ")
    ce_serv_lbl.grid(row = 0, column = 0, sticky = W)
    ce_serv_ent = Entry(ce_frm)
    ce_serv_ent.grid(row = 0, column = 1, sticky = W)
    ce_serv_btn = Button(ce_frm, text = "?", command = lambda: showinfo("Help", "Specifies the URL of the server."))
    ce_serv_btn.grid(row = 0, column = 2, sticky = W)
    # Create the type label, entry, and button.
    ce_port_lbl = Label(ce_frm, text = "Port: ")
    ce_port_lbl.grid(row = 1, column = 0, sticky = W)
    ce_port_ent = Entry(ce_frm)
    ce_port_ent.grid(row = 1, column = 1, sticky = W)
    ce_port_btn = Button(ce_frm, text = "?", command = lambda: showinfo("Help", "Specifies the port."))
    ce_port_btn.grid(row = 1, column = 2, sticky = W)
    # Create the frame for the buttons.
    ce_frm2 = Frame(ce_win)
    ce_frm2.pack(side = TOP)
    # Create the Connect button.
    ce_ok_btn = Button(ce_frm2, text = "Connect", width = 10, default = ACTIVE, command = tools_collab_connect)
    ce_ok_btn.pack(side = LEFT, padx = 5, pady = 5)
    # Create the Cancel button.
    ce_cancel_btn = Button(ce_frm2, text = "Cancel", width = 10, command = ce_win.destroy)
    ce_cancel_btn.pack(side = LEFT, padx = 5, pady = 5)
    # Prefill entries.
    ce_serv_ent.insert(0, CONFIG["collab_server"])
    ce_port_ent.insert(0, CONFIG["collab_port"])
    # Bind the events.
    ce_win.bind("<Return>", lambda event: tools_collab_connect())
    ce_win.bind("<Escape>", lambda event: ce_win.destroy())


def tools_upload_pastebin():
    """Uploads the text to pastebin."""
    # Define the internal function.
    def tools_upload_pastebin_internal():
        """Uploads the text."""
        # Define internal function.
        def tools_upload_pastebin_copy():
            """Copies the text."""
            # Get the selected text.
            text = pb2_ent.get()
            # Add the text to the clipboard.
            text_box.text_box.clipboard_clear()
            text_box.text_box.clipboard_append(text)
        # Get the entries.
        name = pb_name_ent.get()
        ttype = pb_type_ent.get()
        expire = pb_type_ent.get()
        # Get the text.
        text = text_box.text_box.get("1.0", "end-1c")
        # Build the data string.
        data = {"api_option": "paste",
                "api_dev_key": CONFIG["pastebin_dev_key"],
                "api_paste_code": text}
        # Add other options if desired.
        if name:
            data["api_paste_name"] = name
        if ttype:
            data["api_paste_format"] = ttype
        if expire:
            data["api_expire_date"] = expire
        # Encode the data string.
        data = urlencode(data)
        # Upload the text.
        try:
            # Send the data.
            pastebin = urlopen("http://pastebin.com/api/api_post.php", data)
            # Read the result.
            result = pastebin.read()
            # Close the connection.
            pastebin.close()
        except:
            showerror("Upload to Pastebin", "Could not upload text.")
            pb_win.destroy()
            return internal_return_focus()
        # Save the values.
        global gbl_dlg_pb_name
        global gbl_dlg_pb_type
        global gbl_dlg_pb_exp
        gbl_dlg_pb_name = name
        gbl_dlg_pb_type = ttype
        gbl_dlg_pb_exp = expire
        # Close the window.
        pb_win.destroy()
        # Show the user the result.
        # Create the GUI.
        pb2_win = Toplevel()
        pb2_win.title("Upload to Pastebin")
        pb2_win.transient(root)
        pb2_win.grab_set()
        # Create the frame for the label and entry.
        pb21_frm = Frame(pb2_win)
        pb21_frm.pack(side = TOP)
        # Create the label and entry.
        pb2_lbl = Label(pb21_frm, text = "Result: ")
        pb2_lbl.grid(row = 0, column = 0, sticky = W)
        pb2_ent = Entry(pb21_frm)
        pb2_ent.grid(row = 0, column = 1)
        # Create the frame for the buttons.
        pb22_frm = Frame(pb2_win)
        pb22_frm.pack(side = TOP)
        # Create the Open button.
        pb_open_btn = Button(pb22_frm, text = "Open", width = 10, command = lambda: webbrowser.open(result))
        pb_open_btn.pack(side = LEFT, padx = 5, pady = 5)
        # Create the Close button.
        pb_close_btn = Button(pb22_frm, text = "Close", width = 10, default = ACTIVE, command = pb2_win.destroy)
        pb_close_btn.pack(side = LEFT, padx = 5, pady = 5)
        # Insert the result.
        pb2_ent.insert(0, result)
        # Focus on the entry.
        pb2_ent.focus()
        # Bind the events.
        pb2_ent.bind("<Control-Key-c>", lambda event: tools_upload_pastebin_copy())
        pb2_win.bind("<Return>", lambda event: pb2_win.destroy())
        pb2_win.bind("<Escape>", lambda event: pb2_win.destroy())
    # Create the GUI.
    pb_win = Toplevel()
    pb_win.title("Upload to Pastebin")
    pb_win.transient(root)
    pb_win.grab_set()
    pb_win.wm_resizable(0, 0)
    # Create the frame for everything but the buttons.
    pb_inf_frame = Frame(pb_win)
    pb_inf_frame.pack(side = TOP, expand = YES, fill = X)
    # Create the frame for the widgets.
    pb_frm = Frame(pb_inf_frame, padx = 5, pady = 5)
    pb_frm.pack(side = TOP, expand = YES, fill = X)
    # Create the name label, entry, and button.
    pb_name_lbl = Label(pb_frm, text = "Name: ")
    pb_name_lbl.grid(row = 0, column = 0, sticky = W)
    pb_name_ent = Entry(pb_frm)
    pb_name_ent.grid(row = 0, column = 1, sticky = W)
    pb_name_btn = Button(pb_frm, text = "?", command = lambda: showinfo("Help", "Specifies the name of the paste.\n\nThis entry is optional."))
    pb_name_btn.grid(row = 0, column = 2, sticky = W)
    # Create the type label, entry, and button.
    pb_type_lbl = Label(pb_frm, text = "Type: ")
    pb_type_lbl.grid(row = 1, column = 0, sticky = W)
    pb_type_ent = Entry(pb_frm)
    pb_type_ent.grid(row = 1, column = 1, sticky = W)
    pb_name_btn = Button(pb_frm, text = "?", command = lambda: showinfo("Help", "Specifies the language of the paste, used for syntax highlighting.\n\nThis entry is optional."))
    pb_name_btn.grid(row = 1, column = 2, sticky = W)
    # Create the expiration label, entry, and button.
    pb_exp_lbl = Label(pb_frm, text = "Expiration: ")
    pb_exp_lbl.grid(row = 2, column = 0, sticky = W)
    pb_exp_ent = Entry(pb_frm)
    pb_exp_ent.grid(row = 2, column = 1, sticky = W)
    pb_exp_btn = Button(pb_frm, text = "?", command = lambda: showinfo("Help", "Specifies how long the paste will exist before it is deleted.\n\nValid values are \"N\" for never, \"10M\" for ten minutes, \"1H\" for one hour, \"1D\" for one day, and \"1M\" for one month."))
    pb_exp_btn.grid(row = 2, column = 2, sticky = W)
    # Create the frame for the buttons.
    pb3_frm = Frame(pb_win)
    pb3_frm.pack(side = TOP)
    # Create the Upload button.
    pb_ok_btn = Button(pb3_frm, text = "Upload", width = 10, default = ACTIVE, command = tools_upload_pastebin_internal)
    pb_ok_btn.pack(side = LEFT, padx = 5, pady = 5)
    # Create the Cancel button.
    pb_cancel_btn = Button(pb3_frm, text = "Cancel", width = 10, command = pb_win.destroy)
    pb_cancel_btn.pack(side = LEFT, padx = 5, pady = 5)
    # Auto focus on the first entry.
    pb_name_ent.focus()
    # Pre-fill the entries.
    pb_name_ent.insert(0, gbl_dlg_pb_name)
    pb_type_ent.insert(0, gbl_dlg_pb_type)
    pb_exp_ent.insert(0, gbl_dlg_pb_exp)
    # Bind the events.
    pb_win.bind("<Return>", lambda event: tools_upload_pastebin_internal())
    pb_win.bind("<Escape>", lambda event: pb_win.destroy())


def tools_download_pastebin():
    """Downloads and inserts text from Pastebin."""
    global gbl_dlg_paste
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    # Prompt the user for the paste id.
    paste = askstring("Download from Pastebin", "Enter paste ID: ", initialvalue = gbl_dlg_paste)
    if not paste:
        return internal_return_focus()
    try:
        # Open the connection.
        paste_api = urlopen("http://pastebin.com/raw.php?i=%s" % paste)
        # Read the data.
        paste_data = paste_api.read()
        # Close the connection.
        paste_api.close()
    except:
        showerror("Download from Pastebin", "Could not download the text for ID \"%s\"." % paste)
        return internal_return_focus()
    # Open a new document.
    file_new()
    if gbl_text_modified:
        return internal_return_focus()
    # Insert the text.
    text_box.text_box.insert("insert", paste_data)
    # Set the cursor and modified flag.
    text_box.text_box.mark_set("insert", "1.0")
    internal_text_modified(True)
    # Update the title.
    update_title()
    # Save the value.
    gbl_dlg_paste = paste
    # Return focus to the text box.
    return internal_return_focus()
    

def tools_upload_pastehtml():
    """Uploads the text to pastehtml."""
    # Define the internal function.
    def tools_upload_pastehtml_internal():
        """Uploads the text."""
        # Define internal function.
        def tools_upload_pastehtml_copy():
            """Copies the text."""
            # Get the selected text.
            text = ph2_ent.get()
            # Add the text to the clipboard.
            text_box.text_box.clipboard_clear()
            text_box.text_box.clipboard_append(text)
        # Get the entry.
        type_ = ph_type_ent.get()
        # Get the text.
        text = text_box.text_box.get("1.0", "end-1c")
        # Build the data string.
        data = {"txt": text}
        # Encode the data string.
        data = urlencode(data)
        # Upload the text.
        try:
            # Send the data.
            pastehtml = urlopen("http://pastehtml.com/upload/create?input_type=%s&result=address" % type_, data)
            # Read the result.
            result = pastehtml.read()
            # Close the connection.
            pastehtml.close()
        except:
            showerror("Upload to PasteHTML", "Could not upload text.")
            ph_win.destroy()
            return internal_return_focus()
        # Save the value.
        global gbl_dlg_ph_type
        gbl_dlg_ph_type = type_
        # Close the window.
        ph_win.destroy()
        # Show the user the result.
        # Create the GUI.
        ph2_win = Toplevel()
        ph2_win.title("Upload to PasteHTMl")
        ph2_win.transient(root)
        ph2_win.grab_set()
        # Create the frame for the label and entry.
        ph21_frm = Frame(ph2_win)
        ph21_frm.pack(side = TOP)
        # Create the label and entry.
        ph2_lbl = Label(ph21_frm, text = "Result: ")
        ph2_lbl.grid(row = 0, column = 0, sticky = W)
        ph2_ent = Entry(ph21_frm)
        ph2_ent.grid(row = 0, column = 1)
        # Create the frame for the buttons.
        ph22_frm = Frame(ph2_win)
        ph22_frm.pack(side = TOP)
        # Create the Open button.
        ph_open_btn = Button(ph22_frm, text = "Open", width = 10, command = lambda: webbrowser.open(result))
        ph_open_btn.pack(side = LEFT, padx = 5, pady = 5)
        # Create the Close button.
        ph_close_btn = Button(ph22_frm, text = "Close", width = 10, default = ACTIVE, command = ph2_win.destroy)
        ph_close_btn.pack(side = LEFT, padx = 5, pady = 5)
        # Insert the result.
        ph2_ent.insert(0, result)
        # Focus on the entry.
        ph2_ent.focus()
        # Bind the events.
        ph2_ent.bind("<Control-Key-c>", lambda event: tools_upload_pastehtml_copy())
        ph2_win.bind("<Return>", lambda event: ph2_win.destroy())
        ph2_win.bind("<Escape>", lambda event: ph2_win.destroy())
    # Create the GUI.
    ph_win = Toplevel()
    ph_win.title("Upload to PasteHTML")
    ph_win.transient(root)
    ph_win.grab_set()
    ph_win.wm_resizable(0, 0)
    # Create the frame for everything but the buttons.
    ph_inf_frame = Frame(ph_win)
    ph_inf_frame.pack(side = TOP, expand = YES, fill = X)
    # Create the frame for the widgets.
    ph_frm = Frame(ph_inf_frame, padx = 5, pady = 5)
    ph_frm.pack(side = TOP, expand = YES, fill = X)
    # Create the type label, entry, and button.
    ph_type_lbl = Label(ph_frm, text = "Type: ")
    ph_type_lbl.grid(row = 0, column = 0, sticky = W)
    ph_type_ent = Entry(ph_frm)
    ph_type_ent.grid(row = 0, column = 1, sticky = W)
    ph_type_btn = Button(ph_frm, text = "?", command = lambda: showinfo("Help", "Specifies the type of text uploaded.\n\nValid values are \"txt\" for text, \"html\" for HTML, and \"mrk\" for Markdown."))
    ph_type_btn.grid(row = 0, column = 2, sticky = W)
    # Create the frame for the buttons.
    ph3_frm = Frame(ph_win)
    ph3_frm.pack(side = TOP)
    # Create the Upload button.
    ph_ok_btn = Button(ph3_frm, text = "Upload", width = 10, default = ACTIVE, command = tools_upload_pastehtml_internal)
    ph_ok_btn.pack(side = LEFT, padx = 5, pady = 5)
    # Create the Cancel button.
    ph_cancel_btn = Button(ph3_frm, text = "Cancel", width = 10, command = ph_win.destroy)
    ph_cancel_btn.pack(side = LEFT, padx = 5, pady = 5)
    # Auto focus on the first entry.
    ph_type_ent.focus()
    # Pre-fill the entry.
    ph_type_ent.insert(0, gbl_dlg_ph_type)
    # Bind the events.
    ph_win.bind("<Return>", lambda event: tools_upload_pastehtml_internal())
    ph_win.bind("<Escape>", lambda event: ph_win.destroy())


def tools_send_ftp():
    """Sends the file over FTP."""
    # If the file has not been saved, this cannot be done.
    if gbl_file_name == "":
        showinfo("Send Via FTP", "File must be saved to do this. Please save the file and try again.")
        return internal_return_focus()
    # Define internal functions.
    def tools_send_ftp_auth():
        """Handles GUI changes."""
        # If the checkbox is checked, show the frame.
        if ftp_iv_var.get():
            ftp2_frm.pack(side = TOP, expand = YES, fill = X)
        # Otherwise, hide it.
        else:
            ftp2_frm.pack_forget()
    def tools_send_ftp_internal():
        """Sends the email."""
        # Get the data.
        server = ftp_serv_ent.get()
        directory = ftp_dir_ent.get()
        if not server:
            return
        # Start the connection.
        try:
            ftp = ftplib.FTP(server)
            # Switch directories, if desired.
            if directory:
                ftp.cwd(directory)
            # Authenticate, if specified.
            if ftp_iv_var.get():
                name = ftp_name_ent.get()
                password = ftp_pass_ent.get()
                ftp.login(name, password)
            # Send the file.
            ftp.storbinary("STOR " + gbl_file_name_short, open(gbl_file_name, "wb"))
            # End the connection.
            ftp.quit()
        except:
            showerror("Send Via FTP", "Could not transfer file.")
        # Close the window.
        ftp_win.destroy()
        # Return focus to the text box.
        return internal_return_focus()
    # Create the GUI.
    ftp_win = Toplevel()
    ftp_win.title("Send Via FTP")
    ftp_win.transient(root)
    ftp_win.grab_set()
    ftp_win.wm_resizable(0, 0)
    # Create the variable for the checkbox.
    ftp_iv_var = IntVar()
    # Create the frame for everything but the buttons.
    ftp_inf_frame = Frame(ftp_win, padx = 5, pady = 5)
    ftp_inf_frame.pack(side = TOP, expand = YES, fill = X)
    # Create the frame for the widgets.
    ftp_frm = Frame(ftp_inf_frame)
    ftp_frm.pack(side = TOP, expand = YES, fill = X)
    # Create the server label, entry, and button.
    ftp_serv_lbl = Label(ftp_frm, text = "Server: ")
    ftp_serv_lbl.grid(row = 0, column = 0, sticky = W)
    ftp_serv_ent = Entry(ftp_frm)
    ftp_serv_ent.grid(row = 0, column = 1)
    ftp_serv_btn = Button(ftp_frm, text = "?", command = lambda: showinfo("Help", "Specifies the server to which the file will be uploaded."))
    ftp_serv_btn.grid(row = 0, column = 2, sticky = W)
    # Create the directory label and entry.
    ftp_dir_lbl = Label(ftp_frm, text = "Directory: ")
    ftp_dir_lbl.grid(row = 1, column = 0, sticky = W)
    ftp_dir_ent = Entry(ftp_frm)
    ftp_dir_ent.grid(row = 1, column = 1)
    ftp_dir_btn = Button(ftp_frm, text = "?", command = lambda: showinfo("Help", "Specifies the directory in which the file will be placed."))
    ftp_dir_btn.grid(row = 1, column = 2, sticky = W)
    # Create the authenticate checkbox.
    ftp_chkbox = Checkbutton(ftp_inf_frame, text = "Authenticate", variable = ftp_iv_var, command = tools_send_ftp_auth)
    ftp_chkbox.pack(side = TOP)
    # Create the frame for the second set of widgets.
    ftp2_frm = Frame(ftp_inf_frame)
    # Create the server label and entry.
    ftp_name_lbl = Label(ftp2_frm, text = "Name: ")
    ftp_name_lbl.grid(row = 0, column = 0, sticky = W)
    ftp_name_ent = Entry(ftp2_frm)
    ftp_name_ent.grid(row = 0, column = 1)
    ftp_name_btn = Button(ftp2_frm, text = "?", command = lambda: showinfo("Help", "Specifies the name of the user."))
    ftp_name_btn.grid(row = 0, column = 2, sticky = W)
    # Create the from label and entry.
    ftp_pass_lbl = Label(ftp2_frm, text = "Password: ")
    ftp_pass_lbl.grid(row = 1, column = 0, sticky = W)
    ftp_pass_ent = Entry(ftp2_frm, show = "*")
    ftp_pass_ent.grid(row = 1, column = 1)
    ftp_pass_btn = Button(ftp2_frm, text = "?", command = lambda: showinfo("Help", "Specifies the user's password."))
    ftp_pass_btn.grid(row = 1, column = 2, sticky = W)
    # Create the frame for the buttons.
    ftp3_frm = Frame(ftp_win)
    ftp3_frm.pack(side = TOP)
    # Create the Send button.
    ftp_ok_btn = Button(ftp3_frm, text = "Send", width = 10, default = ACTIVE, command = tools_send_ftp_internal)
    ftp_ok_btn.pack(side = LEFT, padx = 5, pady = 5)
    # Create the Cancel button.
    ftp_cancel_btn = Button(ftp3_frm, text = "Cancel", width = 10, command = ftp_win.destroy)
    ftp_cancel_btn.pack(side = LEFT, padx = 5, pady = 5)
    # Pre-fill the entries.
    ftp_serv_ent.insert(0, CONFIG["ftp_server"])
    # Auto focus on the first entry.
    ftp_serv_ent.focus()
    # Bind the events.
    ftp_win.bind("<Return>", lambda event: tools_send_ftp_internal())
    ftp_win.bind("<Escape>", lambda event: ftp_win.destroy())


def tools_send_email():
    """Sends the text as an email."""
    # Define internal functions.
    def tools_send_email_auth():
        """Handles GUI changes."""
        # If the checkbox is checked, show the frame.
        if mail_iv_var.get():
            mail2_frm.pack(side = TOP, expand = YES, fill = X)
        # Otherwise, hide it.
        else:
            mail2_frm.pack_forget()
    def tools_send_email_internal():
        """Sends the email."""
        # Get the data.
        server = mail_serv_ent.get()
        from_user = mail_from_ent.get()
        to_user = mail_to_ent.get()
        subject = mail_subj_ent.get()
        text = text_box.text_box.get("1.0", "end-1c")
        if not server or not from_user or not to_user:
            return internal_return_focus()
        # Build the string.
        email_str = "From: %s\nTo: %s\nSubject: %s\n\n%s" % (from_user, to_user, subject, text)
        # Start the connection.
        try:
            email = smtplib.SMTP(server)
            email.starttls()
            # Authenticate, if specified.
            if mail_iv_var.get():
                name = mail_name_ent.get()
                password = mail_pass_ent.get()
                email.login(name, password)
            # Send the email.
            email.sendmail(from_user, to_user, email_str)
            # End the connection.
            email.quit()
        except:
            showerror("Send Via Email", "Could not send email.")
        # Close the window.
        mail_win.destroy()
        # Return focus to the text box.
        return internal_return_focus()
    # Create the GUI.
    mail_win = Toplevel()
    mail_win.title("Send Via Email")
    mail_win.transient(root)
    mail_win.grab_set()
    mail_win.wm_resizable(0, 0)
    # Create the variable for the checkbox.
    mail_iv_var = IntVar()
    # Create the frame for everything but the buttons.
    mail_inf_frame = Frame(mail_win, padx = 5, pady = 5)
    mail_inf_frame.pack(side = TOP, expand = YES, fill = X)
    # Create the frame for the widgets.
    mail_frm = Frame(mail_inf_frame)
    mail_frm.pack(side = TOP, expand = YES, fill = X)
    # Create the server label and entry.
    mail_serv_lbl = Label(mail_frm, text = "Server: ")
    mail_serv_lbl.grid(row = 0, column = 0, sticky = W)
    mail_serv_ent = Entry(mail_frm)
    mail_serv_ent.grid(row = 0, column = 1)
    mail_serv_btn = Button(mail_frm, text = "?", command = lambda: showinfo("Help", "Specifies the server used to send the email."))
    mail_serv_btn.grid(row = 0, column = 2, sticky = W)
    # Create the from label and entry.
    mail_from_lbl = Label(mail_frm, text = "From: ")
    mail_from_lbl.grid(row = 1, column = 0, sticky = W)
    mail_from_ent = Entry(mail_frm)
    mail_from_ent.grid(row = 1, column = 1)
    mail_from_btn = Button(mail_frm, text = "?", command = lambda: showinfo("Help", "Specifies the email sender."))
    mail_from_btn.grid(row = 1, column = 2, sticky = W)
    # Create the to label and entry.
    mail_to_lbl = Label(mail_frm, text = "To: ")
    mail_to_lbl.grid(row = 2, column = 0, sticky = W)
    mail_to_ent = Entry(mail_frm)
    mail_to_ent.grid(row = 2, column = 1)
    mail_to_btn = Button(mail_frm, text = "?", command = lambda: showinfo("Help", "Specifies the email recipient."))
    mail_to_btn.grid(row = 2, column = 2, sticky = W)
    # Create the subject label and entry.
    mail_subj_lbl = Label(mail_frm, text = "Subject: ")
    mail_subj_lbl.grid(row = 3, column = 0, sticky = W)
    mail_subj_ent = Entry(mail_frm)
    mail_subj_ent.grid(row = 3, column = 1)
    mail_subj_btn = Button(mail_frm, text = "?", command = lambda: showinfo("Help", "Specifies the email subject."))
    mail_subj_btn.grid(row = 3, column = 2, sticky = W)
    # Create the authenticate checkbox.
    mail_chkbox = Checkbutton(mail_inf_frame, text = "Authenticate", variable = mail_iv_var, command = tools_send_email_auth)
    mail_chkbox.pack(side = TOP)
    # Create the frame for the second set of widgets.
    mail2_frm = Frame(mail_inf_frame)
    # Create the server label and entry.
    mail_name_lbl = Label(mail2_frm, text = "Name: ")
    mail_name_lbl.grid(row = 0, column = 0, sticky = W)
    mail_name_ent = Entry(mail2_frm)
    mail_name_ent.grid(row = 0, column = 1)
    mail_name_btn = Button(mail2_frm, text = "?", command = lambda: showinfo("Help", "Specifies the name of the user."))
    mail_name_btn.grid(row = 0, column = 2, sticky = W)
    # Create the from label and entry.
    mail_pass_lbl = Label(mail2_frm, text = "Password: ")
    mail_pass_lbl.grid(row = 1, column = 0, sticky = W)
    mail_pass_ent = Entry(mail2_frm, show = "*")
    mail_pass_ent.grid(row = 1, column = 1)
    mail_pass_btn = Button(mail2_frm, text = "?", command = lambda: showinfo("Help", "Specifies the user's password."))
    mail_pass_btn.grid(row = 1, column = 2, sticky = W)
    # Create the frame for the buttons.
    mail3_frm = Frame(mail_win)
    mail3_frm.pack(side = TOP)
    # Create the Send button.
    mail_ok_btn = Button(mail3_frm, text = "Send", width = 10, default = ACTIVE, command = tools_send_email_internal)
    mail_ok_btn.pack(side = LEFT, padx = 5, pady = 5)
    # Create the Cancel button.
    mail_cancel_btn = Button(mail3_frm, text = "Cancel", width = 10, command = mail_win.destroy)
    mail_cancel_btn.pack(side = LEFT, padx = 5, pady = 5)
    # Pre-fill the entries.
    mail_serv_ent.insert(0, CONFIG["email_server"])
    mail_to_ent.insert(0, CONFIG["email_to"])
    mail_from_ent.insert(0, CONFIG["email_from"])
    # Auto focus on the first entry.
    mail_serv_ent.focus()
    # Bind the events.
    mail_win.bind("<Return>", lambda event: tools_send_email_internal())
    mail_win.bind("<Escape>", lambda event: mail_win.destroy())


def tools_statistics():
    """Shows info about the current file/text."""
    # Get the current position.
    location = text_box.text_box.index("insert").split(".")
    # Get the current line.
    line = location[0]
    # Get the current character.
    char = str(int(location[1]) + 1)
    # Get all the text.
    text = text_box.text_box.get(1.0, "end-1c")
    # Get the number of characters
    chars = str(len(text))
    # Get the number of characters, excluding whitespace.
    chars_no_space = str(len(re.sub(r"\s", "", text)))
    # Get the number of words.
    words = len(text.split())
    # Get the number of lines.
    lines = str(len(text.split("\n")))
    # Get the selected text, if any.
    if text_box.text_box.tag_ranges("sel"):
        sel_text = text_box.text_box.get("sel.first", "sel.last")
        # Get the number of selected characters.
        sel_chars = str(len(sel_text))
        # Get the number of selected characters, excluding whitespace.
        sel_chars_no_space = str(len(re.sub(r"\s", "", sel_text)))
        # Get the number of selected words.
        sel_words = str(len(sel_text.split()))
        # Get the number of selected lines.
        sel_lines = str(len(sel_text.split("\n")))
        # Get the selection start.
        sel_start_line, sel_start_char = text_box.text_box.index("sel.first").split(".")
        # Get the selection end.
        sel_end_line, sel_end_char = text_box.text_box.index("sel.last").split(".")
    else:
        # If nothing is selected, set variables to "N/A"
        sel_chars = "0"
        sel_chars_no_space = "0"
        sel_words = "0"
        sel_lines = "0"
    # Create the GUI.
    stat_win = Toplevel()
    stat_win.title("Statistics")
    stat_win.transient(root)
    stat_win.grab_set()
    stat_win.wm_resizable(0, 0)
    # Create the frame for the widgets.
    stat_frm = Frame(stat_win)
    stat_frm.pack(side = TOP, expand = YES, fill = X)
    # Create the cursor location labels.
    stat_cur_frm = Frame(stat_frm, padx = 5, pady = 5, relief = SUNKEN, bd = 2)
    stat_cur_frm.pack(side = TOP, expand = YES, fill = X)
    Label(stat_cur_frm, text = "Cursor Location", pady = 5).pack(side = TOP)
    stat_cur_frm2 = Frame(stat_cur_frm)
    stat_cur_frm2.pack(side = LEFT)
    Label(stat_cur_frm2, text = "Cursor line: ").grid(row = 0, column = 0, sticky = W)
    Label(stat_cur_frm2, text = line).grid(row = 0, column = 1, sticky = W)
    Label(stat_cur_frm2, text = "Cursor column: ").grid(row = 1, column = 0, sticky = W)
    Label(stat_cur_frm2, text = char).grid(row = 1, column = 1, sticky = W)
    # Create the general statistics labels.
    stat_gen_frm = Frame(stat_frm, padx = 5, pady = 5, relief = SUNKEN, bd = 2)
    stat_gen_frm.pack(side = TOP, expand = YES, fill = X)
    Label(stat_gen_frm, text = "General Statistics", pady = 5).pack(side = TOP)
    stat_gen_frm2 = Frame(stat_gen_frm)
    stat_gen_frm2.pack(side = LEFT)
    Label(stat_gen_frm2, text = "Characters: ").grid(row = 0, column = 0, sticky = W)
    Label(stat_gen_frm2, text = chars).grid(row = 0, column = 1, sticky = W)
    Label(stat_gen_frm2, text = "Characters (excluding spaces): ").grid(row = 1, column = 0, sticky = W)
    Label(stat_gen_frm2, text = chars_no_space).grid(row = 1, column = 1, sticky = W)
    Label(stat_gen_frm2, text = "Words: ").grid(row = 2, column = 0, sticky = W)
    Label(stat_gen_frm2, text = words).grid(row = 2, column = 1, sticky = W)
    Label(stat_gen_frm2, text = "Lines: ").grid(row = 3, column = 0, sticky = W)
    Label(stat_gen_frm2, text = lines).grid(row = 3, column = 1, sticky = W)
    # Create the selection labels.
    if text_box.text_box.tag_ranges("sel"):
        # Create the selection locations labels.
        stat_sl_frm = Frame(stat_frm, padx = 5, pady = 5, relief = SUNKEN, bd = 2)
        stat_sl_frm.pack(side = TOP, expand = YES, fill = X)
        Label(stat_sl_frm, text = "Selection Location", pady = 5).pack(side = TOP)
        stat_sl_frm2 = Frame(stat_sl_frm)
        stat_sl_frm2.pack(side = LEFT)
        Label(stat_sl_frm2, text = "Selection start line: ").grid(row = 0, column = 0, sticky = W)
        Label(stat_sl_frm2, text = sel_start_line).grid(row = 0, column = 1, sticky = W)
        Label(stat_sl_frm2, text = "Selection start column: ").grid(row = 1, column = 0, sticky = W)
        Label(stat_sl_frm2, text = sel_start_char).grid(row = 1, column = 1, sticky = W)
        Label(stat_sl_frm2, text = "Selection end line: ").grid(row = 2, column = 0, sticky = W)
        Label(stat_sl_frm2, text = sel_end_line).grid(row = 2, column = 1, sticky = W)
        Label(stat_sl_frm2, text = "Selection end column: ").grid(row = 3, column = 0, sticky = W)
        Label(stat_sl_frm2, text = sel_end_char).grid(row = 3, column = 1, sticky = W)
        # Create the selection statistics labels.
        stat_sel_frm = Frame(stat_frm, padx = 5, pady = 5, relief = SUNKEN, bd = 2)
        stat_sel_frm.pack(side = TOP, expand = YES, fill = X)
        Label(stat_sel_frm, text = "Selection Statistics", pady = 5).pack(side = TOP)
        stat_sel_frm2 = Frame(stat_sel_frm)
        stat_sel_frm2.pack(side = LEFT)
        Label(stat_sel_frm2, text = "Characters: ").grid(row = 0, column = 0, sticky = W)
        Label(stat_sel_frm2, text = sel_chars).grid(row = 0, column = 1, sticky = W)
        Label(stat_sel_frm2, text = "Characters (excluding spaces): ").grid(row = 1, column = 0, sticky = W)
        Label(stat_sel_frm2, text = sel_chars_no_space).grid(row = 1, column = 1, sticky = W)
        Label(stat_sel_frm2, text = "Words: ").grid(row = 2, column = 0, sticky = W)
        Label(stat_sel_frm2, text = sel_words).grid(row = 2, column = 1, sticky = W)
        Label(stat_sel_frm2, text = "Lines: ").grid(row = 3, column = 0, sticky = W)
        Label(stat_sel_frm2, text = sel_lines).grid(row = 3, column = 1, sticky = W)
    # Bind the event.
    stat_win.bind("<Escape>", lambda event: stat_win.destroy())


def code_open_browser():
    """Opens the current file in the user's default web browser."""
    # If the file has not been saved, this cannot be done.
    if gbl_file_name == "":
        showinfo("Open in Web Browser", "File must be saved to do this. Please save the file and try again.")
        return internal_return_focus()
    # If there are unsaved changes, have the user confirm before continuing.
    if gbl_text_modified:
        open_con = askyesno("Open in Web Browser", "File has unsaved changes. Continue?")
        if not open_con:
            return internal_return_focus()
    # Open the file in the user's web browser.
    webbrowser.open(gbl_file_name)
    # Return focus to the text box.
    return internal_return_focus()


def code_run_code(command, args = ""):
    """Runs or compiles the file using the specified command."""
    # If the file has not been saved, this cannot be done.
    if gbl_file_name == "":
        showinfo("Run Code", "File must be saved to do this. Please save the file and try again.")
        return internal_return_focus()
    # If there are unsaved changes, have the user confirm before continuing.
    if gbl_text_modified:
        run_con = askyesno("Run Code", "File has unsaved changes. Continue?")
        if not run_con:
            return internal_return_focus()
    try:
        # Ask the user for the command, if necessary.
        if not command:
            command = askstring("Run Code", "Enter command:")
            if not command:
                return internal_return_focus()
        # Ask the user for extra arguments, if specified.
        if CONFIG["run_code_args"] == "yes":
            args = args or askstring("Run Code", "Enter command line arguments:") or ""
        # Remember the current directory.
        cwd = os.getcwd()
        # Change to the directory of the file.
        file_name1, file_name2 = os.path.split(gbl_file_name)
        os.chdir(file_name1 or cwd)
        # Run the code.
        if sys.platform[:3] == "win":
            os.system(command + " " + gbl_file_name_short + " " + args)
        else:
            file_name = gbl_file_name_short.split()
            if os.fork() == 0:
                os.execvp(command, [command] + file_name)
        # Switch back to the original directory.
        os.chdir(cwd)
    except:
        showerror("Run Code", "File could not be executed with \"" + command + "\".")
    # Return focus to the text box.
    return internal_return_focus()


def code_execute(args = ""):
    """Executes Python code."""
    # If there are unsaved changes, have the user confirm before continuing.
    if gbl_text_modified:
        run_con = askyesno("Execute", "File has unsaved changes. Continue?")
        if not run_con:
            return internal_return_focus()
    try:
        # Ask the user for extra arguments.
        if CONFIG["run_code_args"] == "yes":
            args = args or askstring("Execute", "Enter command line arguments:") or ""
        # Create a namespace for the executed code.
        ns = {"__name__": "__main__"}
        # Set the argv list.
        sys.argv = [gbl_file_name] + args.split()
        # Execute the code.
        exec(text_box.text_box.get("1.0", "end-1c") + "\n", ns)
    except:
        showerror("Execute", "Code could not be executed.\n\nEither an error occured, or the code is not Python.")
    # Return focus to the text box.
    return internal_return_focus()


def code_find_opening():
    """Finds an opening symbol."""
    # If no text is selected, this cannot be done.
    if not text_box.text_box.tag_ranges("sel"):
        showerror("Find Opening Symbol", "No text selected.")
        return internal_return_focus()
    # Get the symbol.
    sym = text_box.text_box.get("sel.first", "sel.last")
    # If it is not one of the supported characters, this cannot be done.
    if sym not in ["]", ")", "}", ">"]:
        showerror("Find Opening Symbol", "Invalid symbol.")
        return internal_return_focus()
    # Determine the opening symbol.
    if sym == "]":
        sym2 = "["
    elif sym == ")":
        sym2 = "("
    elif sym == "}":
        sym2 = "{"
    elif sym == ">":
        sym2 = "<"
    # Find the symbol.
    found = text_box.text_box.search(sym2, "insert", "1.0", backwards = True)
    # If it wasn't found:
    if not found:
        showinfo("Find Opening Symbol", "Symbol not found.")
    # Otherwise:
    else:
        # Move the cursor and select the symbol.
        text_box.text_box.mark_set("insert", found)
        text_box.text_box.tag_remove("sel", "1.0", "end")
        text_box.text_box.tag_add("sel", found, found + "+1c")
    # Return focus to the text box.
    return internal_return_focus()


def code_find_closing():
    """Finds a closing symbol."""
    # If no text is selected, this cannot be done.
    if not text_box.text_box.tag_ranges("sel"):
        showerror("Find Closing Symbol", "No text selected.")
        return internal_return_focus()
    # Get the symbol.
    sym = text_box.text_box.get("sel.first", "sel.last")
    # If it is not one of the supported characters, this cannot be done.
    if sym not in ["[", "(", "{", "<"]:
        showerror("Find Closing Symbol", "Invalid symbol.")
        return internal_return_focus()
    # Determine the closing symbol.
    if sym == "[":
        sym2 = "]"
    elif sym == "(":
        sym2 = ")"
    elif sym == "{":
        sym2 = "}"
    elif sym == "<":
        sym2 = ">"
    # Find the symbol.
    found = text_box.text_box.search(sym2, "insert", "end")
    # If it wasn't found:
    if not found:
        showinfo("Find Closing Symbol", "Symbol not found.")
    # Otherwise:
    else:
        # Move the cursor and select the symbol.
        text_box.text_box.mark_set("insert", found)
        text_box.text_box.tag_remove("sel", "1.0", "end")
        text_box.text_box.tag_add("sel", found, found + "+1c")
    # Return focus to the text box.
    return internal_return_focus()


def code_insert_comment(start, end):
    """Inserts a comment."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # If possible, use the currently selected text.
    # Otherwise, ask the user for the string to use.
    text = ""
    from_sel = False
    if text_box.text_box.tag_ranges("sel"):
        text = text_box.text_box.get("sel.first", "sel.last")
        from_sel = True
    else:
        text = askstring("Insert Comment", "Enter comment:")
        if text == None:
            return internal_return_focus()
    # Build the comment.
    comment = start + text + end
    # Delete the currently selected text, if any.
    if text_box.text_box.tag_ranges("sel"):
        text_box.text_box.delete("sel.first", "sel.last")
    # Insert the comment.
    text_box.text_box.insert("insert", comment)
    # Move the cursor if needed.
    if start == "<!-- ":
        text_box.text_box.mark_set("insert", "insert-4c")
    elif start == "/* ":
        text_box.text_box.mark_set("insert", "insert-3c")
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def code_insert_doctype(which):
    """Inserts a doctype."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # Delete the currently selected text, if any.
    if text_box.text_box.tag_ranges("sel"):
        text_box.text_box.delete("sel.first", "sel.last")
    # Select the doctype.
    doctype = ""
    if which == "html5":
        doctype = "<!doctype html>"
    elif which == "html4strict":
        doctype = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">"""
    elif which == "html4trans":
        doctype = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">"""
    elif which == "html4frame":
        doctype = """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN" "http://www.w3.org/TR/html4/frameset.dtd">"""
    elif which == "xhtml1strict":
       doctype = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">"""
    elif which == "xhtml1trans":
       doctype = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">"""
    elif which == "xhtml1frame":
       doctype = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Frameset//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-frameset.dtd">"""
    elif which == "xhtml11":
       doctype = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">"""
    elif which == "xhtml2":
       doctype = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 2.0//EN" "http://www.w3.org/MarkUp/DTD/xhtml2.dtd">"""
    # Insert the doctype.
    text_box.text_box.insert("insert", doctype)
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def code_insert(insert):
    """Inserts whatever."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # Delete the currently selected text, if any.
    if text_box.text_box.tag_ranges("sel"):
        text_box.text_box.delete("sel.first", "sel.last")
    # Insert the string.
    text_box.text_box.insert("insert", insert)
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def code_insert_tag(tname = None, tattr = None, ttype = None):
    """Inserts an XML/HTML tag."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    # Define the internal function.
    def code_insert_tag_internal():
        """Builds then inserts a tag."""
        text_box.text_box.edit_separator()
        # Get the tag name.
        tag_name = tag_name_ent.get()
        # Get the tag attributes.
        tag_attr = tag_attr_ent.get()
        # Get the type of the tab (single-sided or two-sided).
        tag_type = tag_type_iv.get()
        # Wrap tag around any selected text.
        wrapped_text = ""
        if text_box.text_box.tag_ranges("sel"):
            wrapped_text = text_box.text_box.get("sel.first", "sel.last")
            text_box.text_box.delete("sel.first", "sel.last")
        # Build the tag.
        tag = "<" + tag_name
        if tag_attr:
            tag += " " + tag_attr
        if tag_type:
            tag += " />"
        else:
            tag += ">" + wrapped_text + "</" + tag_name + ">"
        # Insert the tag.
        text_box.text_box.insert("insert", tag)
        # Mark the text as having changes.
        internal_text_modified(True)
        # Update the title.
        update_title()
        text_box.text_box.edit_separator()
        # Close the window.
        tag_win.destroy()
    # Create the GUI.
    tag_win = Toplevel()
    tag_win.title("Insert Tag")
    tag_win.transient(root)
    tag_win.grab_set()
    tag_win.wm_resizable(0, 0)
    # This variable is used by the checkbox.
    tag_type_iv = IntVar()
    # Create the frame for the labels and entries.
    tag_frame1 = Frame(tag_win)
    tag_frame1.pack(side = TOP)
    # Create the label and entry for the tag name.
    tag_name_lbl = Label(tag_frame1, text = "Name:")
    tag_name_lbl.grid(row = 0, column = 0, sticky = W)
    tag_name_ent = Entry(tag_frame1)
    tag_name_ent.grid(row = 0, column = 1)
    # Create the label and entry for the tab attributes.
    tag_attr_lbl = Label(tag_frame1, text = "Attributes:")
    tag_attr_lbl.grid(row = 1, column = 0, sticky = W)
    tag_attr_ent = Entry(tag_frame1)
    tag_attr_ent.grid(row = 1, column = 1)
    # Create the frame for the checkbox.
    tag_frame2 = Frame(tag_win)
    tag_frame2.pack(side = TOP)
    # Create the checkbox.
    tag_chkbox = Checkbutton(tag_frame2, text = "Single sided", variable = tag_type_iv)
    tag_chkbox.pack(side = TOP)
    # Create the frame for the buttons.
    tag_frame3 = Frame(tag_win)
    tag_frame3.pack(side = TOP)
    # Create the OK button.
    tag_ok_btn = Button(tag_frame3, text = "OK", width = 10, default = ACTIVE, command = code_insert_tag_internal)
    tag_ok_btn.pack(side = LEFT, padx = 5, pady = 5)
    # Create the Cancel button.
    tag_cancel_btn = Button(tag_frame3, text = "Cancel", width = 10, command = tag_win.destroy)
    tag_cancel_btn.pack(side = LEFT, padx = 5, pady = 5)
    # Bind the events.
    tag_win.bind("<Return>", lambda event: code_insert_tag_internal())
    tag_win.bind("<Escape>", lambda event: tag_win.destroy())
    # Add in any specified text.
    if tname != None:
        tag_name_ent.delete(0, END)
        tag_name_ent.insert(0, tname)
    if tattr != None:
        tag_attr_ent.delete(0, END)
        tag_attr_ent.insert(0, tattr)
    if ttype != None:
        tag_type_iv.set(ttype)
    # Auto focus on the entry.
    tag_name_ent.focus()


def code_escape_sel():
    """Escapes the selected text."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    # If no text is selected, this cannot be done.
    if not text_box.text_box.tag_ranges("sel"):
        showerror("Escape", "No text selected.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # Get the currently selected text.
    text = text_box.text_box.get("sel.first", "sel.last")
    # Escape the string.
    text = text.replace("\\", "\\\\").replace("\"", "\\\"").replace("\'", "\\\'")
    # Delete the old string and insert the new one.
    text_box.text_box.delete("sel.first", "sel.last")
    text_box.text_box.insert("insert", text)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def code_remove_tags():
    """Removes XML/HTML tags from selected text."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        showwarning("File Locked", "This function is disabled in read-only mode.")
        return internal_return_focus()
    # If no text is selected, this cannot be done.
    if not text_box.text_box.tag_ranges("sel"):
        showerror("Remove Tags", "No text selected.")
        return internal_return_focus()
    text_box.text_box.edit_separator()
    # Get the currently selected text.
    text = text_box.text_box.get("sel.first", "sel.last")
    # Remove the tags.
    text = re.sub("<[^>]*>", "", text)
    # Delete the old string and insert the new one.
    text_box.text_box.delete("sel.first", "sel.last")
    text_box.text_box.insert("insert", text)
    # Update the title.
    update_title()
    text_box.text_box.edit_separator()
    # Return focus to the text box.
    return internal_return_focus()


def opt_options():
    """Shows the Options dialog, and allows the user to change settings."""
    # Define internal functions.
    def opt_hide_panel():
        """Hides the panels."""
        opt_font_frm.pack_forget()
        opt_int_frm.pack_forget()
        opt_edit_frm.pack_forget()
        opt_search_frm.pack_forget()
        opt_net_frm.pack_forget()
        opt_browse_frm.pack_forget()
        opt_menu_frm.pack_forget()
        opt_macro_frm.pack_forget()
        opt_code_frm.pack_forget()
        opt_misc_frm.pack_forget()
    def opt_show_panel(panel):
        """Shows a panel."""
        # Show Font panel:
        if panel == "font":
            opt_font_frm.pack(side = RIGHT, fill = BOTH)
        # Show Interface panel:
        elif panel == "interface":
            opt_int_frm.pack(side = RIGHT, fill = BOTH)
        # Show Editing panel:
        elif panel == "editing":
            opt_edit_frm.pack(side = RIGHT, fill = BOTH)
        # Show Searching panel:
        elif panel == "searching":
            opt_search_frm.pack(side = RIGHT, fill = BOTH)
        # Show Network panel:
        elif panel == "network":
            opt_net_frm.pack(side = RIGHT, fill = BOTH)
        # Show File Browser panel:
        elif panel == "file browser":
            opt_browse_frm.pack(side = RIGHT, fill = BOTH)
        # Show Menus panel:
        elif panel == "menus":
            opt_menu_frm.pack(side = RIGHT, fill = BOTH)
        # Show Macros panel.
        elif panel == "macros":
            opt_macro_frm.pack(side = RIGHT, fill = BOTH)
        # Show Code panel:
        elif panel == "code":
            opt_code_frm.pack(side = RIGHT, fill = BOTH)
        # Show Misc panel:
        elif panel == "misc":
            opt_misc_frm.pack(side = RIGHT, fill = BOTH)
    def opt_give_focus(panel):
        """Adds a visual cue to the current panel's button."""
        # Set all buttons to raised.
        opt_font_btn.config(relief = RAISED)
        opt_int_btn.config(relief = RAISED)
        opt_edit_btn.config(relief = RAISED)
        opt_search_btn.config(relief = RAISED)
        opt_net_btn.config(relief = RAISED)
        opt_browse_btn.config(relief = RAISED)
        opt_menus_btn.config(relief = RAISED)
        opt_macro_btn.config(relief = RAISED)
        opt_code_btn.config(relief = RAISED)
        opt_misc_btn.config(relief = RAISED)
        # Give focus to a specific button.
        if panel == "font":
            opt_font_btn.config(relief = FLAT)
        elif panel == "interface":
            opt_int_btn.config(relief = FLAT)
        elif panel == "editing":
            opt_edit_btn.config(relief = FLAT)
        elif panel == "searching":
            opt_search_btn.config(relief = FLAT)
        elif panel == "network":
            opt_net_btn.config(relief = FLAT)
        elif panel == "file browser":
            opt_browse_btn.config(relief = FLAT)
        elif panel == "menus":
            opt_menus_btn.config(relief = FLAT)
        elif panel == "macros":
            opt_macro_btn.config(relief = FLAT)
        elif panel == "code":
            opt_code_btn.config(relief = FLAT)
        elif panel == "misc":
            opt_misc_btn.config(relief = FLAT)
    def opt_switch(panel):
        """Switches to a different panel."""
        global opt_panel
        # Hide the current panel.
        opt_hide_panel()
        # Give focus to the new button.
        opt_give_focus(panel)
        # Show the new panel.
        opt_show_panel(panel)
        # Remember the new panel.
        opt_panel = panel
    def opt_get_color(entry):
        """Gets a color and inserts it into an entry."""
        # Get the color.
        rbg, color = askcolor()
        if not color:
            return
        # Insert color into the entry.
        entry.delete(0, "end")
        entry.insert(0, color)
        # Don't allow the widget to get focus.
        return "break"
    def opt_get_directory(entry):
        """Gets a directory and inserts it into an entry."""
        # Get the directory
        directory = askdirectory()
        if not directory:
            return
        # Insert the directory into the entry,
        entry.delete(0, "end")
        entry.insert(0, directory)
        # Don't allow the widget to get focus.
        return "break"
    def opt_apply():
        """Saves the options."""
        # Get all the values.
        font = opt_font_ent.get()
        size = opt_size_ent.get()
        # The font size must be a positive integer.
        if size.isdigit() and int(size) > 0:
            size = int(size)
        else:
            size = CONFIG["font_size"]
        if size < 1:
            size = 1
        style = opt_style_var.get()
        fg = opt_fg_ent.get()
        bg = opt_bg_ent.get()
        sel_fg = opt_sfg_ent.get()
        sel_bg = opt_sbg_ent.get()
        wrap = opt_wrap_var.get()
        ui_fg = opt_uifg_ent.get()
        ui_bg = opt_uibg_ent.get()
        menu_tearoff = opt_menu_var.get()
        toolbar_ = opt_tb_var.get()
        line_numbers = opt_ln_var.get()
        status_bar_ = opt_sb_var.get()
        file_name_ = opt_ft_var.get()
        auto_indent = opt_autoi_var.get()
        replace_tabs = opt_replt_var.get()
        block_indent = opt_bautoi_var.get()
        indent = opt_ina_ent.get()
        # The indent amount must be a positive integer.
        if indent.isdigit() and int(indent) > 0:
            indent = int(indent)
        else:
            indent = CONFIG["indent"]
        spaces_tabs = opt_spt_ent.get()
        # The spaces per tab must be a positive integer.
        if spaces_tabs.isdigit() and int(spaces_tabs) > 0:
            spaces_tabs = int(spaces_tabs)
        else:
            spaces_tabs = CONFIG["font_size"]
        reverse_sep = opt_rsep_ent.get()
        join_sep = opt_jsep_ent.get()
        python = opt_py_ent.get()
        perl = opt_pl_ent.get()
        php = opt_php_ent.get()
        c = opt_c_ent.get()
        cpp = opt_cpp_ent.get()
        java = opt_java_ent.get()
        case_sen = opt_cs_var.get()
        regex = opt_re_var.get()
        keep_dlg = opt_kdlg_var.get()
        cursor_pos = opt_curp_var.get()
        init_dir = opt_dir_ent.get()
        def_encode = opt_dencode_ent.get()
        prompt_encode = opt_pencode_var.get()
        date_format = opt_datef_ent.get()
        time_format = opt_timef_ent.get()
        restore_last = opt_resopen_var.get()
        # Set all the options.
        # Set the Font options.
        CONFIG["font_name"] = font
        CONFIG["font_size"] = size
        CONFIG["font_style"] = style
        CONFIG["fg"] = fg
        CONFIG["bg"] = bg
        CONFIG["sel_fg"] = sel_fg
        CONFIG["sel_bg"] = sel_bg
        CONFIG["wrap"] = wrap
        text_box.text_box.config(font = (CONFIG["font_name"], CONFIG["font_size"], CONFIG["font_style"]), bg = CONFIG["bg"], fg = CONFIG["fg"], selectbackground = CONFIG["sel_bg"], selectforeground = CONFIG["sel_fg"], wrap = CONFIG["wrap"])
        if CONFIG["line_numbers"]:
            text_box.line_text.config(font = (CONFIG["font_name"], CONFIG["font_size"], "normal"))
        if CONFIG["command_bar"] == "show":
            command_bar_ent.config(bg = CONFIG["bg"], fg = CONFIG["fg"])
        # Set the Interface options.
        CONFIG["ui_fg"] = ui_fg
        CONFIG["ui_bg"] = ui_bg
        text_box.scroll_h.config(bg = CONFIG["ui_bg"])
        text_box.scroll_v.config(bg = CONFIG["ui_bg"])
        if CONFIG["toolbar"]:
            toolbar.config(bg = CONFIG["ui_bg"])
            tb_new_btn.config(bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"])
            tb_open_btn.config(bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"])
            tb_save_btn.config(bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"])
            tb_previous_btn.config(bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"])
            tb_next_btn.config(bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"])
            tb_undo_btn.config(bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"])
            tb_redo_btn.config(bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"])
            tb_cut_btn.config(bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"])
            tb_copy_btn.config(bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"])
            tb_paste_btn.config(bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"])
            tb_search_btn.config(bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"])
            tb_replace_btn.config(bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"])
        if CONFIG["documents_list"] == "show":
            documents_list.config(bg = CONFIG["bg"], fg = CONFIG["fg"])
            documents_scroll.config(bg = CONFIG["ui_bg"])
        if CONFIG["line_numbers"]:
            text_box.line_text.config(bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"])
        if CONFIG["status_bar"]:
            status_bar.config(bg = CONFIG["ui_bg"])
            status_line_lbl.config(bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"])
            status_col_lbl.config(bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"])
            status_chars_lbl.config(bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"])
            status_words_lbl.config(bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"])
            status_lines_lbl.config(bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"])
            status_file_lbl.config(bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"])
            status_mode_lbl.config(bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"])
        if CONFIG["command_bar"] == "show":
            command_bar.config(bg = CONFIG["ui_bg"])
            command_bar_btn.config(bg = CONFIG["ui_bg"])
        CONFIG["tearoff"] = menu_tearoff
        CONFIG["toolbar"] = toolbar_
        CONFIG["line_numbers"] = line_numbers
        CONFIG["title"] = file_name_
        update_title()
        CONFIG["status_bar"] = opt_sb_var.get()
        # Set the Editing options.
        CONFIG["auto_indent"] = auto_indent
        CONFIG["replace_tabs"] = replace_tabs
        CONFIG["block_indent"] = block_indent
        CONFIG["indent"] = indent
        CONFIG["spaces_tab"] = spaces_tabs
        CONFIG["reverse_sep"] = reverse_sep
        CONFIG["join_sep"] = join_sep
        # Set the Searching options.
        if case_sen == "insensitive":
            CONFIG["case_insensitive"] = True
        else:
            CONFIG["case_insensitive"] = False
        if regex == "yes":
            CONFIG["regex"] = True
        else:
            CONFIG["regex"] = False
        CONFIG["search_keep_dlg"] = keep_dlg
        CONFIG["search_cursor_pos"] = cursor_pos
        # Set the Code options.
        CONFIG["python"] = python
        CONFIG["perl"] = perl
        CONFIG["php"] = php
        CONFIG["c"] = c
        CONFIG["cpp"] = cpp
        CONFIG["java"] = java
        # Set the Misc options.
        CONFIG["init_dir"] = init_dir
        CONFIG["def_encode"] = def_encode
        if prompt_encode == "yes":
            CONFIG["prompt_encode"] = True
        else:
            CONFIG["prompt_encode"] = False
        CONFIG["date"] = date_format
        CONFIG["time"] = time_format
        CONFIG["restore"] = restore_last
        CONFIG["check_modified"] = opt_chmod_var.get()
        CONFIG["save_winsize"] = opt_winsize_var.get()
        CONFIG["comment_cont"] = opt_comc_var.get()
        CONFIG["toolbar_type"] = opt_tbb_var.get()
        CONFIG["toolbar_compound"] = opt_tbi_var.get()
        CONFIG["email_server"] = opt_mail_ent.get()
        CONFIG["ftp_server"] = opt_ftp_ent.get()
        CONFIG["goto_negative"] = opt_goto_var.get()
        CONFIG["advanced_search"] = opt_advs_var.get()
        CONFIG["menu_bar"] = opt_mb_var.get()
        CONFIG["email_from"] = opt_msen_ent.get()
        CONFIG["email_to"] = opt_mrec_ent.get()
        CONFIG["browser_title"] = opt_fbt_var.get()
        CONFIG["browser_toolbar"] = opt_fbti_var.get()
        CONFIG["browser_menubar"] = opt_fbm_var.get()
        CONFIG["browser_sort"] = opt_fbs_var.get()
        CONFIG["browser_folders"] = opt_fbf_var.get()
        CONFIG["browser_btns"] = opt_fbtb_var.get()
        CONFIG["browser_compound"] = opt_fbti2_var.get()
        CONFIG["smart_home"] = opt_shome_var.get()
        CONFIG["menu_file"] = opt_menuf_var.get()
        CONFIG["menu_edit"] = opt_menue_var.get()
        CONFIG["menu_documents"] = opt_menud_var.get()
        CONFIG["menu_search"] = opt_menuse_var.get()
        CONFIG["menu_tools"] = opt_menut_var.get()
        CONFIG["menu_code"] = opt_menuc_var.get()
        CONFIG["menu_options"] = opt_menuo_var.get()
        CONFIG["menu_help"] = opt_menuh_var.get()
        CONFIG["menu_context"] = opt_menuco_var.get()
        CONFIG["font_size_change"] = opt_fontc_ent.get()
        CONFIG["toolbar_size"] = opt_tbis_var.get()
        CONFIG["auto_strip"] = opt_ast_var.get()
        CONFIG["browser_menu_file"] = opt_fbmf_var.get()
        CONFIG["browser_menu_folders"] = opt_fbmo_var.get()
        CONFIG["browser_menu_context"] = opt_fbmc_var.get()
        CONFIG["command_bar"] = opt_cmb_var.get()
        CONFIG["macro_command_bar"] = opt_maccb_var.get()
        CONFIG["macro_run_command"] = opt_macrc_var.get()
        CONFIG["macro_unknown_error"] = opt_macue_var.get()
        CONFIG["macro_stop_error"] = opt_macse_var.get()
        CONFIG["macro_python"] = opt_macps_var.get()
        CONFIG["macro_variables"] = opt_macav_var.get()
        CONFIG["macro_comment_start"] = opt_macco_ent.get()
        CONFIG["macro_variable_start"] = opt_macvs_ent.get()
        CONFIG["macro_python_start"] = opt_macpss_ent.get()
        CONFIG["menu_images"] = opt_menui_var.get()
        CONFIG["cut_copy_line"] = opt_ccl_var.get()
        CONFIG["save_curmode"] = opt_curmode_var.get()
        CONFIG["start_newline"] = opt_pref_ent.get()
        CONFIG["end_newline"] = opt_suff_ent.get()
        CONFIG["fast_scroll"] = opt_fsc_ent.get()
        CONFIG["search_history_order"] = opt_shis_var.get()
        CONFIG["find_history"] = opt_rfh_var.get()
        CONFIG["replace_history"] = opt_rrh_var.get()
        CONFIG["page_scroll"] = opt_psl_ent.get()
        CONFIG["smart_end"] = opt_send_var.get()
        CONFIG["duplicate_line"] = opt_dup_var.get()
        CONFIG["documents_list"] = opt_dl_var.get()
        CONFIG["documents_list_width"] = opt_dlw_ent.get()
        CONFIG["collab_server"] = opt_colse_ent.get()
        CONFIG["collab_port"] = opt_colpo_ent.get()
        CONFIG["auto_wrap"] = opt_awrap_var.get()
        CONFIG["auto_wrap_length"] = opt_awrapl_ent.get()
        CONFIG["run_code_args"] = opt_parg_var.get()
        CONFIG["highlight_line"] = opt_hline_var.get()
        CONFIG["highlight_color"]= opt_hlinec_ent.get()
        # Remember the current directory.
        file_dir = os.getcwd()
        # Switch to the pytextedit main directory.
        os.chdir(gbl_directory)
        try:
            # Open the file.
            config_file = open("resources/config/config", "w")
            # Create a copy of the dictionary.
            save_dict = CONFIG.copy()
            # Change values if needed.
            if save_dict["case_insensitive"] == True:
                save_dict["case_insensitive"] = "insensitive"
            else:
                save_dict["case_insensitive"] = "sensitive"
            if save_dict["regex"] == True:
                save_dict["regex"] = "yes"
            else:
                save_dict["regex"] = "no"
            if save_dict["prompt_encode"] == True:
                save_dict["prompt_encode"] = "yes"
            else:
                save_dict["prompt_encode"] = "no"
            # Create the config string.
            config_str = ""
            for i in save_dict:
                config_str += i + "=" + str(save_dict[i]) + "\n"
            if config_str.endswith("\n"):
                config_str = config_str[:-1]
            # Write to the config file.
            config_file.write(config_str)
            # Close the file.
            config_file.close()
        except IOError:
            showerror("Options", "Error saving config file.")
        # Switch back to the original directory.
        os.chdir(file_dir)
    def opt_save():
        """Saves the options."""
        # Save the options.
        opt_apply()
        # Close the window.
        opt_win.destroy()
    # Create the GUI.
    opt_win = Toplevel()
    opt_win.title("Options")
    opt_win.transient(root)
    opt_win.grab_set()
    opt_win.wm_resizable(0, 0)
    # Create the frame for the buttons and panels.
    opt_frm = Frame(opt_win)
    opt_frm.pack()
    opt_frm.focus()
    # Create the frame for the buttons.
    opt_btn_frm = Frame(opt_frm)
    opt_btn_frm.pack(side = LEFT, fill = Y)
    # Create the Font button.
    opt_font_btn = Button(opt_btn_frm, text = "Font", width = 10, height = 1, command = lambda: opt_switch("font"), relief = FLAT)
    opt_font_btn.pack(side = TOP)
    # Create the Interface button.
    opt_int_btn = Button(opt_btn_frm, text = "Interface", width = 10, height = 1, command = lambda: opt_switch("interface"))
    opt_int_btn.pack(side = TOP)
    # Create the Editing button.
    opt_edit_btn = Button(opt_btn_frm, text = "Editing", width = 10, height = 1, command = lambda: opt_switch("editing"))
    opt_edit_btn.pack(side = TOP)
    # Create the Searching button.
    opt_search_btn = Button(opt_btn_frm, text = "Searching", width = 10, height = 1, command = lambda: opt_switch("searching"))
    opt_search_btn.pack(side = TOP)
    # Create the Network button.
    opt_net_btn = Button(opt_btn_frm, text = "Network", width = 10, height = 1, command = lambda: opt_switch("network"))
    opt_net_btn.pack(side = TOP)
    # Create the File Browser button.
    opt_browse_btn = Button(opt_btn_frm, text = "File Browser", width = 10, height = 1, command = lambda: opt_switch("file browser"))
    opt_browse_btn.pack(side = TOP)
    # Create the Menus button.
    opt_menus_btn = Button(opt_btn_frm, text = "Menus", width = 10, height = 1, command = lambda: opt_switch("menus"))
    opt_menus_btn.pack(side = TOP)
    # Create the Macros button.
    opt_macro_btn = Button(opt_btn_frm, text = "Macros", width = 10, height = 1, command = lambda: opt_switch("macros"))
    opt_macro_btn.pack(side = TOP)
    # Create the Code button.
    opt_code_btn = Button(opt_btn_frm, text = "Code", width = 10, height = 1, command = lambda: opt_switch("code"))
    opt_code_btn.pack(side = TOP)
    # Create the Misc button.
    opt_misc_btn = Button(opt_btn_frm, text = "Misc", width = 10, height = 1, command = lambda: opt_switch("misc"))
    opt_misc_btn.pack(side = TOP)
    # Create the Font frame.
    opt_font_frm = Frame(opt_frm)
    opt_font_frm.pack(side = RIGHT, fill = BOTH)
    # Create the frame for entries, optionmenus, labels, and buttons.
    opt_font_ent_frm = Frame(opt_font_frm)
    opt_font_ent_frm.pack(side = TOP)
    # Create the font name label, entry, and button,
    opt_font_lbl = Label(opt_font_ent_frm, text = "Name:")
    opt_font_lbl.grid(row = 0, column = 0, sticky = W)
    opt_font_ent = Entry(opt_font_ent_frm)
    opt_font_ent.grid(row = 0, column = 1, sticky = W)
    opt_font2_btn = Button(opt_font_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the name of the font to use in the main text box."))
    opt_font2_btn.grid(row = 0, column = 2, sticky = W)
    # Create the font size label, entry, and button,
    opt_size_lbl = Label(opt_font_ent_frm, text = "Size:")
    opt_size_lbl.grid(row = 1, column = 0, sticky = W)
    opt_size_ent = Entry(opt_font_ent_frm)
    opt_size_ent.grid(row = 1, column = 1, sticky = W)
    opt_size_btn = Button(opt_font_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the size of the font to use in the main text box.\n\nThis must be a positive integer."))
    opt_size_btn.grid(row = 1, column = 2, sticky = W)
    # Create the font style label, entry, and button,
    opt_style_lbl = Label(opt_font_ent_frm, text = "Style:")
    opt_style_lbl.grid(row = 2, column = 0, sticky = W)
    opt_style_var = StringVar()
    opt_style_ent = OptionMenu(opt_font_ent_frm, opt_style_var, "normal", "bold", "italic", "underline", "bold italic", "underline italic", "underline bold", "underline bold italic")
    opt_style_ent.grid(row = 2, column = 1, sticky = W)
    opt_style_btn = Button(opt_font_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the style of the font to use in the main text box. "))
    opt_style_btn.grid(row = 2, column = 2, sticky = W)
    # Create the foreground label, entry, and button,
    opt_fg_lbl = Label(opt_font_ent_frm, text = "Foreground:")
    opt_fg_lbl.grid(row = 3, column = 0, sticky = W)
    opt_fg_ent = Entry(opt_font_ent_frm)
    opt_fg_ent.grid(row = 3, column = 1, sticky = W)
    opt_fg_btn = Button(opt_font_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the foreground (text) color to use in the main text box."))
    opt_fg_btn.grid(row = 3, column = 2, sticky = W)
    # Create the background label, entry, and button,
    opt_bg_lbl = Label(opt_font_ent_frm, text = "Background:")
    opt_bg_lbl.grid(row = 4, column = 0, sticky = W)
    opt_bg_ent = Entry(opt_font_ent_frm)
    opt_bg_ent.grid(row = 4, column = 1, sticky = W)
    opt_bg_btn = Button(opt_font_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the background color to use in the main text box."))
    opt_bg_btn.grid(row = 4, column = 2, sticky = W)
    # Create the selected foreground label, entry, and button,
    opt_sfg_lbl = Label(opt_font_ent_frm, text = "Sel. Foreground:")
    opt_sfg_lbl.grid(row = 5, column = 0, sticky = W)
    opt_sfg_ent = Entry(opt_font_ent_frm)
    opt_sfg_ent.grid(row = 5, column = 1, sticky = W)
    opt_sfg_btn = Button(opt_font_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the foreground (text) color to use when text is selected in the main text box."))
    opt_sfg_btn.grid(row = 5, column = 2, sticky = W)
    # Create the selected background label, entry, and button,
    opt_sbg_lbl = Label(opt_font_ent_frm, text = "Sel. Background:")
    opt_sbg_lbl.grid(row = 6, column = 0, sticky = W)
    opt_sbg_ent = Entry(opt_font_ent_frm)
    opt_sbg_ent.grid(row = 6, column = 1, sticky = W)
    opt_sbg_btn = Button(opt_font_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the background color to use when text is selected in the main text box."))
    opt_sbg_btn.grid(row = 6, column = 2, sticky = W)
    # Create the text wrap label, entry, and button,
    opt_wrap_lbl = Label(opt_font_ent_frm, text = "Text Wrap:")
    opt_wrap_lbl.grid(row = 7, column = 0, sticky = W)
    opt_wrap_var = StringVar()
    opt_wrap_ent = OptionMenu(opt_font_ent_frm, opt_wrap_var, "none", "word", "char")
    opt_wrap_ent.grid(row = 7, column = 1, sticky = W)
    opt_wrap_btn = Button(opt_font_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the text wrap to use in the main text box.\n\nText can wrap on the last character (char), on the last word (word), or not at all (none)."))
    opt_wrap_btn.grid(row = 7, column = 2, sticky = W)
    # Create the frame for the Save and Cancel buttons.
    opt_ent_btn_frm = Frame(opt_font_frm)
    opt_ent_btn_frm.pack(side = BOTTOM, fill = X)
    # Create the Cancel button.
    opt_cancel_btn = Button(opt_ent_btn_frm, text = "Cancel", width = 6, command = opt_win.destroy)
    opt_cancel_btn.pack(side = RIGHT)
    # Create the Apply button.
    opt_apply_btn = Button(opt_ent_btn_frm, text = "Apply", width = 6, command = opt_apply)
    opt_apply_btn.pack(side = RIGHT)
    # Create the Ok button.
    opt_save_btn = Button(opt_ent_btn_frm, text = "OK", width = 6, command = opt_save)
    opt_save_btn.pack(side = RIGHT)
    # Create the Interface frame.
    opt_int_frm = Frame(opt_frm)
    # Create the frame for entries, optionmenus, labels, and buttons.
    opt_int_ent_frm = Frame(opt_int_frm)
    opt_int_ent_frm.pack(side = TOP)
    # Create the UI foreground label, entry, and button,
    opt_uifg_lbl = Label(opt_int_ent_frm, text = "UI Foreground:")
    opt_uifg_lbl.grid(row = 0, column = 0, sticky = W)
    opt_uifg_ent = Entry(opt_int_ent_frm)
    opt_uifg_ent.grid(row = 0, column = 1, sticky = W)
    opt_uifg_btn = Button(opt_int_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the foreground (text) color to use in the interface.\n\nNote that this is different from the Foreground option in the Font tab."))
    opt_uifg_btn.grid(row = 0, column = 2, sticky = W)
    # Create the UI background label, entry, and button,
    opt_uibg_lbl = Label(opt_int_ent_frm, text = "UI Background:")
    opt_uibg_lbl.grid(row = 1, column = 0, sticky = W)
    opt_uibg_ent = Entry(opt_int_ent_frm)
    opt_uibg_ent.grid(row = 1, column = 1, sticky = W)
    opt_uibg_btn = Button(opt_int_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the background color to use in the interface.\n\nNote that this is different from the Background option in the Font tab."))
    opt_uibg_btn.grid(row = 1, column = 2, sticky = W)
    # Create the toolbar label, entry, and button,
    opt_tb_lbl = Label(opt_int_ent_frm, text = "Toolbar:")
    opt_tb_lbl.grid(row = 2, column = 0, sticky = W)
    opt_tb_var = StringVar()
    opt_tb_ent = OptionMenu(opt_int_ent_frm, opt_tb_var, "show", "hide")
    opt_tb_ent.grid(row = 2, column = 1, sticky = W)
    opt_tb_btn = Button(opt_int_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the toolbar should be displayed.\n\nThis requires a restart to take effect."))
    opt_tb_btn.grid(row = 2, column = 2, sticky = W)
    # Create the toolbar buttons, entry, and button,
    opt_tbb_lbl = Label(opt_int_ent_frm, text = "Toolbar Buttons:")
    opt_tbb_lbl.grid(row = 3, column = 0, sticky = W)
    opt_tbb_var = StringVar()
    opt_tbb_ent = OptionMenu(opt_int_ent_frm, opt_tbb_var, "text only", "images only", "text and images")
    opt_tbb_ent.grid(row = 3, column = 1, sticky = W)
    opt_tbb_btn = Button(opt_int_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the buttons on the toolbar should use text, images, or both.\n\nThis requires a restart to take effect."))
    opt_tbb_btn.grid(row = 3, column = 2, sticky = W)
    # Create the toolbar images, entry, and button,
    opt_tbi_lbl = Label(opt_int_ent_frm, text = "Toolbar Images:")
    opt_tbi_lbl.grid(row = 4, column = 0, sticky = W)
    opt_tbi_var = StringVar()
    opt_tbi_ent = OptionMenu(opt_int_ent_frm, opt_tbi_var, "top", "bottom", "right", "left")
    opt_tbi_ent.grid(row = 4, column = 1, sticky = W)
    opt_tbi_btn = Button(opt_int_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies where in relation to the text the images on the toolbar buttons should be shown. This is only relevant if the Toolbar Buttons option is set to both.\n\nThis requires a restart to take effect."))
    opt_tbi_btn.grid(row = 4, column = 2, sticky = W)
    # Create the toolbar image size entry, and button.
    opt_tbis_lbl = Label(opt_int_ent_frm, text = "Toolbar Image Size:")
    opt_tbis_lbl.grid(row = 5, column = 0, sticky = W)
    opt_tbis_var = StringVar()
    opt_tbis_ent = OptionMenu(opt_int_ent_frm, opt_tbis_var, "large", "small")
    opt_tbis_ent.grid(row = 5, column = 1, sticky = W)
    opt_tbis_btn = Button(opt_int_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the images on the toolbar buttons should be large or small.\n\nThis requires a restart to take effect."))
    opt_tbis_btn.grid(row = 5, column = 2, sticky = W)
    # Create the line numbers label, entry, and button,
    opt_ln_lbl = Label(opt_int_ent_frm, text = "Line Numbers:")
    opt_ln_lbl.grid(row = 6, column = 0, sticky = W)
    opt_ln_var = StringVar()
    opt_ln_ent = OptionMenu(opt_int_ent_frm, opt_ln_var, "show", "hide")
    opt_ln_ent.grid(row = 6, column = 1, sticky = W)
    opt_ln_btn = Button(opt_int_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the line number should be displayed.\n\nThis requires a restart to take effect."))
    opt_ln_btn.grid(row = 6, column = 2, sticky = W)
    # Create the status bar label, entry, and button,
    opt_sb_lbl = Label(opt_int_ent_frm, text = "Status Bar:")
    opt_sb_lbl.grid(row = 7, column = 0, sticky = W)
    opt_sb_var = StringVar()
    opt_sb_ent = OptionMenu(opt_int_ent_frm, opt_sb_var, "show", "hide")
    opt_sb_ent.grid(row = 7, column = 1, sticky = W)
    opt_sb_btn = Button(opt_int_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the status bar should be displayed.\n\nThis requires a restart to take effect."))
    opt_sb_btn.grid(row = 7, column = 2, sticky = W)
    # Create the status bar label, entry, and button,
    opt_cmb_lbl = Label(opt_int_ent_frm, text = "Command Bar:")
    opt_cmb_lbl.grid(row = 8, column = 0, sticky = W)
    opt_cmb_var = StringVar()
    opt_cmb_ent = OptionMenu(opt_int_ent_frm, opt_cmb_var, "show", "hide")
    opt_cmb_ent.grid(row = 8, column = 1, sticky = W)
    opt_cmb_btn = Button(opt_int_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the command bar should be displayed.\n\nThis requires a restart to take effect."))
    opt_cmb_btn.grid(row = 8, column = 2, sticky = W)
    # Create the toolbar label, entry, and button.
    opt_dl_lbl = Label(opt_int_ent_frm, text = "Documents List:")
    opt_dl_lbl.grid(row = 9, column = 0, sticky = W)
    opt_dl_var = StringVar()
    opt_dl_ent = OptionMenu(opt_int_ent_frm, opt_dl_var, "show", "hide")
    opt_dl_ent.grid(row = 9, column = 1, sticky = W)
    opt_dl_btn = Button(opt_int_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the documents list should be displayed.\n\nThis requires a restart to take effect."))
    opt_dl_btn.grid(row = 9, column = 2, sticky = W)
    # Create the UI background label, entry, and button.
    opt_dlw_lbl = Label(opt_int_ent_frm, text = "Documents List Width:")
    opt_dlw_lbl.grid(row = 10, column = 0, sticky = W)
    opt_dlw_ent = Entry(opt_int_ent_frm)
    opt_dlw_ent.grid(row = 10, column = 1, sticky = W)
    opt_dlw_btn = Button(opt_int_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the width (in characters) of the documents list.\n\nThis requires a restart to take effect."))
    opt_dlw_btn.grid(row = 10, column = 2, sticky = W)
    # Create the long/short filename label, entry, and button,
    opt_ft_lbl = Label(opt_int_ent_frm, text = "Title:")
    opt_ft_lbl.grid(row = 11, column = 0, sticky = W)
    opt_ft_var = StringVar()
    opt_ft_ent = OptionMenu(opt_int_ent_frm, opt_ft_var, "full filename", "short filename")
    opt_ft_ent.grid(row = 11, column = 1, sticky = W)
    opt_ft_btn = Button(opt_int_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the title should display the just the filename or the full path and filename."))
    opt_ft_btn.grid(row = 11, column = 2, sticky = W)
    # Create the long/short filename label, entry, and button.
    opt_hline_lbl = Label(opt_int_ent_frm, text = "Highlight Line:")
    opt_hline_lbl.grid(row = 12, column = 0, sticky = W)
    opt_hline_var = StringVar()
    opt_hline_ent = OptionMenu(opt_int_ent_frm, opt_hline_var, "yes", "no")
    opt_hline_ent.grid(row = 12, column = 1, sticky = W)
    opt_hline_btn = Button(opt_int_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the current line will be highlighted.\n\nThis requires a restart to take effect."))
    opt_hline_btn.grid(row = 12, column = 2, sticky = W)
    # Create the UI background label, entry, and button.
    opt_hlinec_lbl = Label(opt_int_ent_frm, text = "Highlight Line Color:")
    opt_hlinec_lbl.grid(row = 13, column = 0, sticky = W)
    opt_hlinec_ent = Entry(opt_int_ent_frm)
    opt_hlinec_ent.grid(row = 13, column = 1, sticky = W)
    opt_hlinec_btn = Button(opt_int_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the color used for highlighting the current line.\n\nThis requires a restart to take effect."))
    opt_hlinec_btn.grid(row = 13, column = 2, sticky = W)
    # Create the frame for the Save and Cancel buttons.
    opt_ent_btn_frm = Frame(opt_int_frm)
    opt_ent_btn_frm.pack(side = BOTTOM, fill = X)
    # Create the Cancel button.
    opt_cancel_btn = Button(opt_ent_btn_frm, text = "Cancel", width = 6, command = opt_win.destroy)
    opt_cancel_btn.pack(side = RIGHT)
    # Create the Apply button.
    opt_apply_btn = Button(opt_ent_btn_frm, text = "Apply", width = 6, command = opt_apply)
    opt_apply_btn.pack(side = RIGHT)
    # Create the OK button.
    opt_save_btn = Button(opt_ent_btn_frm, text = "OK", width = 6, command = opt_save)
    opt_save_btn.pack(side = RIGHT)
    # Create the Editing frame.
    opt_edit_frm = Frame(opt_frm)
    # Create the frame for entries, optionmenus, labels, and buttons.
    opt_edit_ent_frm = Frame(opt_edit_frm)
    opt_edit_ent_frm.pack(side = TOP)
    # Create the auto-indent label, entry, and button,
    opt_autoi_lbl = Label(opt_edit_ent_frm, text = "Auto-Indent:")
    opt_autoi_lbl.grid(row = 0, column = 0, sticky = W)
    opt_autoi_var = StringVar()
    opt_autoi_ent = OptionMenu(opt_edit_ent_frm, opt_autoi_var, "enabled", "disabled")
    opt_autoi_ent.grid(row = 0, column = 1, sticky = W)
    opt_autoi_btn = Button(opt_edit_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the next line will be automatically indented based on the indentation of the previous line."))
    opt_autoi_btn.grid(row = 0, column = 2, sticky = W)
    # Create the auto-replace tabs label, entry, and button,
    opt_replt_lbl = Label(opt_edit_ent_frm, text = "Replace Tabs:")
    opt_replt_lbl.grid(row = 1, column = 0, sticky = W)
    opt_replt_var = StringVar()
    opt_replt_ent = OptionMenu(opt_edit_ent_frm, opt_replt_var, "enabled", "disabled")
    opt_replt_ent.grid(row = 1, column = 1, sticky = W)
    opt_replt_btn = Button(opt_edit_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether tab characters will be automatically replaced with spaces."))
    opt_replt_btn.grid(row = 1, column = 2, sticky = W)
    # Create the indent label, entry, and button,
    opt_ina_lbl = Label(opt_edit_ent_frm, text = "Indent Amount:")
    opt_ina_lbl.grid(row = 2, column = 0, sticky = W)
    opt_ina_ent = Entry(opt_edit_ent_frm)
    opt_ina_ent.grid(row = 2, column = 1, sticky = W)
    opt_ina_btn = Button(opt_edit_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the indent amount.\n\nThis must be a positive integer."))
    opt_ina_btn.grid(row = 2, column = 2, sticky = W)
    # Create the spaces per tab label, entry, and button,
    opt_spt_lbl = Label(opt_edit_ent_frm, text = "Spaces Per Tab:")
    opt_spt_lbl.grid(row = 3, column = 0, sticky = W)
    opt_spt_ent = Entry(opt_edit_ent_frm)
    opt_spt_ent.grid(row = 3, column = 1, sticky = W)
    opt_spt_btn = Button(opt_edit_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies how many spaces are in a tab, for when automatically replacing tabs.\n\nThis must be a positive integer."))
    opt_spt_btn.grid(row = 3, column = 2, sticky = W)
    # Create the reverse separator label, entry, and button,
    opt_rsep_lbl = Label(opt_edit_ent_frm, text = "Reverse Separator:")
    opt_rsep_lbl.grid(row = 4, column = 0, sticky = W)
    opt_rsep_ent = Entry(opt_edit_ent_frm)
    opt_rsep_ent.grid(row = 4, column = 1, sticky = W)
    opt_rsep_btn = Button(opt_edit_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the separator used when reversing lines."))
    opt_rsep_btn.grid(row = 4, column = 2, sticky = W)
    # Create the join separator label, entry, and button,
    opt_jsep_lbl = Label(opt_edit_ent_frm, text = "Join Separator:")
    opt_jsep_lbl.grid(row = 5, column = 0, sticky = W)
    opt_jsep_ent = Entry(opt_edit_ent_frm)
    opt_jsep_ent.grid(row = 5, column = 1, sticky = W)
    opt_jsep_btn = Button(opt_edit_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the separator used when joining lines."))
    opt_jsep_btn.grid(row = 5, column = 2, sticky = W)
    # Create the "smart" home label, entry, and button,
    opt_shome_lbl = Label(opt_edit_ent_frm, text = "\"Smart\" Home:")
    opt_shome_lbl.grid(row = 6, column = 0, sticky = W)
    opt_shome_var = StringVar()
    opt_shome_ent = OptionMenu(opt_edit_ent_frm, opt_shome_var, "enabled", "disabled")
    opt_shome_ent.grid(row = 6, column = 1, sticky = W)
    opt_shome_btn = Button(opt_edit_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether \"smart\" home will be enabled. When enabled pressing the Home key will move to the first position after any indentation."))
    opt_shome_btn.grid(row = 6, column = 2, sticky = W)
    # Create the "smart" home label, entry, and button,
    opt_send_lbl = Label(opt_edit_ent_frm, text = "\"Smart\" End:")
    opt_send_lbl.grid(row = 7, column = 0, sticky = W)
    opt_send_var = StringVar()
    opt_send_ent = OptionMenu(opt_edit_ent_frm, opt_send_var, "enabled", "disabled")
    opt_send_ent.grid(row = 7, column = 1, sticky = W)
    opt_send_btn = Button(opt_edit_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether \"smart\" end will be enabled. When enabled pressing the End key will move to the last position before any indentation."))
    opt_send_btn.grid(row = 7, column = 2, sticky = W)
    # Create the auto-strip label, entry, and button.
    opt_ast_lbl = Label(opt_edit_ent_frm, text = "Auto-Strip:")
    opt_ast_lbl.grid(row = 8, column = 0, sticky = W)
    opt_ast_var = StringVar()
    opt_ast_ent = OptionMenu(opt_edit_ent_frm, opt_ast_var, "enabled", "disabled")
    opt_ast_ent.grid(row = 8, column = 1, sticky = W)
    opt_ast_btn = Button(opt_edit_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether extra whitespace at the end of a line will be automatically removed."))
    opt_ast_btn.grid(row = 8, column = 2, sticky = W)
    # Create the duplicate line label, entry, and button.
    opt_dup_lbl = Label(opt_edit_ent_frm, text = "Duplicate Line:")
    opt_dup_lbl.grid(row = 9, column = 0, sticky = W)
    opt_dup_var = StringVar()
    opt_dup_ent = OptionMenu(opt_edit_ent_frm, opt_dup_var, "above", "below")
    opt_dup_ent.grid(row = 9, column = 1, sticky = W)
    opt_dup_btn = Button(opt_edit_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether duplicated lines will be positioned above or below the current line."))
    opt_dup_btn.grid(row = 9, column = 2, sticky = W)
    # Create the prepend to line label, entry, and button.
    opt_pref_lbl = Label(opt_edit_ent_frm, text = "Prepend To Line:")
    opt_pref_lbl.grid(row = 10, column = 0, sticky = W)
    opt_pref_ent = Entry(opt_edit_ent_frm)
    opt_pref_ent.grid(row = 10, column = 1, sticky = W)
    opt_pref_btn = Button(opt_edit_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies a string to automatically prepend to the start of a line."))
    opt_pref_btn.grid(row = 10, column = 2, sticky = W)
    # Create the append to line label, entry, and button.
    opt_suff_lbl = Label(opt_edit_ent_frm, text = "Append To Line:")
    opt_suff_lbl.grid(row = 11, column = 0, sticky = W)
    opt_suff_ent = Entry(opt_edit_ent_frm)
    opt_suff_ent.grid(row = 11, column = 1, sticky = W)
    opt_suff_btn = Button(opt_edit_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies a string to automatically append to the end of a line."))
    opt_suff_btn.grid(row = 11, column = 2, sticky = W)
    # Create the auto-wrap label, entry, and button.
    opt_awrap_lbl = Label(opt_edit_ent_frm, text = "Auto-Wrap:")
    opt_awrap_lbl.grid(row = 12, column = 0, sticky = W)
    opt_awrap_var = StringVar()
    opt_awrap_ent = OptionMenu(opt_edit_ent_frm, opt_awrap_var, "enabled", "disabled")
    opt_awrap_ent.grid(row = 12, column = 1, sticky = W)
    opt_awrap_btn = Button(opt_edit_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether automatic line wrapping will be enabled."))
    opt_awrap_btn.grid(row = 12, column = 2, sticky = W)
    # Create the auto-wrap length label, entry, and button.
    opt_awrapl_lbl = Label(opt_edit_ent_frm, text = "Auto-Wrap Length:")
    opt_awrapl_lbl.grid(row = 13, column = 0, sticky = W)
    opt_awrapl_ent = Entry(opt_edit_ent_frm)
    opt_awrapl_ent.grid(row = 13, column = 1, sticky = W)
    opt_awrapl_btn = Button(opt_edit_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the length of lines necessary for them to automatically wrap."))
    opt_awrapl_btn.grid(row = 13, column = 2, sticky = W)
    # Create the frame for the Save and Cancel buttons.
    opt_ent_btn_frm = Frame(opt_edit_frm)
    opt_ent_btn_frm.pack(side = BOTTOM, fill = X)
    # Create the Cancel button.
    opt_cancel_btn = Button(opt_ent_btn_frm, text = "Cancel", width = 6, command = opt_win.destroy)
    opt_cancel_btn.pack(side = RIGHT)
    # Create the Apply button.
    opt_apply_btn = Button(opt_ent_btn_frm, text = "Apply", width = 6, command = opt_apply)
    opt_apply_btn.pack(side = RIGHT)
    # Create the OK button.
    opt_save_btn = Button(opt_ent_btn_frm, text = "OK", width = 6, command = opt_save)
    opt_save_btn.pack(side = RIGHT)
    # Create the Searching frame.
    opt_search_frm = Frame(opt_frm)
    # Create the frame for entries, optionmenus, labels, and buttons.
    opt_search_ent_frm = Frame(opt_search_frm)
    opt_search_ent_frm.pack(side = TOP)
    # Create the case sensitivity label, entry, and button,
    opt_cs_lbl = Label(opt_search_ent_frm, text = "Case Sensitivity:")
    opt_cs_lbl.grid(row = 0, column = 0, sticky = W)
    opt_cs_var = StringVar()
    opt_cs_ent = OptionMenu(opt_search_ent_frm, opt_cs_var, "sensitive", "insensitive")
    opt_cs_ent.grid(row = 0, column = 1, sticky = W)
    opt_cs_btn = Button(opt_search_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether searches are case sensitive by default."))
    opt_cs_btn.grid(row = 0, column = 2, sticky = W)
    # Create the regex label, entry, and button,
    opt_re_lbl = Label(opt_search_ent_frm, text = "Regex Search:")
    opt_re_lbl.grid(row = 1, column = 0, sticky = W)
    opt_re_var = StringVar()
    opt_re_ent = OptionMenu(opt_search_ent_frm, opt_re_var, "yes", "no")
    opt_re_ent.grid(row = 1, column = 1, sticky = W)
    opt_re_btn = Button(opt_search_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether searches use regular expressions by default."))
    opt_re_btn.grid(row = 1, column = 2, sticky = W)
    # Create the cursor pos label, entry, and button,
    opt_curp_lbl = Label(opt_search_ent_frm, text = "Cursor Position:")
    opt_curp_lbl.grid(row = 2, column = 0, sticky = W)
    opt_curp_var = StringVar()
    opt_curp_ent = OptionMenu(opt_search_ent_frm, opt_curp_var, "start", "end")
    opt_curp_ent.grid(row = 2, column = 1, sticky = W)
    opt_curp_btn = Button(opt_search_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the cursor will be positioned at the start or end of a string that has been found."))
    opt_curp_btn.grid(row = 2, column = 2, sticky = W)
    # Create the keep dialog open label, entry, and button,
    opt_kdlg_lbl = Label(opt_search_ent_frm, text = "Keep Dialog Open:")
    opt_kdlg_lbl.grid(row = 3, column = 0, sticky = W)
    opt_kdlg_var = StringVar()
    opt_kdlg_ent = OptionMenu(opt_search_ent_frm, opt_kdlg_var, "yes", "no")
    opt_kdlg_ent.grid(row = 3, column = 1, sticky = W)
    opt_kdlg_btn = Button(opt_search_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the dialog will be kept open after a search by default."))
    opt_kdlg_btn.grid(row = 3, column = 2, sticky = W)
    # Create the goto negative label, entry, and button,
    opt_goto_lbl = Label(opt_search_ent_frm, text = "Negative Lines in Goto:")
    opt_goto_lbl.grid(row = 4, column = 0, sticky = W)
    opt_goto_var = StringVar()
    opt_goto_ent = OptionMenu(opt_search_ent_frm, opt_goto_var, "from end", "from beginning", "ignore")
    opt_goto_ent.grid(row = 4, column = 1, sticky = W)
    opt_goto_btn = Button(opt_search_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies how negative lines in Goto will be treated. It can go that many lines from the end, from the beginning, or simply ignore negative values."))
    opt_goto_btn.grid(row = 4, column = 2, sticky = W)
    # Create the advanced search commands label, entry, and button,
    opt_advs_lbl = Label(opt_search_ent_frm, text = "Advanced Search Commands:")
    opt_advs_lbl.grid(row = 5, column = 0, sticky = W)
    opt_advs_var = StringVar()
    opt_advs_ent = OptionMenu(opt_search_ent_frm, opt_advs_var, "show", "hide")
    opt_advs_ent.grid(row = 5, column = 1, sticky = W)
    opt_advs_btn = Button(opt_search_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether more advanced commands in the Search menu will be shown.\n\nThis requires a restart to take effect."))
    opt_advs_btn.grid(row = 5, column = 2, sticky = W)
    # Create the advanced search commands label, entry, and button.
    opt_rfh_lbl = Label(opt_search_ent_frm, text = "Remember Find History:")
    opt_rfh_lbl.grid(row = 6, column = 0, sticky = W)
    opt_rfh_var = StringVar()
    opt_rfh_ent = OptionMenu(opt_search_ent_frm, opt_rfh_var, "yes", "no")
    opt_rfh_ent.grid(row = 6, column = 1, sticky = W)
    opt_rfh_btn = Button(opt_search_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether Find will remember the history."))
    opt_rfh_btn.grid(row = 6, column = 2, sticky = W)
    # Create the advanced search commands label, entry, and button.
    opt_rrh_lbl = Label(opt_search_ent_frm, text = "Remember Replace History:")
    opt_rrh_lbl.grid(row = 7, column = 0, sticky = W)
    opt_rrh_var = StringVar()
    opt_rrh_ent = OptionMenu(opt_search_ent_frm, opt_rrh_var, "yes", "no")
    opt_rrh_ent.grid(row = 7, column = 1, sticky = W)
    opt_rrh_btn = Button(opt_search_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether Replace will remember the history."))
    opt_rrh_btn.grid(row = 7, column = 2, sticky = W)
    # Create the advanced search commands label, entry, and button.
    opt_shis_lbl = Label(opt_search_ent_frm, text = "Search History Order:")
    opt_shis_lbl.grid(row = 8, column = 0, sticky = W)
    opt_shis_var = StringVar()
    opt_shis_ent = OptionMenu(opt_search_ent_frm, opt_shis_var, "oldest first", "oldest last")
    opt_shis_ent.grid(row = 8, column = 1, sticky = W)
    opt_shis_btn = Button(opt_search_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the Find and Replace history will be shown oldest first or last."))
    opt_shis_btn.grid(row = 8, column = 2, sticky = W)
    # Create the frame for the Save and Cancel buttons.
    opt_ent_btn_frm = Frame(opt_search_frm)
    opt_ent_btn_frm.pack(side = BOTTOM, fill = X)
    # Create the Cancel button.
    opt_cancel_btn = Button(opt_ent_btn_frm, text = "Cancel", width = 6, command = opt_win.destroy)
    opt_cancel_btn.pack(side = RIGHT)
    # Create the Apply button.
    opt_apply_btn = Button(opt_ent_btn_frm, text = "Apply", width = 6, command = opt_apply)
    opt_apply_btn.pack(side = RIGHT)
    # Create the OK button.
    opt_save_btn = Button(opt_ent_btn_frm, text = "OK", width = 6, command = opt_save)
    opt_save_btn.pack(side = RIGHT)
    # Create the Network frame.
    opt_net_frm = Frame(opt_frm)
    # Create the frame for entries, optionmenus, labels, and buttons.
    opt_net_ent_frm = Frame(opt_net_frm)
    opt_net_ent_frm.pack(side = TOP)
    # Create the email server label, entry, and button,
    opt_mail_lbl = Label(opt_net_ent_frm, text = "Email Server:")
    opt_mail_lbl.grid(row = 0, column = 0, sticky = W)
    opt_mail_ent = Entry(opt_net_ent_frm)
    opt_mail_ent.grid(row = 0, column = 1, sticky = W)
    opt_mail_btn = Button(opt_net_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the default email server."))
    opt_mail_btn.grid(row = 0, column = 2, sticky = W)
    # Create the email server label, entry, and button,
    opt_msen_lbl = Label(opt_net_ent_frm, text = "Email Sender:")
    opt_msen_lbl.grid(row = 1, column = 0, sticky = W)
    opt_msen_ent = Entry(opt_net_ent_frm)
    opt_msen_ent.grid(row = 1, column = 1, sticky = W)
    opt_msen_btn = Button(opt_net_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the default email sender."))
    opt_msen_btn.grid(row = 1, column = 2, sticky = W)
    # Create the email server label, entry, and button,
    opt_mrec_lbl = Label(opt_net_ent_frm, text = "Email Recipient:")
    opt_mrec_lbl.grid(row = 2, column = 0, sticky = W)
    opt_mrec_ent = Entry(opt_net_ent_frm)
    opt_mrec_ent.grid(row = 2, column = 1, sticky = W)
    opt_mrec_btn = Button(opt_net_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the default email recipient."))
    opt_mrec_btn.grid(row = 2, column = 2, sticky = W)
    # Create the FTP server label, entry, and button,
    opt_ftp_lbl = Label(opt_net_ent_frm, text = "FTP Server:")
    opt_ftp_lbl.grid(row = 3, column = 0, sticky = W)
    opt_ftp_ent = Entry(opt_net_ent_frm)
    opt_ftp_ent.grid(row = 3, column = 1, sticky = W)
    opt_ftp_btn = Button(opt_net_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the default FTP server."))
    opt_ftp_btn.grid(row = 3, column = 2, sticky = W)
    # Create the FTP server label, entry, and button,
    opt_colse_lbl = Label(opt_net_ent_frm, text = "Collab. Editing Server:")
    opt_colse_lbl.grid(row = 4, column = 0, sticky = W)
    opt_colse_ent = Entry(opt_net_ent_frm)
    opt_colse_ent.grid(row = 4, column = 1, sticky = W)
    opt_colse_btn = Button(opt_net_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the default collaborative editing server."))
    opt_colse_btn.grid(row = 4, column = 2, sticky = W)
    # Create the FTP server label, entry, and button,
    opt_colpo_lbl = Label(opt_net_ent_frm, text = "Collab. Editing Port:")
    opt_colpo_lbl.grid(row = 5, column = 0, sticky = W)
    opt_colpo_ent = Entry(opt_net_ent_frm)
    opt_colpo_ent.grid(row = 5, column = 1, sticky = W)
    opt_colpo_btn = Button(opt_net_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the default collaborative editing port."))
    opt_colpo_btn.grid(row = 5, column = 2, sticky = W)
    # Create the frame for the Save and Cancel buttons.
    opt_ent_btn_frm = Frame(opt_net_frm)
    opt_ent_btn_frm.pack(side = BOTTOM, fill = X)
    # Create the Cancel button.
    opt_cancel_btn = Button(opt_ent_btn_frm, text = "Cancel", width = 6, command = opt_win.destroy)
    opt_cancel_btn.pack(side = RIGHT)
    # Create the Apply button.
    opt_apply_btn = Button(opt_ent_btn_frm, text = "Apply", width = 6, command = opt_apply)
    opt_apply_btn.pack(side = RIGHT)
    # Create the OK button.
    opt_save_btn = Button(opt_ent_btn_frm, text = "OK", width = 6, command = opt_save)
    opt_save_btn.pack(side = RIGHT)
    # Create the File Browser frame.
    opt_browse_frm = Frame(opt_frm)
    # Create the frame for entries, optionmenus, labels, and buttons.
    opt_browse_ent_frm = Frame(opt_browse_frm)
    opt_browse_ent_frm.pack(side = TOP)
    # Create the file browser title label, entry, and button,
    opt_fbt_lbl = Label(opt_browse_ent_frm, text = "Title:")
    opt_fbt_lbl.grid(row = 0, column = 0, sticky = W)
    opt_fbt_var = StringVar()
    opt_fbt_ent = OptionMenu(opt_browse_ent_frm, opt_fbt_var, "current directory", "command name")
    opt_fbt_ent.grid(row = 0, column = 1, sticky = W)
    opt_fbt_btn = Button(opt_browse_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the title will display the current directory or simply \"File Browser\"."))
    opt_fbt_btn.grid(row = 0, column = 2, sticky = W)
    # Create the file browser toolbar label, entry, and button,
    opt_fbti_lbl = Label(opt_browse_ent_frm, text = "Toolbar:")
    opt_fbti_lbl.grid(row = 1, column = 0, sticky = W)
    opt_fbti_var = StringVar()
    opt_fbti_ent = OptionMenu(opt_browse_ent_frm, opt_fbti_var, "show", "hide")
    opt_fbti_ent.grid(row = 1, column = 1, sticky = W)
    opt_fbti_btn = Button(opt_browse_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the toolbar will be displayed."))
    opt_fbti_btn.grid(row = 1, column = 2, sticky = W)
    # Create the file browser toolbar buttons label, entry, and button,
    opt_fbtb_lbl = Label(opt_browse_ent_frm, text = "Toolbar Buttons:")
    opt_fbtb_lbl.grid(row = 2, column = 0, sticky = W)
    opt_fbtb_var = StringVar()
    opt_fbtb_ent = OptionMenu(opt_browse_ent_frm, opt_fbtb_var, "text only", "images only", "text and images")
    opt_fbtb_ent.grid(row = 2, column = 1, sticky = W)
    opt_fbtb_btn = Button(opt_browse_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the buttons on the toolbar should use text, images, or both."))
    opt_fbtb_btn.grid(row = 2, column = 2, sticky = W)
    # Create the file browser toolbar buttons label, entry, and button,
    opt_fbti2_lbl = Label(opt_browse_ent_frm, text = "Toolbar Images:")
    opt_fbti2_lbl.grid(row = 3, column = 0, sticky = W)
    opt_fbti2_var = StringVar()
    opt_fbti2_ent = OptionMenu(opt_browse_ent_frm, opt_fbti2_var, "top", "bottom", "right", "left")
    opt_fbti2_ent.grid(row = 3, column = 1, sticky = W)
    opt_fbti2_btn = Button(opt_browse_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies where in relation to the text the images on the toolbar buttons should be shown.\n\nThis is only relevant if the Toolbar Buttons option is set to both."))
    opt_fbti2_btn.grid(row = 3, column = 2, sticky = W)
    # Create the file browser menu bar label, entry, and button.
    opt_fbm_lbl = Label(opt_browse_ent_frm, text = "Menu Bar:")
    opt_fbm_lbl.grid(row = 4, column = 0, sticky = W)
    opt_fbm_var = StringVar()
    opt_fbm_ent = OptionMenu(opt_browse_ent_frm, opt_fbm_var, "show", "hide")
    opt_fbm_ent.grid(row = 4, column = 1, sticky = W)
    opt_fbm_btn = Button(opt_browse_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the menu bar will be displayed."))
    opt_fbm_btn.grid(row = 4, column = 2, sticky = W)
    # Create the file browser file menu label, entry, and button.
    opt_fbmf_lbl = Label(opt_browse_ent_frm, text = "File Menu:")
    opt_fbmf_lbl.grid(row = 5, column = 0, sticky = W)
    opt_fbmf_var = StringVar()
    opt_fbmf_ent = OptionMenu(opt_browse_ent_frm, opt_fbmf_var, "show", "hide")
    opt_fbmf_ent.grid(row = 5, column = 1, sticky = W)
    opt_fbmf_btn = Button(opt_browse_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the File menu will be displayed."))
    opt_fbmf_btn.grid(row = 5, column = 2, sticky = W)
    # Create the file browser folders menu label, entry, and button.
    opt_fbmo_lbl = Label(opt_browse_ent_frm, text = "Folders Menu:")
    opt_fbmo_lbl.grid(row = 6, column = 0, sticky = W)
    opt_fbmo_var = StringVar()
    opt_fbmo_ent = OptionMenu(opt_browse_ent_frm, opt_fbmo_var, "show", "hide")
    opt_fbmo_ent.grid(row = 6, column = 1, sticky = W)
    opt_fbmo_btn = Button(opt_browse_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the Folders menu will be displayed."))
    opt_fbmo_btn.grid(row = 6, column = 2, sticky = W)
    # Create the file browser context menu label, entry, and button.
    opt_fbmc_lbl = Label(opt_browse_ent_frm, text = "Context Menu:")
    opt_fbmc_lbl.grid(row = 7, column = 0, sticky = W)
    opt_fbmc_var = StringVar()
    opt_fbmc_ent = OptionMenu(opt_browse_ent_frm, opt_fbmc_var, "show", "hide")
    opt_fbmc_ent.grid(row = 7, column = 1, sticky = W)
    opt_fbmc_btn = Button(opt_browse_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the context menu will be displayed."))
    opt_fbmc_btn.grid(row = 7, column = 2, sticky = W)
    # Create the file browser sort label, entry, and button,
    opt_fbs_lbl = Label(opt_browse_ent_frm, text = "Sort Alphabetically:")
    opt_fbs_lbl.grid(row = 8, column = 0, sticky = W)
    opt_fbs_var = StringVar()
    opt_fbs_ent = OptionMenu(opt_browse_ent_frm, opt_fbs_var, "yes", "no")
    opt_fbs_ent.grid(row = 8, column = 1, sticky = W)
    opt_fbs_btn = Button(opt_browse_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the files and folders should be sorted alphabetically."))
    opt_fbs_btn.grid(row = 8, column = 2, sticky = W)
    # Create the file browser sort label, entry, and button,
    opt_fbf_lbl = Label(opt_browse_ent_frm, text = "Folder Position:")
    opt_fbf_lbl.grid(row = 9, column = 0, sticky = W)
    opt_fbf_var = StringVar()
    opt_fbf_ent = OptionMenu(opt_browse_ent_frm, opt_fbf_var, "folders above", "folders below")
    opt_fbf_ent.grid(row = 9, column = 1, sticky = W)
    opt_fbf_btn = Button(opt_browse_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the folders should be displayed above or below the files."))
    opt_fbf_btn.grid(row = 9, column = 2, sticky = W)
    # Create the frame for the Save and Cancel buttons.
    opt_ent_btn_frm = Frame(opt_browse_frm)
    opt_ent_btn_frm.pack(side = BOTTOM, fill = X)
    # Create the Cancel button.
    opt_cancel_btn = Button(opt_ent_btn_frm, text = "Cancel", width = 6, command = opt_win.destroy)
    opt_cancel_btn.pack(side = RIGHT)
    # Create the Apply button.
    opt_apply_btn = Button(opt_ent_btn_frm, text = "Apply", width = 6, command = opt_apply)
    opt_apply_btn.pack(side = RIGHT)
    # Create the OK button.
    opt_save_btn = Button(opt_ent_btn_frm, text = "OK", width = 6, command = opt_save)
    opt_save_btn.pack(side = RIGHT)
    # Create the Menus frame.
    opt_menu_frm = Frame(opt_frm)
    # Create the frame for entries, optionmenus, labels, and buttons.
    opt_menu_ent_frm = Frame(opt_menu_frm)
    opt_menu_ent_frm.pack(side = TOP)
    # Create the menu bar label, entry, and button.
    opt_mb_lbl = Label(opt_menu_ent_frm, text = "Menu Bar:")
    opt_mb_lbl.grid(row = 0, column = 0, sticky = W)
    opt_mb_var = StringVar()
    opt_mb_ent = OptionMenu(opt_menu_ent_frm, opt_mb_var, "show", "hide")
    opt_mb_ent.grid(row = 0, column = 1, sticky = W)
    opt_mb_btn = Button(opt_menu_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the menu bar will be shown.\n\nThis requires a restart to take effect."))
    opt_mb_btn.grid(row = 0, column = 2, sticky = W)
    # Create the menu tearoff label, entry, and button.
    opt_menu_lbl = Label(opt_menu_ent_frm, text = "Tear-off Menus:")
    opt_menu_lbl.grid(row = 1, column = 0, sticky = W)
    opt_menu_var = StringVar()
    opt_menu_ent = OptionMenu(opt_menu_ent_frm, opt_menu_var, "enabled", "disabled")
    opt_menu_ent.grid(row = 1, column = 1, sticky = W)
    opt_menu_btn = Button(opt_menu_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether tear-off menus will be enabled. If enabled, menus can be \"torn\" off from the main application and become separate windows.\n\nThis requires a restart to take effect."))
    opt_menu_btn.grid(row = 1, column = 2, sticky = W)
    # Create the menu icons label, entry, and button.
    opt_menui_lbl = Label(opt_menu_ent_frm, text = "Menu Icons:")
    opt_menui_lbl.grid(row = 2, column = 0, sticky = W)
    opt_menui_var = StringVar()
    opt_menui_ent = OptionMenu(opt_menu_ent_frm, opt_menui_var, "show", "hide")
    opt_menui_ent.grid(row = 2, column = 1, sticky = W)
    opt_menui_btn = Button(opt_menu_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether icons will be shown in the menus.\n\nThis requires a restart to take effect."))
    opt_menui_btn.grid(row = 2, column = 2, sticky = W)
    # Create the file menu label, entry, and button.
    opt_menuf_lbl = Label(opt_menu_ent_frm, text = "File Menu:")
    opt_menuf_lbl.grid(row = 3, column = 0, sticky = W)
    opt_menuf_var = StringVar()
    opt_menuf_ent = OptionMenu(opt_menu_ent_frm, opt_menuf_var, "show", "hide")
    opt_menuf_ent.grid(row = 3, column = 1, sticky = W)
    opt_menuf_btn = Button(opt_menu_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the File menu will be displayed.\n\nThis requires a restart to take effect."))
    opt_menuf_btn.grid(row = 3, column = 2, sticky = W)
    # Create the edit menu label, entry, and button.
    opt_menue_lbl = Label(opt_menu_ent_frm, text = "Edit Menu:")
    opt_menue_lbl.grid(row = 4, column = 0, sticky = W)
    opt_menue_var = StringVar()
    opt_menue_ent = OptionMenu(opt_menu_ent_frm, opt_menue_var, "show", "hide")
    opt_menue_ent.grid(row = 4, column = 1, sticky = W)
    opt_menue_btn = Button(opt_menu_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the Edit menu will be displayed.\n\nThis requires a restart to take effect."))
    opt_menue_btn.grid(row = 4, column = 2, sticky = W)
    # Create the documents menu label, entry, and button.
    opt_menud_lbl = Label(opt_menu_ent_frm, text = "Documents Menu:")
    opt_menud_lbl.grid(row = 5, column = 0, sticky = W)
    opt_menud_var = StringVar()
    opt_menud_ent = OptionMenu(opt_menu_ent_frm, opt_menud_var, "show", "hide")
    opt_menud_ent.grid(row = 5, column = 1, sticky = W)
    opt_menud_btn = Button(opt_menu_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the Documents menu will be displayed.\n\nThis requires a restart to take effect."))
    opt_menud_btn.grid(row = 5, column = 2, sticky = W)
    # Create the search menu label, entry, and button,
    opt_menuse_lbl = Label(opt_menu_ent_frm, text = "Search Menu:")
    opt_menuse_lbl.grid(row = 6, column = 0, sticky = W)
    opt_menuse_var = StringVar()
    opt_menuse_ent = OptionMenu(opt_menu_ent_frm, opt_menuse_var, "show", "hide")
    opt_menuse_ent.grid(row = 6, column = 1, sticky = W)
    opt_menuse_btn = Button(opt_menu_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the Search menu will be displayed.\n\nThis requires a restart to take effect."))
    opt_menuse_btn.grid(row = 6, column = 2, sticky = W)
    # Create the tools menu label, entry, and button.
    opt_menut_lbl = Label(opt_menu_ent_frm, text = "Tools Menu:")
    opt_menut_lbl.grid(row = 7, column = 0, sticky = W)
    opt_menut_var = StringVar()
    opt_menut_ent = OptionMenu(opt_menu_ent_frm, opt_menut_var, "show", "hide")
    opt_menut_ent.grid(row = 7, column = 1, sticky = W)
    opt_menut_btn = Button(opt_menu_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the Tools menu will be displayed.\n\nThis requires a restart to take effect."))
    opt_menut_btn.grid(row = 7, column = 2, sticky = W)
    # Create the code menu label, entry, and button,
    opt_menuc_lbl = Label(opt_menu_ent_frm, text = "Code Menu:")
    opt_menuc_lbl.grid(row = 8, column = 0, sticky = W)
    opt_menuc_var = StringVar()
    opt_menuc_ent = OptionMenu(opt_menu_ent_frm, opt_menuc_var, "show", "hide")
    opt_menuc_ent.grid(row = 8, column = 1, sticky = W)
    opt_menuc_btn = Button(opt_menu_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the Code menu will be displayed.\n\nThis requires a restart to take effect."))
    opt_menuc_btn.grid(row = 8, column = 2, sticky = W)
    # Create the options menu label, entry, and button.
    opt_menuo_lbl = Label(opt_menu_ent_frm, text = "Options Menu:")
    opt_menuo_lbl.grid(row = 9, column = 0, sticky = W)
    opt_menuo_var = StringVar()
    opt_menuo_ent = OptionMenu(opt_menu_ent_frm, opt_menuo_var, "show", "hide")
    opt_menuo_ent.grid(row = 9, column = 1, sticky = W)
    opt_menuo_btn = Button(opt_menu_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the Options menu will be displayed.\n\nThis requires a restart to take effect."))
    opt_menuo_btn.grid(row = 9, column = 2, sticky = W)
    # Create the help menu label, entry, and button.
    opt_menuh_lbl = Label(opt_menu_ent_frm, text = "Help Menu:")
    opt_menuh_lbl.grid(row = 10, column = 0, sticky = W)
    opt_menuh_var = StringVar()
    opt_menuh_ent = OptionMenu(opt_menu_ent_frm, opt_menuh_var, "show", "hide")
    opt_menuh_ent.grid(row = 10, column = 1, sticky = W)
    opt_menuh_btn = Button(opt_menu_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the Help menu will be displayed.\n\nThis requires a restart to take effect."))
    opt_menuh_btn.grid(row = 10, column = 2, sticky = W)
    # Create the context menu label, entry, and button.
    opt_menuco_lbl = Label(opt_menu_ent_frm, text = "Context Menu:")
    opt_menuco_lbl.grid(row = 11, column = 0, sticky = W)
    opt_menuco_var = StringVar()
    opt_menuco_ent = OptionMenu(opt_menu_ent_frm, opt_menuco_var, "show", "hide")
    opt_menuco_ent.grid(row = 11, column = 1, sticky = W)
    opt_menuco_btn = Button(opt_menu_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the context menu will be displayed.\n\nThis requires a restart to take effect."))
    opt_menuco_btn.grid(row = 11, column = 2, sticky = W)
    # Create the frame for the Save and Cancel buttons.
    opt_ent_btn_frm = Frame(opt_menu_frm)
    opt_ent_btn_frm.pack(side = BOTTOM, fill = X)
    # Create the Cancel button.
    opt_cancel_btn = Button(opt_ent_btn_frm, text = "Cancel", width = 6, command = opt_win.destroy)
    opt_cancel_btn.pack(side = RIGHT)
    # Create the Apply button.
    opt_apply_btn = Button(opt_ent_btn_frm, text = "Apply", width = 6, command = opt_apply)
    opt_apply_btn.pack(side = RIGHT)
    # Create the OK button.
    opt_save_btn = Button(opt_ent_btn_frm, text = "OK", width = 6, command = opt_save)
    opt_save_btn.pack(side = RIGHT)
    # Create the Macros frame.
    opt_macro_frm = Frame(opt_frm)
    # Create the frame for entries, optionmenus, labels, and buttons.
    opt_macro_ent_frm = Frame(opt_macro_frm)
    opt_macro_ent_frm.pack(side = TOP)
    # Create the command bar label, entry, and button.
    opt_maccb_lbl = Label(opt_macro_ent_frm, text = "Command Bar:")
    opt_maccb_lbl.grid(row = 0, column = 0, sticky = W)
    opt_maccb_var = StringVar()
    opt_maccb_ent = OptionMenu(opt_macro_ent_frm, opt_maccb_var, "macro commands", "python statements")
    opt_maccb_ent.grid(row = 0, column = 1, sticky = W)
    opt_maccb_btn = Button(opt_macro_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the command bar will run macro commands or Python statements."))
    opt_maccb_btn.grid(row = 0, column = 2, sticky = W)
    # Create the run command label, entry, and button.
    opt_macrc_lbl = Label(opt_macro_ent_frm, text = "Run Command:")
    opt_macrc_lbl.grid(row = 1, column = 0, sticky = W)
    opt_macrc_var = StringVar()
    opt_macrc_ent = OptionMenu(opt_macro_ent_frm, opt_macrc_var, "macro commands", "python statements")
    opt_macrc_ent.grid(row = 1, column = 1, sticky = W)
    opt_macrc_btn = Button(opt_macro_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether \"Run Command\" will run macro commands or Python statements."))
    opt_macrc_btn.grid(row = 1, column = 2, sticky = W)
    # Create the error on unknown commands label, entry, and button.
    opt_macue_lbl = Label(opt_macro_ent_frm, text = "Error on Unknown Commands:")
    opt_macue_lbl.grid(row = 2, column = 0, sticky = W)
    opt_macue_var = StringVar()
    opt_macue_ent = OptionMenu(opt_macro_ent_frm, opt_macue_var, "yes", "no")
    opt_macue_ent.grid(row = 2, column = 1, sticky = W)
    opt_macue_btn = Button(opt_macro_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether unknown commands will cause errors or fail silently."))
    opt_macue_btn.grid(row = 2, column = 2, sticky = W)
    # Create the stop on error label, entry, and button.
    opt_macse_lbl = Label(opt_macro_ent_frm, text = "Stop on Error:")
    opt_macse_lbl.grid(row = 3, column = 0, sticky = W)
    opt_macse_var = StringVar()
    opt_macse_ent = OptionMenu(opt_macro_ent_frm, opt_macse_var, "yes", "no")
    opt_macse_ent.grid(row = 3, column = 1, sticky = W)
    opt_macse_btn = Button(opt_macro_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether execution of a macro will stop when an error occurs."))
    opt_macse_btn.grid(row = 3, column = 2, sticky = W)
    # Create the allow python code label, entry, and button.
    opt_macps_lbl = Label(opt_macro_ent_frm, text = "Allow Python Statements:")
    opt_macps_lbl.grid(row = 4, column = 0, sticky = W)
    opt_macps_var = StringVar()
    opt_macps_ent = OptionMenu(opt_macro_ent_frm, opt_macps_var, "yes", "no")
    opt_macps_ent.grid(row = 4, column = 1, sticky = W)
    opt_macps_btn = Button(opt_macro_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether Python statements are allowed in a macro."))
    opt_macps_btn.grid(row = 4, column = 2, sticky = W)
    # Create the allow variables label, entry, and button.
    opt_macav_lbl = Label(opt_macro_ent_frm, text = "Allow Variables:")
    opt_macav_lbl.grid(row = 5, column = 0, sticky = W)
    opt_macav_var = StringVar()
    opt_macav_ent = OptionMenu(opt_macro_ent_frm, opt_macav_var, "yes", "no")
    opt_macav_ent.grid(row = 5, column = 1, sticky = W)
    opt_macav_btn = Button(opt_macro_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether variables are allowed in a macro."))
    opt_macav_btn.grid(row = 5, column = 2, sticky = W)
    # Create the comment start label, entry, and button,
    opt_macco_lbl = Label(opt_macro_ent_frm, text = "Comment Start:")
    opt_macco_lbl.grid(row = 6, column = 0, sticky = W)
    opt_macco_ent = Entry(opt_macro_ent_frm)
    opt_macco_ent.grid(row = 6, column = 1, sticky = W)
    opt_macco_btn = Button(opt_macro_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the string used to start a comment. It is not recommended to change this."))
    opt_macco_btn.grid(row = 6, column = 2, sticky = W)
    # Create the variable start label, entry, and button,
    opt_macvs_lbl = Label(opt_macro_ent_frm, text = "Variable Start:")
    opt_macvs_lbl.grid(row = 7, column = 0, sticky = W)
    opt_macvs_ent = Entry(opt_macro_ent_frm)
    opt_macvs_ent.grid(row = 7, column = 1, sticky = W)
    opt_macvs_btn = Button(opt_macro_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the string used to start a variable. It is not recommended to change this.\n\nNote that this must be a single character."))
    opt_macvs_btn.grid(row = 7, column = 2, sticky = W)
    # Create the python statement start label, entry, and button,
    opt_macpss_lbl = Label(opt_macro_ent_frm, text = "Python Statement Start:")
    opt_macpss_lbl.grid(row = 8, column = 0, sticky = W)
    opt_macpss_ent = Entry(opt_macro_ent_frm)
    opt_macpss_ent.grid(row = 8, column = 1, sticky = W)
    opt_macpss_btn = Button(opt_macro_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the string used to start a Python statement. It is not recommended to change this."))
    opt_macpss_btn.grid(row = 8, column = 2, sticky = W)
    # Create the frame for the Save and Cancel buttons.
    opt_ent_btn_frm = Frame(opt_macro_frm)
    opt_ent_btn_frm.pack(side = BOTTOM, fill = X)
    # Create the Cancel button.
    opt_cancel_btn = Button(opt_ent_btn_frm, text = "Cancel", width = 6, command = opt_win.destroy)
    opt_cancel_btn.pack(side = RIGHT)
    # Create the Apply button.
    opt_apply_btn = Button(opt_ent_btn_frm, text = "Apply", width = 6, command = opt_apply)
    opt_apply_btn.pack(side = RIGHT)
    # Create the OK button.
    opt_save_btn = Button(opt_ent_btn_frm, text = "OK", width = 6, command = opt_save)
    opt_save_btn.pack(side = RIGHT)
    # Create the Code frame.
    opt_code_frm = Frame(opt_frm)
    # Create the frame for entries, optionmenus, labels, and buttons.
    opt_code_ent_frm = Frame(opt_code_frm)
    opt_code_ent_frm.pack(side = TOP)
    # # Create the Python label, entry, and button,
    opt_py_lbl = Label(opt_code_ent_frm, text = "Python Interpreter:")
    opt_py_lbl.grid(row = 0, column = 0, sticky = W)
    opt_py_ent = Entry(opt_code_ent_frm)
    opt_py_ent.grid(row = 0, column = 1, sticky = W)
    opt_py_btn = Button(opt_code_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the command used for running Python code."))
    opt_py_btn.grid(row = 0, column = 2, sticky = W)
    # Create the Perl label, entry, and button,
    opt_pl_lbl = Label(opt_code_ent_frm, text = "Perl Interpreter:")
    opt_pl_lbl.grid(row = 1, column = 0, sticky = W)
    opt_pl_ent = Entry(opt_code_ent_frm)
    opt_pl_ent.grid(row = 1, column = 1, sticky = W)
    opt_pl_btn = Button(opt_code_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the command used for running Perl code."))
    opt_pl_btn.grid(row = 1, column = 2, sticky = W)
    # Create the PHP label, entry, and button,
    opt_php_lbl = Label(opt_code_ent_frm, text = "PHP Interpreter:")
    opt_php_lbl.grid(row = 2, column = 0, sticky = W)
    opt_php_ent = Entry(opt_code_ent_frm)
    opt_php_ent.grid(row = 2, column = 1, sticky = W)
    opt_php_btn = Button(opt_code_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the command used for running PHP code."))
    opt_php_btn.grid(row = 2, column = 2, sticky = W)
    # Create the C label, entry, and button,
    opt_c_lbl = Label(opt_code_ent_frm, text = "C Compiler:")
    opt_c_lbl.grid(row = 3, column = 0, sticky = W)
    opt_c_ent = Entry(opt_code_ent_frm)
    opt_c_ent.grid(row = 3, column = 1, sticky = W)
    opt_c_btn = Button(opt_code_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the command used for compiling C code."))
    opt_c_btn.grid(row = 3, column = 2, sticky = W)
    # Create the C++ label, entry, and button,
    opt_cpp_lbl = Label(opt_code_ent_frm, text = "C++ Compiler:")
    opt_cpp_lbl.grid(row = 4, column = 0, sticky = W)
    opt_cpp_ent = Entry(opt_code_ent_frm)
    opt_cpp_ent.grid(row = 4, column = 1, sticky = W)
    opt_cpp_btn = Button(opt_code_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the command used for compiling C++ code."))
    opt_cpp_btn.grid(row = 4, column = 2, sticky = W)
    # Create the Java label, entry, and button,
    opt_java_lbl = Label(opt_code_ent_frm, text = "Java Compiler:")
    opt_java_lbl.grid(row = 5, column = 0, sticky = W)
    opt_java_ent = Entry(opt_code_ent_frm)
    opt_java_ent.grid(row = 5, column = 1, sticky = W)
    opt_java_btn = Button(opt_code_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the command used for compiling Java code."))
    opt_java_btn.grid(row = 5, column = 2, sticky = W)
    # Create the auto-block indent label, entry, and button.
    opt_parg_lbl = Label(opt_code_ent_frm, text = "Prompt for Arguments:")
    opt_parg_lbl.grid(row = 6, column = 0, sticky = W)
    opt_parg_var = StringVar()
    opt_parg_ent = OptionMenu(opt_code_ent_frm, opt_parg_var, "yes", "no")
    opt_parg_ent.grid(row = 6, column = 1, sticky = W)
    opt_parg_btn = Button(opt_code_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the user will be prompted for command line arguments when running or compiling code."))
    opt_parg_btn.grid(row = 6, column = 2, sticky = W)
    # Create the auto-block indent label, entry, and button.
    opt_bautoi_lbl = Label(opt_code_ent_frm, text = "Block Indenting:")
    opt_bautoi_lbl.grid(row = 7, column = 0, sticky = W)
    opt_bautoi_var = StringVar()
    opt_bautoi_ent = OptionMenu(opt_code_ent_frm, opt_bautoi_var, "none", "c", "python")
    opt_bautoi_ent.grid(row = 7, column = 1, sticky = W)
    opt_bautoi_btn = Button(opt_code_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether automatic block indenting will be enabled for C code, Python code, or if it will be disabled."))
    opt_bautoi_btn.grid(row = 7, column = 2, sticky = W)
    # Create the comment continuation label, entry, and button.
    opt_comc_lbl = Label(opt_code_ent_frm, text = "Comment Continuation:")
    opt_comc_lbl.grid(row = 8, column = 0, sticky = W)
    opt_comc_var = StringVar()
    opt_comc_ent = OptionMenu(opt_code_ent_frm, opt_comc_var, "none", "c++", "python")
    opt_comc_ent.grid(row = 8, column = 1, sticky = W)
    opt_comc_btn = Button(opt_code_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether comments will be automatically continued for Python-style comments, for C++-style comments, or if it will be disabled."))
    opt_comc_btn.grid(row = 8, column = 2, sticky = W)
    # Create the frame for the Save and Cancel buttons.
    opt_ent_btn_frm = Frame(opt_code_frm)
    opt_ent_btn_frm.pack(side = BOTTOM, fill = X)
    # Create the Cancel button.
    opt_cancel_btn = Button(opt_ent_btn_frm, text = "Cancel", width = 6, command = opt_win.destroy)
    opt_cancel_btn.pack(side = RIGHT)
    # Create the Apply button.
    opt_apply_btn = Button(opt_ent_btn_frm, text = "Apply", width = 6, command = opt_apply)
    opt_apply_btn.pack(side = RIGHT)
    # Create the OK button.
    opt_save_btn = Button(opt_ent_btn_frm, text = "OK", width = 6, command = opt_save)
    opt_save_btn.pack(side = RIGHT)
    # Create the Misc frame.
    opt_misc_frm = Frame(opt_frm)
    # Create the frame for entries, optionmenus, labels, and buttons.
    opt_misc_ent_frm = Frame(opt_misc_frm)
    opt_misc_ent_frm.pack(side = TOP)
    # Create the initial directory label, entry, and button,
    opt_dir_lbl = Label(opt_misc_ent_frm, text = "Initial Directory:")
    opt_dir_lbl.grid(row = 0, column = 0, sticky = W)
    opt_dir_ent = Entry(opt_misc_ent_frm)
    opt_dir_ent.grid(row = 0, column = 1, sticky = W)
    opt_dir_btn = Button(opt_misc_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the initial directory used when displaying the open and save dialogs. Set to \"$HOME\" for it to be automatically set to your home directory after a restart."))
    opt_dir_btn.grid(row = 0, column = 2, sticky = W)
    # Create the default Unicode encoding label, entry, and button,
    opt_dencode_lbl = Label(opt_misc_ent_frm, text = "Default Encoding:")
    opt_dencode_lbl.grid(row = 1, column = 0, sticky = W)
    opt_dencode_ent = Entry(opt_misc_ent_frm)
    opt_dencode_ent.grid(row = 1, column = 1, sticky = W)
    opt_dencode_btn = Button(opt_misc_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the default encoding.\n\nSet to \"DEFAULT\" for it to be automatically replaced with the system default."))
    opt_dencode_btn.grid(row = 1, column = 2, sticky = W)
    # Create the prompt for Unicode encoding label, entry, and button,
    opt_pencode_lbl = Label(opt_misc_ent_frm, text = "Prompt For Encoding:")
    opt_pencode_lbl.grid(row = 2, column = 0, sticky = W)
    opt_pencode_var = StringVar()
    opt_pencode_ent = OptionMenu(opt_misc_ent_frm, opt_pencode_var, "yes", "no")
    opt_pencode_ent.grid(row = 2, column = 1, sticky = W)
    opt_pencode_btn = Button(opt_misc_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the user will be prompted for the encoding before the default encodings are tried."))
    opt_pencode_btn.grid(row = 2, column = 2, sticky = W)
    # Create the date format label, entry, and button,
    opt_datef_lbl = Label(opt_misc_ent_frm, text = "Date Format:")
    opt_datef_lbl.grid(row = 3, column = 0, sticky = W)
    opt_datef_ent = Entry(opt_misc_ent_frm)
    opt_datef_ent.grid(row = 3, column = 1, sticky = W)
    opt_datef_btn = Button(opt_misc_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the format used when inserting dates."))
    opt_datef_btn.grid(row = 3, column = 2, sticky = W)
    # Create the time format label, entry, and button,
    opt_timef_lbl = Label(opt_misc_ent_frm, text = "Time Format:")
    opt_timef_lbl.grid(row = 4, column = 0, sticky = W)
    opt_timef_ent = Entry(opt_misc_ent_frm)
    opt_timef_ent.grid(row = 4, column = 1, sticky = W)
    opt_timef_btn = Button(opt_misc_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies the format used when inserting times."))
    opt_timef_btn.grid(row = 4, column = 2, sticky = W)
    # Create the restore last open label, entry, and button,
    opt_resopen_lbl = Label(opt_misc_ent_frm, text = "Restore Last Opened:")
    opt_resopen_lbl.grid(row = 5, column = 0, sticky = W)
    opt_resopen_var = StringVar()
    opt_resopen_ent = OptionMenu(opt_misc_ent_frm, opt_resopen_var, "yes", "no")
    opt_resopen_ent.grid(row = 5, column = 1, sticky = W)
    opt_resopen_btn = Button(opt_misc_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the file will be automatically reopened next session."))
    opt_resopen_btn.grid(row = 5, column = 2, sticky = W)
    # Create the save window geometry label, entry, and button,
    opt_winsize_lbl = Label(opt_misc_ent_frm, text = "Save Window Geometry:")
    opt_winsize_lbl.grid(row = 6, column = 0, sticky = W)
    opt_winsize_var = StringVar()
    opt_winsize_ent = OptionMenu(opt_misc_ent_frm, opt_winsize_var, "yes", "no")
    opt_winsize_ent.grid(row = 6, column = 1, sticky = W)
    opt_winsize_btn = Button(opt_misc_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the window size and position on exit will be saved and restored next session."))
    opt_winsize_btn.grid(row = 6, column = 2, sticky = W)
    # Create the save window geometry label, entry, and button.
    opt_curmode_lbl = Label(opt_misc_ent_frm, text = "Save Cursor Mode:")
    opt_curmode_lbl.grid(row = 7, column = 0, sticky = W)
    opt_curmode_var = StringVar()
    opt_curmode_ent = OptionMenu(opt_misc_ent_frm, opt_curmode_var, "yes", "no")
    opt_curmode_ent.grid(row = 7, column = 1, sticky = W)
    opt_curmode_btn = Button(opt_misc_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the cursor mode on exit will be saved and restored next session."))
    opt_curmode_btn.grid(row = 7, column = 2, sticky = W)
    # Create the check for modified label, entry, and button,
    opt_chmod_lbl = Label(opt_misc_ent_frm, text = "Confirm on Exit:")
    opt_chmod_lbl.grid(row = 8, column = 0, sticky = W)
    opt_chmod_var = StringVar()
    opt_chmod_ent = OptionMenu(opt_misc_ent_frm, opt_chmod_var, "yes", "no")
    opt_chmod_ent.grid(row = 8, column = 1, sticky = W)
    opt_chmod_btn = Button(opt_misc_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether a confirmation dialog will be shown on exit if there are unsaved changes."))
    opt_chmod_btn.grid(row = 8, column = 2, sticky = W)
    # Create the time format label, entry, and button,
    opt_fontc_lbl = Label(opt_misc_ent_frm, text = "Font Size Change:")
    opt_fontc_lbl.grid(row = 9, column = 0, sticky = W)
    opt_fontc_ent = Entry(opt_misc_ent_frm)
    opt_fontc_ent.grid(row = 9, column = 1, sticky = W)
    opt_fontc_btn = Button(opt_misc_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies how much the font size should be changed when enlarging or shrinking."))
    opt_fontc_btn.grid(row = 9, column = 2, sticky = W)
    # Create the time format label, entry, and button,
    opt_fsc_lbl = Label(opt_misc_ent_frm, text = "Fast Scroll Lines:")
    opt_fsc_lbl.grid(row = 10, column = 0, sticky = W)
    opt_fsc_ent = Entry(opt_misc_ent_frm)
    opt_fsc_ent.grid(row = 10, column = 1, sticky = W)
    opt_fsc_btn = Button(opt_misc_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies how many lines fast scrolling should scroll by."))
    opt_fsc_btn.grid(row = 10, column = 2, sticky = W)
    # Create the time format label, entry, and button,
    opt_psl_lbl = Label(opt_misc_ent_frm, text = "Page Scroll Lines:")
    opt_psl_lbl.grid(row = 11, column = 0, sticky = W)
    opt_psl_ent = Entry(opt_misc_ent_frm)
    opt_psl_ent.grid(row = 11, column = 1, sticky = W)
    opt_psl_btn = Button(opt_misc_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies how many lines PageUp and PageDown will be scrolled by."))
    opt_psl_btn.grid(row = 11, column = 2, sticky = W)
    # Create the copy/cut line label, entry, and button.
    opt_ccl_lbl = Label(opt_misc_ent_frm, text = "Copy/Cut Line:")
    opt_ccl_lbl.grid(row = 12, column = 0, sticky = W)
    opt_ccl_var = StringVar()
    opt_ccl_ent = OptionMenu(opt_misc_ent_frm, opt_ccl_var, "yes", "no")
    opt_ccl_ent.grid(row = 12, column = 1, sticky = W)
    opt_ccl_btn = Button(opt_misc_ent_frm, text = "?", command = lambda: showinfo("Help", "Specifies whether the current line will be copied or cut if nothing is selected."))
    opt_ccl_btn.grid(row = 12, column = 2, sticky = W)
    # Create the frame for the Save and Cancel buttons.
    opt_ent_btn_frm = Frame(opt_misc_frm)
    opt_ent_btn_frm.pack(side = BOTTOM, fill = X)
    # Create the Cancel button.
    opt_cancel_btn = Button(opt_ent_btn_frm, text = "Cancel", width = 6, command = opt_win.destroy)
    opt_cancel_btn.pack(side = RIGHT)
    # Create the Apply button.
    opt_apply_btn = Button(opt_ent_btn_frm, text = "Apply", width = 6, command = opt_apply)
    opt_apply_btn.pack(side = RIGHT)
    # Create the OK button.
    opt_save_btn = Button(opt_ent_btn_frm, text = "OK", width = 6, command = opt_save)
    opt_save_btn.pack(side = RIGHT)
    # Pre-fill the entries and optionmenus.
    opt_font_ent.insert(0, CONFIG["font_name"])
    opt_size_ent.insert(0, CONFIG["font_size"])
    opt_style_var.set(CONFIG["font_style"])
    opt_fg_ent.insert(0, CONFIG["fg"])
    opt_bg_ent.insert(0, CONFIG["bg"])
    opt_sfg_ent.insert(0, CONFIG["sel_fg"])
    opt_sbg_ent.insert(0, CONFIG["sel_bg"])
    opt_wrap_var.set(CONFIG["wrap"])
    opt_uifg_ent.insert(0, CONFIG["ui_fg"])
    opt_uibg_ent.insert(0, CONFIG["ui_bg"])
    opt_menu_var.set("enabled")
    if CONFIG["tearoff"] == False or CONFIG["tearoff"] == "disabled":
        opt_menu_var.set("disabled")
    opt_tb_var.set("show")
    if not CONFIG["toolbar"]:
        opt_tb_var.set("hide")
    opt_ln_var.set("show")
    if not CONFIG["line_numbers"]:
        opt_ln_var.set("hide")
    opt_sb_var.set("show")
    if not CONFIG["status_bar"]:
        opt_sb_var.set("hide")
    opt_ft_var.set(CONFIG["title"])
    opt_autoi_var.set(CONFIG["auto_indent"])
    opt_replt_var.set(CONFIG["replace_tabs"])
    opt_bautoi_var.set(CONFIG["block_indent"])
    opt_ina_ent.insert(0, CONFIG["indent"])
    opt_spt_ent.insert(0, CONFIG["spaces_tab"])
    opt_rsep_ent.insert(0, CONFIG["reverse_sep"])
    opt_jsep_ent.insert(0, CONFIG["join_sep"])
    opt_py_ent.insert(0, CONFIG["python"])
    opt_pl_ent.insert(0, CONFIG["perl"])
    opt_php_ent.insert(0, CONFIG["php"])
    opt_c_ent.insert(0, CONFIG["c"])
    opt_cpp_ent.insert(0, CONFIG["cpp"])
    opt_java_ent.insert(0, CONFIG["java"])
    opt_cs_var.set("insensitive")
    if not CONFIG["case_insensitive"]:
        opt_cs_var.set("sensitive")
    opt_re_var.set("yes")
    if not CONFIG["regex"]:
        opt_re_var.set("no")
    opt_curp_var.set(CONFIG["search_cursor_pos"])
    opt_kdlg_var.set(CONFIG["search_keep_dlg"])
    opt_dir_ent.insert(0, CONFIG["init_dir"])
    opt_dencode_ent.insert(0, CONFIG["def_encode"])
    opt_pencode_var.set("yes")
    if not CONFIG["prompt_encode"]:
        opt_pencode_var.set("no")
    opt_datef_ent.insert(0, CONFIG["date"])
    opt_timef_ent.insert(0, CONFIG["time"])
    opt_resopen_var.set(CONFIG["restore"])
    opt_chmod_var.set(CONFIG["check_modified"])
    opt_winsize_var.set(CONFIG["save_winsize"])
    opt_comc_var.set(CONFIG["comment_cont"])
    opt_tbb_var.set(CONFIG["toolbar_type"])
    opt_tbi_var.set(CONFIG["toolbar_compound"])
    opt_mail_ent.insert(0, CONFIG["email_server"])
    opt_ftp_ent.insert(0, CONFIG["ftp_server"])
    opt_goto_var.set(CONFIG["goto_negative"])
    opt_advs_var.set(CONFIG["advanced_search"])
    opt_mb_var.set(CONFIG["menu_bar"])
    opt_mrec_ent.insert(0, CONFIG["email_from"])
    opt_msen_ent.insert(0, CONFIG["email_to"])
    opt_fbt_var.set(CONFIG["browser_title"])
    opt_fbti_var.set(CONFIG["browser_toolbar"])
    opt_fbm_var.set(CONFIG["browser_menubar"])
    opt_fbs_var.set(CONFIG["browser_sort"])
    opt_fbf_var.set(CONFIG["browser_folders"])
    opt_fbtb_var.set(CONFIG["browser_btns"])
    opt_fbti2_var.set(CONFIG["browser_compound"])
    opt_shome_var.set(CONFIG["smart_home"])
    opt_menuf_var.set(CONFIG["menu_file"])
    opt_menue_var.set(CONFIG["menu_edit"])
    opt_menud_var.set(CONFIG["menu_documents"])
    opt_menuse_var.set(CONFIG["menu_search"])
    opt_menut_var.set(CONFIG["menu_tools"])
    opt_menuc_var.set(CONFIG["menu_code"])
    opt_menuo_var.set(CONFIG["menu_options"])
    opt_menuh_var.set(CONFIG["menu_help"])
    opt_menuco_var.set(CONFIG["menu_context"])
    opt_fontc_ent.insert(0, CONFIG["font_size_change"])
    opt_tbis_var.set(CONFIG["toolbar_size"])
    opt_ast_var.set(CONFIG["auto_strip"])
    opt_fbmf_var.set(CONFIG["browser_menu_file"])
    opt_fbmo_var.set(CONFIG["browser_menu_folders"])
    opt_fbmc_var.set(CONFIG["browser_menu_context"])
    opt_cmb_var.set(CONFIG["command_bar"])
    opt_maccb_var.set(CONFIG["macro_command_bar"])
    opt_macrc_var.set(CONFIG["macro_run_command"])
    opt_macue_var.set(CONFIG["macro_unknown_error"])
    opt_macse_var.set(CONFIG["macro_stop_error"])
    opt_macps_var.set(CONFIG["macro_python"])
    opt_macav_var.set(CONFIG["macro_variables"])
    opt_macco_ent.insert(0, CONFIG["macro_comment_start"])
    opt_macvs_ent.insert(0, CONFIG["macro_variable_start"])
    opt_macpss_ent.insert(0, CONFIG["macro_python_start"])
    opt_menui_var.set(CONFIG["menu_images"])
    opt_ccl_var.set(CONFIG["cut_copy_line"])
    opt_curmode_var.set(CONFIG["save_curmode"])
    opt_pref_ent.insert(0, CONFIG["start_newline"])
    opt_suff_ent.insert(0, CONFIG["end_newline"])
    opt_fsc_ent.insert(0, CONFIG["fast_scroll"])
    opt_shis_var.set(CONFIG["search_history_order"])
    opt_rfh_var.set(CONFIG["find_history"])
    opt_rrh_var.set(CONFIG["replace_history"])
    opt_psl_ent.insert(0, CONFIG["page_scroll"])
    opt_send_var.set(CONFIG["smart_end"])
    opt_dup_var.set(CONFIG["duplicate_line"])
    opt_dl_var.set(CONFIG["documents_list"])
    opt_dlw_ent.insert(0, CONFIG["documents_list_width"])
    opt_colse_ent.insert(0, CONFIG["collab_server"])
    opt_colpo_ent.insert(0, CONFIG["collab_port"])
    opt_awrap_var.set(CONFIG["auto_wrap"])
    opt_awrapl_ent.insert(0, CONFIG["auto_wrap_length"])
    opt_parg_var.set(CONFIG["run_code_args"])
    opt_hline_var.set(CONFIG["highlight_line"])
    opt_hlinec_ent.insert(0, CONFIG["highlight_color"])
    # Bind the events.
    opt_fg_ent.bind("<Button-1>", lambda x: opt_get_color(opt_fg_ent))
    opt_bg_ent.bind("<Button-1>", lambda x: opt_get_color(opt_bg_ent))
    opt_sfg_ent.bind("<Button-1>", lambda x: opt_get_color(opt_sfg_ent))
    opt_sbg_ent.bind("<Button-1>", lambda x: opt_get_color(opt_sbg_ent))
    opt_uifg_ent.bind("<Button-1>", lambda x: opt_get_color(opt_uifg_ent))
    opt_uibg_ent.bind("<Button-1>", lambda x: opt_get_color(opt_uibg_ent))
    opt_hlinec_ent.bind("<Button-1>", lambda x: opt_get_color(opt_hlinec_ent))
    opt_dir_ent.bind("<Button-1>", lambda x: opt_get_directory(opt_dir_ent))
    opt_win.bind("<Escape>", lambda x: opt_win.destroy())
    opt_win.bind("<Control-Key-1>", lambda event: opt_switch("font"))
    opt_win.bind("<Control-Key-2>", lambda event: opt_switch("interface"))
    opt_win.bind("<Control-Key-3>", lambda event: opt_switch("editing"))
    opt_win.bind("<Control-Key-4>", lambda event: opt_switch("searching"))
    opt_win.bind("<Control-Key-5>", lambda event: opt_switch("network"))
    opt_win.bind("<Control-Key-6>", lambda event: opt_switch("file browser"))
    opt_win.bind("<Control-Key-7>", lambda event: opt_switch("menus"))
    opt_win.bind("<Control-Key-8>", lambda event: opt_switch("macros"))
    opt_win.bind("<Control-Key-9>", lambda event: opt_switch("code"))
    opt_win.bind("<Control-Key-0>", lambda event: opt_switch("misc"))
    opt_win.bind("<Control-Key-s>", lambda event: opt_save())
    opt_win.bind("<Shift-Control-Key-S>", lambda event: opt_apply())


def opt_revert():
    """Reverts to default options."""
    # Prompt the user for confirmation.
    rev_conf = askyesno("Revert to Default", "Are you sure you want to revert to default options?")
    if not rev_conf:
        return internal_return_focus()
    # Remember the current directory, and switch to the main one.
    curr_dir = os.getcwd()
    os.chdir(gbl_directory)
    # Delete the old config file.
    os.remove("resources/config/config")
    # Copy the backup file.
    shutil.copyfile("resources/defconfig/config", "resources/config/config")
    # Tell the user that files have been copied.
    showinfo("Revert to Default", "Configuration file has been replaced. Changes will take effect after a restart.")
    # Return focus to the text box.
    return internal_return_focus()


def opt_font_size(add):
    """Changes the font size."""
    # Increase the font size by one:
    if add:
        CONFIG["font_size"] += int(CONFIG["font_size_change"])
        text_box.text_box.config(font = (CONFIG["font_name"], CONFIG["font_size"], CONFIG["font_style"]))
        if CONFIG["line_numbers"]:
            text_box.line_text.config(font = (CONFIG["font_name"], CONFIG["font_size"], CONFIG["font_style"]))
    # Decrease the font size by one.
    else:
        # The font size cannot be less than 1.
        if CONFIG["font_size"] - int(CONFIG["font_size_change"]) < 1:
            return internal_return_focus()
        CONFIG["font_size"] -= int(CONFIG["font_size_change"])
        text_box.text_box.config(font = (CONFIG["font_name"], CONFIG["font_size"], CONFIG["font_style"]))
        if CONFIG["line_numbers"]:
            text_box.line_text.config(font = (CONFIG["font_name"], CONFIG["font_size"], CONFIG["font_style"]))
    # Return focus to the text box.
    return internal_return_focus()


def opt_font_size_scroll(event):
    """Changes the font size. This is bound to the mousewheel."""
    # Increase the font size.
    if event.num == 4:
        opt_font_size(True)
    # Decrease the font size.
    elif event.num == 5:
        opt_font_size(False)


def opt_font_size_scroll_win(event):
    """Changes the font size. This is bound to the mousewheel. (Windows compatability)"""
    # Increase the font size.
    if event.delta == 120:
        opt_font_size(True)
    # Decrease the font size.
    elif event.delta == -120:
        opt_font_size(False)


def opt_edit_favorites():
    """Edits the favorites list."""
    def opt_edit_favorites_add():
        """Adds an item to the listbox."""
        # Ask user for the file.
        filename = askopenfilename(title = "Choose File", initialdir = CONFIG["init_dir"], filetypes = gbl_file_types)
        if not filename:
            return internal_return_focus()
        # Insert the file at the end of the listbox.
        fav2_list.insert("end", filename)
    def opt_edit_favorites_remove():
        """Removes an item from the listbox."""
        fav2_list.delete(fav2_list.curselection())
    def opt_edit_favorites_save():
        """Saves the list to the file."""
        # Get all the items.
        items = []
        # Loop through the listbox until all the items are in the array.
        items_current = 0
        while True:
            item = fav2_list.get(items_current)
            if item == "":
                break
            items.append(item)
            items_current += 1
        # Delete all the items in the favorites list, and add the new ones.
        del gbl_favorites[:]
        gbl_favorites[:] = items
        # Join the list items.
        items_str = "\n".join(gbl_favorites)
        # Remember the current directory.
        file_dir = os.getcwd()
        # Switch to the pytextedit main directory.
        os.chdir(gbl_directory)
        # Open the favorites file, write the new string, and close the file.
        try:
            fav_file = open("resources/favorites", "w")
            fav_file.write(items_str)
            fav_file.close()
        except:
            showerror("Edit Favorites", "Error saving data file \"favorites\".")
        # Switch back to the original directory.
        os.chdir(file_dir)
        # Show a dialog telling the user that the favorites have been saved.
        showinfo("Edit Favorites", "Favorites saved.")
    # Create the GUI.
    fav2_win = Toplevel()
    fav2_win.title("Edit Favorites")
    fav2_win.transient(root)
    fav2_win.grab_set()
    # Create the frame for the listbox and scrollbar.
    fav2_frm = Frame(fav2_win)
    fav2_frm.pack(expand = YES, fill = BOTH, side = TOP)
    # Create the listbox and scrollbar.
    fav2_list = Listbox(fav2_frm, bg = CONFIG["bg"], fg = CONFIG["fg"], relief = SUNKEN, width = 60)
    fav2_scroll = Scrollbar(fav2_frm)
    fav2_scroll.config(command = fav2_list.yview)
    fav2_list.config(yscrollcommand = fav2_scroll.set)
    fav2_scroll.pack(side = RIGHT, fill = Y)
    fav2_list.pack(side = LEFT, expand = YES, fill = BOTH)
    fav2_list.focus()
    # Populate the listbox.
    for i in gbl_favorites:
        fav2_list.insert("end", str(i))
    # Create the frame for the buttons.
    fav2_frm2 = Frame(fav2_win)
    fav2_frm2.pack(expand = NO, fill = X, side = TOP)
    # Create the Add button.
    fav2_add_btn = Button(fav2_frm2, text = "Add", width = 20, command = opt_edit_favorites_add)
    fav2_add_btn.pack(side = LEFT)
    # Create the Remove button.
    fav2_rmv_btn = Button(fav2_frm2, text = "Remove", width = 20, command = opt_edit_favorites_remove)
    fav2_rmv_btn.pack(side = LEFT)
    # Create the Save button.
    fav2_sav_btn = Button(fav2_frm2, text = "Save", width = 20, command = opt_edit_favorites_save)
    fav2_sav_btn.pack(side = LEFT)
    # Bind the event.
    fav2_win.bind("<Escape>", lambda event: fav2_win.destroy())


def opt_edit_filetypes():
    """Edits the filetypes."""
    def opt_edit_filetypes_add():
        """Adds an item to the listbox."""
        # Ask the user for the file type.
        ftype = askstring("Edit File Types", "Enter file type:")
        if not ftype:
            return
        # Ask the user for the file type extensions.
        fext = askstring("Edit File Types", "Enter extension(s) for file type \"%s\":" % ftype)
        if not fext:
            return
        # Insert the filetype at the end of the listbox.
        ftypes_list.insert("end", "%s - %s" % (ftype, fext))
    def opt_edit_filetypes_remove():
        """Removes an item from the listbox."""
        ftypes_list.delete(ftypes_list.curselection())
    def opt_edit_filetypes_save():
        """Saves the list to the file."""
        # Get all the items.
        items = []
        # Loop through the listbox until all the items are in the array.
        items_current = 0
        while True:
            item = ftypes_list.get(items_current)
            if item == "":
                break
            items.append(item)
            items_current += 1
        # Split the items into their components.
        for i in range(0, len(items)):
            items[i] = tuple(items[i].split(" - "))
        # Delete all the items in the filetypes list, and add the new ones.
        del gbl_file_types[:]
        gbl_file_types[:] = items
        # Join the list items.
        for i in range(0, len(items)):
            items[i] = "=".join(list(items[i]))
        items_str = "\n".join(items)
        # Remember the current directory.
        file_dir = os.getcwd()
        # Switch to the pytextedit main directory.
        os.chdir(gbl_directory)
        # Open the filetypes file, write the new string, and close the file.
        try:
            ftype_file = open("resources/filetypes", "w")
            ftype_file.write(items_str)
            ftype_file.close()
        except:
            showerror("Edit File Types", "Error saving data file \"filetypes\".")
        # Switch back to the original directory.
        os.chdir(file_dir)
        # Show a dialog telling the user that the filetypes have been saved.
        showinfo("Edit File Types", "File types saved.")
    # Create the GUI.
    ftypes_win = Toplevel()
    ftypes_win.title("Edit File Types")
    ftypes_win.transient(root)
    ftypes_win.grab_set()
    # Create the frame for the listbox and scrollbar.
    ftypes_frm = Frame(ftypes_win)
    ftypes_frm.pack(expand = YES, fill = BOTH, side = TOP)
    # Create the listbox and scrollbar.
    ftypes_list = Listbox(ftypes_frm, bg = CONFIG["bg"], fg = CONFIG["fg"], relief = SUNKEN, width = 60)
    ftypes_scroll = Scrollbar(ftypes_frm)
    ftypes_scroll.config(command = ftypes_list.yview)
    ftypes_list.config(yscrollcommand = ftypes_scroll.set)
    ftypes_scroll.pack(side = RIGHT, fill = Y)
    ftypes_list.pack(side = LEFT, expand = YES, fill = BOTH)
    ftypes_list.focus()
    # Populate the listbox.
    for i in gbl_file_types:
        ftypes_list.insert("end", "%s - %s" % i)
    # Create the frame for the buttons.
    ftypes_frm2 = Frame(ftypes_win)
    ftypes_frm2.pack(expand = NO, fill = X, side = TOP)
    # Create the Add button.
    ftypes_add_btn = Button(ftypes_frm2, text = "Add", width = 20, command = opt_edit_filetypes_add)
    ftypes_add_btn.pack(side = LEFT)
    # Create the Remove button.
    ftypes_rmv_btn = Button(ftypes_frm2, text = "Remove", width = 20, command = opt_edit_filetypes_remove)
    ftypes_rmv_btn.pack(side = LEFT)
    # Create the Save button.
    ftypes_sav_btn = Button(ftypes_frm2, text = "Save", width = 20, command = opt_edit_filetypes_save)
    ftypes_sav_btn.pack(side = LEFT)
    # Bind the event.
    ftypes_win.bind("<Escape>", lambda event: ftypes_win.destroy())


def opt_clear_find_history():
    """Clears the Find history."""
    global gbl_find_history
    # Ask the user for confirmation.
    clear_conf = askyesno("Clear Find History", "Are you sure you want to clear the history?")
    if not clear_conf:
        return internal_return_focus()
    # Clear the list.
    gbl_find_history[:] = []
    # Remember the current directory.
    file_dir = os.getcwd()
    # Switch to the pytextedit main directory.
    os.chdir(gbl_directory)
    # Clear the file.
    try:
        find_file = open("resources/findhistory", "w")
        find_file.close()
    except IOError:
        showerror("Clear Find History", "Could not clear the file.")
        return internal_return_focus()
    # Switch back to the original directory.
    os.chdir(file_dir)
    # Tell the user the history has been cleared.
    showinfo("Clear Find History", "History has been cleared.")
    # Return focus to the main text box.
    return internal_return_focus()


def opt_clear_replace_history():
    """Clears the Replace history."""
    global gbl_replace_history
    # Ask the user for confirmation.
    clear_conf = askyesno("Clear Replace History", "Are you sure you want to clear the history?")
    if not clear_conf:
        return internal_return_focus()
    # Clear the list.
    gbl_replace_history[:] = []
    # Remember the current directory.
    file_dir = os.getcwd()
    # Switch to the pytextedit main directory.
    os.chdir(gbl_directory)
    # Clear the file.
    try:
        replace_file = open("resources/replacehistory", "w")
        replace_file.close()
    except IOError:
        showerror("Clear Replace History", "Could not clear the file.")
        return internal_return_focus()
    # Switch back to the original directory.
    os.chdir(file_dir)
    # Tell the user the history has been cleared.
    showinfo("Clear Replace History", "History has been cleared.")
    # Return focus to the main text box.
    return internal_return_focus()


def help_about():
    """Shows info about pytextedit."""
    # Define the internal functions.
    def help_about_readme():
        """Shows the README file."""
        # Remember the current directory.
        current_dir = os.getcwd()
        # Switch to the pytextedit main directory.
        os.chdir(gbl_directory)
        # Load the file.
        try:
            readme_file = open("resources/about/README", "r")
            readme = readme_file.read()
            readme_file.close()
        except:
            showerror("About", "Could not read file \"README\".")
            return
        # Switch back to the original directory.
        os.chdir(current_dir)
        # Create the GUI.
        ar_win = Toplevel(about_win)
        ar_win.title("About: Readme")
        ar_win.geometry("600x400")
        # Create the frame for everything.
        ar_frm = Frame(ar_win)
        ar_frm.pack(side = LEFT, expand = YES, fill = BOTH)
        # Create the text box and scrollbar.
        ar_text = Text(ar_frm, wrap = WORD, bg = "white", fg = "black", font = ("arial", CONFIG["font_size"], "normal"))
        ar_scroll = Scrollbar(ar_frm)
        # Set up scrolling.
        ar_text.config(yscrollcommand = ar_scroll.set)
        ar_scroll.config(command = ar_text.yview)
        # Pack the text box and scrollbar.
        ar_scroll.pack(fill = Y, side = RIGHT)
        ar_text.pack(side = LEFT, expand = YES, fill = BOTH)
        # Insert the documentation.
        ar_text.insert("1.0", readme)
        # Set text box to read only.
        ar_text.config(state = DISABLED)
        # Give the window focus.
        ar_win.grab_set()
        ar_text.focus()
    def help_about_license():
        """Shows the LICENSE file."""
        # Remember the current directory.
        current_dir = os.getcwd()
        # Switch to the pytextedit main directory.
        os.chdir(gbl_directory)
        # Load the file.
        try:
            license_file = open("resources/about/LICENSE", "r")
            license_ = license_file.read()
            license_file.close()
        except:
            showerror("About", "Could not read file \"LICENSE\".")
            return
        # Switch back to the original directory.
        os.chdir(current_dir)
        # Create the GUI.
        al_win = Toplevel(about_win)
        al_win.title("About: License")
        al_win.geometry("600x400")
        # Create the frame for everything.
        al_frm = Frame(al_win)
        al_frm.pack(side = LEFT, expand = YES, fill = BOTH)
        # Create the text box and scrollbar.
        al_text = Text(al_frm, wrap = WORD, bg = "white", fg = "black", font = ("arial", CONFIG["font_size"], "normal"))
        al_scroll = Scrollbar(al_frm)
        # Set up scrolling.
        al_text.config(yscrollcommand = al_scroll.set)
        al_scroll.config(command = al_text.yview)
        # Pack the text box and scrollbar.
        al_scroll.pack(fill = Y, side = RIGHT)
        al_text.pack(side = LEFT, expand = YES, fill = BOTH)
        # Insert the documentation.
        al_text.insert("1.0", license_)
        # Set text box to read only.
        al_text.config(state = DISABLED)
        # Give the window focus.
        al_win.grab_set()
        al_text.focus()
    # Create the About window.
    about_win = Toplevel(root)
    about_win.title("About pytextedit")
    about_win.wm_resizable(0, 0)
    # Create the frame for the first set of labels.
    about_frm1 = Frame(about_win, padx = 10, pady = 10, relief = GROOVE, bd = 3, bg = "#424242")
    about_frm1.pack(side = TOP, fill = X)
    # Create the first set of labels.
    about_lbl1 = Label(about_frm1, text = "pytextedit", font = ("arial", 30, "bold"), bg = "#424242", fg = "white")
    about_lbl1.pack(side = TOP, anchor = W)
    about_lbl2 = Label(about_frm1, text = "a simple text editor", font = ("arial", 14, "normal"), bg = "#424242", fg = "white")
    about_lbl2.pack(side = TOP, anchor = W)
    # Create the frame for the third set of labels.
    about_frm2 = Frame(about_win, padx = 10, pady = 10, relief = GROOVE, bd = 3, bg = "#424242")
    about_frm2.pack(side = TOP, fill = X)
    # Create the second set of labels.
    about_lbl3 = Label(about_frm2, text = "version: %s" % gbl_meta_version, bg = "#424242", fg = "white", font = ("arial", 10, "normal"))
    about_lbl3.pack(side = TOP, anchor = W)
    about_lbl4 = Label(about_frm2, text = "last updated: %s" % gbl_meta_lastupdated, bg = "#424242", fg = "white", font = ("arial", 10, "normal"))
    about_lbl4.pack(side = TOP, anchor = W)
    # Create the frame for the third set of labels.
    about_frm3 = Frame(about_win, padx = 10, pady = 10, relief = GROOVE, bd = 3, bg = "#424242")
    about_frm3.pack(side = TOP, fill = X)
    # Create the second set of labels.
    about_lbl5 = Label(about_frm3, text = "website: http://code.google.com/p/pytextedit", bg = "#424242", fg = "white", font = ("arial", 10, "normal"))
    about_lbl5.pack(side = TOP, anchor = W)
    about_lbl5.bind("<Button-1>", lambda event: webbrowser.open("http://code.google.com/p/pytextedit"))
    about_lbl6 = Label(about_frm3, text = "email: achesak@yahoo.com", bg = "#424242", fg = "white", font = ("arial", 10, "normal"))
    about_lbl6.pack(side = TOP, anchor = W)
    # Create the frame for the buttons.
    about_frm4 = Frame(about_win, padx = 10, pady = 10, relief = GROOVE, bd = 3, bg = "#424242")
    about_frm4.pack(side = TOP, fill = X)
    # Create the buttons.
    about_btn_frm = Frame(about_frm4, bg = "#424242")
    about_btn_frm.pack(side = TOP)
    # Create the Readme button.
    about_readme_btn = Button(about_btn_frm, text = "Readme", width = 10, command = help_about_readme, font = ("arial", 10, "normal"))
    about_readme_btn.pack(side = LEFT)
    # Spacer.
    Label(about_btn_frm, text = " ", bg = "#424242").pack(side = LEFT)
    # Create the License button.
    about_licence_btn = Button(about_btn_frm, text = "License", width = 10, command = help_about_license, font = ("arial", 10, "normal"))
    about_licence_btn.pack(side = LEFT)
    # Create the frame for the Close button.
    about_close_frm = Frame(about_win, pady = 10)
    about_close_frm.pack(side = TOP)
    # Create the Close button.
    about_close_btn = Button(about_close_frm, text = "Close", width = 7, command = about_win.destroy, font = ("arial", 10, "normal"))
    about_close_btn.pack(side = TOP)
    # Bind the event.
    about_win.bind("<Escape>", lambda event: about_win.destroy())


def help_help():
    """Shows documentation."""
    # Define internal function.
    def help_help_open_click():
        """Manages double-click events."""
        # Get the item.
        h_name = doc_list.get("active")
        if not h_name:
            return
        # Show the help.
        help_help_show(h_name)
    # Create the GUI.
    doc_win = Toplevel(root)
    doc_win.title("Help")
    doc_win.grab_set()
    # Create the frame for the listbox and scrollbar
    doc_frm = Frame(doc_win)
    doc_frm.pack(expand = YES, fill = BOTH, side = TOP)
    # Create the listbox and scrollbar.
    doc_list = Listbox(doc_frm, bg = CONFIG["bg"], fg = CONFIG["fg"], relief = SUNKEN, width = 50)
    doc_scroll = Scrollbar(doc_frm)
    doc_scroll.config(command = doc_list.yview)
    doc_list.config(yscrollcommand = doc_scroll.set)
    doc_scroll.pack(side = RIGHT, fill = Y)
    doc_list.pack(side = LEFT, expand = YES, fill = BOTH)
    # Populate the listbox.
    doc_list.insert("end", "Collaborative Editing")
    doc_list.insert("end", "Configuration")
    doc_list.insert("end", "Keybindings")
    doc_list.insert("end", "Macros")
    # Give the listbox focus.
    doc_list.focus()
    # Bind the events.
    doc_list.bind("<Double-1>", lambda event: help_help_open_click())
    doc_list.bind("<Return>", lambda event: help_help_open_click())
    doc_list.bind("<Escape>", lambda event: doc_win.destroy())


def help_help_show(subject):
    """Shows help."""
    # Determine which file to load.
    if subject == "Macros":
        help_fname = "macro_docs"
    elif subject == "Keybindings":
        help_fname = "keybinding_docs"
    elif subject == "Configuration":
        help_fname = "configuration_docs"
    elif subject == "Collaborative Editing":
        help_fname = "collab_docs"
    # Remember the current directory, and switch to the resource directory.
    curr_dir = os.getcwd()
    os.chdir(gbl_directory)
    # Read the file.
    try:
        help_file = open("resources/docs/%s" % help_fname, "r")
        help_docs = help_file.read()
        help_file.close()
    except:
        showerror("Help", "Could not read documentation file \"%s\"." % help_fname)
        os.chdir(curr_dir)
        return internal_return_focus()
    # Switch back to the original directory.
    os.chdir(gbl_directory)
    # Create the GUI.
    help2_win = Toplevel(root)
    help2_win.title("Help: %s" % subject)
    help2_win.geometry("600x400")
    # Create the frame for everything.
    help2_frm = Frame(help2_win)
    help2_frm.pack(side = LEFT, expand = YES, fill = BOTH)
    # Create the text box and scrollbar.
    help2_text = Text(help2_frm, wrap = WORD, bg = "white", fg = "black", font = ("arial", CONFIG["font_size"], "normal"))
    help2_scroll = Scrollbar(help2_frm)
    # Set up scrolling.
    help2_text.config(yscrollcommand = help2_scroll.set)
    help2_scroll.config(command = help2_text.yview)
    # Pack the text box and scrollbar.
    help2_scroll.pack(fill = Y, side = RIGHT)
    help2_text.pack(side = LEFT, expand = YES, fill = BOTH)
    # Insert the documentation.
    help2_text.insert("1.0", help_docs)
    # Set text box to read only.
    help2_text.config(state = DISABLED)
    # Apply the formatting.
    help2_text.tag_config("title", font = ("arial", CONFIG["font_size"] + 5, "underline"), justify = "center")
    if subject == "Collaborative Editing":
        help2_text.tag_add("title", "1.0", "1.end")
        help2_text.tag_add("title", "5.0", "5.end")
        help2_text.tag_add("title", "26.0", "26.end")
    elif subject == "Macros":
        help2_text.tag_add("title", "1.0", "1.end")
        help2_text.tag_add("title", "5.0", "5.end")
        help2_text.tag_add("title", "142.0", "142.end")
        help2_text.tag_add("title", "146.0", "146.end")
        help2_text.tag_add("title", "153.0", "153.end")
        help2_text.tag_add("title", "157.0", "157.end")
        help2_text.tag_add("title", "171.0", "171.end")
    elif subject == "Keybindings":
        help2_text.tag_add("title", "1.0", "1.end")
        help2_text.tag_add("title", "5.0", "5.end")
        help2_text.tag_add("title", "78.0", "78.end")
        help2_text.tag_add("title", "95.0", "95.end")
        help2_text.tag_add("title", "119.0", "119.end")
        help2_text.tag_add("title", "134.0", "134.end")
    elif subject == "Configuration":
        help2_text.tag_add("title", "1.0", "1.end")
        help2_text.tag_add("title", "5.0", "5.end")
        help2_text.tag_add("title", "16.0", "16.end")
        help2_text.tag_add("title", "33.0", "33.end")
        help2_text.tag_add("title", "50.0", "50.end")
        help2_text.tag_add("title", "62.0", "62.end")
        help2_text.tag_add("title", "71.0", "71.end")
        help2_text.tag_add("title", "84.0", "84.end")
        help2_text.tag_add("title", "99.0", "99.end")
        help2_text.tag_add("title", "111.0", "111.end")
        help2_text.tag_add("title", "123.0", "123.end")
    # Give the window focus. This causes an error, but I'm not sure how to avoid it. Will fix later.
    try:
        help2_win.grab_set()
        help2_text.focus()
    except:
        pass
    # Bind the event.
    help2_win.bind("<Escape>", lambda event: help2_win.destroy())


def command_bar_run():
    """Runs the command in the command bar."""
    # Get the string.
    command = command_bar_ent.get()
    # Run Python statement, if the user wants that.
    if CONFIG["macro_command_bar"] == "python statements":
        command = CONFIG["macro_python_start"] + command
    # Run the command.
    tools_macro_parse(0, command, "command")
    # Delete the text.
    command_bar_ent.delete(0, "end")
    # Give focus back to the entry.
    command_bar_focus("entry")
    # Update the title.
    update_title()


def command_bar_focus(focus):
    """Gives focus to either the text box or the entry."""
    # Give focus to the text box.
    if focus == "text":
        text_box.text_box.focus()
    # Give focus to the entry.
    elif focus == "entry":
        command_bar_ent.focus()
    # Override the default action.
    return "break"


def line_number_click():
    """Handles clicks on the line numbers."""
    # Get the line number.
    line = text_box.line_text.index("current").split(".")[0]
    line = text_box.line_text.get("%s.0" % line, "%s.end" % line).lstrip()
    # Move the text box cursor to the start of that line.
    try:
        text_box.text_box.mark_set("insert", "%s.0" % line)
    except:
        pass
    # Make sure the line is visible.
    text_box.text_box.see("insert")
    # Update the status bar.
    update_status()


def documents_list_update():
    """Handles clicks on the documents list."""
    global gbl_mdi_current
    global gbl_file_name
    global gbl_file_name_short
    global gbl_file_locked
    global gbl_text_modified
    # Get the index number of the document.
    item = documents_list.get("active")
    if not item:
        return internal_return_focus()
    found_pos = int(re.findall(r'\d+', item)[0])
    # Switch to the other document.
    gbl_file_name = gbl_mdi[found_pos][0]
    gbl_file_name_short = gbl_mdi[found_pos][1]
    gbl_file_locked = gbl_mdi[found_pos][2]
    gbl_text_modified = gbl_mdi[found_pos][3]
    text_box.text_box.config(state = "normal")
    text_box.text_box.delete("1.0", "end")
    text_box.text_box.insert("1.0", gbl_mdi[found_pos][7])
    if gbl_file_locked:
            text_box.text_box.config(state = "disabled")
    text_box.text_box.mark_set("insert", gbl_mdi[found_pos][4])
    text_box.text_box.tag_remove("sel", "1.0", "end")
    if gbl_mdi[found_pos][5] != None:
        text_box.text_box.tag_add("sel", gbl_mdi[found_pos][5], gbl_mdi[found_pos][6])
    gbl_mdi_current = found_pos
    # Update the title and status bar.
    update_title()
    update_status()
    update_status_file(gbl_file_name_short, gbl_last_encode)
    # Update the documents list.
    update_documents_list()
    # Return focus to the text box.
    return internal_return_focus()


def check_newline_space(event):
    """Adds spaces to the start of a new line based on the indent of the previous line."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        return internal_return_focus()
    curr_pos = text_box.text_box.index("insert").split(".")[1]
    if curr_pos != text_box.text_box.index("insert lineend").split(".")[1]:
        return
    # Delete the currently selected text, if any.
    if text_box.text_box.tag_ranges("sel"):
        text_box.text_box.delete("sel.first", "sel.last")
    spaces = 0
    # Get the previous line.
    line, col = text_box.text_box.index("insert").split(".")
    # Strip extra space from the end of the last line, if the user wants that.
    if CONFIG["auto_strip"] == "enabled":
        # Get the text.
        text = text_box.text_box.get("%s.0" % line, "%s.end" % line)
        # Strip from the end.
        text = text.rstrip()
        # Delete the old text and insert the new.
        text_box.text_box.delete("%s.0" % line, "%s.end" % line)
        text_box.text_box.insert("insert", text)
    # Append to the line.
    text_box.text_box.insert("insert", CONFIG["end_newline"])
    # Automatically indent, if the user wants that.
    if CONFIG["auto_indent"] == "enabled":
        prev_line = text_box.text_box.get(line + ".0", "insert")
        # Determine the number of spaces.
        spaces = len(prev_line) - len(prev_line.lstrip())
    # Add indents based on line ending, if the user wants that.
    # Add indents for Python code:
    if CONFIG["block_indent"] == "python" and text_box.text_box.get("%s.end-1c" % line, "%s.end" % line) == ":":
        spaces += CONFIG["indent"]
    # Add indents for C code, for at least C-style blocks:
    elif CONFIG["block_indent"] == "c" and text_box.text_box.get("%s.end-1c" % line, "%s.end" % line) == "{":
        spaces += CONFIG["indent"]
    # Insert the appropriate number of spaces.
    text_box.text_box.insert("insert", "\n" + (" " * spaces))
    # Prepend to the line.
    text_box.text_box.insert("insert", CONFIG["start_newline"])
    # Add a comment continuation, if the user wants that.
    # Add continuation for C++ code:
    if CONFIG["comment_cont"] == "c++" and (prev_line.lstrip()[:2] == "/*" or prev_line.lstrip()[:1] == "*"):
        text_box.text_box.insert("insert", "* ")
    # Add continuation for Python code:
    elif CONFIG["comment_cont"] == "python" and prev_line.lstrip()[:1] == "#":
        text_box.text_box.insert("insert", "# ")
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    # Go to the new line.
    text_box.text_box.see("insert")
    # Return focus to the text box.
    return internal_return_focus()


def check_tab(event):
    """Replaces tabs with spaces."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        return internal_return_focus()
    # Only auto replace tabs if desired:
    if CONFIG["replace_tabs"] == "enabled":
        # Replace the tab with the config-specified number of spaces.
        text_box.text_box.insert("insert", (" " * CONFIG["spaces_tab"]))
    # Mark the text as having changes.
    internal_text_modified(True)
    # Update the title.
    update_title()
    # Override the default action, if needed.
    if CONFIG["replace_tabs"] == "enabled":
        return internal_return_focus()


def check_modified(event):
    """Checks if the text has been modified."""
    # Auto-wrap the line, if the user wants that.
    if CONFIG["auto_wrap"] == "enabled" and not gbl_file_locked and event.char != "":
        # Get the current position.
        pos = text_box.text_box.index("insert").split(".")[1]
        # If the character position is at the specified limit, start a new line.
        if int(pos) > int(CONFIG["auto_wrap_length"]) - 2:
            text_box.text_box.insert("insert", "\n")
    # If overwrite mode is enabled, overwrite the next character.
    if gbl_overwrite and event.char != "" and not gbl_file_locked:
        # Delete the next character, as long as it is not a newline.
        if text_box.text_box.get("insert", "insert+1c") != "\n":
            text_box.text_box.delete("insert", "insert+1c")
    # Update the current line tag, if the user wants that.
    if CONFIG["highlight_line"] == "yes":
        line = text_box.text_box.index("insert").split(".")[0]
        text_box.text_box.tag_remove("current_line", "1.0", "end")
        text_box.text_box.tag_add("current_line", "%s.0" % line, "%s.end" % line)
    # If the file is locked, or this is a non-printing keypress, this cannot be done.
    if not gbl_file_locked and event.char != "" and not gbl_text_modified:
        # Mark text as having changes.
        internal_text_modified(True)
        # Update the title.
        update_title()


def check_escape(event):
    """Bind an event to the Escape key so that it doesn't mark as having changed the text."""
    return


def check_home(event):
    """Checks for Home key presses, for "smart" home."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        return internal_return_focus()
    # Only do smart home if desired:
    if CONFIG["smart_home"] == "enabled":
        # Get the current character position and line.
        line, char = text_box.text_box.index("insert").split(".")
        char = int(char)
        # Get the number of spaces at the start of the line.
        text = text_box.text_box.get("%s.0" % line, "%s.end" % line)
        spaces = len(text) - len(text.lstrip())
        # If the number of spaces is more or the same as the current pos, move the cursor to the start of the line.
        if spaces >= char:
            # Move the cursor.
            text_box.text_box.mark_set("insert", "%s.0" % line)
        # Otherwise move it to the start of the indenting.
        else:
            # Move the cursor.
            text_box.text_box.mark_set("insert", "%s.%d" % (line, spaces))
    # Update the title.
    update_title()
    # Override the default action, if needed.
    if CONFIG["smart_home"] == "enabled":
        return internal_return_focus()


def check_end(event):
    """Checks for End key presses, for "smart" end."""
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        return internal_return_focus()
    # Only do smart end if desired:
    if CONFIG["smart_end"] == "enabled":
        # Get the current character position and line.
        line, char = text_box.text_box.index("insert").split(".")
        char = int(char)
        # Get the number of spaces at the end of the line.
        text = text_box.text_box.get("%s.0" % line, "%s.end" % line)
        spaces = len(text) - len(text.rstrip())
        # Get the length of the line.
        line_len = len(text)
        # If the number of spaces at the end is greater than the current position, move the cursor to the end.
        if line_len - spaces <= char:
            # Move the cursor.
            text_box.text_box.mark_set("insert", "%s.end" % line)
        # Otherwise move it to the start of the indenting.
        else:
            # Move the cursor.
            text_box.text_box.mark_set("insert", "%s.%d" % (line, line_len - spaces))
    # Update the title.
    update_title()
    # Override the default action, if needed.
    if CONFIG["smart_end"] == "enabled":
        return internal_return_focus()


def check_insert(event):
    """Toggles overwrite mode."""
    global gbl_overwrite
    # Set the variable.
    if gbl_overwrite == True:
        gbl_overwrite = False
    else:
        gbl_overwrite = True
    # Update the status bar.
    update_status()
    # Cancel the default action.
    return "break"


def check_alt_scroll(event):
    """Scrolls up or down by ten lines (by default)."""
    # Scroll up.
    if event.num == 4:
        diff = - int(CONFIG["fast_scroll"])
    # Scroll down.
    elif event.num == 5:
        diff = int(CONFIG["fast_scroll"])
    # Get the current line and position.
    line, char = text_box.text_box.index("insert").split(".")
    line = int(line)
    # Set the cursor ten lines higher or lower.
    text_box.text_box.mark_set("insert", "%d.%s" % (line + diff, char))
    # Make sure the cursor is visible.
    text_box.text_box.see("insert")
    # Update the status bar.
    update_status()


def check_alt_scroll_win(event):
    """Scrolls up or down by ten lines (by default). (Windows compatability)"""
    # Scroll up.
    if event.delta == 120:
        check_alt_scroll({"num": 4})
    # Scroll down.
    elif event.delta == -120:
        check_alt_scroll({"num": 5})


def check_alt_arrow(arrow):
    """Scrolls up or down by ten lines (by default)."""
    # Scroll up.
    if arrow == "up":
        diff = - int(CONFIG["fast_scroll"]) + 1
    # Scroll down.
    elif arrow == "down":
        diff = int(CONFIG["fast_scroll"]) - 1
    # Get the current line and position.
    line, char = text_box.text_box.index("insert").split(".")
    line = int(line)
    # Set the cursor ten lines higher or lower.
    text_box.text_box.mark_set("insert", "%d.%s" % (line + diff, char))
    # Make sure the cursor is visible.
    text_box.text_box.see("insert")
    # Update the status bar.
    update_status()


def check_page_up(event):
    """Scrolls up by fifty lines (by default)."""
    # Scroll up.
    diff = - int(CONFIG["page_scroll"]) + 1
    # Get the current line and position.
    line, char = text_box.text_box.index("insert").split(".")
    line = int(line)
    # Set the cursor ten lines higher.
    text_box.text_box.mark_set("insert", "%d.%s" % (line + diff, char))
    # Make sure the cursor is visible.
    text_box.text_box.see("insert")
    # Update the status bar.
    update_status()


def check_page_down(event):
    """Scrolls down by fifty lines (by default)."""
    # Scroll down.
    diff = int(CONFIG["page_scroll"]) - 1
    # Get the current line and position.
    line, char = text_box.text_box.index("insert").split(".")
    line = int(line)
    # Set the cursor ten lines lower.
    text_box.text_box.mark_set("insert", "%d.%s" % (line + diff, char))
    # Make sure the cursor is visible.
    text_box.text_box.see("insert")
    # Update the status bar.
    update_status()


def update_title():
    """Changes the title."""
    # Determine which filename to use.
    if CONFIG["title"] == "full filename":
        filename = gbl_file_name
    else:
        filename = gbl_file_name_short
    # Determine the new title.
    title = ""
    if gbl_text_modified:
        title += "*"
    if filename:
        title += filename
        if gbl_file_locked:
            title += " [READ ONLY]"
        title += " - pytextedit"
    elif gbl_text_modified:
        title += " "
        if gbl_file_locked:
            title += "[READ ONLY] "
        title += "pytextedit"
    else:
        if gbl_file_locked:
            title += "[READ ONLY] "
        title += "pytextedit"
    # Update the title.
    root.title(title)
    # Update the status labels as well.
    update_status()
    # Get info about the current document.
    curr_cursor = text_box.text_box.index("insert")
    if text_box.text_box.tag_ranges("sel"):
        curr_sel_start = text_box.text_box.index("sel.first")
        curr_sel_end = text_box.text_box.index("sel.last")
    else:
        curr_sel_start = None
        curr_sel_end = None
    curr_text = text_box.text_box.get("1.0", "end-1c")
    # Store info about the current document.
    gbl_mdi[gbl_mdi_current] = [gbl_file_name, gbl_file_name_short, gbl_file_locked, gbl_text_modified, curr_cursor, curr_sel_start, curr_sel_end, curr_text]
    # Update the documents list also.
    update_documents_list()
    # Finally, make sure the cursor is in view.
    text_box.text_box.see("insert")


def update_status_cursor():
    """Changes the cursor position labels."""
    # If the status bar is hidden, this cannot be done.
    if not CONFIG["status_bar"]:
        return
    # Get the cursor position.
    index = tuple(text_box.text_box.index("insert").split("."))
    # Update the labels.
    status_line_lbl.config(text = "Line: %s" % index[0])
    status_col_lbl.config(text = "Col: %s" % str(int(index[1]) + 1))


def update_status_statistics():
    """Changes the statistics labels."""
    # If the status bar is hidden, this cannot be done.
    if not CONFIG["status_bar"]:
        return
    # Get all the text.
    text = text_box.text_box.get(1.0, "end-1c")
    # Get the characters, words, and lines.
    chars = len(text)
    words = len(text.split())
    lines = len(text.split("\n"))
    # Get the text write mode.
    mode = "INS"
    if gbl_overwrite:
        mode = "OVER"
    # Update the labels.
    status_chars_lbl.config(text = "Chars: %d" % chars)
    status_words_lbl.config(text = "Words: %d" % words)
    status_lines_lbl.config(text = "Lines: %d" % lines)
    status_mode_lbl.config(text = mode)
    


def update_status_file(filename, encoding):
    """Changes the action label."""
    # If the status bar is hidden, this cannot be done.
    if not CONFIG["status_bar"]:
        return
    # If there is no filename, use the default label.
    if not filename:
        filename = "No File"
    # Update the label.
    status_file_lbl.config(text = "%s (%s)" % (filename, encoding))


def update_status():
    """Updates the cursor and statistics file labels."""
    if not CONFIG["status_bar"]:
        return
    # If the file is locked, this cannot be done.
    if gbl_file_locked:
        return
    # Update the current line tag, if the user wants that.
    if CONFIG["highlight_line"] == "yes":
        line = text_box.text_box.index("insert").split(".")[0]
        text_box.text_box.tag_remove("current_line", "1.0", "end")
        text_box.text_box.tag_add("current_line", "%s.0" % line, "%s.end" % line)
    # Update the labels.
    update_status_cursor()
    update_status_statistics()


def update_documents_list():
    """Updates the documents list."""
    # If the documents list is hidden, this cannot be done.
    if CONFIG["documents_list"] == "hide":
        return
    # Clear the listbox.
    documents_list.delete("0", "end")
    # Populate the listbox.
    for i in range(len(gbl_mdi)):
        if gbl_mdi[i] == None:
            continue
        filename = gbl_mdi[i][1]
        if filename == "":
            filename = "[unsaved file]"
        locked = gbl_mdi[i][2]
        if locked:
            locked = "[READ ONLY]"
        else:
            locked = ""
        modified = gbl_mdi[i][3]
        if modified:
            modified = "*"
        else:
            modified = ""
        documents_list.insert("end", "%d - %s%s %s" % (i, modified, filename, locked))


def internal_return_focus():
    """Returns focus to the text box."""
    text_box.text_box.focus()
    return "break"


def internal_text_modified(change):
    """Marks text as having changes, or as having no changes."""
    # Mark the text.
    global gbl_text_modified
    gbl_text_modified = change
    # If text has been changed, update the status bar labels.
    if change:
        # Update the labels.
        update_status()


###############################################################################


# INITIAL LOAD, PART 1 ########################################################
# Try to load a file from command line arguments, part 1.

# Get the file to load.
# If file is specified on the command line:
if len(sys.argv) == 2:
    file_to_load = sys.argv[1]
    if not os.path.isfile(file_to_load):
        print("Open: \"%s\" does not exist, or is not a file." % file_to_load)
        sys.exit()
    load_from_last = False
# Otherwise load from last file:
elif CONFIG["restore"] == "yes" and last_file != "[{NEW}{FILE}]":
    file_to_load = last_file
    load_from_last = True
    if not os.path.isfile(file_to_load):
        load_from_last = False
else:
    load_from_last = False

# This is the text to load.
to_load = ""
# Use this variable to remember if it was loaded from the command line.
load_cmd = False
# Use this to remember if the file should be locked.
load_lock = False
# If file was loaded from last and last file was locked:
if CONFIG["restore"] == "yes" and load_from_last and last_lock == "true":
    # Mark the file as locked.
    load_lock = True

# Open the file.
if len(sys.argv) == 2 or load_from_last:
    to_load = None
    t_file = None
    # If this is running in python 2, change the open function so unicode can be used.
    if gbl_py_version == 2:
        open = codecs.open
    # Try to open the file using the last encoding, if loading from last session.
    if load_from_last and to_load == None and not CONFIG["prompt_encode"] and last_encode != "binary":
        try:
            t_file = open(file_to_load, "r", encoding = last_encode)
            to_load = t_file.read()
            gbl_last_encode = last_encode
        except IOError:
            print("Open: File could not be opened.")
            sys.exit()
        except UnicodeError:
            pass
    # Try to open the file using the config-specified encoding.
    if to_load == None and not CONFIG["prompt_encode"]:
        try:
            t_file = open(file_to_load, "r", encoding = CONFIG["def_encode"])
            to_load = t_file.read()
            gbl_last_encode = CONFIG["def_encode"]
        except IOError:
            print("Open: File could not be opened.")
            sys.exit()
        except UnicodeError:
            pass
    # Ask the user for the encoding.
    if to_load == None and CONFIG["prompt_encode"]:
        try:
            encode = input("Enter encoding (default=\"" + sys.getdefaultencoding() + "\"): ")
            if encode:
                t_file = open(file_to_load, "r", encoding = encode)
                to_load = t_file.read()
                gbl_last_encode = encode
        except IOError:
            print("Open: File could not be opened.")
            sys.exit()
        except UnicodeError:
            pass
    # Try to open the file using the system's default encoding.
    if to_load == None:
        try:
            t_file = open(file_to_load, "r", encoding = sys.getdefaultencoding())
            to_load = t_file.read()
            gbl_last_encode = sys.getdefaultencoding()
        except IOError:
            print("Open: File could not be opened.")
            sys.exit()
        except UnicodeError:
            pass
    # If all else fails, try to open the file in binary mode.
    if to_load == None:
        try:
            t_file = open(file_to_load, "rb")
            to_load = t_file.read().replace(b'\r\n', b'\n')
            gbl_last_encode = "binary"
        except IOError:
            print("Open: File could not be opened.")
            sys.exit()
        except UnicodeError:
            pass
    # None of the encodings worked. File cannot be opened.
    if to_load == None:
        print("Open: Could not open or decode file.")
        sys.exit()
    else:
        t_file.close()
    # Split and save the file name.
    gbl_file_name = file_to_load
    gbl_file_name_short = os.path.split(file_to_load)[1]
    # Mark file as having been opened from the command line.
    load_cmd = True


###############################################################################


# GUI #########################################################################
# Create the GUI.

# Create the GUI.
root = Tk()
# Set the default window title.
root.title("pytextedit")
# Also set the size.
root.geometry(gbl_winsize)
# Register event for when the user clicks the close button.
root.protocol("WM_DELETE_WINDOW", file_exit)

# Create tkinter variables.
# This is used for "Lock File".
tkvar_lock = BooleanVar()
# This is used for "Find" and "Replace".
tkvar_case = BooleanVar()


# Load all the images.
# Switch to the application directory so images can be loaded.
toolbar_temp_dir = os.getcwd()
os.chdir(gbl_directory)
# Load the images.
img_new = PhotoImage(file = "resources/images/new.gif")
img_open = PhotoImage(file = "resources/images/open.gif")
img_save = PhotoImage(file = "resources/images/save.gif")
img_previous = PhotoImage(file = "resources/images/previous.gif")
img_next = PhotoImage(file = "resources/images/next.gif")
img_close = PhotoImage(file = "resources/images/close.gif")
img_cut = PhotoImage(file = "resources/images/cut.gif")
img_copy = PhotoImage(file = "resources/images/copy.gif")
img_paste = PhotoImage(file = "resources/images/paste.gif")
img_undo = PhotoImage(file = "resources/images/undo.gif")
img_redo = PhotoImage(file = "resources/images/redo.gif")
img_search = PhotoImage(file = "resources/images/search.gif")
img_replace = PhotoImage(file = "resources/images/replace.gif")
img_blank = PhotoImage(file = "resources/images/menu/blank.gif")
img_file_new = PhotoImage(file = "resources/images/menu/new.gif")
img_file_open = PhotoImage(file = "resources/images/menu/open.gif")
img_file_openfromurl = PhotoImage(file = "resources/images/menu/openfromurl.gif")
img_file_reload = PhotoImage(file = "resources/images/menu/reload.gif")
img_file_favorites = PhotoImage(file = "resources/images/menu/favorites.gif")
img_file_save = PhotoImage(file = "resources/images/menu/save.gif")
img_file_saveas = PhotoImage(file = "resources/images/menu/saveas.gif")
img_file_delete = PhotoImage(file = "resources/images/menu/delete.gif")
img_file_browse = PhotoImage(file = "resources/images/menu/browse.gif")
img_file_print = PhotoImage(file = "resources/images/menu/print.gif")
img_file_exit = PhotoImage(file = "resources/images/menu/exit.gif")
img_edit_undo = PhotoImage(file = "resources/images/menu/undo.gif")
img_edit_redo = PhotoImage(file = "resources/images/menu/redo.gif")
img_edit_cut = PhotoImage(file = "resources/images/menu/cut.gif")
img_edit_copy = PhotoImage(file = "resources/images/menu/copy.gif")
img_edit_paste = PhotoImage(file = "resources/images/menu/paste.gif")
img_edit_selectall = PhotoImage(file = "resources/images/menu/selectall.gif")
img_documents_new = PhotoImage(file = "resources/images/menu/new.gif")
img_documents_open = PhotoImage(file = "resources/images/menu/open.gif")
img_documents_close = PhotoImage(file = "resources/images/menu/close.gif")
img_documents_previous = PhotoImage(file = "resources/images/menu/previous.gif")
img_documents_next = PhotoImage(file = "resources/images/menu/next.gif")
img_documents_viewall = PhotoImage(file = "resources/images/menu/viewall.gif")
img_search_find = PhotoImage(file = "resources/images/menu/find.gif")
img_search_replace = PhotoImage(file = "resources/images/menu/replace.gif")
img_search_goto = PhotoImage(file = "resources/images/menu/goto.gif")
img_search_jumptotop = PhotoImage(file = "resources/images/menu/jumptotop.gif")
img_search_jumptobottom = PhotoImage(file = "resources/images/menu/jumptobottom.gif")
img_search_jumplinestart = PhotoImage(file = "resources/images/menu/jumplinestart.gif")
img_search_jumplineend = PhotoImage(file = "resources/images/menu/jumplineend.gif")
img_search_searchselected = PhotoImage(file = "resources/images/menu/searchselected.gif")
img_tools_bookmarks = PhotoImage(file = "resources/images/menu/viewbookmarks.gif")
img_tools_add_bookmark = PhotoImage(file = "resources/images/menu/addbookmark.gif")
img_tools_clear_bookmarks = PhotoImage(file = "resources/images/menu/clearbookmarks.gif")
img_tools_macro_run = PhotoImage(file = "resources/images/menu/runmacro.gif")
img_tools_macro_bindings = PhotoImage(file = "resources/images/menu/bindings.gif")
img_tools_indent = PhotoImage(file = "resources/images/menu/indent.gif")
img_tools_unindent = PhotoImage(file = "resources/images/menu/unindent.gif")
img_tools_notes = PhotoImage(file = "resources/images/menu/notes.gif")
img_tools_collab = PhotoImage(file = "resources/images/menu/collab.gif")
img_tools_sendftp = PhotoImage(file = "resources/images/menu/sendftp.gif")
img_tools_sendemail = PhotoImage(file = "resources/images/menu/sendemail.gif")
img_tools_statistics = PhotoImage(file = "resources/images/menu/statistics.gif")
img_code_openinwebbrowser = PhotoImage(file = "resources/images/menu/openinwebbrowser.gif")
img_code_run_code = PhotoImage(file = "resources/images/menu/runcode.gif")
img_code_compile = PhotoImage(file = "resources/images/menu/compile.gif")
img_opt_options = PhotoImage(file = "resources/images/menu/options.gif")
img_opt_enlarge = PhotoImage(file = "resources/images/menu/enlargefont.gif")
img_opt_shrink = PhotoImage(file = "resources/images/menu/shrinkfont.gif")
img_help_about = PhotoImage(file = "resources/images/menu/about.gif")
img_fold_back = PhotoImage(file = "resources/images/previous2.gif")
img_fold_up = PhotoImage(file = "resources/images/up2.gif")
img_help_about2 = PhotoImage(file = "resources/images/menu/about2.gif")
img_opt_revert = PhotoImage(file = "resources/images/menu/revertdefault.gif")
img_help_report = PhotoImage(file = "resources/images/menu/reportaproblem.gif")
img_browse_newdoc = PhotoImage(file = "resources/images/browser/newdocument.gif")
img_browse_newdir = PhotoImage(file = "resources/images/browser/newfolder.gif")
img_browse_about = PhotoImage(file = "resources/images/browser/about.gif")
img_browse_delete = PhotoImage(file = "resources/images/browser/delete.gif")
img_browse_refresh = PhotoImage(file = "resources/images/browser/refresh.gif")
img_browse_exit = PhotoImage(file = "resources/images/browser/exit.gif")
img_browse_folder = PhotoImage(file = "resources/images/browser/folder.gif")
# Switch back to other directory.
os.chdir(toolbar_temp_dir)

# Determine what images the menus should use.
if CONFIG["menu_images"] == "hide":
    img_file_new = img_blank
    img_file_open = img_blank
    img_file_openfromurl = img_blank
    img_file_reload = img_blank
    img_file_favorites = img_blank
    img_file_save = img_blank
    img_file_saveas = img_blank
    img_file_delete = img_blank
    img_file_print = img_blank
    img_file_exit = img_blank
    img_edit_undo = img_blank
    img_edit_redo = img_blank
    img_edit_cut = img_blank
    img_edit_copy = img_blank
    img_edit_paste = img_blank
    img_edit_selectall = img_blank
    img_documents_new = img_blank
    img_documents_open = img_blank
    img_documents_close = img_blank
    img_documents_previous = img_blank
    img_documents_next = img_blank
    img_documents_viewall = img_blank
    img_search_find = img_blank
    img_search_replace = img_blank
    img_search_goto = img_blank
    img_search_jumptotop = img_blank
    img_search_jumptobottom = img_blank
    img_search_searchselected =img_blank
    img_tools_bookmarks = img_blank
    img_tools_add_bookmark = img_blank
    img_tools_clear_bookmarks = img_blank
    img_tools_macro_run = img_blank
    img_tools_macro_bindings = img_blank
    img_tools_indent = img_blank
    img_tools_unindent = img_blank
    img_tools_notes = img_blank
    img_tools_collab = img_blank
    img_tools_statistics = img_blank
    img_code_openinwebbrowser = img_blank
    img_code_run_code = img_blank
    img_code_compile = img_blank
    img_opt_options = img_blank
    img_opt_enlarge = img_blank
    img_opt_shrink = img_blank
    img_help_about = img_blank
    img_file_browse = img_blank
    img_search_jumplinestart = img_blank
    img_search_jumplineend = img_blank
    img_tools_sendftp = img_blank
    img_tools_sendemail = img_blank
    img_help_about2 = img_blank
    img_help_report = img_blank
    img_opt_revert = img_blank
    img_browse_newdoc = img_blank
    img_browse_newdir = img_blank
    img_browse_about = img_blank
    img_browse_delete = img_blank
    img_browse_refresh = img_blank
    img_browse_exit = img_blank
    img_browse_folder = img_blank

# Determine which images the toolbar should use.
if CONFIG["toolbar_size"] == "small":
    img_new = img_file_new
    img_open = img_file_open
    img_save = img_file_save
    img_previous = img_documents_previous
    img_next = img_documents_next
    img_close = img_documents_close
    img_cut = img_edit_cut
    img_copy = img_edit_copy
    img_paste = img_edit_paste
    img_undo = img_edit_undo
    img_redo = img_edit_redo
    img_search = img_search_find
    img_replace = img_search_replace


# Create the frame containing all widgets.
app = Frame(root)
app.pack(expand = 1, fill = BOTH)
# Show the status bar, if the user wants it.
if CONFIG["status_bar"]:
    # Create the frame for the status bar.
    status_bar = Frame(app, bg = CONFIG["ui_bg"])
    status_bar.pack(side = BOTTOM, expand = NO, fill = X)
    # Create the cursor line label.
    status_line_lbl = Label(status_bar, text = "Line: 1", bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], relief = SUNKEN)
    status_line_lbl.pack(side = LEFT)
    # Create the cursor column label.
    status_col_lbl = Label(status_bar, text = "Col: 1", bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], relief = SUNKEN)
    status_col_lbl.pack(side = LEFT)
    # Create the character statistics label.
    status_chars_lbl = Label(status_bar, text = "Chars: 0", bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], relief = SUNKEN)
    status_chars_lbl.pack(side = LEFT)
    # Create the words statistics label.
    status_words_lbl = Label(status_bar, text = "Words: 0", bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], relief = SUNKEN)
    status_words_lbl.pack(side = LEFT)
    # Create the lines statistics label.
    status_lines_lbl = Label(status_bar, text = "Lines: 1", bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], relief = SUNKEN)
    status_lines_lbl.pack(side = LEFT)
    # Create the text mode label.
    status_mode_lbl = Label(status_bar, text = "INS", bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], relief = SUNKEN)
    status_mode_lbl.pack(side = LEFT)
    # Create the file label.
    status_file_lbl = Label(status_bar, text = "No File (None)", bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], relief = SUNKEN)
    status_file_lbl.pack(side = RIGHT)
# Show the command bar, if the user wants it.
if CONFIG["command_bar"] == "show":
    # Create the frame for the command bar.
    command_bar = Frame(app, bg = CONFIG["ui_bg"])
    command_bar.pack(side = BOTTOM, expand = YES, fill = X)
    # Create the command entry.
    command_bar_ent = Entry(command_bar, bg = CONFIG["bg"], fg = CONFIG["fg"])
    command_bar_ent.pack(side = LEFT, expand = YES, fill = X)
    # Create the Execute button.
    command_bar_btn = Button(command_bar, text = "Execute", bg = CONFIG["ui_bg"], command = command_bar_run)
    command_bar_btn.pack(side = RIGHT)
# Show the toolbar, if the user wants it.
if CONFIG["toolbar"]:
    # Image only:
    if CONFIG["toolbar_type"] == "images only":
        # Create the frame for the toolbar
        toolbar = Frame(app, bg = CONFIG["ui_bg"])
        toolbar.pack(side = TOP, expand = NO, fill = X)
        # Create the New button.
        tb_new_btn = Button(toolbar, image = img_new, relief = FLAT, command = file_new, bg = CONFIG["ui_bg"], highlightthickness = 0)
        tb_new_btn.pack(side = LEFT)
        # Create the Open button.
        tb_open_btn = Button(toolbar, image = img_open, relief = FLAT, command = file_open, bg = CONFIG["ui_bg"], highlightthickness = 0)
        tb_open_btn.pack(side = LEFT)
        # Create the Save button.
        tb_save_btn = Button(toolbar, image = img_save, relief = FLAT, command = file_save, bg = CONFIG["ui_bg"], highlightthickness = 0)
        tb_save_btn.pack(side = LEFT, padx = (0, 20))
        # Create the Previous button.
        tb_previous_btn = Button(toolbar, image = img_previous, relief = FLAT, command = documents_previous, bg = CONFIG["ui_bg"], highlightthickness = 0)
        tb_previous_btn.pack(side = LEFT)
        # Create the Next button.
        tb_next_btn = Button(toolbar, image = img_next, relief = FLAT, command = documents_next, bg = CONFIG["ui_bg"], highlightthickness = 0)
        tb_next_btn.pack(side = LEFT)
        # Create the Close button.
        tb_close_btn = Button(toolbar, image = img_close, relief = FLAT, command = documents_close, bg = CONFIG["ui_bg"], highlightthickness = 0)
        tb_close_btn.pack(side = LEFT, padx = (0, 20))
        # Create the Cut button.
        tb_cut_btn = Button(toolbar, image = img_cut, relief = FLAT, command = edit_cut, bg = CONFIG["ui_bg"], highlightthickness = 0)
        tb_cut_btn.pack(side = LEFT)
        # Create the Copy button.
        tb_copy_btn = Button(toolbar, image = img_copy, relief = FLAT, command = edit_copy, bg = CONFIG["ui_bg"], highlightthickness = 0)
        tb_copy_btn.pack(side = LEFT)
        # Create the Paste button.
        tb_paste_btn = Button(toolbar, image = img_paste, relief = FLAT, command = edit_paste, bg = CONFIG["ui_bg"], highlightthickness = 0)
        tb_paste_btn.pack(side = LEFT, padx = (0, 20))
        # Create the Undo button.
        tb_undo_btn = Button(toolbar, image = img_undo, relief = FLAT, command = edit_undo, bg = CONFIG["ui_bg"], highlightthickness = 0)
        tb_undo_btn.pack(side = LEFT)
        # Create the Redo button.
        tb_redo_btn = Button(toolbar, image = img_redo, relief = FLAT, command = edit_redo, bg = CONFIG["ui_bg"], highlightthickness = 0)
        tb_redo_btn.pack(side = LEFT, padx = (0, 20))
        # Create the Search button.
        tb_search_btn = Button(toolbar, image = img_search, relief = FLAT, command = search_find, bg = CONFIG["ui_bg"], highlightthickness = 0)
        tb_search_btn.pack(side = LEFT)
        # Create the Replace button.
        tb_replace_btn = Button(toolbar, image = img_replace, relief = FLAT, command = search_replace, bg = CONFIG["ui_bg"], highlightthickness = 0)
        tb_replace_btn.pack(side = LEFT)
    # Text only:
    elif CONFIG["toolbar_type"] == "text only":
        # Create the frame for toolbar
        toolbar = Frame(app, bg = CONFIG["ui_bg"])
        toolbar.pack(side = TOP, expand = NO, fill = X)
        # Create the New button.
        tb_new_btn = Button(toolbar, text = "New", relief = FLAT, command = file_new, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_new_btn.pack(side = LEFT)
        # Create the Open button.
        tb_open_btn = Button(toolbar, text = "Open", relief = FLAT, command = file_open, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_open_btn.pack(side = LEFT)
        # Create the Save button.
        tb_save_btn = Button(toolbar, text = "Save", relief = FLAT, command = file_save, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_save_btn.pack(side = LEFT, padx = (0, 20))
        # Create the Previous button.
        tb_previous_btn = Button(toolbar, text = "Previous", relief = FLAT, command = documents_previous, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_previous_btn.pack(side = LEFT)
        # Create the Next button.
        tb_next_btn = Button(toolbar, text = "Next", relief = FLAT, command = documents_next, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_next_btn.pack(side = LEFT)
        # Create the Close button.
        tb_close_btn = Button(toolbar, text = "Close", relief = FLAT, command = documents_close, bg = CONFIG["ui_bg"], highlightthickness = 0)
        tb_close_btn.pack(side = LEFT, padx = (0, 20))
        # Create the Cut button.
        tb_cut_btn = Button(toolbar, text = "Cut", relief = FLAT, command = edit_cut, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_cut_btn.pack(side = LEFT)
        # Create the Copy button.
        tb_copy_btn = Button(toolbar, text = "Copy", relief = FLAT, command = edit_copy, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_copy_btn.pack(side = LEFT)
        # Create the Paste button.
        tb_paste_btn = Button(toolbar, text = "Paste", relief = FLAT, command = edit_paste, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_paste_btn.pack(side = LEFT, padx = (0, 20))
        # Create the Undo button.
        tb_undo_btn = Button(toolbar, text = "Undo", relief = FLAT, command = edit_undo, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_undo_btn.pack(side = LEFT)
        # Create the Redo button.
        tb_redo_btn = Button(toolbar, text = "Redo", relief = FLAT, command = edit_redo, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_redo_btn.pack(side = LEFT, padx = (0, 20))
        # Create the Search button.
        tb_search_btn = Button(toolbar, text = "Search", relief = FLAT, command = search_find, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_search_btn.pack(side = LEFT)
        # Create the Replace button.
        tb_replace_btn = Button(toolbar, text = "Replace", relief = FLAT, command = search_replace, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_replace_btn.pack(side = LEFT)
    # Text and images:
    elif CONFIG["toolbar_type"] == "text and images":
        # Create the frame for toolbar
        toolbar = Frame(app, bg = CONFIG["ui_bg"])
        toolbar.pack(side = TOP, expand = NO, fill = X)
        # Create the New button.
        tb_new_btn = Button(toolbar, image = img_new, compound = CONFIG["toolbar_compound"], text = "New", relief = FLAT, command = file_new, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_new_btn.pack(side = LEFT)
        # Create the Open button.
        tb_open_btn = Button(toolbar, image = img_open, compound = CONFIG["toolbar_compound"], text = "Open", relief = FLAT, command = file_open, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_open_btn.pack(side = LEFT)
        # Create the Save button.
        tb_save_btn = Button(toolbar, image = img_save, compound = CONFIG["toolbar_compound"], text = "Save", relief = FLAT, command = file_save, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_save_btn.pack(side = LEFT, padx = (0, 20))
        # Create the Previous button.
        tb_previous_btn = Button(toolbar, image = img_previous, compound = CONFIG["toolbar_compound"], text = "Previous", relief = FLAT, command = documents_previous, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_previous_btn.pack(side = LEFT)
        # Create the Next button.
        tb_next_btn = Button(toolbar, image = img_next, compound = CONFIG["toolbar_compound"], text = "Next", relief = FLAT, command = documents_next, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_next_btn.pack(side = LEFT)
        # Create the Close button.
        tb_close_btn = Button(toolbar, image = img_close, compound = CONFIG["toolbar_compound"], text = "Close", relief = FLAT, command = documents_close, bg = CONFIG["ui_bg"], highlightthickness = 0)
        tb_close_btn.pack(side = LEFT, padx = (0, 20))
        # Create the Cut button.
        tb_cut_btn = Button(toolbar, image = img_cut, compound = CONFIG["toolbar_compound"], text = "Cut", relief = FLAT, command = edit_cut, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_cut_btn.pack(side = LEFT)
        # Create the Copy button.
        tb_copy_btn = Button(toolbar, image = img_copy, compound = CONFIG["toolbar_compound"], text = "Copy", relief = FLAT, command = edit_copy, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_copy_btn.pack(side = LEFT)
        # Create the Paste button.
        tb_paste_btn = Button(toolbar, image = img_paste, compound = CONFIG["toolbar_compound"], text = "Paste", relief = FLAT, command = edit_paste, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_paste_btn.pack(side = LEFT, padx = (0, 20))
        # Create the Undo button.
        tb_undo_btn = Button(toolbar, image = img_undo, compound = CONFIG["toolbar_compound"], text = "Undo", relief = FLAT, command = edit_undo, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_undo_btn.pack(side = LEFT)
        # Create the Redo button.
        tb_redo_btn = Button(toolbar, image = img_redo, compound = CONFIG["toolbar_compound"], text = "Redo", relief = FLAT, command = edit_redo, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_redo_btn.pack(side = LEFT, padx = (0, 20))
        # Create the Search button.
        tb_search_btn = Button(toolbar, image = img_search, compound = CONFIG["toolbar_compound"], text = "Search", relief = FLAT, command = search_find, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_search_btn.pack(side = LEFT)
        # Create the Replace button.
        tb_replace_btn = Button(toolbar, image = img_replace, compound = CONFIG["toolbar_compound"], text = "Replace", relief = FLAT, command = search_replace, bg = CONFIG["ui_bg"], fg = CONFIG["ui_fg"], highlightthickness = 0, padx = 2)
        tb_replace_btn.pack(side = LEFT)

# Create the frame for the text box and document list.
app2 = Frame(app)
app2.pack(expand = 1, fill = BOTH)
# Show the documents list, if the user wants it.
if CONFIG["documents_list"] == "show":
    # Create the document list and scrollbar.
    app3 = Frame(app2)
    app3.pack(fill = Y, side = LEFT)
    documents_list = Listbox(app3, bg = CONFIG["bg"], fg = CONFIG["fg"], relief = SUNKEN, width = int(CONFIG["documents_list_width"]))
    documents_scroll = Scrollbar(app3)
    documents_scroll.config(command = documents_list.yview)
    documents_list.config(yscrollcommand = documents_scroll.set)
    documents_scroll.pack(side = RIGHT, fill = Y)
    documents_list.pack(side = LEFT, expand = YES, fill = BOTH)
# Show the main text box and scrollbars.
# Also show line numbers, if the user wants it.
if CONFIG["line_numbers"]:
    text_box = TextboxLN(app2)
    text_box.frame.pack(side = TOP)
else:
    text_box = Textbox(app2)
    text_box.frame.pack(side = TOP)

# Give the text box focus.
text_box.text_box.focus()

# Bind events.
# Bind the return/enter event to auto-indent, if the user wants that.
text_box.text_box.bind("<Return>", check_newline_space)
# Bind the tab event to auto-replace tabs
text_box.text_box.bind("<Tab>", check_tab)
# Bind the "Help" window to F1.
text_box.text_box.bind("<F1>", lambda event: help_help())
# Bind a general keypress to check if the text has modified.
text_box.text_box.bind("<Key>", check_modified)
# Bind the Home key for "smart" home.
text_box.text_box.bind("<Home>", check_home)
# Bind the End key for "smart" end.
text_box.text_box.bind("<End>", check_end)
# Bind the Escape key.
text_box.text_box.bind("<Escape>", check_escape)
# Bind the Insert key for toggling insert and overwrite mode.
text_box.text_box.bind("<Insert>", check_insert)
# Bind the PageUp and PageDown keys for scrolling up or down.
text_box.text_box.bind("<Prior>", check_page_up)
text_box.text_box.bind("<Next>", check_page_down)
# Bind events for updating status bar labels.
text_box.text_box.bind("<Button-1>", lambda event: update_status())
text_box.text_box.bind("<B1-Motion>", lambda event: update_status())
text_box.text_box.bind("<ButtonRelease-1>", lambda event: update_status())
text_box.text_box.bind("<KeyRelease>", lambda event: update_status())
# Bind the rest of the keyboard shortcuts.
text_box.text_box.bind("<Control-Key-n>", lambda event: file_new())
text_box.text_box.bind("<Control-Key-o>", lambda event: file_open())
text_box.text_box.bind("<Control-space>", lambda event: file_quick_open())
text_box.text_box.bind("<Control-Alt-space>", lambda event: file_favorites())
text_box.text_box.bind("<Control-Key-s>", lambda event: file_save())
text_box.text_box.bind("<Shift-Control-Key-S>", lambda event: file_save(mode = "saveas"))
text_box.text_box.bind("<Alt-Control-Key-s>", lambda event: file_save_copy())
text_box.text_box.bind("<F4>", lambda event: file_browse())
text_box.text_box.bind("<F10>", lambda event: file_rename())
text_box.text_box.bind("<F11>", lambda event: file_delete())
text_box.text_box.bind("<Control-Key-p>", lambda event: file_print())
text_box.text_box.bind("<Control-Key-q>", lambda event: file_exit())
text_box.text_box.bind("<Control-Key-z>", lambda event: edit_undo())
text_box.text_box.bind("<Shift-Control-Key-Z>", lambda event: edit_redo())
text_box.text_box.bind("<Control-Key-y>", lambda event: edit_redo())
text_box.text_box.bind("<Control-Key-x>", lambda event: edit_cut())
text_box.text_box.bind("<Control-Key-c>", lambda event: edit_copy())
text_box.text_box.bind("<Control-Key-v>", lambda event: edit_paste())
text_box.text_box.bind("<Shift-Control-Key-V>", lambda event: edit_paste_overwrite())
text_box.text_box.bind("<Alt-Control-Key-v>", lambda event: edit_paste_indent())
text_box.text_box.bind("<Control-Key-a>", lambda event: edit_select_all())
text_box.text_box.bind("<Shift-Control-Key-A>", lambda event: edit_deselect_all())
text_box.text_box.bind("<Shift-Control-Key-N>", lambda event: documents_new())
text_box.text_box.bind("<Shift-Control-Key-O>", lambda event: documents_open())
text_box.text_box.bind("<Shift-Control-Key-Q>", lambda event: documents_close())
text_box.text_box.bind("<Alt-Left>", lambda event: documents_previous())
text_box.text_box.bind("<Shift-Control-Tab>", lambda event: documents_previous())
text_box.text_box.bind("<Alt-Right>", lambda event: documents_next())
text_box.text_box.bind("<Control-Tab>", lambda event: documents_next())
text_box.text_box.bind("<Control-Key-m>", lambda event: documents_view())
text_box.text_box.bind("<Control-Key-f>", lambda event: search_find())
text_box.text_box.bind("<Shift-Control-Key-F>", lambda event: search_find_selected())
text_box.text_box.bind("<Control-Key-h>", lambda event: search_replace())
text_box.text_box.bind("<Shift-Control-Key-H>", lambda event: search_replace_selected())
text_box.text_box.bind("<Control-Key-w>", lambda event: search_find_history())
text_box.text_box.bind("<Shift-Control-Key-W>", lambda event: search_replace_history())
text_box.text_box.bind("<Control-Key-g>", lambda event: search_goto())
text_box.text_box.bind("<Control-Key-l>", lambda event: search_goto())
text_box.text_box.bind("<Control-Key-b>", lambda event: tools_bookmarks_add())
text_box.text_box.bind("<Shift-Control-Key-B>", lambda event: tools_bookmarks_view())
text_box.text_box.bind("<Control-Key-r>", lambda event: tools_macro_run())
text_box.text_box.bind("<Shift-Control-Key-R>", lambda event: tools_run_command())
text_box.text_box.bind("<Shift-Control-Key-T>", lambda event: tools_insert_time())
text_box.text_box.bind("<Shift-Control-Key-D>", lambda event: tools_insert_date())
text_box.text_box.bind("<Control-Key-i>", lambda event: tools_indent())
text_box.text_box.bind("<Shift-Control-Key-I>", lambda event: tools_unindent())
text_box.text_box.bind("<Control-Key-j>", lambda event: tools_notes())
text_box.text_box.bind("<Shift-Control-Key-J>", lambda event: tools_tasks())
text_box.text_box.bind("<Control-Key-e>", lambda event: tools_collab())
text_box.text_box.bind("<Control-Key-u>", lambda event: tools_upload_pastebin())
text_box.text_box.bind("<Shift-Control-Key-U>", lambda event: tools_download_pastebin())
text_box.text_box.bind("<F2>", lambda event: tools_statistics())
text_box.text_box.bind("<F3>", lambda event: opt_options())
text_box.text_box.bind("<F5>", lambda event: file_reload())
text_box.text_box.bind("<F6>", lambda event: search_jump_top())
text_box.text_box.bind("<F7>", lambda event: search_jump_bottom())
text_box.text_box.bind("<F8>", lambda event: internal_return_focus())
text_box.text_box.bind("<Control-Key-F1>", lambda event: help_about())
text_box.text_box.bind("<Control-Key-Up>", lambda event: opt_font_size(True))
text_box.text_box.bind("<Control-Key-Down>", lambda event: opt_font_size(False))
# Bind document list events.
if CONFIG["documents_list"] == "show":
    documents_list.bind("<Double-1>", lambda event: documents_list_update())
    documents_list.bind("<Return>", lambda event: documents_list_update())
# Bind right-clicks on buttons.
if CONFIG["toolbar"]:
    tb_new_btn.bind("<Button-3>", lambda event: showinfo("Help", "Opens a new file."))
    tb_open_btn.bind("<Button-3>", lambda event: showinfo("Help", "Opens a file."))
    tb_save_btn.bind("<Button-3>", lambda event: showinfo("Help", "Saves the current file."))
    tb_previous_btn.bind("<Button-3>", lambda event: showinfo("Help", "Switches to the previous document."))
    tb_next_btn.bind("<Button-3>", lambda event: showinfo("Help", "Switches to the next document."))
    tb_close_btn.bind("<Button-3>", lambda event: showinfo("Help", "Closes the current document."))
    tb_undo_btn.bind("<Button-3>", lambda event: showinfo("Help", "Undoes the last change"))
    tb_redo_btn.bind("<Button-3>", lambda event: showinfo("Help", "Redoes the last undo."))
    tb_cut_btn.bind("<Button-3>", lambda event: showinfo("Help", "Cuts the selected text."))
    tb_copy_btn.bind("<Button-3>", lambda event: showinfo("Help", "Copies the selected text."))
    tb_paste_btn.bind("<Button-3>", lambda event: showinfo("Help", "Pastes the text in the clipboard."))
    tb_search_btn.bind("<Button-3>", lambda event: showinfo("Help", "Searches for text."))
    tb_replace_btn.bind("<Button-3>", lambda event: showinfo("Help", "Replaces text."))
    tb_new_btn.bind("<Control-Button-1>", lambda event: showinfo("Help", "Opens a new file."))
    tb_open_btn.bind("<Control-Button-1>", lambda event: showinfo("Help", "Opens a file."))
    tb_save_btn.bind("<Control-Button-1>", lambda event: showinfo("Help", "Saves the current file."))
    tb_previous_btn.bind("<Control-Button-1>", lambda event: showinfo("Help", "Switches to the previous document."))
    tb_next_btn.bind("<Control-Button-1>", lambda event: showinfo("Help", "Switches to the next document."))
    tb_close_btn.bind("<Control-Button-1>", lambda event: showinfo("Help", "Closes the current document."))
    tb_undo_btn.bind("<Control-Button-1>", lambda event: showinfo("Help", "Undoes the last change"))
    tb_redo_btn.bind("<Control-Button-1>", lambda event: showinfo("Help", "Redoes the last undo."))
    tb_cut_btn.bind("<Control-Button-1>", lambda event: showinfo("Help", "Cuts the selected text."))
    tb_copy_btn.bind("<Control-Button-1>", lambda event: showinfo("Help", "Copies the selected text."))
    tb_paste_btn.bind("<Control-Button-1>", lambda event: showinfo("Help", "Pastes the text in the clipboard."))
    tb_search_btn.bind("<Control-Button-1>", lambda event: showinfo("Help", "Searches for text."))
    tb_replace_btn.bind("<Control-Button-1>", lambda event: showinfo("Help", "Replaces text."))
# Bind right-clicks on status bar labels.
if CONFIG["status_bar"]:
    status_line_lbl.bind("<Button-3>", lambda event: showinfo("Help", "Shows the current line number."))
    status_col_lbl.bind("<Button-3>", lambda event: showinfo("Help", "Shows the current character position."))
    status_chars_lbl.bind("<Button-3>", lambda event: showinfo("Help", "Shows the number of characters."))
    status_words_lbl.bind("<Button-3>", lambda event: showinfo("Help", "Shows the number of words."))
    status_lines_lbl.bind("<Button-3>", lambda event: showinfo("Help", "Shows the number of lines."))
    status_mode_lbl.bind("<Button-3>", lambda event: showinfo("Help", "Shows whether the cursor is in insert (INS) or overwrite (OVER) mode."))
    status_file_lbl.bind("<Button-3>", lambda event: showinfo("Help", "Shows the current file and encoding."))
    status_line_lbl.bind("<Control-Button-1>", lambda event: showinfo("Help", "Shows the current line number."))
    status_col_lbl.bind("<Control-Button-1>", lambda event: showinfo("Help", "Shows the current character position."))
    status_chars_lbl.bind("<Control-Button-1>", lambda event: showinfo("Help", "Shows the number of characters."))
    status_words_lbl.bind("<Control-Button-1>", lambda event: showinfo("Help", "Shows the number of words."))
    status_lines_lbl.bind("<Control-Button-1>", lambda event: showinfo("Help", "Shows the number of lines."))
    status_mode_lbl.bind("<Control-Button-1>", lambda event: showinfo("Help", "Shows whether the cursor is in insert (INS) or overwrite (OVER) mode."))
    status_file_lbl.bind("<Control-Button-1>", lambda event: showinfo("Help", "Shows the current file and encoding."))
# Bind command bar events.
if CONFIG["command_bar"] == "show":
    command_bar_ent.bind("<Return>", lambda event: command_bar_run())
    command_bar_ent.bind("<Alt-Return>", lambda event: command_bar_focus("text"))
    text_box.text_box.bind("<Alt-Return>", lambda event: command_bar_focus("entry"))
# Bind line number events.
if CONFIG["line_numbers"]:
    text_box.line_text.bind("<Button-1>", lambda event: line_number_click())
    text_box.line_text.bind("<Button-3>", lambda event: line_number_click())
# Bind middle-clicks to edit_paste().
text_box.text_box.bind("<Button-2>", lambda event: edit_paste())

# Bind Control+MouseWheel events for changing the font size.
text_box.text_box.bind("<Control-Button-4>", opt_font_size_scroll)
text_box.text_box.bind("<Control-Button-5>", opt_font_size_scroll)
text_box.text_box.bind("<Control-MouseWheel>", opt_font_size_scroll_win)

# Bind Alt+MouseWheel events for scrolling by larger amounts.
text_box.text_box.bind("<Alt-Button-4>", check_alt_scroll)
text_box.text_box.bind("<Alt-Button-5>", check_alt_scroll)
text_box.text_box.bind("<Alt-MouseWheel>", check_alt_scroll_win)
# Bind Alt+Up/Down Arrow events for scrolling by larger amounts.
text_box.text_box.bind("<Alt-Up>", lambda event: check_alt_arrow("up"))
text_box.text_box.bind("<Alt-Down>", lambda event: check_alt_arrow("down"))

# Bind macros.
if gbl_mac_bindings[0]:
    text_box.text_box.bind("<Control-Key-1>", lambda event: tools_macro_run_file(gbl_mac_bindings[0]))
if gbl_mac_bindings[1]:
    text_box.text_box.bind("<Control-Key-2>", lambda event: tools_macro_run_file(gbl_mac_bindings[1]))
if gbl_mac_bindings[2]:
    text_box.text_box.bind("<Control-Key-3>", lambda event: tools_macro_run_file(gbl_mac_bindings[2]))
if gbl_mac_bindings[3]:
    text_box.text_box.bind("<Control-Key-4>", lambda event: tools_macro_run_file(gbl_mac_bindings[3]))
if gbl_mac_bindings[4]:
    text_box.text_box.bind("<Control-Key-5>", lambda event: tools_macro_run_file(gbl_mac_bindings[4]))
if gbl_mac_bindings[5]:
    text_box.text_box.bind("<Control-Key-6>", lambda event: tools_macro_run_file(gbl_mac_bindings[5]))
if gbl_mac_bindings[6]:
    text_box.text_box.bind("<Control-Key-7>", lambda event: tools_macro_run_file(gbl_mac_bindings[6]))
if gbl_mac_bindings[7]:
    text_box.text_box.bind("<Control-Key-8>", lambda event: tools_macro_run_file(gbl_mac_bindings[7]))
if gbl_mac_bindings[8]:
    text_box.text_box.bind("<Control-Key-9>", lambda event: tools_macro_run_file(gbl_mac_bindings[8]))
if gbl_mac_bindings[9]:
    text_box.text_box.bind("<Control-Key-0>", lambda event: tools_macro_run_file(gbl_mac_bindings[9]))

if CONFIG["menu_bar"] == "show":
    # Show the menu bar.
    menu = Menu(root)
    root.config(menu = menu)
    
    if CONFIG["menu_file"] == "show":
        # Create the File menu.
        file_menu = Menu(menu, tearoff = CONFIG["tearoff"])
        menu.add_cascade(label = "File", menu = file_menu, underline = 0)
        file_menu.add_command(label = "New", image = img_file_new, compound = LEFT, underline = 0, command = file_new, accelerator = "Ctrl+N")
        file_menu.add_command(label = "Open...", image = img_file_open, compound = LEFT, underline = 0, command = file_open, accelerator = "Ctrl+O")
        # Create the File -> Open with Encoding submenu.
        file_owe_menu = Menu(tearoff = CONFIG["tearoff"])
        file_menu.add_cascade(label = "Open with Encoding", image = img_blank, compound = LEFT, menu = file_owe_menu, underline = 5)
        # Create the File -> Open with Encoding -> Unicode submenu.
        file_owe_uni_menu = Menu(tearoff = CONFIG["tearoff"])
        file_owe_menu.add_cascade(label = "Unicode", image = img_blank, compound = LEFT, menu = file_owe_uni_menu, underline = 0)
        file_owe_uni_menu.add_command(label = "UTF-8 (utf-8)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "utf-8"))
        file_owe_uni_menu.add_command(label = "UTF-8 with BOM (utf-8-sig)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "utf-8-sig"))
        file_owe_uni_menu.add_command(label = "UTF-16 (utf-16)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "utf-16"))
        file_owe_uni_menu.add_command(label = "UTF-16 BE (utf-16-be)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "utf-16-be"))
        file_owe_uni_menu.add_command(label = "UTF-16 LE (utf-16-le)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "utf-16-le"))
        file_owe_uni_menu.add_command(label = "UTF-32 (utf-32)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "utf-32"))
        file_owe_uni_menu.add_command(label = "UTF-32 BE (utf-32-be)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "utf-32-be"))
        file_owe_uni_menu.add_command(label = "UTF-32 LE (utf-32-le)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "utf-32-le"))
        file_owe_menu.add_command(label = "Other...", image = img_blank, compound = LEFT, command = file_open_encoding)
        file_owe_menu.add_separator()
        # Create the File -> Open with Encoding -> Arabic submenu.
        file_owe_ar_menu = Menu(tearoff = CONFIG["tearoff"])
        file_owe_menu.add_cascade(label = "Arabic", image = img_blank, compound = LEFT, menu = file_owe_ar_menu, underline = 0)
        file_owe_ar_menu.add_command(label = "Arabic (cp864)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp864"))
        file_owe_ar_menu.add_command(label = "Arabic (cp1256)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp1256"))
        file_owe_ar_menu.add_command(label = "Arabic (iso8859_6)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "iso8859_6"))
        # Create the File -> Open with Encoding -> Baltic Languages submenu.
        file_owe_ba_menu = Menu(tearoff = CONFIG["tearoff"])
        file_owe_menu.add_cascade(label = "Baltic Languages", image = img_blank, compound = LEFT, menu = file_owe_ba_menu, underline = 0)
        file_owe_ba_menu.add_command(label = "Baltic Languages (cp775)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp775"))
        file_owe_ba_menu.add_command(label = "Baltic Languages (cp1257)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp1257"))
        file_owe_ba_menu.add_command(label = "Baltic Languages (iso8859_4)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "iso8859_4"))
        file_owe_ba_menu.add_command(label = "Baltic Languages (iso8859_13)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "iso8859_13"))
        # Create the File -> Open with Encoding -> Central European Languages submenu.
        file_owe_ce_menu = Menu(tearoff = CONFIG["tearoff"])
        file_owe_menu.add_cascade(label = "Central European Languages", image = img_blank, compound = LEFT, menu = file_owe_ce_menu, underline = 0)
        file_owe_ce_menu.add_command(label = "Central European Languages (cp852)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp852"))
        file_owe_ce_menu.add_command(label = "Central European Languages (cp1250)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp1250"))
        file_owe_ce_menu.add_command(label = "Central European Languages (iso8859_2)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "iso8859_2"))
        file_owe_ce_menu.add_command(label = "Central European Languages (mac_latin2)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "mac_latin2"))
        # Create the File -> Open with Encoding -> Chinese submenu.
        file_owe_ch_menu = Menu(tearoff = CONFIG["tearoff"])
        file_owe_menu.add_cascade(label = "Chinese", image = img_blank, compound = LEFT, menu = file_owe_ch_menu, underline = 1)
        file_owe_ch_menu.add_command(label = "Chinese Traditional (big5)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "big5"))
        file_owe_ch_menu.add_command(label = "Chinese Traditional (big5hkscs)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "big5hkscs"))
        file_owe_ch_menu.add_command(label = "Chinese Traditional (cp950)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp950"))
        file_owe_ch_menu.add_command(label = "Chinese Simplified (gb2312)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "gb2312"))
        file_owe_ch_menu.add_command(label = "Chinese Simplified (hz)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "hz"))
        file_owe_ch_menu.add_command(label = "Chinese Unified (gbk)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "gbk"))
        file_owe_ch_menu.add_command(label = "Chinese Unified (gb18030)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "gb18030"))
        # Create the File -> Open with Encoding -> Cyrillic submenu.
        file_owe_cy_menu = Menu(tearoff = CONFIG["tearoff"])
        file_owe_menu.add_cascade(label = "Cyrillic", image = img_blank, compound = LEFT, menu = file_owe_cy_menu, underline = 1)
        file_owe_cy_menu.add_command(label = "Cyrillic (iso8859_5)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "iso8859_5"))
        file_owe_cy_menu.add_command(label = "Cyrillic (mac_cyrillic)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "mac_cyrillic"))
        file_owe_cy_menu.add_command(label = "Cyrillic (ptcp154)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "ptcp154"))
        file_owe_cy_menu.add_command(label = "Cyrillic (cp866)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp866"))
        file_owe_cy_menu.add_command(label = "Cyrillic (cp1251)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp1251"))
        file_owe_cy_menu.add_command(label = "Cyrillic (iso8859_5)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "iso8859_5"))
        file_owe_cy_menu.add_command(label = "Cyrillic (koi8_r)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "koi8_r"))
        file_owe_cy_menu.add_command(label = "Cyrillic (koi8_u)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "koi8_u"))
        # Create the File -> Open with Encoding -> Greek submenu.
        file_owe_gr_menu = Menu(tearoff = CONFIG["tearoff"])
        file_owe_menu.add_cascade(label = "Greek", image = img_blank, compound = LEFT, menu = file_owe_gr_menu, underline = 0)
        file_owe_gr_menu.add_command(label = "Greek (cp737)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp737"))
        file_owe_gr_menu.add_command(label = "Greek (cp869)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp869"))
        file_owe_gr_menu.add_command(label = "Greek (cp875)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp875"))
        file_owe_gr_menu.add_command(label = "Greek (cp1253)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp1253"))
        file_owe_gr_menu.add_command(label = "Greek (iso8859_7)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "iso8859_7"))
        file_owe_gr_menu.add_command(label = "Greek (mac_greek)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "mac_greek"))
        # Create the File -> Open with Encoding -> Hebrew submenu.
        file_owe_he_menu = Menu(tearoff = CONFIG["tearoff"])
        file_owe_menu.add_cascade(label = "Hebrew", image = img_blank, compound = LEFT, menu = file_owe_he_menu, underline = 0)
        file_owe_he_menu.add_command(label = "Hebrew (cp424)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp424"))
        file_owe_he_menu.add_command(label = "Hebrew (cp856)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp856"))
        file_owe_he_menu.add_command(label = "Hebrew (cp862)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp862"))
        file_owe_he_menu.add_command(label = "Hebrew (cp1255)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp1255"))
        file_owe_he_menu.add_command(label = "Hebrew (iso8859_8)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "iso8859_8"))
        # Create the File -> Open with Encoding -> Japanese submenu.
        file_owe_ja_menu = Menu(tearoff = CONFIG["tearoff"])
        file_owe_menu.add_cascade(label = "Japanese", image = img_blank, compound = LEFT, menu = file_owe_ja_menu, underline = 0)
        file_owe_ja_menu.add_command(label = "Japanese (cp932)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp932"))
        file_owe_ja_menu.add_command(label = "Japanese (euc_jp)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "euc_jp"))
        file_owe_ja_menu.add_command(label = "Japanese (euc_jis_2004)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "euc_jis_2004"))
        file_owe_ja_menu.add_command(label = "Japanese (euc_jisx0213)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "euc_jisx0213"))
        file_owe_ja_menu.add_command(label = "Japanese (iso2022_jp)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "iso2022_jp"))
        file_owe_ja_menu.add_command(label = "Japanese (iso2022_jp_1)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "iso2022_jp_1"))
        file_owe_ja_menu.add_command(label = "Japanese (iso2022_jp_2)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "iso2022_jp_2"))
        file_owe_ja_menu.add_command(label = "Japanese (iso2022_jp_2004)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "iso2022_jp_2004"))
        file_owe_ja_menu.add_command(label = "Japanese (iso2022_jp_3)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "iso2022_jp_3"))
        file_owe_ja_menu.add_command(label = "Japanese (iso2022_jp_ext)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "iso2022_jp_ext"))
        file_owe_ja_menu.add_command(label = "Japanese (shift_jis)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "shift_jis"))
        file_owe_ja_menu.add_command(label = "Japanese (shift_jis_2004)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "shift_jis_2004"))
        file_owe_ja_menu.add_command(label = "Japanese (shift_jisx0213)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "shift_jisx0213"))
        # Create the File -> Open with Encoding -> Korean submenu.
        file_owe_ko_menu = Menu(tearoff = CONFIG["tearoff"])
        file_owe_menu.add_cascade(label = "Korean", image = img_blank, compound = LEFT, menu = file_owe_ko_menu, underline = 0)
        file_owe_ko_menu.add_command(label = "Korean (cp949)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp949"))
        file_owe_ko_menu.add_command(label = "Korean (euc_kr)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "euc_kr"))
        file_owe_ko_menu.add_command(label = "Korean (iso2022_kr)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "iso2022_kr"))
        file_owe_ko_menu.add_command(label = "Korean (johab)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "johab"))
        # Create the File -> Open with Encoding -> South-East Asian Languages submenu.
        file_owe_se_menu = Menu(tearoff = CONFIG["tearoff"])
        file_owe_menu.add_cascade(label = "South-East Asian Languages", image = img_blank, compound = LEFT, menu = file_owe_se_menu, underline = 0)
        file_owe_se_menu.add_command(label = "Thai (cp874)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp874"))
        file_owe_se_menu.add_command(label = "Vietnamese (cp1258)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp1258"))
        # Create the File -> Open with Encoding -> Turkish submenu.
        file_owe_se_menu = Menu(tearoff = CONFIG["tearoff"])
        file_owe_menu.add_cascade(label = "Turkish", image = img_blank, compound = LEFT, menu = file_owe_se_menu, underline = 0)
        file_owe_se_menu.add_command(label = "Turkish (cp857)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp857"))
        file_owe_se_menu.add_command(label = "Turkish (cp1026)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp1026"))
        file_owe_se_menu.add_command(label = "Turkish (cp1254)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp1254"))
        file_owe_se_menu.add_command(label = "Turkish (iso8859_9)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "iso8859_9"))
        file_owe_se_menu.add_command(label = "Turkish (mac_turkish)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "mac_turkish"))
        # Create the File -> Open with Encoding -> Western European submenu.
        file_owe_we_menu = Menu(tearoff = CONFIG["tearoff"])
        file_owe_menu.add_cascade(label = "Western European Languages", image = img_blank, compound = LEFT, menu = file_owe_we_menu, underline = 0)
        file_owe_we_menu.add_command(label = "Western European (latin_1)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "latin_1"))
        file_owe_we_menu.add_command(label = "Western European (ascii)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "ascii"))
        file_owe_we_menu.add_command(label = "Western European (cp037)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp037"))
        file_owe_we_menu.add_command(label = "Western European (cp437)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp437"))
        file_owe_we_menu.add_command(label = "Western European (cp500)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp500"))
        file_owe_we_menu.add_command(label = "Western European (cp850)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp850"))
        file_owe_we_menu.add_command(label = "Western European (cp1140)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp1140"))
        file_owe_we_menu.add_command(label = "Western European (cp1252)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "cp1252"))
        file_owe_we_menu.add_command(label = "Western European (iso8859_15)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "iso8859_15"))
        file_owe_we_menu.add_command(label = "Western European (mac_roman)", image = img_blank, compound = LEFT, command = lambda: file_open_encoding(encoding = "mac_roman"))
        file_menu.add_command(label = "Quick Open...", image = img_blank, compound = LEFT, underline = 0, command = file_quick_open, accelerator = "Ctrl+[Space]")
        file_menu.add_command(label = "Open from URL...", image = img_file_openfromurl, compound = LEFT, underline = 10, command = file_open_url)
        file_menu.add_command(label = "Open from Selection", image = img_blank, compound = LEFT, underline = 5, command = file_open_sel)
        file_menu.add_command(label = "Reload", image = img_file_reload, compound = LEFT, underline = 1, command = file_reload, accelerator = "F5")
        # Create the File -> Reload with Encoding submenu.
        file_rwe_menu = Menu(tearoff = CONFIG["tearoff"])
        file_menu.add_cascade(label = "Reload with Encoding", image = img_blank, compound = LEFT, menu = file_rwe_menu, underline = 9)
        # Create the File -> Reload with Encoding -> Unicode submenu.
        file_rwe_uni_menu = Menu(tearoff = CONFIG["tearoff"])
        file_rwe_menu.add_cascade(label = "Unicode", image = img_blank, compound = LEFT, menu = file_rwe_uni_menu, underline = 0)
        file_rwe_uni_menu.add_command(label = "UTF-8 (utf-8)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "utf-8"))
        file_rwe_uni_menu.add_command(label = "UTF-8 with BOM (utf-8-sig)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "utf-8-sig"))
        file_rwe_uni_menu.add_command(label = "UTF-16 (utf-16)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "utf-16"))
        file_rwe_uni_menu.add_command(label = "UTF-16 BE (utf-16-be)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "utf-16-be"))
        file_rwe_uni_menu.add_command(label = "UTF-16 LE (utf-16-le)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "utf-16-le"))
        file_rwe_uni_menu.add_command(label = "UTF-32 (utf-32)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "utf-32"))
        file_rwe_uni_menu.add_command(label = "UTF-32 BE (utf-32-be)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "utf-32-be"))
        file_rwe_uni_menu.add_command(label = "UTF-32 LE (utf-32-le)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "utf-32-le"))
        file_rwe_menu.add_command(label = "Other...", image = img_blank, compound = LEFT, command = file_reload_encoding)
        file_rwe_menu.add_separator()
        # Create the File -> Reload with Encoding -> Arabic submenu.
        file_rwe_ar_menu = Menu(tearoff = CONFIG["tearoff"])
        file_rwe_menu.add_cascade(label = "Arabic", image = img_blank, compound = LEFT, menu = file_rwe_ar_menu, underline = 0)
        file_rwe_ar_menu.add_command(label = "Arabic (cp864)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp864"))
        file_rwe_ar_menu.add_command(label = "Arabic (cp1256)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp1256"))
        file_rwe_ar_menu.add_command(label = "Arabic (iso8859_6)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "iso8859_6"))
        # Create the File -> Reload with Encoding -> Baltic Languages submenu.
        file_rwe_ba_menu = Menu(tearoff = CONFIG["tearoff"])
        file_rwe_menu.add_cascade(label = "Baltic Languages", image = img_blank, compound = LEFT, menu = file_rwe_ba_menu, underline = 0)
        file_rwe_ba_menu.add_command(label = "Baltic Languages (cp775)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp775"))
        file_rwe_ba_menu.add_command(label = "Baltic Languages (cp1257)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp1257"))
        file_rwe_ba_menu.add_command(label = "Baltic Languages (iso8859_4)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "iso8859_4"))
        file_rwe_ba_menu.add_command(label = "Baltic Languages (iso8859_13)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "iso8859_13"))
        # Create the File -> Reload with Encoding -> Central European Languages submenu.
        file_rwe_ce_menu = Menu(tearoff = CONFIG["tearoff"])
        file_rwe_menu.add_cascade(label = "Central European Languages", image = img_blank, compound = LEFT, menu = file_rwe_ce_menu, underline = 0)
        file_rwe_ce_menu.add_command(label = "Central European Languages (cp852)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp852"))
        file_rwe_ce_menu.add_command(label = "Central European Languages (cp1250)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp1250"))
        file_rwe_ce_menu.add_command(label = "Central European Languages (iso8859_2)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "iso8859_2"))
        file_rwe_ce_menu.add_command(label = "Central European Languages (mac_latin2)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "mac_latin2"))
        # Create the File -> Reload with Encoding -> Chinese submenu.
        file_rwe_ch_menu = Menu(tearoff = CONFIG["tearoff"])
        file_rwe_menu.add_cascade(label = "Chinese", image = img_blank, compound = LEFT, menu = file_rwe_ch_menu, underline = 1)
        file_rwe_ch_menu.add_command(label = "Chinese Traditional (big5)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "big5"))
        file_rwe_ch_menu.add_command(label = "Chinese Traditional (big5hkscs)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "big5hkscs"))
        file_rwe_ch_menu.add_command(label = "Chinese Traditional (cp950)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp950"))
        file_rwe_ch_menu.add_command(label = "Chinese Simplified (gb2312)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "gb2312"))
        file_rwe_ch_menu.add_command(label = "Chinese Simplified (hz)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "hz"))
        file_rwe_ch_menu.add_command(label = "Chinese Unified (gbk)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "gbk"))
        file_rwe_ch_menu.add_command(label = "Chinese Unified (gb18030)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "gb18030"))
        # Create the File -> Reload with Encoding -> Cyrillic submenu.
        file_rwe_cy_menu = Menu(tearoff = CONFIG["tearoff"])
        file_rwe_menu.add_cascade(label = "Cyrillic", image = img_blank, compound = LEFT, menu = file_rwe_cy_menu, underline = 1)
        file_rwe_cy_menu.add_command(label = "Cyrillic (iso8859_5)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "iso8859_5"))
        file_rwe_cy_menu.add_command(label = "Cyrillic (mac_cyrillic)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "mac_cyrillic"))
        file_rwe_cy_menu.add_command(label = "Cyrillic (ptcp154)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "ptcp154"))
        file_rwe_cy_menu.add_command(label = "Cyrillic (cp866)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp866"))
        file_rwe_cy_menu.add_command(label = "Cyrillic (cp1251)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp1251"))
        file_rwe_cy_menu.add_command(label = "Cyrillic (iso8859_5)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "iso8859_5"))
        file_rwe_cy_menu.add_command(label = "Cyrillic (koi8_r)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "koi8_r"))
        file_rwe_cy_menu.add_command(label = "Cyrillic (koi8_u)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "koi8_u"))
        # Create the File -> Reload with Encoding -> Greek submenu.
        file_rwe_gr_menu = Menu(tearoff = CONFIG["tearoff"])
        file_rwe_menu.add_cascade(label = "Greek", image = img_blank, compound = LEFT, menu = file_rwe_gr_menu, underline = 0)
        file_rwe_gr_menu.add_command(label = "Greek (cp737)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp737"))
        file_rwe_gr_menu.add_command(label = "Greek (cp869)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp869"))
        file_rwe_gr_menu.add_command(label = "Greek (cp875)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp875"))
        file_rwe_gr_menu.add_command(label = "Greek (cp1253)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp1253"))
        file_rwe_gr_menu.add_command(label = "Greek (iso8859_7)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "iso8859_7"))
        file_rwe_gr_menu.add_command(label = "Greek (mac_greek)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "mac_greek"))
        # Create the File -> Reload with Encoding -> Hebrew submenu.
        file_rwe_he_menu = Menu(tearoff = CONFIG["tearoff"])
        file_rwe_menu.add_cascade(label = "Hebrew", image = img_blank, compound = LEFT, menu = file_rwe_he_menu, underline = 0)
        file_rwe_he_menu.add_command(label = "Hebrew (cp424)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp424"))
        file_rwe_he_menu.add_command(label = "Hebrew (cp856)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp856"))
        file_rwe_he_menu.add_command(label = "Hebrew (cp862)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp862"))
        file_rwe_he_menu.add_command(label = "Hebrew (cp1255)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp1255"))
        file_rwe_he_menu.add_command(label = "Hebrew (iso8859_8)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "iso8859_8"))
        # Create the File -> Reload with Encoding -> Japanese submenu.
        file_rwe_ja_menu = Menu(tearoff = CONFIG["tearoff"])
        file_rwe_menu.add_cascade(label = "Japanese", image = img_blank, compound = LEFT, menu = file_rwe_ja_menu, underline = 0)
        file_rwe_ja_menu.add_command(label = "Japanese (cp932)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp932"))
        file_rwe_ja_menu.add_command(label = "Japanese (euc_jp)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "euc_jp"))
        file_rwe_ja_menu.add_command(label = "Japanese (euc_jis_2004)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "euc_jis_2004"))
        file_rwe_ja_menu.add_command(label = "Japanese (euc_jisx0213)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "euc_jisx0213"))
        file_rwe_ja_menu.add_command(label = "Japanese (iso2022_jp)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "iso2022_jp"))
        file_rwe_ja_menu.add_command(label = "Japanese (iso2022_jp_1)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "iso2022_jp_1"))
        file_rwe_ja_menu.add_command(label = "Japanese (iso2022_jp_2)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "iso2022_jp_2"))
        file_rwe_ja_menu.add_command(label = "Japanese (iso2022_jp_2004)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "iso2022_jp_2004"))
        file_rwe_ja_menu.add_command(label = "Japanese (iso2022_jp_3)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "iso2022_jp_3"))
        file_rwe_ja_menu.add_command(label = "Japanese (iso2022_jp_ext)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "iso2022_jp_ext"))
        file_rwe_ja_menu.add_command(label = "Japanese (shift_jis)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "shift_jis"))
        file_rwe_ja_menu.add_command(label = "Japanese (shift_jis_2004)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "shift_jis_2004"))
        file_rwe_ja_menu.add_command(label = "Japanese (shift_jisx0213)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "shift_jisx0213"))
        # Create the File -> Reload with Encoding -> Korean submenu.
        file_rwe_ko_menu = Menu(tearoff = CONFIG["tearoff"])
        file_rwe_menu.add_cascade(label = "Korean", image = img_blank, compound = LEFT, menu = file_rwe_ko_menu, underline = 0)
        file_rwe_ko_menu.add_command(label = "Korean (cp949)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp949"))
        file_rwe_ko_menu.add_command(label = "Korean (euc_kr)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "euc_kr"))
        file_rwe_ko_menu.add_command(label = "Korean (iso2022_kr)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "iso2022_kr"))
        file_rwe_ko_menu.add_command(label = "Korean (johab)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "johab"))
        # Create the File -> Reload with Encoding -> South-East Asian Languages submenu.
        file_rwe_se_menu = Menu(tearoff = CONFIG["tearoff"])
        file_rwe_menu.add_cascade(label = "South-East Asian Languages", image = img_blank, compound = LEFT, menu = file_rwe_se_menu, underline = 0)
        file_rwe_se_menu.add_command(label = "Thai (cp874)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp874"))
        file_rwe_se_menu.add_command(label = "Vietnamese (cp1258)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp1258"))
        # Create the File -> Reload with Encoding -> Turkish submenu.
        file_rwe_se_menu = Menu(tearoff = CONFIG["tearoff"])
        file_rwe_menu.add_cascade(label = "Turkish", image = img_blank, compound = LEFT, menu = file_rwe_se_menu, underline = 0)
        file_rwe_se_menu.add_command(label = "Turkish (cp857)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp857"))
        file_rwe_se_menu.add_command(label = "Turkish (cp1026)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp1026"))
        file_rwe_se_menu.add_command(label = "Turkish (cp1254)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp1254"))
        file_rwe_se_menu.add_command(label = "Turkish (iso8859_9)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "iso8859_9"))
        file_rwe_se_menu.add_command(label = "Turkish (mac_turkish)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "mac_turkish"))
        # Create the File -> Reload with Encoding -> Western European submenu.
        file_rwe_we_menu = Menu(tearoff = CONFIG["tearoff"])
        file_rwe_menu.add_cascade(label = "Western European Languages", image = img_blank, compound = LEFT, menu = file_rwe_we_menu, underline = 0)
        file_rwe_we_menu.add_command(label = "Western European (latin_1)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "latin_1"))
        file_rwe_we_menu.add_command(label = "Western European (ascii)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "ascii"))
        file_rwe_we_menu.add_command(label = "Western European (cp037)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp037"))
        file_rwe_we_menu.add_command(label = "Western European (cp437)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp437"))
        file_rwe_we_menu.add_command(label = "Western European (cp500)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp500"))
        file_rwe_we_menu.add_command(label = "Western European (cp850)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp850"))
        file_rwe_we_menu.add_command(label = "Western European (cp1140)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp1140"))
        file_rwe_we_menu.add_command(label = "Western European (cp1252)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "cp1252"))
        file_rwe_we_menu.add_command(label = "Western European (iso8859_15)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "iso8859_15"))
        file_rwe_we_menu.add_command(label = "Western European (mac_roman)", image = img_blank, compound = LEFT, command = lambda: file_reload_encoding(encoding = "mac_roman"))
        # Create the File -> Recently Opened submenu.
        file_recent_open_menu = Menu(file_menu, tearoff = CONFIG["tearoff"])
        file_recent_open_menu.add_command(label = "Clear List", image = img_blank, compound = LEFT, underline = 0, command = file_recent_open_clear)
        file_recent_open_menu.add_separator()
        file_menu.add_cascade(label = "Recently Opened", image = img_blank, compound = LEFT, menu = file_recent_open_menu, underline = 0)
        file_menu.add_separator()
        file_menu.add_command(label = "Favorites...", image = img_file_favorites, compound = LEFT, underline = 2, command = file_favorites, accelerator = "Ctrl+Alt+[Space]")
        file_menu.add_separator()
        file_menu.add_command(label = "Save", image = img_file_save, compound = LEFT, underline = 0, command = file_save, accelerator = "Ctrl+S")
        file_menu.add_command(label = "Save As...", image = img_file_saveas, compound = LEFT, underline = 5, command = lambda: file_save(mode = "saveas"), accelerator = "Shift+Ctrl+S")
        # Create the File -> Save with Encoding submenu.
        file_swe_menu = Menu(tearoff = CONFIG["tearoff"])
        file_menu.add_cascade(label = "Save with Encoding", image = img_blank, compound = LEFT, menu = file_swe_menu, underline = 8)
        # Create the File -> Save with Encoding -> Unicode submenu.
        file_swe_uni_menu = Menu(tearoff = CONFIG["tearoff"])
        file_swe_menu.add_cascade(label = "Unicode", image = img_blank, compound = LEFT, menu = file_swe_uni_menu, underline = 0)
        file_swe_uni_menu.add_command(label = "UTF-8 (utf-8)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "utf-8"))
        file_swe_uni_menu.add_command(label = "UTF-8 with BOM (utf-8-sig)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "utf-8-sig"))
        file_swe_uni_menu.add_command(label = "UTF-16 (utf-16)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "utf-16"))
        file_swe_uni_menu.add_command(label = "UTF-16 BE (utf-16-be)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "utf-16-be"))
        file_swe_uni_menu.add_command(label = "UTF-16 LE (utf-16-le)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "utf-16-le"))
        file_swe_uni_menu.add_command(label = "UTF-32 (utf-32)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "utf-32"))
        file_swe_uni_menu.add_command(label = "UTF-32 BE (utf-32-be)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "utf-32-be"))
        file_swe_uni_menu.add_command(label = "UTF-32 LE (utf-32-le)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "utf-32-le"))
        file_swe_menu.add_command(label = "Other...", image = img_blank, compound = LEFT, command = file_save_encoding)
        file_swe_menu.add_separator()
        # Create the File -> Save with Encoding -> Arabic submenu.
        file_swe_ar_menu = Menu(tearoff = CONFIG["tearoff"])
        file_swe_menu.add_cascade(label = "Arabic", image = img_blank, compound = LEFT, menu = file_swe_ar_menu, underline = 0)
        file_swe_ar_menu.add_command(label = "Arabic (cp864)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp864"))
        file_swe_ar_menu.add_command(label = "Arabic (cp1256)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp1256"))
        file_swe_ar_menu.add_command(label = "Arabic (iso8859_6)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "iso8859_6"))
        # Create the File -> Save with Encoding -> Baltic Languages submenu.
        file_swe_ba_menu = Menu(tearoff = CONFIG["tearoff"])
        file_swe_menu.add_cascade(label = "Baltic Languages", image = img_blank, compound = LEFT, menu = file_swe_ba_menu, underline = 0)
        file_swe_ba_menu.add_command(label = "Baltic Languages (cp775)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp775"))
        file_swe_ba_menu.add_command(label = "Baltic Languages (cp1257)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp1257"))
        file_swe_ba_menu.add_command(label = "Baltic Languages (iso8859_4)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "iso8859_4"))
        file_swe_ba_menu.add_command(label = "Baltic Languages (iso8859_13)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "iso8859_13"))
        # Create the File -> Save with Encoding -> Central European Languages submenu.
        file_swe_ce_menu = Menu(tearoff = CONFIG["tearoff"])
        file_swe_menu.add_cascade(label = "Central European Languages", image = img_blank, compound = LEFT, menu = file_swe_ce_menu, underline = 0)
        file_swe_ce_menu.add_command(label = "Central European Languages (cp852)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp852"))
        file_swe_ce_menu.add_command(label = "Central European Languages (cp1250)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp1250"))
        file_swe_ce_menu.add_command(label = "Central European Languages (iso8859_2)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "iso8859_2"))
        file_swe_ce_menu.add_command(label = "Central European Languages (mac_latin2)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "mac_latin2"))
        # Create the File -> Save with Encoding -> Chinese submenu.
        file_swe_ch_menu = Menu(tearoff = CONFIG["tearoff"])
        file_swe_menu.add_cascade(label = "Chinese", image = img_blank, compound = LEFT, menu = file_swe_ch_menu, underline = 1)
        file_swe_ch_menu.add_command(label = "Chinese Traditional (big5)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "big5"))
        file_swe_ch_menu.add_command(label = "Chinese Traditional (big5hkscs)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "big5hkscs"))
        file_swe_ch_menu.add_command(label = "Chinese Traditional (cp950)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp950"))
        file_swe_ch_menu.add_command(label = "Chinese Simplified (gb2312)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "gb2312"))
        file_swe_ch_menu.add_command(label = "Chinese Simplified (hz)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "hz"))
        file_swe_ch_menu.add_command(label = "Chinese Unified (gbk)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "gbk"))
        file_swe_ch_menu.add_command(label = "Chinese Unified (gb18030)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "gb18030"))
        # Create the File -> Save with Encoding -> Cyrillic submenu.
        file_swe_cy_menu = Menu(tearoff = CONFIG["tearoff"])
        file_swe_menu.add_cascade(label = "Cyrillic", image = img_blank, compound = LEFT, menu = file_swe_cy_menu, underline = 1)
        file_swe_cy_menu.add_command(label = "Cyrillic (iso8859_5)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "iso8859_5"))
        file_swe_cy_menu.add_command(label = "Cyrillic (mac_cyrillic)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "mac_cyrillic"))
        file_swe_cy_menu.add_command(label = "Cyrillic (ptcp154)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "ptcp154"))
        file_swe_cy_menu.add_command(label = "Cyrillic (cp866)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp866"))
        file_swe_cy_menu.add_command(label = "Cyrillic (cp1251)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp1251"))
        file_swe_cy_menu.add_command(label = "Cyrillic (iso8859_5)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "iso8859_5"))
        file_swe_cy_menu.add_command(label = "Cyrillic (koi8_r)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "koi8_r"))
        file_swe_cy_menu.add_command(label = "Cyrillic (koi8_u)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "koi8_u"))
        # Create the File -> Save with Encoding -> Greek submenu.
        file_swe_gr_menu = Menu(tearoff = CONFIG["tearoff"])
        file_swe_menu.add_cascade(label = "Greek", image = img_blank, compound = LEFT, menu = file_swe_gr_menu, underline = 0)
        file_swe_gr_menu.add_command(label = "Greek (cp737)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp737"))
        file_swe_gr_menu.add_command(label = "Greek (cp869)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp869"))
        file_swe_gr_menu.add_command(label = "Greek (cp875)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp875"))
        file_swe_gr_menu.add_command(label = "Greek (cp1253)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp1253"))
        file_swe_gr_menu.add_command(label = "Greek (iso8859_7)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "iso8859_7"))
        file_swe_gr_menu.add_command(label = "Greek (mac_greek)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "mac_greek"))
        # Create the File -> Save with Encoding -> Hebrew submenu.
        file_swe_he_menu = Menu(tearoff = CONFIG["tearoff"])
        file_swe_menu.add_cascade(label = "Hebrew", image = img_blank, compound = LEFT, menu = file_swe_he_menu, underline = 0)
        file_swe_he_menu.add_command(label = "Hebrew (cp424)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp424"))
        file_swe_he_menu.add_command(label = "Hebrew (cp856)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp856"))
        file_swe_he_menu.add_command(label = "Hebrew (cp862)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp862"))
        file_swe_he_menu.add_command(label = "Hebrew (cp1255)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp1255"))
        file_swe_he_menu.add_command(label = "Hebrew (iso8859_8)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "iso8859_8"))
        # Create the File -> Save with Encoding -> Japanese submenu.
        file_swe_ja_menu = Menu(tearoff = CONFIG["tearoff"])
        file_swe_menu.add_cascade(label = "Japanese", image = img_blank, compound = LEFT, menu = file_swe_ja_menu, underline = 0)
        file_swe_ja_menu.add_command(label = "Japanese (cp932)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp932"))
        file_swe_ja_menu.add_command(label = "Japanese (euc_jp)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "euc_jp"))
        file_swe_ja_menu.add_command(label = "Japanese (euc_jis_2004)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "euc_jis_2004"))
        file_swe_ja_menu.add_command(label = "Japanese (euc_jisx0213)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "euc_jisx0213"))
        file_swe_ja_menu.add_command(label = "Japanese (iso2022_jp)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "iso2022_jp"))
        file_swe_ja_menu.add_command(label = "Japanese (iso2022_jp_1)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "iso2022_jp_1"))
        file_swe_ja_menu.add_command(label = "Japanese (iso2022_jp_2)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "iso2022_jp_2"))
        file_swe_ja_menu.add_command(label = "Japanese (iso2022_jp_2004)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "iso2022_jp_2004"))
        file_swe_ja_menu.add_command(label = "Japanese (iso2022_jp_3)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "iso2022_jp_3"))
        file_swe_ja_menu.add_command(label = "Japanese (iso2022_jp_ext)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "iso2022_jp_ext"))
        file_swe_ja_menu.add_command(label = "Japanese (shift_jis)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "shift_jis"))
        file_swe_ja_menu.add_command(label = "Japanese (shift_jis_2004)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "shift_jis_2004"))
        file_swe_ja_menu.add_command(label = "Japanese (shift_jisx0213)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "shift_jisx0213"))
        # Create the File -> Save with Encoding -> Korean submenu.
        file_swe_ko_menu = Menu(tearoff = CONFIG["tearoff"])
        file_swe_menu.add_cascade(label = "Korean", image = img_blank, compound = LEFT, menu = file_swe_ko_menu, underline = 0)
        file_swe_ko_menu.add_command(label = "Korean (cp949)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp949"))
        file_swe_ko_menu.add_command(label = "Korean (euc_kr)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "euc_kr"))
        file_swe_ko_menu.add_command(label = "Korean (iso2022_kr)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "iso2022_kr"))
        file_swe_ko_menu.add_command(label = "Korean (johab)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "johab"))
        # Create the File -> Save with Encoding -> South-East Asian Languages submenu.
        file_swe_se_menu = Menu(tearoff = CONFIG["tearoff"])
        file_swe_menu.add_cascade(label = "South-East Asian Languages", image = img_blank, compound = LEFT, menu = file_swe_se_menu, underline = 0)
        file_swe_se_menu.add_command(label = "Thai (cp874)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp874"))
        file_swe_se_menu.add_command(label = "Vietnamese (cp1258)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp1258"))
        # Create the File -> Save with Encoding -> Turkish submenu.
        file_swe_se_menu = Menu(tearoff = CONFIG["tearoff"])
        file_swe_menu.add_cascade(label = "Turkish", image = img_blank, compound = LEFT, menu = file_swe_se_menu, underline = 0)
        file_swe_se_menu.add_command(label = "Turkish (cp857)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp857"))
        file_swe_se_menu.add_command(label = "Turkish (cp1026)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp1026"))
        file_swe_se_menu.add_command(label = "Turkish (cp1254)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp1254"))
        file_swe_se_menu.add_command(label = "Turkish (iso8859_9)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "iso8859_9"))
        file_swe_se_menu.add_command(label = "Turkish (mac_turkish)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "mac_turkish"))
        # Create the File -> Save with Encoding -> Western European submenu.
        file_swe_we_menu = Menu(tearoff = CONFIG["tearoff"])
        file_swe_menu.add_cascade(label = "Western European Languages", image = img_blank, compound = LEFT, menu = file_swe_we_menu, underline = 0)
        file_swe_we_menu.add_command(label = "Western European (latin_1)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "latin_1"))
        file_swe_we_menu.add_command(label = "Western European (ascii)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "ascii"))
        file_swe_we_menu.add_command(label = "Western European (cp037)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp037"))
        file_swe_we_menu.add_command(label = "Western European (cp437)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp437"))
        file_swe_we_menu.add_command(label = "Western European (cp500)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp500"))
        file_swe_we_menu.add_command(label = "Western European (cp850)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp850"))
        file_swe_we_menu.add_command(label = "Western European (cp1140)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp1140"))
        file_swe_we_menu.add_command(label = "Western European (cp1252)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "cp1252"))
        file_swe_we_menu.add_command(label = "Western European (iso8859_15)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "iso8859_15"))
        file_swe_we_menu.add_command(label = "Western European (mac_roman)", image = img_blank, compound = LEFT, command = lambda: file_save_encoding(encoding = "mac_roman"))
        file_menu.add_command(label = "Save Copy...", image = img_blank, compound = LEFT, underline = 5, command = file_save_copy, accelerator = "Alt+Ctrl+S")
        file_menu.add_command(label = "Revert to Last Save...", image = img_blank, compound = LEFT, underline = 10, command = file_revert_save)
        file_menu.add_separator()
        # Create the File -> Binary Mode submenu.
        file_bin_menu = Menu(file_menu, tearoff = CONFIG["tearoff"])
        file_menu.add_cascade(label = "Binary Mode", image = img_blank, compound = LEFT, menu = file_bin_menu, underline= 5)
        file_bin_menu.add_command(label = "Open in Binary Mode...", image = img_blank, compound = LEFT, underline = 0, command = file_open_binary)
        file_bin_menu.add_command(label = "Reload in Binary Mode...", image = img_blank, compound = LEFT, underline = 0, command = file_reload_binary)
        file_bin_menu.add_command(label = "Save in Binary Mode...", image = img_blank, compound = LEFT, underline = 0, command = file_save_binary)
        file_menu.add_separator()
        file_menu.add_command(label = "Insert...", image = img_blank, compound = LEFT, underline = 0, command = lambda: file_open(insert = True))
        file_menu.add_separator()
        file_menu.add_command(label = "Browse...", image = img_file_browse, compound = LEFT, underline = 0, command = file_browse, accelerator = "F4")
        file_menu.add_command(label = "Rename...", image = img_blank, compound = LEFT, underline = 2, command = file_rename, accelerator = "F10")
        file_menu.add_command(label = "Delete...", image = img_file_delete, compound = LEFT, underline = 0, command = file_delete, accelerator = "F11")
        file_menu.add_separator()
        file_menu.add_command(label = "Print...", image = img_file_print, compound = LEFT, underline = 0, command = file_print, accelerator = "Ctrl+P")
        file_menu.add_separator()
        file_menu.add_command(label = "Exit", image = img_file_exit, compound = LEFT, underline = 1, command = file_exit, accelerator = "Ctrl+Q")
    
    if CONFIG["menu_edit"] == "show":
        # Create the Edit menu.
        edit_menu = Menu(menu, tearoff = CONFIG["tearoff"])
        menu.add_cascade(label = "Edit", menu = edit_menu, underline = 0)
        edit_menu.add_command(label = "Undo", image = img_edit_undo, compound = LEFT, underline = 0, command = edit_undo, accelerator = "Ctrl+Z")
        edit_menu.add_command(label = "Redo", image = img_edit_redo, compound = LEFT, underline = 2, command = edit_redo, accelerator = "Shift+Ctrl+Z, Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label = "Cut", image = img_edit_cut, compound = LEFT, underline = 0, command = edit_cut, accelerator = "Ctrl+X")
        edit_menu.add_command(label = "Copy", image = img_edit_copy, compound = LEFT, underline = 2, command = edit_copy, accelerator = "Ctrl+C")
        edit_menu.add_command(label = "Paste", image = img_edit_paste, compound = LEFT, underline = 0, command = edit_paste, accelerator = "Ctrl+V")
        edit_menu.add_command(label = "Paste Overwrite", image = img_blank, compound = LEFT, underline = 7, command = edit_paste_overwrite, accelerator = "Shift+Ctrl+V")
        edit_menu.add_command(label = "Paste Indent", image = img_blank, compound = LEFT, underline = 7, command = edit_paste_indent, accelerator = "Alt+Ctrl+V")
        edit_menu.add_command(label = "Clear Clipboard", image = img_blank, compound = LEFT, underline = 1, command = edit_clear_clipboard)
        # Create the Edit -> Copy to Clipboard submenu.
        edit_clip_menu = Menu(edit_menu, tearoff = CONFIG["tearoff"])
        edit_clip_menu.add_command(label = "Full Path", image = img_blank, compound = LEFT, underline = 5, command = lambda: edit_copy_clipboard("path"))
        edit_clip_menu.add_command(label = "Filename", image = img_blank, compound = LEFT, underline = 0, command = lambda: edit_copy_clipboard("file"))
        edit_clip_menu.add_command(label = "Directory", image = img_blank, compound = LEFT, underline = 0, command = lambda: edit_copy_clipboard("dir"))
        edit_menu.add_cascade(label = "Copy to Clipboard", image = img_blank, compound = LEFT, menu = edit_clip_menu, underline = 12)
        edit_menu.add_separator()
        edit_menu.add_checkbutton(label = "Lock File", underline = 3, onvalue = True, offvalue = False, variable = tkvar_lock, command = edit_lock)
        edit_menu.add_separator()
        # Create the Edit -> Change Case submenu.
        edit_case_menu = Menu(edit_menu, tearoff = CONFIG["tearoff"])
        edit_case_menu.add_command(label = "Lowercase", image = img_blank, compound = LEFT, underline = 0, command = lambda: edit_change_case("lower"))
        edit_case_menu.add_command(label = "Uppercase", image = img_blank, compound = LEFT, underline = 0, command = lambda: edit_change_case("upper"))
        edit_case_menu.add_command(label = "Capitalize", image = img_blank, compound = LEFT, underline = 0, command = lambda: edit_change_case("cap"))
        edit_case_menu.add_command(label = "Reverse", image = img_blank, compound = LEFT, underline = 0, command = lambda: edit_change_case("rev"))
        edit_menu.add_cascade(label = "Change Case", image = img_blank, compound = LEFT, menu = edit_case_menu, underline = 1)
        # Create the Edit -> Line submenu.
        edit_line_menu = Menu(edit_menu, tearoff = CONFIG["tearoff"])
        edit_line_menu.add_command(label = "Join Lines", image = img_blank, compound = LEFT, underline = 0, command = edit_line_join)
        edit_line_menu.add_separator()
        edit_line_menu.add_command(label = "Copy Line", image = img_blank, compound = LEFT, underline = 2, command = edit_line_copy)
        edit_line_menu.add_command(label = "Cut Line", image = img_blank, compound = LEFT, underline = 0, command = edit_line_cut)
        edit_line_menu.add_separator()
        edit_line_menu.add_command(label = "Reverse Line", image = img_blank, compound = LEFT, underline = 0, command = edit_line_reverse)
        edit_line_menu.add_command(label = "Duplicate Line", image = img_blank, compound = LEFT, underline = 1, command = edit_line_duplicate)
        edit_line_menu.add_command(label = "Delete Line", image = img_blank, compound = LEFT, underline = 0, command = edit_line_delete)
        edit_menu.add_cascade(label = "Line", image = img_blank, compound = LEFT, menu = edit_line_menu, underline = 1)
        # Create the Edit -> Spacing submenu.
        edit_space_menu = Menu(edit_menu, tearoff = CONFIG["tearoff"])
        edit_space_menu.add_command(label = "Normalize", image = img_blank, compound = LEFT, underline = 0, command = edit_normalize)
        edit_space_menu.add_separator()
        edit_space_menu.add_command(label = "Strip Leading Space", image = img_blank, compound = LEFT, underline = 6, command = tools_strip_leading)
        edit_space_menu.add_command(label = "Strip Trailing Space", image = img_blank, compound = LEFT, underline = 6, command = tools_strip_trailing)
        edit_space_menu.add_separator()
        edit_space_menu.add_command(label = "Replace Tabs with Spaces", image = img_blank, compound = LEFT, underline = 8, command = lambda: tools_spaces_tabs("t2s"))
        edit_space_menu.add_command(label = "Replace Spaces with Tabs", image = img_blank, compound = LEFT, underline = 0, command = lambda: tools_spaces_tabs("s2t"))
        edit_menu.add_cascade(label = "Spacing", image = img_blank, compound = LEFT, menu = edit_space_menu, underline = 6)
        edit_menu.add_separator()
        edit_menu.add_command(label = "Select All", image = img_edit_selectall, compound = LEFT, underline = 7, command = edit_select_all, accelerator = "Ctrl+A")
        edit_menu.add_command(label = "Deselect All", image = img_blank, compound = LEFT, underline = 4, command = edit_deselect_all, accelerator = "Shift+Ctrl+A")
        # Create the Edit -> Selection submenu.
        edit_sel_menu = Menu(edit_menu, tearoff = CONFIG["tearoff"])
        edit_sel_menu.add_command(label = "Select From...", image = img_blank, compound = LEFT, underline = 7, command = edit_select_from)
        edit_sel_menu.add_command(label = "Select All Before Insert", image = img_blank, compound = LEFT, underline = 11, command = lambda: edit_select_from(start = "1.0", end = "insert"))
        edit_sel_menu.add_command(label = "Select All Ater Insert", image = img_blank, compound = LEFT, underline = 11, command = lambda: edit_select_from(start = "insert", end = "end"))
        edit_sel_menu.add_command(label = "Select Line Before Insert", image = img_blank, compound = LEFT, underline = 7, command = lambda: edit_select_from(start = "LINESTART", end = "insert"))
        edit_sel_menu.add_command(label = "Select Line After Insert", image = img_blank, compound = LEFT, underline = 13, command = lambda: edit_select_from(start = "insert", end = "LINEEND"))
        edit_sel_menu.add_separator()
        edit_sel_menu.add_command(label = "Join Selected Lines", image = img_blank, compound = LEFT, underline = 0, command = edit_line_join)
        edit_sel_menu.add_separator()
        edit_sel_menu.add_command(label = "Delete Selected", image = img_blank, compound = LEFT, underline = 0, command = edit_delete_selected)
        edit_sel_menu.add_command(label = "Delete Nonselected", image = img_blank, compound = LEFT, underline = 7, command = edit_delete_nonselected)
        edit_menu.add_cascade(label = "Selection", image = img_blank, compound = LEFT, menu = edit_sel_menu, underline = 0)
    
    if CONFIG["menu_documents"] == "show":
        # Create the Documents menu.
        documents_menu = Menu(menu, tearoff = CONFIG["tearoff"])
        menu.add_cascade(label = "Documents", menu = documents_menu, underline = 0)
        documents_menu.add_command(label = "New Document", image = img_documents_new, compound = LEFT, underline = 0, command = documents_new, accelerator = "Shift+Ctrl+N")
        documents_menu.add_command(label = "Open Document", image = img_documents_open, compound = LEFT, underline = 0, command = documents_open, accelerator = "Shift+Ctrl+O")
        documents_menu.add_command(label = "Close Document", image = img_documents_close, compound = LEFT, underline = 0, command = documents_close, accelerator = "Shift+Ctrl+Q")
        documents_menu.add_separator()
        documents_menu.add_command(label = "Previous", image = img_documents_previous, compound = LEFT, underline = 0, command = documents_previous, accelerator = "Alt+LeftArrow, Shift+Ctrl+Tab")
        documents_menu.add_command(label = "Next", image = img_documents_next, compound = LEFT, underline = 2, command = documents_next, accelerator = "Alt+RightArrow, Ctrl+Tab")
        documents_menu.add_separator()
        documents_menu.add_command(label = "View All", image = img_documents_viewall, compound = LEFT, underline = 0, command = documents_view, accelerator = "Ctrl+M")
    
    if CONFIG["menu_search"] == "show":
        # Create the Search menu.
        search_menu = Menu(menu, tearoff = CONFIG["tearoff"])
        menu.add_cascade(label = "Search", menu = search_menu, underline = 0)
        search_menu.add_command(label = "Find...", image = img_search_find, compound = LEFT, underline = 0, command = search_find, accelerator = "Ctrl+F")
        if CONFIG["advanced_search"] == "show":
            search_menu.add_command(label = "Find Selected...", image = img_blank, compound = LEFT, underline = 5, command = search_find_selected, accelerator = "Shift+Ctrl+F")
            search_menu.add_command(label = "Find in Selected...", image = img_blank, compound = LEFT, underline = 5, command = search_find_in_selected)
        search_menu.add_command(label = "Replace...", image = img_search_replace, compound = LEFT, underline = 0, command = search_replace, accelerator = "Ctrl+H")
        if CONFIG["advanced_search"] == "show":
            search_menu.add_command(label = "Replace Selected...", image = img_blank, compound = LEFT, underline = 1, command = search_replace_selected, accelerator = "Shift+Ctrl+H")
            search_menu.add_command(label = "Replace in Selected...", image = img_blank, compound = LEFT, underline = 3, command = search_replace_in_selected)
            search_menu.add_separator()
            search_menu.add_command(label = "Find History...", image = img_blank, compound = LEFT, underline = 5, command = search_find_history, accelerator = "Ctrl+W")
            search_menu.add_command(label = "Replace History...", image = img_blank, compound = LEFT, underline = 14, command = search_replace_history, accelerator = "Shift+Ctrl+W")
        search_menu.add_separator()
        search_menu.add_command(label = "Goto...", image = img_search_goto, compound = LEFT, underline = 0, command = search_goto, accelerator = "Ctrl+G, Ctrl+L")
        search_menu.add_separator()
        search_menu.add_command(label = "Jump to Top", image = img_search_jumptotop, compound = LEFT, underline = 1, command = search_jump_top, accelerator = "F6")
        search_menu.add_command(label = "Jump to Bottom", image = img_search_jumptobottom, compound = LEFT, underline = 2, command = search_jump_bottom, accelerator = "F7")
        search_menu.add_command(label = "Jump to Insert", image = img_blank, compound = LEFT, underline = 3, command = internal_return_focus, accelerator = "F8")
        search_menu.add_command(label = "Jump to Selection Start", image = img_blank, compound = LEFT, underline = 12, command = search_jump_select_start)
        search_menu.add_command(label = "Jump to Selection End", image = img_blank, compound = LEFT, underline = 19, command = search_jump_select_end)
        search_menu.add_command(label = "Jump to Line Start", image = img_search_jumplinestart, compound = LEFT, underline = 14, command = search_jump_line_start, accelerator = "Home")
        search_menu.add_command(label = "Jump to Line End", image = img_search_jumplineend, compound = LEFT, underline = 15, command = search_jump_line_end, accelerator = "End")
        search_menu.add_separator()
        search_menu.add_command(label = "Open URL in Web Browser", image = img_blank, compound = LEFT, underline = 16, command = search_open_url)
        # Create the Search -> Web Search submenu.
        search_sel_menu = Menu(search_menu, tearoff = CONFIG["tearoff"])
        search_sel_menu.add_command(label = "Google", image = img_blank, compound = LEFT, underline = 0, command = lambda: search_search_sel("http://www.google.com/search?q="))
        search_sel_menu.add_command(label = "DuckDuckGo", image = img_blank, compound = LEFT, underline = 0, command = lambda: search_search_sel("http://www.duckduckgo.com/?q="))
        search_sel_menu.add_command(label = "Yahoo", image = img_blank, compound = LEFT, underline = 0, command = lambda: search_search_sel("http://search.yahoo.com/search?p="))
        search_sel_menu.add_command(label = "Bing", image = img_blank, compound = LEFT, underline = 0, command = lambda: search_search_sel("http://www.bing.com/search?q="))
        search_sel_menu.add_separator()
        search_sel_menu.add_command(label = "Wikipedia", image = img_blank, compound = LEFT, underline = 0, command = lambda: search_search_sel("http://www.wikipedia.org/wiki/"))
        search_sel_menu.add_command(label = "Wiktionary", image = img_blank, compound = LEFT, underline = 6, command = lambda: search_search_sel("http://www.wiktionary.org/wiki/"))
        search_sel_menu.add_command(label = "Wikidata", image = img_blank, compound = LEFT, underline = 2, command = lambda: search_search_sel("http://www.wikidata.org/wiki/"))
        search_sel_menu.add_command(label = "Wikisource", image = img_blank, compound = LEFT, underline = 6, command = lambda: search_search_sel("http://www.wikisource.org/wiki/"))
        search_sel_menu.add_separator()
        search_sel_menu.add_command(label = "Youtube", image = img_blank, compound = LEFT, underline = 3, command = lambda: search_search_sel("http://www.youtube.com/results?search_query="))
        search_sel_menu.add_command(label = "Wolfram|Alpha", image = img_blank, compound = LEFT, underline = 1, command = lambda: search_search_sel("http://www.wolframalpha.com/input/?i="))
        search_sel_menu.add_command(label = "About.com", image = img_blank, compound = LEFT, underline = 0, command = lambda: search_search_sel("http://search.about.com/?q="))
        search_sel_menu.add_separator()
        search_sel_menu.add_command(label = "Is.gd Shorten", image = img_blank, compound = LEFT, underline = 6, command = lambda: search_search_sel("http://is.gd/create.php?format=simple&url="))
        search_sel_menu.add_command(label = "Is.gd Lookup", image = img_blank, compound = LEFT, underline = 0, command = lambda: search_search_sel("http://is.gd/forward.php?shorturl="))
        search_menu.add_cascade(label = "Web Search", image = img_search_searchselected, compound = LEFT, menu = search_sel_menu, underline = 0)
    
    if CONFIG["menu_tools"] == "show":
        # Create the Tools menu.
        tools_menu = Menu(menu, tearoff = CONFIG["tearoff"])
        menu.add_cascade(label = "Tools", menu = tools_menu, underline = 0)
        # Create the Tools -> Bookmarks submenu.
        tools_bm_menu = Menu(tools_menu, tearoff = CONFIG["tearoff"])
        tools_bm_menu.add_command(label = "Add Bookmark...", image = img_tools_add_bookmark, compound = LEFT, underline = 0, command = tools_bookmarks_add, accelerator = "Ctrl+B")
        tools_bm_menu.add_command(label = "View Bookmarks...", image = img_tools_bookmarks, compound = LEFT, underline = 0, command = tools_bookmarks_view, accelerator = "Shift+Ctrl+B")
        tools_bm_menu.add_command(label = "Clear Bookmarks...", image = img_tools_clear_bookmarks, compound = LEFT, underline = 0, command = tools_bookmarks_clear)
        tools_bm_menu.add_separator()
        tools_bm_menu.add_command(label = "Save Bookmarks...", image = img_file_save, compound = LEFT, underline = 0, command = tools_bookmarks_save)
        tools_bm_menu.add_command(label = "Open Bookmarks...", image = img_file_open, compound = LEFT, underline = 0, command = tools_bookmarks_open)
        tools_menu.add_cascade(label = "Bookmarks", image = img_tools_bookmarks, compound = LEFT, menu = tools_bm_menu, underline = 0)
        tools_menu.add_separator()
        # Create the Tools -> Macro submenu.
        tools_mac_menu = Menu(tools_menu, tearoff = CONFIG["tearoff"])
        tools_mac_menu.add_command(label = "Run Macro...", image = img_tools_macro_run, compound = LEFT, underline = 0, command = tools_macro_run, accelerator = "Ctrl+R")
        tools_mac_menu.add_separator()
        tools_mac_menu.add_command(label = "Change Macro Bindings...", image = img_tools_macro_bindings, compound = LEFT, underline = 13, command = tools_macro_bindings)
        tools_menu.add_cascade(label = "Macros...", image = img_tools_macro_run, compound = LEFT, menu = tools_mac_menu, underline = 0)
        tools_menu.add_command(label = "Run Command...", image = img_blank, compound = LEFT, underline = 4, command = tools_run_command, accelerator = "Shift+Ctrl+R")
        tools_menu.add_separator()
        tools_menu.add_command(label = "Insert Time", image = img_blank, compound = LEFT, underline = 7, command = tools_insert_time, accelerator = "Shift+Ctrl+T")
        tools_menu.add_command(label = "Insert Time (Words)", image = img_blank, compound = LEFT, underline = 13, command = tools_insert_time_words)
        tools_menu.add_command(label = "Insert Date", image = img_blank, compound = LEFT, underline = 7, command = tools_insert_date, accelerator = "Shift+Ctrl+D")
        tools_menu.add_command(label = "Insert Color...", image = img_blank, compound = LEFT, underline = 4, command = tools_insert_color)
        # Create the Tools -> Insert submenu.
        tools_ins_menu = Menu(tools_menu, tearoff = CONFIG["tearoff"])
        tools_menu.add_cascade(label = "Insert", image = img_blank, compound = LEFT, menu = tools_ins_menu, underline = 1)
        # Create the Tools -> Insert -> More Times submenu.
        tools_ins_time_menu = Menu(tools_ins_menu, tearoff = CONFIG["tearoff"])
        tools_ins_menu.add_cascade(label = "More Times", image = img_blank, compound = LEFT, menu = tools_ins_time_menu, underline = 5)
        tools_ins_time_menu.add_command(label = "%H:%M:%S", image = img_blank, compound = LEFT, command = lambda: tools_insert_time("%H:%M:%S"))
        tools_ins_time_menu.add_command(label = "%I:%M:%S", image = img_blank, compound = LEFT, command = lambda: tools_insert_time("%I:%M:%S"))
        tools_ins_time_menu.add_command(label = "%H:%M:%S %p", image = img_blank, compound = LEFT, command = lambda: tools_insert_time("%H:%M:%S %p"))
        tools_ins_time_menu.add_command(label = "%I:%M:%S %p", image = img_blank, compound = LEFT, command = lambda: tools_insert_time("%I:%M:%S%p"))
        tools_ins_time_menu.add_command(label = "%H:%M", image = img_blank, compound = LEFT, command = lambda: tools_insert_time("%H:%M"))
        tools_ins_time_menu.add_command(label = "%I:%M", image = img_blank, compound = LEFT, command = lambda: tools_insert_time("%I:%M"))
        tools_ins_time_menu.add_command(label = "%H:%M %p", image = img_blank, compound = LEFT, command = lambda: tools_insert_time("%H:%M %p"))
        tools_ins_time_menu.add_command(label = "%I:%M %p", image = img_blank, compound = LEFT, command = lambda: tools_insert_time("%I:%M %p"))
        tools_ins_time_menu.add_separator()
        tools_ins_time_menu.add_command(label = "Other...", image = img_blank, compound = LEFT, command = lambda: tools_insert_time(mode = "other"))
        # Create the Tools -> Insert -> More Dates submenu.
        tools_ins_date_menu = Menu(tools_ins_menu, tearoff = CONFIG["tearoff"])
        tools_ins_menu.add_cascade(label = "More Dates", image = img_blank, compound = LEFT, menu = tools_ins_date_menu, underline = 5)
        tools_ins_date_menu.add_command(label = "%d/%m/%y", image = img_blank, compound = LEFT, command = lambda : tools_insert_date("%d/%m/%y"))
        tools_ins_date_menu.add_command(label = "%e/%m/%y", image = img_blank, compound = LEFT, command = lambda : tools_insert_date("%e/%m/%y"))
        tools_ins_date_menu.add_command(label = "%d/%m/%Y", image = img_blank, compound = LEFT, command = lambda : tools_insert_date("%d/%m/%Y"))
        tools_ins_date_menu.add_command(label = "%e/%m/%Y", image = img_blank, compound = LEFT, command = lambda : tools_insert_date("%e/%m/%Y"))
        tools_ins_date_menu.add_command(label = "%d-%m-%y", image = img_blank, compound = LEFT, command = lambda : tools_insert_date("%d-%m-%y"))
        tools_ins_date_menu.add_command(label = "%e-%m-%y", image = img_blank, compound = LEFT, command = lambda : tools_insert_date("%e-%m-%y"))
        tools_ins_date_menu.add_command(label = "%d-%m-%Y", image = img_blank, compound = LEFT, command = lambda : tools_insert_date("%d-%m-%Y"))
        tools_ins_date_menu.add_command(label = "%e-%m-%Y", image = img_blank, compound = LEFT, command = lambda : tools_insert_date("%e-%m-%Y"))
        tools_ins_date_menu.add_command(label = "%d %B, %y", image = img_blank, compound = LEFT, command = lambda : tools_insert_date("%d %B, %y"))
        tools_ins_date_menu.add_command(label = "%d %B, %Y", image = img_blank, compound = LEFT, command = lambda : tools_insert_date("%d %B, %Y"))
        tools_ins_date_menu.add_command(label = "%d %b, %y", image = img_blank, compound = LEFT, command = lambda : tools_insert_date("%d %b, %y"))
        tools_ins_date_menu.add_command(label = "%d %b, %Y", image = img_blank, compound = LEFT, command = lambda : tools_insert_date("%d %b, %Y"))
        tools_ins_date_menu.add_separator()
        tools_ins_date_menu.add_command(label = "Other...", image = img_blank, compound = LEFT, command = lambda: tools_insert_date(mode = "other"))
        tools_ins_menu.add_separator()
        tools_ins_menu.add_command(label = "Line", image = img_blank, compound = LEFT, underline = 0,  command = lambda: tools_insert("line"))
        tools_ins_menu.add_command(label = "Position", image = img_blank, compound = LEFT, underline = 1, command = lambda: tools_insert("position"))
        tools_ins_menu.add_separator()
        tools_ins_menu.add_command(label = "Full Path", image = img_blank, compound = LEFT, underline = 5, command = lambda: tools_insert("fullpath"))
        tools_ins_menu.add_command(label = "Filename", image = img_blank, compound = LEFT, underline = 0, command = lambda: tools_insert("filename"))
        tools_ins_menu.add_command(label = "Directory", image = img_blank, compound = LEFT, underline = 2, command = lambda: tools_insert("directory"))
        tools_menu.add_separator()
        tools_menu.add_command(label = "Indent", image = img_tools_indent, compound = LEFT, underline = 0, command = tools_indent, accelerator = "Ctrl+I")
        tools_menu.add_command(label = "Unindent", image = img_tools_unindent, compound = LEFT, underline = 0, command = tools_unindent, accelerator = "Shift+Ctrl+I")
        tools_menu.add_separator()
        tools_menu.add_command(label = "Encode URL", image = img_blank, compound = LEFT, underline = 0, command = tools_encode_url)
        tools_menu.add_command(label = "Decode URL", image = img_blank, compound = LEFT, underline = 3, command = tools_decode_url)
        tools_menu.add_separator()
        tools_menu.add_command(label = "Notes...", image = img_tools_notes, compound = LEFT, underline = 0, command = tools_notes, accelerator = "Ctrl+J")
        tools_menu.add_command(label = "Tasks...", image = img_blank, compound = LEFT, underline = 3, command = tools_tasks, accelerator = "Shift+Ctrl+J")
        tools_menu.add_separator()
        tools_menu.add_command(label = "Collaborative Editing...", image = img_tools_collab, compound = LEFT, underline = 2, command = tools_collab, accelerator = "Ctrl+E")
        tools_menu.add_separator()
        # Create the Tools -> Pastebin submenu.
        tools_paste_menu = Menu(tools_menu, tearoff = CONFIG["tearoff"])
        tools_paste_menu.add_command(label = "Upload to Pastebin...", image = img_blank, compound = LEFT, underline = 0, command = tools_upload_pastebin, accelerator = "Ctrl+U")
        tools_paste_menu.add_command(label = "Download from Pastebin...", image = img_blank, compound = LEFT, underline = 0, command = tools_download_pastebin, accelerator = "Shift+Ctrl+U")
        tools_menu.add_cascade(label = "Pastebin", image = img_blank, compound = LEFT, menu = tools_paste_menu, underline = 0)
        # Create the Tools -> PasteHTML submenu.
        tools_phtml_menu = Menu(tools_menu, tearoff = CONFIG["tearoff"])
        tools_phtml_menu.add_command(label = "Upload to PasteHTML...", image = img_blank, compound = LEFT, underline = 0, command = tools_upload_pastehtml)
        tools_menu.add_cascade(label = "PasteHTML", image = img_blank, compound = LEFT, menu = tools_phtml_menu, underline = 5)
        # Create the Tools -> Send File submenu.
        tools_svia_menu = Menu(tools_menu, tearoff = CONFIG["tearoff"])
        tools_svia_menu.add_command(label = "Send Via FTP...", image = img_tools_sendftp, compound = LEFT, underline = 9, command = tools_send_ftp)
        tools_svia_menu.add_command(label = "Send Via Email...", image = img_tools_sendemail, compound = LEFT, underline = 9, command = tools_send_email)
        tools_menu.add_cascade(label = "Send File", image = img_blank, compound = LEFT, menu = tools_svia_menu, underline = 5)
        tools_menu.add_separator()
        tools_menu.add_command(label = "Statistics...", image = img_tools_statistics, compound = LEFT, underline = 0, command = tools_statistics, accelerator = "F2")
    
    if CONFIG["menu_code"] == "show":
        # Create the Code menu.
        code_menu = Menu(menu, tearoff = CONFIG["tearoff"])
        menu.add_cascade(label = "Code", menu = code_menu, underline = 0)
        code_menu.add_command(label = "Open in Web Browser", image = img_code_openinwebbrowser, compound = LEFT, underline = 12, command = code_open_browser)
        code_menu.add_separator()
        # Create the Code -> Run Code submenu.
        code_run_menu = Menu(code_menu, tearoff = CONFIG["tearoff"])
        code_run_menu.add_command(label = "Run Code (Python)", image = img_blank, compound = LEFT, underline = 10, command = lambda: code_run_code(CONFIG["python"]))
        code_run_menu.add_command(label = "Run Code (Perl)", image = img_blank, compound = LEFT, underline = 11, command = lambda: code_run_code(CONFIG["perl"]))
        code_run_menu.add_command(label = "Run Code (PHP)", image = img_blank, compound = LEFT, underline = 11, command = lambda: code_run_code(CONFIG["php"]))
        code_menu.add_cascade(label = "Run Code", image = img_code_run_code, compound = LEFT, menu = code_run_menu, underline = 0)
        # Create the Code -> Compile submenu.
        code_compile_menu = Menu(code_menu, tearoff = CONFIG["tearoff"])
        code_compile_menu.add_command(label = "Compile (C)", image = img_blank, compound = LEFT, underline = 9, command = lambda: code_run_code(CONFIG["c"]))
        code_compile_menu.add_command(label = "Compile (C++)", image = img_blank, compound = LEFT, underline = 1, command = lambda: code_run_code(CONFIG["cpp"]))
        code_compile_menu.add_command(label = "Compile (Java)", image = img_blank, compound = LEFT, underline = 9, command = lambda: code_run_code(CONFIG["java"]))
        code_menu.add_cascade(label = "Compile", image = img_code_compile, compound = LEFT, menu = code_compile_menu, underline = 3)
        code_menu.add_command(label = "Run Code (Other)", image = img_blank, compound = LEFT, underline = 12, command = lambda: code_run_code(None))
        code_menu.add_command(label = "Execute...", image = img_blank, compound = LEFT, underline = 0, command = code_execute)
        code_menu.add_separator()
        code_menu.add_command(label = "Find Opening Symbol", image = img_blank, compound = LEFT, underline = 5, command = code_find_opening)
        code_menu.add_command(label = "Find Closing Symbol", image = img_blank, compound = LEFT, underline = 13, command = code_find_closing)
        code_menu.add_separator()
        # Create the Code -> Insert Comment submenu.
        code_comment_menu = Menu(code_menu, tearoff = CONFIG["tearoff"])
        code_comment_menu.add_command(label = "Python", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_comment("# ", ""))
        code_comment_menu.add_command(label = "HTML", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_comment("<!-- ", " -->"))
        code_comment_menu.add_command(label = "C-style Single Line", image = img_blank, compound = LEFT, underline = 8, command = lambda: code_insert_comment("// ", ""))
        code_comment_menu.add_command(label = "C-style Multiline", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_comment("/* ", " */"))
        code_menu.add_cascade(label = "Insert Comment", image = img_blank, compound = LEFT, menu = code_comment_menu, underline = 7)
        # Create the Code -> Insert Doctype submenu.
        code_doctype_menu = Menu(code_menu, tearoff = CONFIG["tearoff"])
        code_doctype_menu.add_command(label = "HTML5", image = img_blank, compound = LEFT, underline = 4, command = lambda: code_insert_doctype("html5"))
        code_doctype_menu.add_command(label = "HTML 4.01 Strict", image = img_blank, compound = LEFT, underline = 10, command = lambda: code_insert_doctype("html4strict"))
        code_doctype_menu.add_command(label = "HTML 4.01 Transitional", image = img_blank, compound = LEFT, underline = 10, command = lambda: code_insert_doctype("html4trans"))
        code_doctype_menu.add_command(label = "HTML 4.01 Frameset", image = img_blank, compound = LEFT, underline = 10, command = lambda: code_insert_doctype("html4frame"))
        code_doctype_menu.add_command(label = "XHTML 1.0 Strict", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_doctype("xhtml1strict"))
        code_doctype_menu.add_command(label = "XHTML 1.0 Transitional", image = img_blank, compound = LEFT, underline = 1, command = lambda: code_insert_doctype("xhtml1trans"))
        code_doctype_menu.add_command(label = "XHTML 1.0 Frameset", image = img_blank, compound = LEFT, underline = 3, command = lambda: code_insert_doctype("xhtml1frame"))
        code_doctype_menu.add_command(label = "XHTML 1.1", image = img_blank, compound = LEFT, underline = 6, command = lambda: code_insert_doctype("xhtml11"))
        code_doctype_menu.add_command(label = "XHTML 2.0", image = img_blank, compound = LEFT, underline = 6, command = lambda: code_insert_doctype("xhtml2"))
        code_menu.add_cascade(label = "Insert Doctype", image = img_blank, compound = LEFT, menu = code_doctype_menu, underline = 7)
        code_menu.add_command(label = "Insert XML Prolog", image = img_blank, compound = LEFT, underline = 7, command = lambda: code_insert("""<?xml version="1.0" encoding="UTF-8"?>"""))
        code_menu.add_command(label = "Insert Tag...", image = img_blank, compound = LEFT, underline = 7, command = code_insert_tag)
        #  Create the Code -> Insert HTML submenu.
        code_tag_menu = Menu(code_menu, tearoff = CONFIG["tearoff"])
        # Create the Code -> Insert HTML -> Structure submenu.
        code_tag_struct_menu = Menu(code_tag_menu, tearoff = CONFIG["tearoff"])
        code_tag_struct_menu.add_command(label = "HTML", image = img_blank, compound = LEFT, underline = 2, command = lambda: code_insert_tag(tname = "html", ttype = False))
        code_tag_struct_menu.add_command(label = "Head", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "head", ttype = False))
        code_tag_struct_menu.add_command(label = "Body", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "body", ttype = False))
        code_tag_menu.add_cascade(label = "Structure", image = img_blank, compound = LEFT, menu = code_tag_struct_menu, underline = 0)
        # Create the Code -> Insert HTML -> General submenu.
        code_tag_gen_menu = Menu(code_tag_menu, tearoff = CONFIG["tearoff"])
        code_tag_gen_menu.add_command(label = "Hyperlink", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "a", ttype = False))
        code_tag_gen_menu.add_command(label = "Details", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "details", ttype = False))
        code_tag_gen_menu.add_command(label = "Summary", image = img_blank, compound = LEFT, underline = 1, command = lambda: code_insert_tag(tname = "summary", ttype = False))
        code_tag_gen_menu.add_command(label = "Inline Frame", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "iframe", ttype = False))
        code_tag_gen_menu.add_command(label = "Script", image = img_blank, compound = LEFT, underline = 1, command = lambda: code_insert_tag(tname = "script", ttype = False))
        code_tag_gen_menu.add_command(label = "Style", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "style", ttype = False))
        code_tag_gen_menu.add_command(label = "Link", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "link", ttype = True))
        code_tag_gen_menu.add_command(label = "Meta", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "meta", ttype = True))
        code_tag_menu.add_cascade(label = "General", image = img_blank, compound = LEFT, menu = code_tag_gen_menu, underline = 0)
        # Create the Code -> Insert HTML -> Layout submenu.
        code_tag_lay_menu = Menu(code_tag_menu, tearoff = CONFIG["tearoff"])
        code_tag_lay_menu.add_command(label = "Division", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "div", ttype = False))
        code_tag_lay_menu.add_command(label = "Article", image = img_blank, compound = LEFT, underline = 1, command = lambda: code_insert_tag(tname = "article", ttype = False))
        code_tag_lay_menu.add_command(label = "Header", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "header", ttype = False))
        code_tag_lay_menu.add_command(label = "Section", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "section", ttype = False))
        code_tag_lay_menu.add_command(label = "Navigation", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "nav", ttype = False))
        code_tag_lay_menu.add_command(label = "Aside", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "aside", ttype = False))
        code_tag_lay_menu.add_command(label = "Footer", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "footer", ttype = False))
        code_tag_menu.add_cascade(label = "Layout", image = img_blank, compound = LEFT, menu = code_tag_lay_menu, underline = 2)
        # Create the Code -> Insert HTML -> Table submenu.
        code_tag_table_menu = Menu(code_tag_menu, tearoff = CONFIG["tearoff"])
        code_tag_table_menu.add_command(label = "Table", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "table", ttype = False))
        code_tag_table_menu.add_command(label = "Row", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "tr", ttype = False))
        code_tag_table_menu.add_command(label = "Data", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "td", ttype = False))
        code_tag_table_menu.add_separator()
        code_tag_table_menu.add_command(label = "Head", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "thead", ttype = False))
        code_tag_table_menu.add_command(label = "Body", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "tbody", ttype = False))
        code_tag_table_menu.add_command(label = "Footer", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "tfoot", ttype = False))
        code_tag_table_menu.add_separator()
        code_tag_table_menu.add_command(label = "Column", image = img_blank, compound = LEFT, underline = 2, command = lambda: code_insert_tag(tname = "col", ttype = False))
        code_tag_table_menu.add_command(label = "Column Group", image = img_blank, compound = LEFT, underline = 7, command = lambda: code_insert_tag(tname = "colgroup", ttype = False))
        code_tag_table_menu.add_separator()
        code_tag_table_menu.add_command(label = "Caption", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "caption", ttype = False))
        code_tag_menu.add_cascade(label = "Table", image = img_blank, compound = LEFT, menu = code_tag_table_menu, underline = 0)
        # Create the Code -> Insert HTML -> List submenu.
        code_tag_list_menu = Menu(code_tag_menu, tearoff = CONFIG["tearoff"])
        code_tag_list_menu.add_command(label = "Unordered List", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "ul", ttype = False))
        code_tag_list_menu.add_command(label = "Ordered List", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "ol", ttype = False))
        code_tag_list_menu.add_command(label = "Definition List", image = img_blank, compound = LEFT, underline = 2, command = lambda: code_insert_tag(tname = "dl", ttype = False))
        code_tag_list_menu.add_separator()
        code_tag_list_menu.add_command(label = "List Item", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "li", ttype = False))
        code_tag_list_menu.add_command(label = "Definition Term", image = img_blank, compound = LEFT, underline = 11, command = lambda: code_insert_tag(tname = "dt", ttype = False))
        code_tag_list_menu.add_command(label = "Definition Description", image = img_blank, compound = LEFT, underline = 11, command = lambda: code_insert_tag(tname = "dd", ttype = False))
        code_tag_menu.add_cascade(label = "List", image = img_blank, compound = LEFT, menu = code_tag_list_menu, underline = 0)
        # Create the Code -> Insert HTML -> Headers submenu.
        code_tag_header_menu = Menu(code_tag_menu, tearoff = CONFIG["tearoff"])
        code_tag_header_menu.add_command(label = "Header 1", image = img_blank, compound = LEFT, underline = 7, command = lambda: code_insert_tag(tname = "h1", ttype = False))
        code_tag_header_menu.add_command(label = "Header 2", image = img_blank, compound = LEFT, underline = 7, command = lambda: code_insert_tag(tname = "h2", ttype = False))
        code_tag_header_menu.add_command(label = "Header 3", image = img_blank, compound = LEFT, underline = 7, command = lambda: code_insert_tag(tname = "h3", ttype = False))
        code_tag_header_menu.add_command(label = "Header 4", image = img_blank, compound = LEFT, underline = 7, command = lambda: code_insert_tag(tname = "h4", ttype = False))
        code_tag_header_menu.add_command(label = "Header 5", image = img_blank, compound = LEFT, underline = 7, command = lambda: code_insert_tag(tname = "h5", ttype = False))
        code_tag_header_menu.add_command(label = "Header 6", image = img_blank, compound = LEFT, underline = 7, command = lambda: code_insert_tag(tname = "h6", ttype = False))
        code_tag_header_menu.add_separator()
        code_tag_header_menu.add_command(label = "Header Group", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "hgroup", ttype = False))
        code_tag_menu.add_cascade(label = "Headers", image = img_blank, compound = LEFT, menu = code_tag_header_menu, underline = 0)
        # Create the Code -> Insert HTML -> Media submenu.
        code_tag_media_menu = Menu(code_tag_menu, tearoff = CONFIG["tearoff"])
        code_tag_media_menu.add_command(label = "Image", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "img", ttype = True))
        code_tag_media_menu.add_command(label = "Canvas", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "canvas", ttype = False))
        code_tag_media_menu.add_command(label = "Figure", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "figure", ttype = False))
        code_tag_media_menu.add_command(label = "Figure Caption", image = img_blank, compound = LEFT, underline = 2, command = lambda: code_insert_tag(tname = "figcaption", ttype = False))
        code_tag_media_menu.add_separator()
        code_tag_media_menu.add_command(label = "Video", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "video", ttype = False))
        code_tag_media_menu.add_command(label = "Audio", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "audio", ttype = False))
        code_tag_media_menu.add_command(label = "Source", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "source", ttype = True))
        code_tag_media_menu.add_separator()
        code_tag_media_menu.add_command(label = "Embed", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "embed", ttype = True))
        code_tag_media_menu.add_command(label = "Object", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "object", ttype = False))
        code_tag_media_menu.add_command(label = "Param", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "param", ttype = True))
        code_tag_menu.add_cascade(label = "Media", image = img_blank, compound = LEFT, menu = code_tag_media_menu, underline = 0)
        # Create the Code -> Insert HTML -> Form submenu.
        code_tag_form_menu = Menu(code_tag_menu, tearoff = CONFIG["tearoff"])
        code_tag_form_menu.add_command(label = "Form", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "form", ttype = False))
        code_tag_form_menu.add_command(label = "Input", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "input", ttype = True))
        code_tag_form_menu.add_command(label = "Button", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "button", ttype = False))
        code_tag_form_menu.add_command(label = "Text Area", image = img_blank, compound = LEFT, underline = 5, command = lambda: code_insert_tag(tname = "textarea", ttype = False))
        code_tag_form_menu.add_command(label = "Output", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "output", ttype = True))
        code_tag_form_menu.add_command(label = "Datalist", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "datalist", ttype = False))
        code_tag_form_menu.add_command(label = "Select", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "select", ttype = False))
        code_tag_form_menu.add_command(label = "Option", image = img_blank, compound = LEFT, underline = 2, command = lambda: code_insert_tag(tname = "option", ttype = False))
        code_tag_form_menu.add_command(label = "Option Group", image = img_blank, compound = LEFT, underline = 7, command = lambda: code_insert_tag(tname = "optgroup", ttype = False))
        code_tag_form_menu.add_command(label = "Meter", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "meter", ttype = True))
        code_tag_form_menu.add_command(label = "Progressbar", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "progressbar", ttype = True))
        code_tag_menu.add_cascade(label = "Form", image = img_blank, compound = LEFT, menu = code_tag_form_menu, underline = 0)
        # Create the Code -> Insert HTML -> Format submenu
        code_tag_frmt_menu = Menu(code_tag_menu, tearoff = CONFIG["tearoff"])
        # Create the Code -> Insert HTML -> Format -> General submenu.
        code_tag_frmt_gen_menu = Menu(code_tag_frmt_menu, tearoff = CONFIG["tearoff"])
        code_tag_frmt_gen_menu.add_command(label = "Strong", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "strong", ttype = False))
        code_tag_frmt_gen_menu.add_command(label = "Emphasis", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "em", ttype = False))
        code_tag_frmt_gen_menu.add_command(label = "Code", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "code", ttype = False))
        code_tag_frmt_gen_menu.add_command(label = "Variable", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "var", ttype = False))
        code_tag_frmt_gen_menu.add_command(label = "Sample", image = img_blank, compound = LEFT, underline = 3, command = lambda: code_insert_tag(tname = "samp", ttype = False))
        code_tag_frmt_gen_menu.add_command(label = "Keyboard", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "kbd", ttype = False))
        code_tag_frmt_gen_menu.add_command(label = "Preformatted", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "pre", ttype = False))
        code_tag_frmt_gen_menu.add_command(label = "Inserted", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "ins", ttype = False))
        code_tag_frmt_gen_menu.add_command(label = "Deleted", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "del", ttype = False))
        code_tag_frmt_gen_menu.add_command(label = "Marked", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "mark", ttype = False))
        code_tag_frmt_gen_menu.add_command(label = "Address", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "address", ttype = False))
        code_tag_frmt_gen_menu.add_command(label = "Definition", image = img_blank, compound = LEFT, underline = 2, command = lambda: code_insert_tag(tname = "def", ttype = False))
        code_tag_frmt_gen_menu.add_command(label = "Abbreviation", image = img_blank, compound = LEFT, underline = 1, command = lambda: code_insert_tag(tname = "abbr", ttype = False))
        code_tag_frmt_menu.add_cascade(label = "General", image = img_blank, compound = LEFT, menu = code_tag_frmt_gen_menu, underline = 0)
        # Create the Code -> Insert HTML -> Format -> Structure submenu.
        code_tag_frmt_struct_menu = Menu(code_tag_frmt_menu, tearoff = CONFIG["tearoff"])
        code_tag_frmt_struct_menu.add_command(label = "Paragraph", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "p", ttype = False))
        code_tag_frmt_struct_menu.add_command(label = "Span", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "span", ttype = False))
        code_tag_frmt_menu.add_cascade(label = "Structure", image = img_blank, compound = LEFT, menu = code_tag_frmt_struct_menu, underline = 0)
        # Create the Code -> Insert HTML -> Format -> Quotes submenu.
        code_tag_frmt_quot_menu = Menu(code_tag_frmt_menu, tearoff = CONFIG["tearoff"])
        code_tag_frmt_quot_menu.add_command(label = "Quotation", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "q", ttype = False))
        code_tag_frmt_quot_menu.add_command(label = "Blockquote", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "blockquote", ttype = False))
        code_tag_frmt_quot_menu.add_command(label = "Citation", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "cite", ttype = False))
        code_tag_frmt_menu.add_cascade(label = "Quotes", image = img_blank, compound = LEFT, menu = code_tag_frmt_quot_menu, underline = 0)
        code_tag_frmt_br_menu = Menu(code_tag_frmt_menu, tearoff = CONFIG["tearoff"])
        # Create the Code -> Insert HTML -> Format -> Breaks submenu.
        code_tag_frmt_br_menu.add_command(label = "Line Break", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "br", ttype = True))
        code_tag_frmt_br_menu.add_command(label = "Word Break", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert_tag(tname = "wbr", ttype = True))
        code_tag_frmt_menu.add_cascade(label = "Breaks", image = img_blank, compound = LEFT, menu = code_tag_frmt_br_menu, underline = 0)
        code_tag_menu.add_cascade(label = "Formatting", image = img_blank, compound = LEFT, menu = code_tag_frmt_menu, underline = 1)
        code_menu.add_cascade(label = "Insert HTML", image = img_blank, compound = LEFT, menu = code_tag_menu, underline = 9)
        # Create the Code -> Insert Special Characters submenu.
        code_special_menu = Menu(code_menu, tearoff = CONFIG["tearoff"])
        # Create the Code -> Insert Special Characters -> Code submenu.
        code_special_code_menu = Menu(code_special_menu, tearoff = CONFIG["tearoff"])
        code_special_code_menu.add_command(label = "Nonbreaking Space", image = img_blank, compound = LEFT, underline = 12, command = lambda: code_insert("&nbsp;"))
        code_special_code_menu.add_command(label = "Less Than", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert("&lt;"))
        code_special_code_menu.add_command(label = "Greater Than", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert("&gt;"))
        code_special_code_menu.add_command(label = "Ampersand", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert("&amp;"))
        code_special_menu.add_cascade(label = "Code", image = img_blank, compound = LEFT, menu = code_special_code_menu, underline = 0)
        # Create the Code -> Insert Special Characters -> General submenu.
        code_special_gen_menu = Menu(code_special_menu, tearoff = CONFIG["tearoff"])
        code_special_gen_menu.add_command(label = "Section", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert("&sect;"))
        code_special_gen_menu.add_command(label = "Paragraph", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert("&para;"))
        code_special_gen_menu.add_separator()
        code_special_gen_menu.add_command(label = "Copywrite", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert("&copy;"))
        code_special_gen_menu.add_command(label = "Trademark", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert("&tm;"))
        code_special_gen_menu.add_command(label = "Reg. Trademark", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert("&reg;"))
        code_special_gen_menu.add_separator()
        code_special_gen_menu.add_command(label = "Em Dash", image = img_blank, compound = LEFT, underline = 1, command = lambda: code_insert("&mdash;"))
        code_special_gen_menu.add_command(label = "En Dash", image = img_blank, compound = LEFT, underline = 1, command = lambda: code_insert("&ndash;"))
        code_special_gen_menu.add_separator()
        code_special_gen_menu.add_command(label = "Degree", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert("&deg;"))
        code_special_menu.add_cascade(label = "General", image = img_blank, compound = LEFT, menu = code_special_gen_menu, underline = 0)
        # Create the Code -> Insert Special Characters -> Math submenu.
        code_special_math_menu = Menu(code_special_menu, tearoff = CONFIG["tearoff"])
        code_special_math_menu.add_command(label = "Plus-minus", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert("&plusmn;"))
        code_special_math_menu.add_command(label = "Multiply", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert("&times;"))
        code_special_math_menu.add_command(label = "Divide", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert("&divide;"))
        code_special_math_menu.add_separator()
        code_special_math_menu.add_command(label = "One Fourth", image = img_blank, compound = LEFT, underline = 4, command = lambda: code_insert("&frac14;"))
        code_special_math_menu.add_command(label = "One Half", image = img_blank, compound = LEFT, underline = 4, command = lambda: code_insert("&frac12;"))
        code_special_math_menu.add_command(label = "Three Fourth", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert("&frac34;"))
        code_special_menu.add_cascade(label = "Math", image = img_blank, compound = LEFT, menu = code_special_math_menu, underline = 0)
        # Create the Code -> Insert Special Characters -> Currency submenu.
        code_special_cur_menu = Menu(code_special_menu, tearoff = CONFIG["tearoff"])
        code_special_cur_menu.add_command(label = "Cent", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert("&cent;"))
        code_special_cur_menu.add_command(label = "Euro", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert("&euro;"))
        code_special_cur_menu.add_command(label = "Pound", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert("&pound;"))
        code_special_cur_menu.add_command(label = "Yen", image = img_blank, compound = LEFT, underline = 0, command = lambda: code_insert("&yen;"))
        code_special_menu.add_cascade(label = "Currency", image = img_blank, compound = LEFT, menu = code_special_cur_menu, underline = 2)
        code_menu.add_cascade(label = "Insert Special Character", image = img_blank, compound = LEFT, menu = code_special_menu, underline = 7)
        code_menu.add_separator()
        code_menu.add_command(label = "Escape", image = img_blank, compound = LEFT, underline = 0, command = code_escape_sel)
        code_menu.add_command(label = "Remove Tags", image = img_blank, compound = LEFT, underline = 4, command = code_remove_tags)
    
    if CONFIG["menu_options"] == "show":
        # Create the Options menu.
        opt_menu = Menu(menu, tearoff = CONFIG["tearoff"])
        menu.add_cascade(label = "Options", menu = opt_menu, underline = 0)
        opt_wrap_menu = Menu(opt_menu, tearoff = CONFIG["tearoff"])
        opt_menu.add_command(label = "Options...", image = img_opt_options, compound = LEFT, underline = 0, command = opt_options, accelerator = "F3")
        opt_menu.add_command(label = "Revert to Default...", image = img_opt_revert, compound = LEFT, underline = 0, command = opt_revert)
        opt_menu.add_separator()
        opt_menu.add_command(label = "Enlarge Font", image = img_opt_enlarge, compound = LEFT, underline = 0, command = lambda: opt_font_size(True), accelerator = "Ctrl+UpArrow")
        opt_menu.add_command(label = "Shrink Font" ,image = img_opt_shrink, compound = LEFT, underline = 0, command = lambda: opt_font_size(False), accelerator = "Ctrl+DownArrow")
        opt_menu.add_separator()
        opt_menu.add_command(label = "Edit Favorites...", image = img_blank, compound = LEFT, underline = 5, command = opt_edit_favorites)
        opt_menu.add_command(label = "Edit File Types...", image = img_blank, compound = LEFT, underline = 10, command = opt_edit_filetypes)
        if CONFIG["advanced_search"] == "show":
            opt_menu.add_separator()
            opt_menu.add_command(label = "Clear Find History...", image = img_blank, compound = LEFT, underline = 0, command = opt_clear_find_history)
            opt_menu.add_command(label = "Clear Replace History...", image = img_blank, compound = LEFT, underline = 1, command = opt_clear_replace_history)
    
    if CONFIG["menu_help"] == "show":
        # Create the Help menu.
        help_menu = Menu(menu, tearoff = CONFIG["tearoff"])
        menu.add_cascade(label = "Help", menu = help_menu, underline = 0)
        help_menu.add_command(label = "About...", image = img_help_about2, compound = LEFT, underline = 0, command = help_about, accelerator = "Ctrl+F1")
        help_menu.add_separator()
        help_menu.add_command(label = "Help...", image = img_help_about, compound = LEFT, underline = 0, command = help_help, accelerator = "F1")
        help_menu.add_command(label = "Report a Problem...", image = img_help_report, compound = LEFT, underline = 0, command = lambda: webbrowser.open("https://code.google.com/p/pytextedit/issues/list"))
    
# Create the context menu.
context_menu = Menu(root, tearoff = False)
# This command is needed because of a bug where the context menu won't close, I will try to fix it later.
context_menu.add_command(label = "Close Menu", image = img_blank, compound = LEFT, underline = 6)
context_menu.add_separator()
context_menu.add_command(label = "Undo", image = img_edit_undo, compound = LEFT, underline = 0, command = edit_undo, accelerator = "Ctrl+Z")
context_menu.add_command(label = "Redo", image = img_edit_redo, compound = LEFT, underline = 2, command = edit_redo, accelerator = "Shift+Ctrl+Z")
context_menu.add_separator()
context_menu.add_command(label = "Copy", image = img_edit_copy, compound = LEFT, underline = 0, command = edit_copy, accelerator = "Ctrl+C")
context_menu.add_command(label = "Cut", image = img_edit_cut, compound = LEFT, underline = 2, command = edit_cut, accelerator = "Ctrl+X")
context_menu.add_command(label = "Paste", image = img_edit_paste, compound = LEFT, underline = 0, command = edit_paste, accelerator = "Ctrl+V")
context_menu.add_separator()
context_menu.add_command(label = "Select All", image = img_edit_selectall, compound = LEFT, underline = 7, command = edit_select_all, accelerator = "Ctrl+A")
context_menu.add_separator()
context_menu.add_command(label = "Find...", image = img_search_find, compound = LEFT, underline = 0, command = search_find, accelerator = "Ctrl+F")
context_menu.add_command(label = "Replace...", image = img_search_replace, compound = LEFT, underline = 0, command = search_replace, accelerator = "Ctrl+H")
context_menu.add_command(label = "Goto...", image = img_search_goto, compound = LEFT, underline = 0, command = search_goto, accelerator = "Ctrl+G, Ctrl+L")
context_menu.add_separator()
# Create the context menu -> Documents submenu.
context_doc_menu = Menu(context_menu, tearoff = False)
context_menu.add_cascade(label = "Documents", image = img_documents_viewall, compound = LEFT, menu = context_doc_menu, underline = 0)
context_doc_menu.add_command(label = "New Document", image = img_documents_new, compound = LEFT, underline = 0, command = documents_new, accelerator = "Shift+Ctrl+N")
context_doc_menu.add_command(label = "Open Document", image = img_documents_open, compound = LEFT, underline = 0, command = documents_open, accelerator = "Shift+Ctrl+O")
context_doc_menu.add_command(label = "Close Document", image = img_documents_close, compound = LEFT, underline = 0, command = documents_close, accelerator = "Shift+Ctrl+Q")
context_doc_menu.add_separator()
context_doc_menu.add_command(label = "Previous", image = img_documents_previous, compound = LEFT, underline = 0, command = documents_previous, accelerator = "Alt+LeftArrow, Shift+Ctrl+Tab")
context_doc_menu.add_command(label = "Next", image = img_documents_next, compound = LEFT, underline = 2, command = documents_next, accelerator = "Alt+RightArrow, Ctrl+Tab")
context_doc_menu.add_separator()
context_doc_menu.add_command(label = "View All", image = img_documents_viewall, compound = LEFT, underline = 0, command = documents_view, accelerator = "Ctrl+M")
context_menu.add_separator()
# Create the context menu -> Bookmarks submenu.
context_bm_menu = Menu(context_menu, tearoff = False)
context_menu.add_cascade(label = "Bookmarks", image = img_tools_bookmarks, compound = LEFT, menu = context_bm_menu, underline = 0)
context_bm_menu.add_command(label = "Add Bookmark...", image = img_tools_add_bookmark, compound = LEFT, underline = 0, command = tools_bookmarks_add, accelerator = "Ctrl+B")
context_bm_menu.add_command(label = "View Bookmarks...", image = img_tools_bookmarks, compound = LEFT, underline = 0, command = tools_bookmarks_view, accelerator = "Shift+Ctrl+B")
context_bm_menu.add_command(label = "Clear Bookmarks...", image = img_tools_clear_bookmarks, compound = LEFT, underline = 0, command = tools_bookmarks_clear)
context_bm_menu.add_separator()
context_bm_menu.add_command(label = "Save Bookmarks...", image = img_file_save, compound = LEFT, underline = 0, command = tools_bookmarks_save)
context_bm_menu.add_command(label = "Open Bookmarks...", image = img_file_open, compound = LEFT, underline = 0, command = tools_bookmarks_open)
# Define the function to show the context menu.
def show_context_menu(event):
    """Shows the context menu."""
    try:
       # context_menu.tk_popup(event.x_root, event.y_root, 0)
       context_menu.post(event.x_root, event.y_root)
       context_menu.grab_set()
    finally:
        context_menu.grab_release()
# Bind the right-click event to show the context menu.
if CONFIG["menu_context"] == "show":
    # OS X:
    if (root.tk.call("tk", "windowingsystem") == "aqua"):
        text_box.text_box.bind("<Button-2>", show_context_menu)
        text_box.text_box.bind("<Control-1>", show_context_menu)
    # Other systems:
    else:
        text_box.text_box.bind("<Button-3>", show_context_menu)
        text_box.text_box.bind("<Control-Button-1>", show_context_menu)


###############################################################################


# INITIAL LOAD, PART 2 ########################################################
# Try to load a file from command line arguments, part 2.

# If it was loaded from the command line:
if load_cmd:
    # Insert the text.
    text_box.text_box.insert("1.0", to_load)
    # If last file was locked, lock the current one.
    if load_lock:
        tkvar_lock.set(True)
        edit_lock()
    # Set insert cursor to first position.
    text_box.text_box.mark_set("insert", 1.0)
    # Add the file to the recent open list.
    gbl_recent_open.append(gbl_file_name)
    # Update the title.
    update_title()
    # Update the status bar.
    update_status()
    update_status_file(gbl_file_name_short, gbl_last_encode)
    # Reset the undo/redo stack, so opening the file can't be undone.
    text_box.text_box.edit_reset()

if CONFIG["menu_file"] == "show":
    # Update the File -> Recently Opened submenu.
    file_recent_open_update(initial = True)

# Update the MDI.
gbl_mdi[0] = [gbl_file_name, gbl_file_name_short, load_lock, False, "1.0", None, None, to_load]
update_documents_list()
# Update the status bar.
update_status()


###############################################################################


# FIRST TIME DIALOG ###########################################################
# Show this dialog if it's the user's first time using the application.


if gbl_first == "yes":
    # Create the text to show.
    first_info = """Welcome to pytextedit %s!

pytextedit is a simple text editor written in Python using Tk for the GUI.

If you need more information on how a feature works, basic documentation is available from the "Help" option in the Help menu.

If you don't like the default settings, you can change them from the "Options" dialog, accessible from the Options menu.

Found a bug?

If you find a bug or any other problem, please let me know! You can submit a bug report at "http://code.google.com/p/pytextedit/issues/list".

Note to Windows users

If you're using Windows and you don't want the command prompt to appear, simply change the file extension to ".pyw".


(Don't worry, you'll only be bothered with this dialog once!)""" % gbl_meta_version
    # Create the window.
    first_win = Toplevel(root)
    first_win.title("Welcome to pytextedit %s" % gbl_meta_version)
    first_win.transient(root)
    first_win.grab_set()
    first_win.wm_resizable(0, 0)
    # Create the frame for everything.
    first_frm = Frame(first_win)
    first_frm.pack(side = TOP, expand = YES, fill = BOTH)
    # Create the text box and scrollbar.
    first_text = Text(first_frm, wrap = WORD, bg = "white", fg = "black", font = ("arial", CONFIG["font_size"], "normal"))
    first_scroll = Scrollbar(first_frm)
    # Set up scrolling.
    first_text.config(yscrollcommand = first_scroll.set)
    first_scroll.config(command = first_text.yview)
    # Pack the text box and scrollbar.
    first_scroll.pack(fill = Y, side = RIGHT)
    first_text.pack(side = LEFT, expand = YES, fill = BOTH)
    # Insert the text.
    first_text.insert("1.0", first_info)
    # Setup the formatting.
    first_text.tag_config("main_title", font = ("arial", CONFIG["font_size"] + 5, "underline"), justify = "center")
    first_text.tag_config("second_title", font = ("arial", CONFIG["font_size"] + 3, "underline"), justify = "center")
    first_text.tag_config("note", font = ("arial", CONFIG["font_size"], "normal"), justify = "center")
    first_text.tag_add("main_title", "1.0", "1.end")
    first_text.tag_add("second_title", "9.0", "9.end")
    first_text.tag_add("second_title", "13.0", "13.end")
    first_text.tag_add("note", "end-1l", "end")
    # Set text box to read only.
    first_text.config(state = DISABLED)
    # Give focus to the text box.
    first_text.focus()
    # Create the frame for the Close button.
    first_frm2 = Frame(first_win, pady = 5)
    first_frm2.pack(side = TOP)
    # Create the Close button.
    first_btn = Button(first_frm2, text = "Close", width = 7, command = first_win.destroy, font = ("arial", 10, "normal"))
    first_btn.pack(side = TOP)

# Add the curent line tag.
if CONFIG["highlight_line"] == "yes":
    text_box.text_box.tag_add("current_line", "1.0", "1.end")


###############################################################################


# MAIN LOOP ###################################################################
# Start the program!

# Start the main loop.
root.mainloop()

###############################################################################