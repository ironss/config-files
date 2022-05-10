# umldiagrameditor.py
#
# This Zim plugin allows you to insert a UML diagram in a page.
#
# © 2019 Voyvode
# © 2014 Rolf Kleef
# © 2012 Yao-Po Wang
# GPL-2.0-or-later
#
# Author: Voyvode <voyvode@yandex.com>
# Date: 2019-11-06


from zim.plugins import PluginClass
from zim.plugins.base.imagegenerator \
	import ImageGeneratorClass, BackwardImageGeneratorObjectType

from zim.fs import File, TmpFile
from zim.config import data_file
from zim.applications import Application, ApplicationError


# TODO put these commands in preferences
dotcmd = ('plantuml')


class InsertPlantumlPlugin(PluginClass):

	plugin_info = {
		'name': _('Insert UML Diagram'), # T: plugin name
		'description': _('''\
This plugin provides a diagram editor based on PlantUML.
'''), # T: plugin description
        'help': 'Plugins:UML Diagram Editor',
		'author': 'Voyvode',
	}

	@classmethod
	def check_dependencies(klass):
		has_dotcmd = Application(dotcmd).tryexec()
		return has_dotcmd, [("PlantUML", has_dotcmd, True)]


class BackwardPlantumlImageObjectType(BackwardImageGeneratorObjectType):

	name = 'image+umldiagram'
	label = _('UML Diagram') # T: menu item
	syntax = 'plantuml'
	scriptname = 'umldiagram.puml'
	imagefile_extension = '.png'


class PlantumlGenerator(ImageGeneratorClass):

	def __init__(self, plugin, notebook, page):
		ImageGeneratorClass.__init__(self, plugin, notebook, page)
		self.dotfile = TmpFile('umldiagram.puml')
		self.dotfile.touch()
		self.pngfile = File(self.dotfile.path[:-5] + '.png') # len('.puml') == 5

	def generate_image(self, text):
		# Write to tmp file
		self.dotfile.writelines(text)

		# Call PlantUML
		try:
			dot = Application(dotcmd)
			dot.run((self.pngfile, self.dotfile))
		except ApplicationError:
			return None, None # Sorry, no log
		else:
			if self.pngfile.exists():
				return self.pngfile, None
			else:
				# When supplying a dot file with a syntax error, the dot command
				# doesn't return an error code (so we don't raise
				# ApplicationError), but we still don't have a png file to
				# return, so return None.
				return None, None

	def cleanup(self):
		self.dotfile.remove()
		self.pngfile.remove()
