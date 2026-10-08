
from PyQt5.QtCore import (pyqtSignal,QThread)

class CommonWorker(QThread):
	fun = None
	finished = pyqtSignal()
	threadID = 0
	def __init__(self, parent =None):
		super().__init__(parent)
	def run(self):
		if self.fun:
			self.fun()
			self.finished.emit()



class ThreadPool:
	instance = None
	def __init__(self):
		self.poolsize = 16
		self.threads:list[CommonWorker] = [None]*self.poolsize
	def get_one_thread(self):
		while True:
			for i in range(self.poolsize):
				find_thread = False
				if not self.threads[i]:
					self.threads[i] = CommonWorker()
					self.threads[i].threadID = i;
					find_thread = True
				elif not self.threads[i].isRunning():
					find_thread = True
				else:
					pass
				if find_thread:
					self.threads[i].fun = None
					try:
						self.threads[i].finished.disconnect()
					except:
						pass
					return self.threads[i]
	@classmethod
	def get(cls):
		if not cls.instance:
			cls.instance = cls()
		return cls.instance