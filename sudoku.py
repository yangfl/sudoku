#!/usr/bin/python3
#encoding=utf-8
from __future__ import with_statement, print_function
import time, os, sys
if sys.version_info < (3,):
    try:
        import cPickle as pickle
    except:
        import pickle
else:
    import pickle

class sudoku:
    __dump__ = os.path.join(os.path.dirname(__file__), 'sudoku.dmp')
    @staticmethod
    def where(node_number):
        '''返回点的位置'''
        row_number, column_number = divmod(node_number, 9)
        yield row_number
        yield column_number
        yield row_number//3*3+column_number//3
    try:
        if os.access(__dump__, os.R_OK):
            with open(__dump__, 'rb') as dump_file:
                __blanklist, __all_number, __unit_list, __related_node_list = pickle.load(dump_file)
    except:
        __blanklist = list(0 for node_number in range(81))
        __all_number = set(range(1, 10))
        #制作单元索引
        row_list = tuple(tuple(row_number*9+column_number for column_number in range(9)) for row_number in range(9))
        column_list = tuple(tuple(row_number*9+column_number for row_number in range(9)) for column_number in range(9))
        box_list = tuple(tuple((row_number+3*box_row_number)*9+column_number+3*box_column_number for row_number in range(3) for column_number in range(3)) for box_row_number in range(3) for box_column_number in range(3))
        __unit_list = (row_list, column_list, box_list)
        del row_list, column_list, box_list
        __related_node_list = []
        for node_number in range(81):
            related_node = set()
            node_where = where(None, node_number)
            related_node.update(__unit_list[0][next(node_where)], __unit_list[1][next(node_where)], __unit_list[2][next(node_where)])
            related_node.discard(node_number)
            __related_node_list.append(tuple(related_node))
        __related_node_list = tuple(__related_node_list)
        del related_node, node_where
        try:
            if not os.path.isfile(__dump__) and os.access(os.path.dirname(__file__), os.W_OK):
                with open(__dump__, 'wb') as dump_file:
                    pickle.dump((__blanklist, __all_number, __unit_list, __related_node_list), dump_file)
        except:
            pass
    del __dump__
    __clean = 1
    __len = 0
    
    
    def __init__(self, nodes_value = ''):
        '''初始化'''
        self.__snapshot = tuple(list(self.__blanklist) for i in range(3))
        self.__puzzle = list(self.__blanklist)
        self.__status = list(self.__blanklist)
        self.__available_number = list(self.__blanklist)
        self.extend(nodes_value)
    
    
    #运行时管理(清除含node_number)
    def __ClearRunningState(self, node_start_number = 0, list_list = None):
        '''清除运行状态'''
        if list_list == None:
            list_list = (self.__status, self.__available_number)
        for one_list in list_list:
            for node_number in range(node_start_number,81):
                one_list[node_number] = 0    #手动/未设置 0 自动 1
        if self.__puzzle in list_list:
            self.__len_delete(self.__len-1)
    def __len_add(self, node_number):
        '''添加点时改变长度'''
        if node_number >= self.__len:
            self.__len = node_number+1
    def __len_delete(self, node_number):
        '''删除点时改变长度'''
        if node_number+1 == self.__len:
            for node_number in range(80, -1, -1):
                if not self.__status[node_number] and self.__puzzle[node_number]:
                    self.__len = int(node_number+1)
                    return
            self.__len = 0
    
    #有效性检查
    def NodeValidCheck(self, node_number, node_value):
        '''检查点'''
        self.NodeNumberCheck(node_number)
        self.NodeValueCheck(node_value)
    def NodeNumberCheck(self, node_number):
        '''检查点的序号'''
        test = self.__puzzle[node_number]
    @staticmethod
    def NodeValueCheck(node_value):
        '''检查点的数值'''
        if not isinstance(node_value, int):
            raise ValueError('must an integer')
        if not -1 < node_value < 10:
            raise ValueError('must between 0 and 9')
    def UnitValidCheck(self, node_start_number = None, node_end_number = None):
        '''检查单元'''
        def OneUnitValidCheck(one_unit):
            NodeValueForCheck = tuple(self.__puzzle[node_number] for node_number in one_unit)
            for number in range(1,10):
                if NodeValueForCheck.count(number) > 1:
                    raise ValueError('number duplicated in one unit')
        if node_start_number is None:
            node_number_list = tuple(range(81))
        elif isinstance(node_start_number, int) and not isinstance(node_end_number, int):
            node_number_list = (node_start_number, )
        elif isinstance(node_start_number, int) and isinstance(node_end_number, int):
            node_number_list = tuple(range(node_start_number, node_end_number))
        elif isinstance(node_start_number, (list, tuple)):
            node_number_list = node_start_number
        unit_to_check = (set(), set(), set())
        for one_node in node_number_list:
            for unit_number, unit_unit_number in zip(range(3), self.where(one_node)):
                unit_to_check[unit_number].add(unit_unit_number)
        for unit_number in range(3):
            for unit_unit_number in unit_to_check[unit_number]:
                OneUnitValidCheck(self.__unit_list[unit_number][unit_unit_number])
    def ThroughCheck(self):
        for node_number in range(81):
            if not self.available(node_number):
                raise ValueError('no (more) solution')
    
    #列表操作
    def __getitem__(self, node_number):
        '''获得一个点'''
        return self.__puzzle[node_number]
    def __setitem__(self, node_number, node_value):
        '''设置一个点'''
        if node_value == 0:
            del self[node_number]
        if not node_value:
            return
        self.NodeValidCheck(node_number, node_value)
        node_old_value, self.__puzzle[node_number] = self.__puzzle[node_number], node_value
        try:
            self.UnitValidCheck(node_number)
        except:
            self.__puzzle[node_number] = node_old_value
            raise
        self.__status[node_number] = 0
        self.__len_add(node_number)
        self.reset()
    def append(self, node_value):
        '''追加一个点'''
        self[len(self)] = node_value
    def extend(self, nodes_value):
        '''追加一些点'''
        if not nodes_value:
            return
        node_start_number = len(self)
        if node_start_number == 81:
            raise IndexError('list assignment index out of range')
        node_number = node_start_number
        if os.path.isfile(str(nodes_value)):
            with open(nodes_value) as a_file:    #, encoding='utf-8'
                nodes_value = a_file.readlines()
        for node_value in str(nodes_value):
            if node_value in '0123456789':
                self.__puzzle[node_number], self.__snapshot[0][node_number]= int(node_value), self.__puzzle[node_number]
                if node_value != '0':
                    self.__len_add(node_number)
                node_number += 1
                if node_number > 80:
                    break
        try:
            self.UnitValidCheck(node_start_number, node_number)
        except:
            for node_number in range(node_start_number, node_number):
                self.__puzzle[node_number] = self.__snapshot[0][node_number]
            self.__len = node_start_number
            raise
        for node_number in range(node_start_number, node_number):
            self.__status[node_number] = 0
        self.reset()
    def __delitem__(self, node_number):
        '''删除一个点'''
        self.__puzzle[node_number] = 0
        self.__len_delete(node_number)
        self.reset()
    def reset(self, node_start_number = 0):
        '''重置自动计算的点'''
        if not self.__clean:
            self.NodeNumberCheck(node_start_number)
            for node_number in range(node_start_number,81):
                if self.__status[node_number]:
                    self.__puzzle[node_number] = 0
            self.__ClearRunningState(node_start_number)
            if not node_start_number:
                self.__clean = 1
    def clear(self):
        '''清除所有点'''
        self.__ClearRunningState(list_list = (self.__status, self.__available_number, self.__puzzle))
        self.__clean = 1
        self.__len = 0
    def __len__(self):
        '''返回长度'''
        return self.__len
    
    
    '''#迭代器
    def __iter__(self):
        self.reset()
        return self
    def __next__(self):
        self.solve()
        return self.list()'''
    
    
    #输出
    def __repr__(self):
        '''可读输出'''
        return '\n'.join(' '.join(str(self.__puzzle[node_number]) for node_number in one_row) for one_row in self.__unit_list[0])
    def status(self, node_number):
        '''返回点的状态'''
        return self.__status[node_number]
    def d(self):
        '''调试'''
        print('\n'.join((str(self), str(self.__status), str(self.__available_number))))
    
    
    #计算
    def available(self, node_number):
        '''计算点的可用数字'''
        return list(self.__all_number.difference(set(self.__puzzle[related_node_number] for related_node_number in self.__related_node_list[node_number])))
    def solve(self, node_start_number = 0):
        '''自动解数独'''
        self.ThroughCheck()
        self.NodeNumberCheck(node_start_number)
        #确认在给定节点之前没有空节点
        for node_number in range(node_start_number):
            if not self.__puzzle[node_number]:
                raise ValueError('node ' + str(node_number) + ' hasn\'t set yet')
        #建立快照
        for node_number in range(node_start_number, 81):
            self.__snapshot[0][node_number] = self.__puzzle[node_number]
            self.__snapshot[1][node_number] = self.__status[node_number]
            self.__snapshot[2][node_number] = self.__available_number[node_number]
        #确定开始节点
        for node_number in range(80, node_start_number-1, -1):
            if self.__status[node_number]:
                break
        forward = 1
        while node_start_number <= node_number < 81:
            #若为手动设置则过
            if not self.__status[node_number] and self.__puzzle[node_number]:
                node_number += forward
                continue
            #若无可用节点列表则设置
            if self.__available_number[node_number] == 0:
                self.__available_number[node_number] = self.available(node_number)
            #若可用节点列表为空则回退
            if not len(self.__available_number[node_number]):
                forward = -1
                self.__puzzle[node_number] = 0
                self.__status[node_number] = 0
                self.__available_number[node_number] = 0
            #若可用节点列表不为空则弹出一个数字
            else:
                forward = 1
                self.__puzzle[node_number] = self.__available_number[node_number].pop(int(time.time()*1000000%len(self.__available_number[node_number])))
                self.__status[node_number] = 1
            node_number += forward
        if node_number < node_start_number:
            for node_number in range(node_start_number, 81):
                self.__puzzle[node_number] = self.__snapshot[0][node_number]
                self.__status[node_number] = self.__snapshot[1][node_number]
                self.__available_number[node_number] = self.__snapshot[2][node_number]
            raise ValueError('no (more) solution')
        self.__clean = 0


class sudoku_cmd(sudoku):
    def __init__(self):
        sudoku.__init__(self)
        if len(sys.argv) > 1:
            self.extend(sys.argv[1])
        else:
            print('Please enter a puzzle\nPress enter to end inputing')
            while len(self) < 81:
                if sys.version_info < (3,):
                    a_line = raw_input('>>>')
                else:
                    a_line = input('>>>')
                if not a_line:
                    break
                if not len(self):
                    try:
                        a_file = eval(a_line,{'__builtins__':None},{})
                    except:
                        a_file = a_line
                    if isinstance(a_file, str) and os.path.isfile(a_file):
                        self.extend(a_file)
                        break
                self.extend(a_file)
        if len(self):
            print('\n'.join(('Input:', str(self), '')))
        self.solve()
        print('\n'.join(('Result:', str(self))))

if __name__ == "__main__":
    sudoku_cmd()
