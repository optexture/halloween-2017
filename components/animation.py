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
		self._LogBegin('Step(cursor: {})'.format(self._Cursor))
		try:
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
		finally:
			self._LogEnd('Step(cursor: {})'.format(self._Cursor))

	def WriteToCHOP(self, chop):
		# self._LogBegin('WriteToCHOP({})'.format(chop))
		# try:
		chop.clear()
		if not self.tracks:
			# self._LogEvent(' -- no tracks!: {}'.format(repr(self.tracks)))
			return
		w, h = self._Size
		# self._LogEvent(' -- size: {}, {}'.format(w, h))
		chop.numSamples = w * 4
		rchans, gchans, bchans, achans = [], [], [], []
		for y in range(h):
			rchans.append(chop.appendChan('r{}'.format(y)))
			gchans.append(chop.appendChan('g{}'.format(y)))
			bchans.append(chop.appendChan('b{}'.format(y)))
			achans.append(chop.appendChan('a{}'.format(y)))
		for x in range(w):
			track = self.tracks[x]
			for y in range(h):
				rchans[y][x] = track.r[y]
				gchans[y][x] = track.g[y]
				bchans[y][x] = track.b[y]
				achans[y][x] = track.a[y]
		# finally:
		# 	self._LogEnd('WriteToCHOP()')

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
