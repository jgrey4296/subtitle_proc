#!/usr/bin/env python3
"""
Processor for SRT subtitles files.
https://docs.fileformat.com/video/srt/

Reformats text lines into 2 line blocks of 42 chars each

"""
from typing import List, Set, Dict, Tuple, Optional, Any
from typing import Callable, Iterator, Union, Match
from typing import Mapping, MutableMapping, Sequence, Iterable
from typing import cast, ClassVar, TypeVar, Generic

from os.path import join, isfile, exists, abspath
from os.path import split, isdir, splitext, expanduser
from os import listdir
import re
import datetime
import tkinter as tk
import tkinter.ttk as ttk
from tkinterdnd2 import *

# Setup root_logger:
from os.path import splitext, split
import logging as root_logger
LOGLEVEL = root_logger.DEBUG
LOG_FILE_NAME = "log.{}".format(splitext(split(__file__)[1])[0])
root_logger.basicConfig(filename=LOG_FILE_NAME, level=LOGLEVEL, filemode='w')

console = root_logger.StreamHandler()
console.setLevel(root_logger.INFO)
root_logger.getLogger('').addHandler(console)
logging = root_logger.getLogger(__name__)
##############################

TIME_PAIR   = re.compile("^.+?-->")
COUNTER     = re.compile("^[0-9]+$")
MAX_WIDTH   = 42
LINE_GROUPS = 2
MARK_STR    = " _!!!_"
MAIN_SIZE   = 300

INSTRUCTION_TEXT = """Instructions:
Drag and Drop files into the area below, one file per line.
Then press 'Process'.
The files will be copied, with the name {file}_backup, and the originals processed.
"""

def drop(event):
    logging.info("Dropped: {}".format(event.data))
    event.widget.insert("1.0", event.data + "\n")


def process(text: str, max_width=42, mark=False) -> List[str]:
    if not bool(text):
        return []
    if len(text) < max_width:
        return [text]

    words       = text.split(" ")
    constrained = []
    summed      = words[0][:]
    for word in words[1:]:
        if (len(summed + word) + 1) < max_width:
            summed += " "
            summed += word
        else:
            if mark:
                summed += MARK_STR

            constrained.append(summed)
            summed = word[:]

    constrained.append(summed)

    counter = 0
    final   = []
    # Split into groups of two lines
    for line in constrained:
        final.append(line)
        counter += 1
        if counter >= 2:
            counter = 0
            final.append("")

    return final

class SubtitleProcessor(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        master.minsize(width=MAIN_SIZE,height=MAIN_SIZE)
        self.files         = []
        self.strip_data    = False
        self.mark_changes  = False
        self.label_txt     = tk.StringVar()
        self.label_txt.set("")

        # Widgets
        self.instructions       = tk.Label(text=INSTRUCTION_TEXT )
        self.input_files = tk.Text()

        self.options            = ttk.Labelframe(text="Options")
        self.strip_sync         = tk.Checkbutton(self.options, text="Strip Sync Data", command=self.set_strip_data)
        self.mark_changes_check = tk.Checkbutton(self.options, text="Mark Changes with '_!!!_' ", command=self.set_mark)

        self.status_label       = tk.Label(textvariable=self.label_txt)
        self.go_button          = tk.Button(text="Process", command=self.get_and_process_files)

        self.instructions.grid(column=0, row=0)
        self.input_files.grid(column=0, row=1)
        self.strip_sync.pack()
        self.mark_changes_check.pack()
        self.options.grid(column=0, row=2)

        self.go_button.grid(column=0, row=3)
        self.status_label.grid(column=0, row=4, rowspan=2)

        self.input_files.drop_target_register(DND_FILES)
        self.input_files.dnd_bind("<<Drop>>", drop)


    def update_status(self, s:str):
        current = self.label_txt.get().split("\n")
        if len(current) > 5:
            current = current[-5:]

        current.append(s)
        self.label_txt.set("\n".join(current))

    def set_strip_data(self):
        self.strip_data = not self.strip_data

    def set_mark(self):
        self.mark_changes = not self.mark_changes


    def get_and_process_files(self):
        text = [x.strip() for x in self.input_files.get("1.0", tk.END).split("\n")]
        logging.info("Got: {}".format(text))
        non_null = [x for x in text if bool(x)]
        self.update_status("Processing {} files".format(len(non_null)))
        self.process_files(non_null)
        self.update_status("Finished.")

    def process_files(self, files: List[str]):
        lines : List[str] = []
        if self.strip_data:
            self.update_status("Stripping Sync Data")

        for target in files:
            try:
                logging.info("Processing: {}".format(target))
                self.update_status("Processing: {}".format(target))

                with open(target, 'r') as f:
                    lines = f.readlines()

                with open("{}.backup".format(target), 'w') as bkup:
                    bkup.write("\n".join(lines))

                # Loop over lines, reformatting as necessary
                cleaned : List[str] = []
                joined  : str       = ""
                logging.info("Processing {} lines".format(len(lines)))
                for line in [x.strip() for x in lines]:
                    if COUNTER.match(line):
                        logging.info("Counter")
                        if not self.strip_data:
                            cleaned.append(line)
                    elif TIME_PAIR.match(line):
                        logging.info("time")
                        if not self.strip_data:
                            cleaned.append(line)
                    elif not bool(line.strip()):
                        logging.info("Empty Line")
                        cleaned += process(joined, MAX_WIDTH, self.mark_changes)
                        cleaned.append(line)
                        joined = ""
                    else:
                        joined += line
                        continue

                # Add any accumulated that remain
                if bool(joined):
                    cleaned += process(joined, MAX_WIDTH, self.mark_changes)


                with open(target, 'w') as f:
                    f.write("\n".join(cleaned))

            except Exception as err:
                err_text = str(err)
                self.update_status("Processing Failed: {}".format(err_text))

        logging.info("Finished processing")

    def destroy(self):
        """ Customised destroy method  """
        logging.info("Closing program")
        tk.Frame.destroy(self)

if __name__ == '__main__':
    root = Tk()
    root.title("Subtitle Processor")

    app = SubtitleProcessor(master=root)
    root.update_idletasks()
    root.mainloop()
