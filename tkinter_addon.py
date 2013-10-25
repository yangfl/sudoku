#!/usr/bin/python3
#encoding=utf-8
try:
    import Tkinter as tkinter
except:
    import tkinter
#import traceback

def AddDebugFrame(master, debug_mode = True, **kargv):
    if not debug_mode:
        return
    debug_frame = DebugFrame(master, **kargv)
    debug_frame.pack(side = 'bottom', fill = 'x')
    return debug_frame.debug_entry

class DebugFrame(tkinter.Frame):
    def __init__(self, master, **kargv):
        tkinter.Frame.__init__(self, master)
        self.debug_entry = DebugEntry(self, **kargv)
        self.debug_entry.pack(side = 'left', fill = 'x', expand = 1)
        tkinter.Button(self, text = '执行', command = self.debug_entry.do).pack(side = 'left')

# class DebugEntry(tkinter.Entry):
class DebugEntry(tkinter.Text):
    # def __init__(self, master, command = lambda:None, width = 1, **kargv):
    def __init__(self, master, command = lambda:None, width = 1, height = 1, **kargv):
        # tkinter.Entry.__init__(self, master, width = width, **kargv)
        tkinter.Text.__init__(self, master, width = width, height = height, **kargv)
        CopyPasteMenu(self)
        self.__command = command
        self.__history_statement = []
        self.__temp_history_statement = {}
        self.__pointer = 0
        self.__block_statement = False
        self.bind('<Return>', self.do)
        self.bind('<Up>', self.get_history_statement)
        self.bind('<Down>', self.get_history_statement)
    
    def set(self, text = ''):
        # self.delete(0,'end')
        self.delete(1.0,'end')
        self.insert('end', text)
        # self.icursor('end')
        self.mark_set('insert','end')
    
    def do(self, event = None):
        # statement = self.get()
        statement = self.get(1.0,'end-1c')
        if not statement:
            return 'break'
        if statement and statement[-1] == ':':
            self.__block_statement = True
        if self.__block_statement:
            if statement[-1] == '\n':
                self.config(height = 1)
            else:
                self.config(height = self['height']+1)
                return
        for one_statement in statement.split('\n'):
            if one_statement and not self.__history_statement or one_statement != self.__history_statement[-1]:
                self.__history_statement.append(one_statement)
        self.__temp_history_statement = {}
        self.__pointer = len(self.__history_statement)
        self.set()
        if self.__block_statement:
            self.__block_statement = False
            self.callback(statement)
        else:
            for one_statement in statement.split('\n'):
                self.callback(statement)
        return 'break'
    
    def callback(self, statement):
        self.text = statement
        try:
            self.__command()
        except:
            raise
            #print(traceback.format_exc())
    
    def get_history_statement(self, event):
        # self.__temp_history_statement[self.__pointer] = self.get()
        self.__temp_history_statement[self.__pointer] = self.get(1.0,'end-1c')
        if event.keysym == 'Up' and self.__pointer > 0:
            self.__pointer -= 1
        elif event.keysym == 'Down' and self.__pointer < len(self.__history_statement):
            self.__pointer += 1
        else:
            return
        if self.__pointer in self.__temp_history_statement:
            self.set(self.__temp_history_statement[self.__pointer])
        else:
            self.set(self.__history_statement[self.__pointer])

def CopyPasteMenu(master):
    if isinstance(master, tkinter.Entry):
        select_all = lambda:master.select_range(0, 'end')
    elif isinstance(master, tkinter.Text):
        select_all = lambda:master.tag_add('sel', '1.0', 'end')
    else:
        return
    the_menu = tkinter.Menu(master, tearoff=0)
    for label, command in (
        ('剪切(T)', lambda:master.event_generate('<<Cut>>')),
        ('复制(C)', lambda:master.event_generate('<<Copy>>')),
        ('粘贴(P)', lambda:master.event_generate('<<Paste>>')),
        ('删除(D)', lambda:master.event_generate('<Delete>')),
        ('全选(L)', select_all)
        ):
        the_menu.add_command(label = label, command = command, underline = 3)
    master.bind('<Button-3><ButtonRelease-3>', lambda event:the_menu.tk.call('tk_popup', the_menu, event.x_root, event.y_root))

class NumberSpinbox(tkinter.Spinbox):
    def __init__(self, master, from_ = None, to = None, increment = 1, default = None, strict = False, **kargv):
        tkinter.Spinbox.__init__(self, master, **kargv)
        if isinstance(from_, (int, float)):
            self.from_ = from_
        else:
            self.from_ = None
        if isinstance(to, (int, float)):
            self.to = to
        else:
            self.to = None
        self.increment = isinstance(increment, (int, float)) and increment or 1
        self.strict = None
        if strict:
            if self.from_ is not None:
                self.strict = self.from_
            elif self.to is not None:
                self.strict = self.to
        if isinstance(default, (int, float)) and self.check(default):
            self.set(default)
        self.bind('<Button-1>', self.mousepress)
        self.bind('<KeyPress>', self.keypress)
    
    def mousepress(self, event):
        action = self.identify(event.x, event.y)
        if action is None or action == 'entry':
            return
        value = int(self.get()) + ((action == 'buttonup' and self.increment) or (action == 'buttondown' and 0-self.increment))
        if self.check(value):
            self.set(value)
    
    def check(self, value):
        if not isinstance(value, (int, float)):
            raise ValueError('not a number')
        if (self.from_ is not None and value < self.from_) or (self.to is not None and value > self.to) or (self.strict is not None and (value-self.strict)%self.increment):
            return False
        return True
    
    def set(self, value):
        self.delete(0, 'end')
        self.insert(0, value)
    
    def keypress(self, event):
        if event.keysym == 'BackSpace' or event.keysym == 'Delete' or event.keysym == 'period' or event.keysym in '0123456789':
            self.old_value = self.get()
            self.after(0, self.after_keypress)
        else:
            return 'break'
    
    def after_keypress(self):
        try:
            print(self.get())
            if self.check(int(self.get())):
                return
        except:
            raise
        finally:
            self.set(self.old_value)
        

if __name__ == "__main__":
    pass
