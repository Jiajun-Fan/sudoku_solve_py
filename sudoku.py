#!/usr/bin/env python
import copy
import sys
import string

def getValueList(expt = 0):
    ret = {i:i for i in range(1, 10)}
    if ret.has_key(expt): 
        del ret[expt]
    return ret

def getRowId(row, col):
    return (string.uppercase[row], col+1)

def getColumnId(row, col):
    return (str(col+1), row+1)

def getGroupId(row, col):
    return ("X{0}".format((row-row%3)+col/3+1), (row%3)*3+(col%3)+1)

def getIndexFromRowAndColumn(row, col):
    return "{0}{1}".format(string.uppercase[row], col+1)
    
class JJFAN_SUDOKU_SET:
    def __init__(self, position, name):
        self.name = name
        self.pos = [0] + position

    def getPositionList(self, value):
        ret = copy.copy(self.pos)
        del ret[value]
        return ret

    def Print(self):
        print "Set {0}, Positions {1}".format(self.name, self.pos)

class JJFAN_SUDOKU_SQ:
    def __init__(self, row, col, value=0):
        self.value = value
        self.name = getIndexFromRowAndColumn(row, col)
        (self.rowName, self.rowId) = getRowId(row, col)
        (self.colName, self.colId) = getColumnId(row, col)
        (self.groupName, self.groupId) = getGroupId(row, col)
        if not self.value:
            self.remain = getValueList()
        else:
            self.remain = {}
        
    def assignValue(self, value):
        if 0 != value:
            self.value = value
            self.remain = {}

    def deleteRemain(self, value):
        if self.remain.has_key(value):
            del self.remain[value]
            
    def Print(self):
        print "Node {0}: value: {1}, possible value: {2}".format(self.name, self.value, self.remain) 
        print "In Row {0}, position {1}".format(self.rowName, self.rowId)
        print "In Column {0}, position {1}".format(self.colName, self.colId)
        print "In Group {0}, position {1}".format(self.groupName, self.groupId)
        print

