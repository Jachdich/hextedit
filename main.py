#Doesn't scroll down...

from binascii import hexlify, unhexlify
from itertools import izip_longest
import tkinter as tk

import tkFileDialog as tk_file_dialog


DEFAULT_FILE_TYPES = (
        ("Hexadecimal Files",   "*.hex"),
        ("Windows Executables", "*.exe"),
        ("Linux Binaries",      "*.elf"),
        ("All files",           "*.*")
)


def character_grouper(iterable, n):
    """Group consecutive n values of iterable into tuples.

    Pad the last tuple with '' if need be.

    >>> list(character_grouper('This is a test', 3))
    [('T', 'h', 'i'), ('s', ' ', 'i'), ('s', ' ', 'a'), (' ', 't', 'e'), ('s', 't', '')]
    """
    args = [iter(iterable)] * n
    return izip_longest(*args, fillvalue='')


class Window():
    def __init__(self, width=47, height=20):
        """Create an editor window.

        Editor will allow you to select a file to inspect and
        modify its content as hexadecimal values.
        """
        self.root = tk.Tk()
        self.width = width
        self.height = height
        self.filename = ""
        self.raw_data = ""
        self.lines = []
        self.line_number = 0
        self.create_widgets()

    def run(self):
        """Start the Tkinter main loop on this window and wait for its destruction"""
        self.root.mainloop()

    def create_widgets(self):
        self.menu = tk.Menu(self.root)

        self.filemenu = tk.Menu(self.menu, tearoff=0)
        self.filemenu.add_command(label="Save", command=self.save_file, accelerator="Ctrl-s")
        self.filemenu.add_command(label="Save as...", command=self.saveas_window, accelerator="Ctrl-S")
        self.filemenu.add_command(label="Open...", command=self.open_window, accelerator="Ctrl-o")
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Quit", command=self.save_and_close, accelerator="Ctrl-q")
        self.filemenu.add_command(label="Quit without saving", command=self.root.destroy, accelerator="Ctrl-Q")

        self.menu.add_cascade(label="File", menu=self.filemenu)

        self.main_text = tk.Text(self.root, width=self.width, height=self.height)

        self.main_text.pack(fill="both", expand=1)
        self.main_text.insert("1.0", self.format_current_buffer())

        self.root.config(menu=self.menu)
        self.root.bind("<Down>", self.scroll)
        self.root.bind("<Up>", self.scroll)
        self.root.bind("<Control-s>", self.save_file)
        self.root.bind("<Control-o>", self.open_window)
        self.root.bind("<Control-S>", self.saveas_window)
        self.root.bind("<Control-q>", self.save_and_close)
        self.root.bind("<Control-Q>", self.close)
        self.root.bind("<Configure>", self.resize)
        self.root.protocol('WM_DELETE_WINDOW', self.save_and_close)

    def resize(self, event=None):
        """Update the amount of characters on each row when the window is resized"""
        self.width = self.main_text.winfo_width() / 8
        self.height = self.main_text.winfo_height() / 16
        if self.width / 3 != 0:
            self._preprocess_raw_data()

    def open_file(self, filename):
        """Open a file and display the content"""
        self.filename = filename
        with open(filename, "rb") as f:
            self.raw_data = chr(0) + f.read()
        self.line_number = 0
        self._preprocess_raw_data()

    def _preprocess_raw_data(self):
        """Convert the content of a file to a list of lines
        suitable for the current width.
        """
        data = hexlify(self.raw_data)[2:]
        chars = self.width - (self.width / 3)
        self.lines = [
                "".join(line)
                for line in character_grouper(data, chars)
        ]
        self.main_text.delete("1.0", "end")
        self.main_text.insert("1.0", self.format_current_buffer())

    def save_file(self, event=None):
        """Save the current modifications into the current file"""
        self.update_current_buffer()
        with open(self.filename, "wb") as f:
            f.write(unhexlify("".join(self.lines)))

    def save_and_close(self, event=None):
        self.save_file()
        self.close()

    def close(self, event=None):
        self.root.destroy()

    def saveas_window(self, event=None):
        """Open the 'save as' popup"""
        f = tk_file_dialog.asksaveasfilename(filetypes=DEFAULT_FILE_TYPES)
        if f:
            self.filename = f
            self.save_file()

    def open_window(self, event=None):
        """Open the 'open' popup"""
        f = tk_file_dialog.askopenfilename(filetypes=DEFAULT_FILE_TYPES)
        if f:
            self.open_file(f)

    def format_current_buffer(self):
        """Create the text to display in the main text area.

        Each line of the current view window ("height" lines from current
        line) is formatted by inserting a space every two characters.
        """
        content = self.lines[self.line_number:self.line_number + self.height]
        return "\n".join(" ".join(map("".join, character_grouper(line, 2))) for line in content)

    def update_current_buffer(self):
        """Save the modification made in the main text area into memory"""
        content = self.main_text.get("1.0", "end").replace(" ", "").split("\n")
        for i, line in enumerate(filter(bool, content)):
            self.lines[i + self.line_number] = line

    def scroll(self, event=None, direction=None):
        """Scroll up or down depending on the current position"""
        cursor_position = self.main_text.index("insert")
        current_line = int(cursor_position.split(".")[0])
        if current_line == self.height + 1:
            line_movement = 1
        elif current_line == 1:
            line_movement = -1
        else:
            return

        if 0 < self.line_number < len(self.lines) - self.height:
            self.update_current_buffer()
            self.line_number += line_movement
            self.main_text.delete("1.0", "end")
            self.main_text.insert("1.0", self.format_current_buffer())
            self.main_text.mark_set("insert", cursor_position)


if __name__ == '__main__':
    Window().run()
