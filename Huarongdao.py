# coding=utf-8

from abc import ABCMeta, abstractmethod
import collections
import os
import copy

# 状态
class State(object):
	def __init__(self, size):
		self.size = size
		self.data = []
		self.parent = None
		self.move_from_parent = None

	def __eq__(self, other):
		return self.feature().__eq__(other.feature())

	def __hash__(self):
		return self.feature().__hash__()

	def __str__(self):
		ret = ''
		for row_idx in range(self.size):
			for col_idx in range(self.size):
				idx = row_idx*self.size+col_idx
				ret += '%02d '%(self.data[idx])
			ret += os.linesep
		return ret

	def feature(self):
		ret = ''
		for i in range(self.size*self.size):
			ret += '%02d'%self.data[i]
		return ret
		
	def setData(self, data):
		assert(len(data)==self.size*self.size)
		self.data = data

	def data(self):
		return self.data

# 左移/右移/上移/下移
class Move(object):
	def __init__(self):
		self.stat_from = None
		self.stat_to = None

	def move(self, stat):
		self.stat_from = stat
		self.stat_to = State(stat.size)
		self.stat_to.parent = stat
		self.stat_to.move_from_parent = self

	@abstractmethod
	def opposite(self):
		pass

class MoveLeft(Move):
	def __init__(self):
		super(MoveLeft, self).__init__()

	def __str__(self):
		return "Right"

	def move(self, stat):
		super(MoveLeft, self).move(stat)
		
		stat = self.stat_from
		idx = stat.data.index(0)
		row_idx = idx/stat.size
		col_idx = idx%stat.size
		if col_idx==0:
			return None

		new_row_idx = row_idx
		new_col_idx = col_idx-1
		new_idx = new_row_idx*stat.size+new_col_idx
		
		new_data = copy.deepcopy(stat.data)
		tmp = new_data[new_idx]
		new_data[new_idx] = new_data[idx]
		new_data[idx] = tmp
		self.stat_to.setData(new_data)

		return self.stat_to

	def opposite(self):
		ret = MoveRight()
		ret.stat_to = self.stat_from
		ret.stat_from = self.stat_to
		return ret

class MoveRight(Move):
	def __init__(self):
		super(MoveRight, self).__init__()

	def __str__(self):
		return 'Left'

	def move(self, stat):
		super(MoveRight, self).move(stat)

		stat = self.stat_from
		idx = stat.data.index(0)
		row_idx = idx/stat.size
		col_idx = idx%stat.size
		if col_idx+1==stat.size:
			return None

		new_row_idx = row_idx
		new_col_idx = col_idx+1
		new_idx = new_row_idx*stat.size+new_col_idx
		
		new_data = copy.deepcopy(stat.data)
		tmp = new_data[new_idx]
		new_data[new_idx] = new_data[idx]
		new_data[idx] = tmp
		self.stat_to.setData(new_data)

		return self.stat_to

	def opposite(self):
		ret = MoveLeft()
		ret.stat_to = self.stat_from
		ret.stat_from = self.stat_to
		return ret

class MoveUp(Move):
	def __init__(self):
		super(MoveUp, self).__init__()

	def __str__(self):
		return 'Down'

	def move(self, stat):
		super(MoveUp, self).move(stat)

		stat = self.stat_from
		idx = stat.data.index(0)
		row_idx = idx/stat.size
		col_idx = idx%stat.size
		if row_idx==0:
			return None

		new_row_idx = row_idx-1
		new_col_idx = col_idx
		new_idx = new_row_idx*stat.size+new_col_idx
		
		new_data = copy.deepcopy(stat.data)
		tmp = new_data[new_idx]
		new_data[new_idx] = new_data[idx]
		new_data[idx] = tmp
		self.stat_to.setData(new_data)

		return self.stat_to

	def opposite(self):
		ret = MoveDown()
		ret.stat_to = self.stat_from
		ret.stat_from = self.stat_to
		return ret

class MoveDown(Move):
	def __init__(self):
		super(MoveDown, self).__init__()

	def __str__(self):
		return 'Up'

	def move(self, stat):
		super(MoveDown, self).move(stat)
		
		stat = self.stat_from
		idx = stat.data.index(0)
		row_idx = idx/stat.size
		col_idx = idx%stat.size
		if row_idx+1==stat.size:
			return None

		new_row_idx = row_idx+1
		new_col_idx = col_idx
		new_idx = new_row_idx*stat.size+new_col_idx
		
		new_data = copy.deepcopy(stat.data)
		tmp = new_data[new_idx]
		new_data[new_idx] = new_data[idx]
		new_data[idx] = tmp
		self.stat_to.setData(new_data)

		return self.stat_to

	def opposite(self):
		ret = MoveUp()
		ret.stat_to = self.stat_from
		ret.stat_from = self.stat_to
		return ret