class JJFAN_SUDOKU:
    def __init__(self, fileName):
        self.sq = {}
        self.sets = {}
        self.done = 0
        self.fileName = fileName
        self.debug = True
        #self.debug = False
        self.initSets()
        self.assume = [10, []]
        self.stack = []
        self.rst = 0

    def initSets(self):
        for row in string.uppercase[:9]:
            self.sets[row] = JJFAN_SUDOKU_SET(["{0}{1}".format(row, i) for i in range(1, 10)], row)
        for col in string.digits[1:]:
            self.sets[col] = JJFAN_SUDOKU_SET(["{0}{1}".format(i, col) for i in string.uppercase[:9]], col)
        for i in range(0, 9):
            groupName = "X{0}".format(i+1)
            self.sets[groupName] = JJFAN_SUDOKU_SET(
                ["{0}{1}".format(string.uppercase[(i/3*3+j/3)], (i%3)*3+j%3+1) for j in range(0, 9)], groupName)

    def readPuzzle(self):
        try:
            fp = file(self.fileName, "r")
        except:
            print "Can't open file {0}".format(self.fileName)
            sys.exit(1)

        try:
            for i in range(0, 9):
                line = fp.readline()
                strs = line.split()
                for j in range(0, 9):
                    key = getIndexFromRowAndColumn(i, j)
                    if "-" == strs[j] or "*" == strs[j] :
                        self.sq[key] = JJFAN_SUDOKU_SQ(i, j)
                    else:
                        self.sq[key] = JJFAN_SUDOKU_SQ(i, j, string.atoi(strs[j]))
                        if 0 != self.sq[key].value:
                            self.done = self.done + 1
                        if self.sq[key] > 9:
                            print "input value large than 9"
                            sys.exit(1)
        except:
            print "Parsing Error"
            sys.exit(1)

    def printValue(self):
        print "============================================"
        print "   |  1   2   3  |  4   5   6  |  7   8   9"
        print "--------------------------------------------"
        for row in string.uppercase[:9]:
            print " {0} |".format(row),
            for col in string.digits[1:]:
                key = row + col
                if 0 == self.sq[key].value:
                    print " * ",
                else:
                    print " {0} ".format(self.sq[key].value),
                if col in ("3", "6"):
                    print "|",
            print
            if row in ("C", "F", "I"):
                print "--------------------------------------------"
        print self.done
        print

    def checkValue(self, node):
        rowPosList = self.sets[node.rowName].getPositionList(node.rowId)[1:]
        colPosList = self.sets[node.colName].getPositionList(node.colId)[1:]
        groupPosList = self.sets[node.groupName].getPositionList(node.groupId)[1:]
        for pos in rowPosList + colPosList + groupPosList:
            if self.sq[pos].value == node.value:
                print "Conflict detected! {0} and {1} both have value {2}".format(node.name, pos, node.value)
                if len(self.stack):
                    self.backupValue()
                    return 1
                else:
                    sys.exit(1)
        return 0 

    def deleteRemainValue(self, node):
        rowPosList = self.sets[node.rowName].getPositionList(node.rowId)[1:]
        colPosList = self.sets[node.colName].getPositionList(node.colId)[1:]
        groupPosList = self.sets[node.groupName].getPositionList(node.groupId)[1:]
        for pos in rowPosList + colPosList + groupPosList:
            self.sq[pos].deleteRemain(node.value)

    def solvePuzzlePhase1(self):
        if self.debug:
            self.printValue()
        for a in self.sq:
            if 0 != (self.sq[a].value):
                ret = self.checkValue(self.sq[a])
                if 1 == ret:
                    return

    def solvePuzzlePhase2(self):
        for a in self.sq:
            if 0 != self.sq[a].value:
                self.deleteRemainValue(self.sq[a])

    def solvePuzzlePhase3(self):
        doneValue = self.done
        self.assume = [10, []]
        for a in self.sq:
            possible = len(self.sq[a].remain)
            if possible == 1:
                if 0 == self.sq[a].value:
                    self.sq[a].assignValue(self.sq[a].remain.popitem()[0])
                    self.done = self.done + 1
                    return 1
            if possible > 1 and possible < self.assume[0]:
                self.assume[0] = len(self.sq[a].remain)
                assume = []
                for it in self.sq[a].remain:
                    assume.append((self.sq[a].name, it))
                self.assume[1] = assume
        for a in self.sets:
            valuePos = [{} for i in range(0, 10)]
            for setId in range(1, 10):
                node = self.sq[self.sets[a].pos[setId]]
                for value in node.remain:
                    valuePos[value][setId] = setId
            for value in range(1, 10): 
                possible = len(valuePos[value])
                if possible == 1:
                    position = valuePos[value].popitem()[0]
                    node = self.sq[self.sets[a].pos[position]]
                    if 0 == node.value:
                        node.assignValue(value)
                        self.done = self.done + 1
                        return 1
                if possible > 1 and possible < self.assume[0]:
                    self.assume[0] = len(valuePos[value])
                    assume = []
                    for it in valuePos[value]:
                        name = self.sets[a].pos[it]
                        assume.append((name, value))
                    self.assume[1] = assume
        return 0

    def assumeValue(self):
        if self.assume[0] == 10 or self.assume[0] < 2:
            if len(self.stack):
                self.backupValue()
                return
            else:
                print "Can't solve puzzle!"
                sys.exit(1)

        if 81 == self.done:
            return
        for i in range(0, self.assume[0] - 1):
            info = (self.assume[1][i][0], self.assume[1][i][1], self.assume[0]-1, self.rst)
            self.stack.append((copy.deepcopy(self.sq), copy.deepcopy(self.sets), self.done, info))
        name = self.assume[1][self.assume[0]-1][0]
        value = self.assume[1][self.assume[0]-1][1]
        self.debugprint("make restore point {0}".format(self.rst))
        self.rst = self.rst + 1
        self.debugprint("Assume that {0} = {1}".format(name, value))
        self.sq[name].assignValue(value)
        self.done = self.done + 1

    def backupValue(self):
        self.debugprint("Backup Value")
        (self.sq, self.sets, self.done, info) = self.stack.pop() 
        (name, value, count, rst) = info
        self.debugprint("Restore from restore point {0}".format(rst))
        self.printValue()
        if count > 1:
            self.debugprint("Assume that {0} = {1}".format(name, value))
        self.sq[name].assignValue(value)
        self.done = self.done + 1

    def debugprint(self, value):
        if self.debug:
            print value

    def execute(self):
        self.readPuzzle()
        self.debugprint("Input puzzle:")
        while True:
            self.solvePuzzlePhase1()
            self.solvePuzzlePhase2()
            if self.solvePuzzlePhase3() == 0:
                self.assumeValue()
            if 81 == self.done:
                break
        self.printValue()

if "__main__" == __name__:
    tool = JJFAN_SUDOKU(sys.argv[1])
    tool.execute()
