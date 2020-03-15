import tkinter as tk
import tkinter.font
import tkinter.scrolledtext
from tkinter import filedialog
from get_param import param
import sys


class GUI:
    def __init__(self):
        # Initialize root
        self.root = tk.Tk()
        self.root.title("Power system analysis with flow computation")
        self.root.geometry("800x900")
    # canvas to display image.
        self.canvas = tk.Canvas(self.root, height=700, width=800)
        image_file = tk.PhotoImage(file='sample.png')
        self.imageArea = self.canvas.create_image(0, 0, anchor='nw', image=image_file)
        self.canvas.pack(side='top')
    # text area to display report.
        self.font = tkinter.font.Font(family="helvetica", size=12)
        self.text = tk.scrolledtext.ScrolledText(width=790, height=11, font=self.font, wrap=tk.WORD)
        tk.scrolledtext.ScrolledText()
        self.text.place(x=0, y=500)
        self.readme()
    # button to import file that specify parameters
        self.btn_import = tk.Button(self.root, text='source file', command=self.import_file)
        self.btn_import.place(x=700, y=800)
    # button to close the app
        self.btn_close = tk.Button(self.root, text='close', command=self.close)
        self.btn_close.place(x=390, y=800)
    # whether to use multiprocessing
        self.parallelism = tk.BooleanVar()
        self.checkbox = tk.Checkbutton(self.root, text="Parallelism?", variable=self.parallelism)
        self.checkbox.place(x=700, y=780)
        self.root.mainloop()

    def readme(self):
        file = open("user_guide.txt", "r")
        readme = file.readlines()
        file.close()
        self.text.delete(1.0, tk.END)
        for line in readme:
            self.text.insert("insert", line)

    def import_file(self):
        filename = filedialog.askopenfilename(initialdir="/", title="Select a file.")
        self.text.delete(1.0, tk.END)
        try:
            param(filename, self.parallelism.get())
        except RuntimeError:
            self.text.insert("insert", "Error 01: computation fail to converge.\n")
            return
        except ValueError:
            self.text.insert("insert", "Error 02: invalid input.\n")
            return
    # image
        image_file = tk.PhotoImage(file='power_network.png')
        self.canvas.itemconfigure(self.imageArea, image=image_file)
        self.canvas.image = image_file
    # report
        file = open("flow.report", "r")
        report = file.readlines()
        file.close()
        self.text.insert("insert", "Flow computation report:\n")
        for line in report:
            self.text.insert("insert", line)

    def close(self):
        self.root.destroy()
        sys.exit()


def main():
    app = GUI()


if __name__ == '__main__':
    main()















