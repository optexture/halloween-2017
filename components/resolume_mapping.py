import xml.etree.ElementTree as ET
import random
import copy

class _Converter:
	def __init__(self, templatexml, panels):
		self.root = ET.fromstring(templatexml)
		self.doc = self.root.find('XmlState')
		self.slicetemplate = self.root.find('Slice')
		self.panels = panels
		self.usedids = self._GatherUsedIds()
		self.screenselem = self.doc.find('./ScreenSetup/screens')
		self.width = 1920
		self.height = 1080

	def _GatherUsedIds(self):
		return {
			int(elem.get('uniqueId'))
			for elem in self.doc.findall('.//*[@uniqueId]')
		}

	def _NewId(self):
		while True:
			uid = random.randint(1000000000000, 9999999999999)
			if uid not in self.usedids:
				self.usedids.add(uid)
				return uid

	def _AddNewId(self, elem):
		if 'uniqueId' in elem.attrib:
			uid = self._NewId()
			elem.set('uniqueId', str(uid))

	def _AddNewIds(self, root):
		self._AddNewId(root)
		for elem in root.findall('.//*[@uniqueId]'):
			self._AddNewId(elem)

	def _CreateSlice(self, panel):
		sliceelem = copy.deepcopy(self.slicetemplate)
		sliceelem.find('./Params[@name="Common"]/Param[@name="Name"]').set('value', str(panel.index))
		verts = [
			[v.uv[0] * self.width, v.uv[1] * self.height]
			for v in panel
		]
		left = min([v[0] for v in verts])
		right = max([v[0] for v in verts])
		top = min([v[1] for v in verts])
		bottom = max([v[1] for v in verts])

		rectverts = [
			[left, top],
			[left, bottom],
			[right, bottom],
			[right, top],
		]
		_replaceVertElems(sliceelem.find('./InputRect'), rectverts)
		_replaceVertElems(sliceelem.find('./OutputRect'), rectverts)
		_replaceVertElems(sliceelem.find('./SliceMask/ShapeObject/Rect'), rectverts)

		_replaceVertElems(sliceelem.find('./SliceMask/ShapeObject/Shape/Countour/points'), verts)

		self._AddNewIds(sliceelem)
		return sliceelem

	def Generate(self):
		pass

	def GetXml(self):
		return self.doc.tostring()

def _replaceVertElems(parent, verts):
	for elem in list(parent):
		parent.remove(elem)
	for x, y in verts:
		parent.SubElement('v', {'x': x, 'y': y})

def Convert(templatexml, panels):
	conv = _Converter(templatexml, panels)
	conv.Generate()
	return conv.GetXml()
