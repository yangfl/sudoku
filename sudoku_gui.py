#!/usr/bin/python3
#encoding=utf-8
from __future__ import print_function
import sudoku, sys
import tkinter_addon
if sys.version_info < (3,):
    import Tkinter as tkinter
    import tkFileDialog, tkFont
    tkinter.filedialog = tkFileDialog
    tkinter.font = tkFont
else:
    import tkinter, tkinter.filedialog, tkinter.font

class sudoku_gui(tkinter.Tk):
    debug = 1
    def __init__(self):
        tkinter.Tk.__init__(self, className = '数独计算器')
        self.a_puzzle = sudoku.sudoku()
        self.__solving = 0
        self.__clean = 1
        self.custom_font = tkinter.font.Font(size = 9)
        
        #Main Frame
        main_frame = tkinter.Frame(self)
        
        node_frame = tkinter.Frame(main_frame)
        row_frame = tuple(tkinter.Frame(node_frame) for row_number in range(9))
        self.node_entry = tuple(NodeEntry(row_frame[node_number//9], command = lambda event, node_number = node_number: self.node_entry_action(event, node_number = node_number), font = self.custom_font) for node_number in range(81))
        for node_number in range(81):
            self.node_entry[node_number].pack(side = 'left', fill = 'both', expand = 1)
        for one_row_frame in row_frame:
            one_row_frame.pack(fill = 'both', expand = 1)
        node_frame.pack(side = 'left', fill = 'both', expand = 1)
        
        button_frame = tkinter.Frame(main_frame)
        for text, command in ('计算', self.button_do_action), ('重置', self.button_clear_action), ('导入', self.button_input_action), ('关闭', self.quit):
            tkinter.Button(button_frame, font = self.custom_font, text = text, command = command).pack(fill = 'y', expand = 1)
            tkinter.Label(button_frame).pack(fill = 'y', expand = 1)
        button_frame.pack(side = 'right', fill = 'y', ipadx = 20)
        
        main_frame.pack(fill = 'both', expand = 1)
        
        self.debug_entry = tkinter_addon.AddDebugFrame(self, self.debug, command = self.button_debug_action)
        
        #Info Label
        self.label_text = tkinter.StringVar()
        tkinter.Label(font = self.custom_font, textvariable = self.label_text).pack(side = 'bottom', anchor='w', fill = 'x')
        
        self.protocol('WM_DELETE_WINDOW', self.quit)
        self.bind('<Configure>', lambda event:self.custom_font.config(size = int(0.02*self.winfo_width()+3.2)))    #过点(290,9)
    
    def button_do_action(self):
        try:
            #self.a_puzzle.reset(int(time.time()*1000000%81))
            self.a_puzzle.solve()
        except Exception as e:
            self.label_text.set(e)
            return
        self.sync_puzzle()
        self.__clean = 0
    
    def button_clear_action(self):
        self.a_puzzle.clear()
        self.sync_puzzle()
        self.__clean = 1
        
    def button_input_action(self):
        b_puzzle = sudoku.sudoku()
        def extend(nodes_value):
            try:
                b_puzzle.extend(nodes_value)
            except Exception as e:
                input_label_text.set(e)
                b_puzzle.clear()
                return
            self.button_clear_action()
            self.a_puzzle.extend(nodes_value)
            self.sync_puzzle()
            self.node_entry[len(self.a_puzzle) == 81 and 80 or len(self.a_puzzle)].focus()
            input_top.destroy()
        def button_ok_action():
            nodes_value = input_text.get(1.0, 'end')
            if not nodes_value:
                input_top.destroy()
            extend(nodes_value)
        def button_loadfile_action():
            extend(tkinter.filedialog.askopenfilename(title='选择文件'))
        input_top = tkinter.Toplevel(self)
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
    
    def button_debug_action(self):
        exec(self.debug_entry.text)
    
    def node_entry_action(self, event, node_number):
        if event.keysym == 'Up' and node_number > 8:
            self.node_entry[node_number-9].mark_end()
            return
        elif event.keysym == 'Down' and node_number < 72:
            self.node_entry[node_number+9].mark_end()
            return
        elif event.keysym == 'Left' and node_number:
            self.node_entry[node_number-1].mark_end()
            return
        elif event.keysym == 'Right' and node_number < 80:
            self.node_entry[node_number+1].mark_end()
            return
        elif event.keysym == 'BackSpace':
            if node_number and self.node_entry[node_number].index('insert') == 0:
                self.node_entry[node_number-1].delete(0,'end')
                self.node_entry[node_number-1].mark_end()
                self.add_puzzle(node_number-1, 0)
            else:
                self.add_puzzle(node_number, 0)
            self.clear_autonode()
            return
        elif event.keysym == 'Delete':
            self.clear_autonode()
            return
        elif event.keysym in '123456789':
            node_value = self.node_entry[node_number].get()
            if node_value and node_number < 80:
                next_node_number = node_number+1
                if self.add_puzzle(next_node_number, int(event.keysym)) == 'break':
                    self.node_entry[node_number].mark_end()
                else:
                    self.node_entry[next_node_number].set(event.keysym)
                    self.node_entry[next_node_number].mark_end()
                return 'break'
            if not node_value:
                return self.add_puzzle(node_number, int(event.keysym))
        return 'break'
    
    def add_puzzle(self, node_number, node_value):
        try:
            self.a_puzzle[node_number] = node_value and int(node_value) or 0
        except Exception as e:
            self.label_text.set(e)
            return 'break'
        else:
            self.clear_autonode()
            self.label_text.set('')
    
    def sync_puzzle(self):
        for node_number in range(81):
            self.node_entry[node_number].set(self.a_puzzle[node_number] or '')
            self.node_entry[node_number].config(fg = self.a_puzzle.status(node_number) and 'blue' or 'black')
        self.label_text.set('')
        
    def clear_autonode(self):
        if not self.__clean:
            self.a_puzzle.reset()
            self.sync_puzzle()
            self.__clean = 1


class NodeEntry(tkinter.Entry):
    def __init__(self, master, command = lambda event:None, width = 2, **kargv):
        tkinter.Entry.__init__(self, master, width = width, **kargv)
        self.__command = command
        self.bind('<KeyPress>', self.__command)
    
    def mark_end(self):
        self.focus()
        self.icursor('end')
    
    def set(self, text):
        self.delete(0, 'end')
        self.insert('end', text)


if __name__ == "__main__":
    sudoku_gui().mainloop()