# 策略
class SingleStrategy(object):

	def __init__(self, start):
		self.start = start # 起点

		self.reached = {} # 已到达过的点
		self.reached[self.start.feature()] = self.start

		self.front_reached = set() # 最新到达的点
		self.front_reached.add(self.start)

	def setTwin(self, twin):
		self.twin = twin

	# 若相遇,返回相遇点的状态,否则返回None
	def meetTwin(self):
		for self_stat in self.front_reached:
			if self.twin.reached.has_key(self_stat.feature()):
				twin_stat = self.twin.reached[self_stat.feature()]
				return (self_stat, twin_stat)
		return None

	def run_once(self):
		objs = [self, self.twin]
		for obj in objs:
			meet_stat = obj.meetTwin()
			if meet_stat!=None:
				from_self = True
				if obj!=self:
					from_self = False
				return obj.formatRecord(meet_stat, from_self)

			new_front_reached = set()
			for stat in obj.front_reached:
				moves = [MoveLeft(), MoveRight(), MoveUp(), MoveDown()]
				for move in moves:
					new_stat = move.move(stat)
					if new_stat!=None: # 移动合理
						if not obj.reached.has_key(new_stat.feature()): # 找到了新状态
							obj.reached[new_stat.feature()] = new_stat
							new_front_reached.add(new_stat)
			obj.front_reached = new_front_reached
		if len(self.front_reached)<=0 and len(self.twin.front_reached)<=0:
			raise Exception('no solution for this problem')
		return None
		
	def run(self):
		while True:
			ret = self.run_once()
			if ret!=None:
				return ret

	def formatRecord(self, meet_stat, from_self):
		stats = []
		moves = []
		
		if from_self:
			meet_in_this = meet_stat[0]
			meet_in_that = meet_stat[1]
		else:
			meet_in_this = meet_stat[1]
			meet_in_that = meet_stat[0]
		node = None

		node = meet_in_this
		stats.append(node)
		while node.parent!=None and node.move_from_parent!=None:
			moves.append(node.move_from_parent)
			node = node.parent
			stats.append(node)
		stats.reverse()
		moves.reverse()

		node = meet_in_that
		while node.parent!=None and node.move_from_parent!=None:
			moves.append(node.move_from_parent.opposite())
			node = node.parent
			stats.append(node)
		
		return (stats,moves)
		
class Strategy(object):
	def __init__(self, start, end):
		self.forward = SingleStrategy(start)
		self.backward = SingleStrategy(end)
		self.forward.setTwin(self.backward)
		self.backward.setTwin(self.forward)

	def run(self):
		return self.forward.run()

import random
def randomState(size=3):
	assert(size>1)
	limit = size*size
	buf = []

	while len(buf)<limit-1:
		num = int(random.random()*(limit-1))+1
		if num not in buf:
			buf.append(num)
	buf.append(0)

	stat = State(size)
	stat.setData(buf)
	return stat

import curses   
class Terminal(object):

	def __init__(self):
		self.terminal = curses.initscr()
		#self.terminal.border(0)

	def draw(self, x, y, s):
		l = s.split('\n')
		iter_x = x
		iter_y = y
		for item in l:
			self.terminal.addstr(iter_y, iter_x, item.strip('\r '))
			iter_y += 1
		self.terminal.refresh()

	def getchar(self):
		self.terminal.getch()

	def end(self):
		curses.endwin()

if __name__=='__main__':
	size = 4
	'''
	init_stat = randomState(size)
	final_stat = randomState(size)
	'''
	init_stat = State(size)
	init_stat.setData([1,7,14,12,2,6,13,11,8,4,5,10,9,3,15,0])
	final_stat = State(size)
	final_stat.setData([1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,0])

	'''
	print str(init_stat)
	print ''
	print str(final_stat)
	'''

	terminal = Terminal()
	terminal.draw(5, 2, str(init_stat))
	terminal.draw(15, 3, '->')
	terminal.draw(20, 2, str(final_stat))

	s = Strategy(init_stat, final_stat)
	try:
		stats, moves = s.run()
	except Exception as e:
		indicator_x = 5
		indicator_y = 7
		terminal.draw(indicator_x, indicator_y-1, str(e))
		terminal.getchar()
		terminal.end()
		import sys
		sys.exit(-1)
	assert(len(stats)-1==len(moves))
	
	indicator_x = 5
	indicator_y = 7
	s = 'Press key to start animation'
	terminal.draw(indicator_x, indicator_y-1, s)
	terminal.getchar()
	s = '%d moves : '%(len(moves))
	terminal.draw(indicator_x, indicator_y, s)
	animation_x = 13
	animation_y = 8
	for i in range(len(moves)):
		stat = stats[i]
		move = moves[i]
		#print str(stat)
		terminal.draw(animation_x, animation_y, str(stat))
		#print str(move)
		assert(move.stat_from==stat and move.stat_to==stats[i+1])
		import time
		time.sleep(1)
	#print str(stats[-1])
	terminal.draw(animation_x, animation_y, str(stats[-1]))

	terminal.getchar()
	terminal.end()
	
