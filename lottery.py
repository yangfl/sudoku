#!/usr/bin/python3
#encoding=utf-8
from __future__ import with_statement, print_function
import sys, random
import tkinter_addon
if sys.version_info < (3,):
    import Tkinter as tkinter
    import tkFileDialog, tkMessageBox, tkFont
    tkinter.filedialog = tkFileDialog
    tkinter.messagebox = tkMessageBox
    tkinter.font = tkFont
else:
    import tkinter, tkinter.filedialog, tkinter.messagebox, tkinter.font

class lottery(tkinter.Tk):
    debug = 1
    callback = None
    row = None
    column = None
    node_entry = None
    def __init__(self, delay = 10, row = 3, column = 3, font_size = 15, date = ()):
        tkinter.Tk.__init__(self, className = 'tk')
        date = [1,2,3,4,5,6,7,8,9,'a','b','c','d','e','f']
        self.set_date(date)
        self.delay = isinstance(delay, int) and delay > 0 and delay or 10
        self.font_size = isinstance(font_size, int) and font_size > 0 and font_size or 15
        self.node_font = tkinter.font.Font(size = self.font_size)
        self.button_font = tkinter.font.Font(size = 15)
        
        main_frame = tkinter.Frame(self)
        
        self.node_frame = tkinter.Frame(main_frame)
        self.node_frame.pack(side = 'left', fill = 'both', expand = 1)
        self.config_node_frame(row, column)
        
        button_frame = tkinter.Frame(main_frame)
        for text, command in ('开始', self.button_start_action), ('停止', self.button_stop_action), ('导入', self.button_input_action), ('设置', self.button_setting_action):
            tkinter.Button(button_frame, font = self.button_font, text = text, command = command).pack(fill = 'y', expand = 1)
            tkinter.Label(button_frame).pack(fill = 'y', expand = 1)
        button_frame.pack(side = 'right', fill = 'y')
        
        main_frame.pack(fill = 'both', expand = 1)
        
        self.debug_entry = tkinter_addon.AddDebugFrame(self, self.debug, command = self.button_debug_action)
        
        self.protocol('WM_DELETE_WINDOW', self.quit)
    
    def button_debug_action(self):
        exec(self.debug_entry.text)
    
    def button_start_action(self):
        if not self.date:
            if tkinter.messagebox.askyesno('警告', '未导入数据，现在导入？'):
                self.button_input_action()
            return
        if self.date_len < self.node:
            if tkinter.messagebox.askyesno('警告', '数据不足，重新设置窗口？'):
                self.button_setting_action()
            return
        if self.callback is None:
            self.callback = self.after(self.delay, self.loop)
    
    def loop(self):
        available = list(range(self.date_len))
        for node_number in range(self.node):
            self.node_text[node_number].set(self.date[available.pop(random.randint(0, self.date_len-1-node_number))])
        self.callback = self.after(self.delay, self.loop)
    
    def button_stop_action(self):
        if self.callback is not None:
            self.after_cancel(self.callback)
            self.callback = None
    
    def button_input_action(self):
        if self.callback is not None:
            return
        def button_ok_action():
            date = input_text.get(1.0, 'end-1c')
            if date:
                self.set_date(date.split('\n'))
            input_top.destroy()
        def button_loadfile_action():
            file_path = tkinter.filedialog.askopenfilename(title = '选择文件')
            if file_path:
                with open(file_path) as a_file:
                    self.set_date(a_file.read().split('\n'))
                input_top.destroy()
        input_top = tkinter.Toplevel(self)
        input_top.title('导入')
        tkinter.Label(input_top, text = '请输入').pack()
        input_text = tkinter.Text(input_top, height = 15, width = 30)
        input_text.pack()
        tkinter_addon.CopyPasteMenu(input_text)
        input_text.focus()
        input_label_text = tkinter.StringVar()
        tkinter.Label(input_top, textvariable = input_label_text).pack(fill = 'x')
        input_top_botton_frame = tkinter.Frame(input_top)
        tkinter.Button(input_top_botton_frame, text = '从文件加载', command = button_loadfile_action).pack(side = 'left')
        tkinter.Button(input_top_botton_frame, text = '确定', command = button_ok_action).pack(side = 'left')
        input_top_botton_frame.pack()
    
    def button_setting_action(self):
        if self.callback is not None:
            return
        def button_ok_action():
            try:
                row = int(spinbox_row.get())
                column = int(spinbox_column.get())
                self.font_size = int(spinbox_font_size.get())
            except:
                tkinter.messagebox.showwarning('警告', '请输入整数！')
                return
            self.node_font.config(size = self.font_size)
            setting_top.destroy()
            self.config_node_frame(row, column)
        setting_top = tkinter.Toplevel(self)
        setting_top.title('设置')
        tkinter.Label(setting_top, text = '行：').grid(row = 0)
        spinbox_row = tkinter_addon.NumberSpinbox(setting_top, from_ = 1, strict = 1, default = self.row, width = 2)
        spinbox_row.grid(row = 0, column = 1)
        tkinter.Label(setting_top, text = '列：').grid(row = 1)
        spinbox_column = tkinter.Spinbox(setting_top, from_ = 1, to = 20, width = 2)
        spinbox_column.grid(row = 1, column = 1)
        spinbox_column.delete(0, 'end')
        spinbox_column.insert(0, self.column)
        tkinter.Label(setting_top, text = '字号：').grid(row = 2)
        spinbox_font_size = tkinter.Spinbox(setting_top, from_ = 1, to = 100, width = 2)
        spinbox_font_size.grid(row = 2, column = 1)
        spinbox_font_size.delete(0, 'end')
        spinbox_font_size.insert(0, self.font_size)
        tkinter.Button(setting_top, text = '确定', command = button_ok_action).grid(row = 3)
    
    def set_date(self, date):
        if isinstance(date, (tuple, list)):
            self.date = list(date)
            while True:
                try:
                    self.date.remove('')
                except:
                    break
            self.date_len = len(self.date)
    
    def config_node_frame(self, row, column):
        if not isinstance(row, int) or row <= 0 or not isinstance(column, int) or column <= 0:
            raise ValueError('not a positive integer')
        if self.row == row and self.column == column:
            return
        self.row, self.column, self.node = row, column, row*column
        if self.node_entry is not None:
            for one_node_entry in self.node_entry:
                one_node_entry.destroy()
            for one_row_frame in self.row_frame:
                one_row_frame.destroy()
        self.node_text = tuple(tkinter.StringVar() for node_number in range(self.node))
        self.row_frame = tuple(tkinter.Frame(self.node_frame) for row_number in range(self.row))
        self.node_entry = tuple(tkinter.Label(self.row_frame[node_number//self.column], font = self.node_font, textvariable = self.node_text[node_number]) for node_number in range(self.node))
        for one_row_frame in self.row_frame:
            one_row_frame.pack(fill = 'both', expand = 1)
        for one_node_entry in self.node_entry:
            one_node_entry.pack(side = 'left', fill = 'both', expand = 1)

if __name__ == "__main__":
    lottery().mainloop()
