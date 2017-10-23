import xml.etree.ElementTree as ET
import random
import copy

class _Converter:
	def __init__(self, templatexml):
		self.root = ET.fromstring(templatexml)
		self.doc = self.root.find('XmlState')
		self.slicetemplate = self.root.find('Slice')
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
		sliceelem.find('./Params[@name="Common"]/Param[@name="Name"]').set('value', 'Panel ' + str(panel.index))
		verts = [
			[v.uv[0] * self.width, (1 - v.uv[1]) * self.height]
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
		shapeobj = sliceelem.find('.//ShapeObject')
		_replaceVertElems(shapeobj.find('Rect'), rectverts)

		_replaceVertElems(shapeobj.find('.//Contour/points'), verts)
		shapeobj.find('.//Contour/segments').text = 'L' * len(verts)

		self._AddNewIds(sliceelem)
		return sliceelem

	def _RebuildScreenSlices(self, screenelem, panels):
		layerselem = screenelem.find('layers')
		layerselem.clear()
		for panel in panels:
			sliceelem = self._CreateSlice(panel)
			layerselem.append(sliceelem)

	def Generate(self, panels):
		for screen in self.doc.findall('.//ScreenSetup/screens/Screen'):
			if screen.attrib['name'].startswith('Projector'):
				self._RebuildScreenSlices(screen, panels)

	def GetXml(self):
		return ET.tostring(self.doc, encoding='unicode')

def _replaceVertElems(parent, verts):
	for elem in list(parent):
		parent.remove(elem)
	for x, y in verts:
		ET.SubElement(parent, 'v', {'x': str(x), 'y': str(y)})

def Convert(templatexml, panels):
	conv = _Converter(templatexml)
	conv.Generate(panels)
	return conv.GetXml()
