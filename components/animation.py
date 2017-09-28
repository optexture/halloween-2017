try:
	import common_base as base
except ImportError:
	import base

try:
	import common_util as util
except ImportError:
	import util

class PixelTrickler(base.Extension):
	def __init__(self, comp):
		super().__init__(comp)
		self.inpixels = comp.op('./input_pixels')
		self.nodevals = comp.op('./node_vals')
		self.currentSize = self._Size
		self.tracks = []

	@property
	def _Size(self):
		return int(self.comp.par.Cols), int(self.comp.par.Rows)

	@property
	def _Cursor(self):
		return int(self.comp.par.Cursor)

	@_Cursor.setter
	def _Cursor(self, i):
		self.comp.par.Cursor = i

	def _SetUp(self):
		self._LogBegin('_SetUp()')
		try:
			size = self._Size
			self.currentSize = size
			self.tracks = [
				_TrickleTrack(size[1])
				for _ in range(size[0])
			]
			self._Cursor = 0
		finally:
			self._LogEnd('_SetUp()')

	def Step(self):
		# self._LogBegin('Step() - BEGIN (cursor: {})'.format(self._Cursor))
		# try:
		if not self.tracks or self._Size != self.currentSize:
			self._SetUp()
			if not self.tracks:
				return
		cur = self._Cursor
		self.tracks[cur].PushColor(
			self.inpixels['r'][cur],
			self.inpixels['g'][cur],
			self.inpixels['b'][cur],
			self.inpixels['a'][cur],
		)
		self._Cursor = (cur + 1) % self._Size[0]
		# finally:
		# 	self._LogEnd('Step() - END (cursor: {})'.format(self._Cursor))

	def WriteToCHOP(self, chop):
		chop.clear()
		if not self.tracks:
			return
		w, h = self._Size
		chop.numSamples = self.nodevals.numSamples
		for c in 'rgba':
			chop.appendChan(c)
		for i in range(self.nodevals.numSamples):
			u = self.nodevals['u'][i]
			v = self.nodevals['v'][i]
			x = round(u * (w - 1))
			y = round((1 - v) * (h - 1))
			track = self.tracks[x]
			chop['r'][i], chop['g'][i], chop['b'][i], chop['a'][i] = track.GetPixel(y)

	def WriteToDebugDAT(self, dat):
		dat.clear()
		if not self.tracks or self._Size != self.currentSize:
			self._SetUp()
			if not self.tracks:
				return
		w, h = self._Size
		for x in range(w):
			track = self.tracks[x]
			dat.appendCol([
				_PixelDebugStr(track.GetPixel(y))
				for y in range(h)
			])


def _PixelDebugStr(pixel):
	return repr(['{:.2f}'.format(v) for v in pixel])

class _TrickleTrack:
	def __init__(self, height):
		self.height = height
		self.r = [0] * height
		self.g = [0] * height
		self.b = [0] * height
		self.a = [0] * height

	def PushColor(self, r, g, b, a):
		self.r.pop(-1)
		self.r.insert(0, r)
		self.g.pop(-1)
		self.g.insert(0, g)
		self.b.pop(-1)
		self.b.insert(0, b)
		self.a.pop(-1)
		self.a.insert(0, a)

	def GetPixel(self, y):
		return self.r[y], self.g[y], self.b[y], self.a[y]
