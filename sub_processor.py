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

TIME_PAIR = re.compile("^.+?-->")
COUNTER   = re.compile("^[0-9]+$")

MAIN_SIZE = 300

def drop(event):
    logging.info("Dropped: {}".format(event.data))
    event.widget.insert("1.0", event.data + "\n")

def process(text: str) -> List[str]:
    words = text.split(" ")
    result = []
    summed = ""
    for word in words:
        if (len(summed + word) + 1) < 42:
            summed += " "
            summed += word
        else:
            result.append(summed)
            summed = word[:]

    result.append(summed)
    return result

class SubtitleProcessor(tk.Frame):

    def __init__(self, master=None):
        super().__init__(master)
        master.minsize(width=MAIN_SIZE,height=MAIN_SIZE)
        self.files = []
        self.label_txt = tk.StringVar()
        self.label_txt.set("Drag and Drop Files to be processed. Backups will be created.")

        self.label = tk.Label(textvariable=self.label_txt)
        self.go_button = tk.Button(text="Process", command=self.get_and_process_files)
        self.input_files_widget = tk.Text(name="file_drop")

        self.input_files_widget.pack()
        self.go_button.pack()
        self.label.pack()

        self.input_files_widget.drop_target_register(DND_FILES)
        self.input_files_widget.dnd_bind("<<Drop>>", drop)

    def get_and_process_files(self):
        files = self.input_files_widget.get("1.0", tk.END).split("\n")
        logging.info("Got: {}".format(files))
        self.process_files([x for x in files if bool(x.strip())])


    def process_files(self, files: List[str]):
        lines : List[str] = []

        for target in files:
            logging.info("Processing: {}".format(target))
            with open(target, 'r') as f:
                lines = f.readlines()

            with open("{}.backup".format(target), 'w') as bkup:
                bkup.write("\n".join(lines))

            # Loop over lines, reformatting as necessary
            cleaned : List[str] = []
            joined : str = ""
            logging.info("Processing {} lines".format(len(lines)))
            for line in lines:
                if not bool(line.strip()):
                    logging.info("Empty Line")
                    cleaned += process(joined)
                    cleaned.append(line)
                    joined = ""
                elif COUNTER.match(line):
                    logging.info("Counter")
                    cleaned.append(line)
                elif TIME_PAIR.match(line):
                    logging.info("time")
                    cleaned.append(line)
                else:
                    joined += line
                    continue

            if bool(joined):
                cleaned += process(joined)

            cleaned.append("DONE")

            with open(target, 'w') as f:
                f.write("\n".join(cleaned))

        logging.info("Finished")
        self.label_txt.set("Finished, it is safe to quit.")

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
