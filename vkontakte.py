# - encoding: utf8 - 
#
# Copyright © 2010 Alexey Grunichev
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import rb

from gi.repository import GObject, Peas, Gtk, GdkPixbuf
from gi.repository import RB

from VkontakteSource import VkontakteSource

class VkontakteEntryType(RB.RhythmDBEntryType):
  def __init__(self):
    RB.RhythmDBEntryType.__init__(self, name='vkontakte')

  def do_can_sync_metadata(self, entry):
    return True

class Vkontakte(GObject.Object, Peas.Activatable):
  __gtype_name = 'Vkontakte'
  object = GObject.property(type=GObject.GObject)

  def __init__(self):
    GObject.Object.__init__(self)

  def do_activate(self):
    shell = self.object
    db = shell.props.db
    model = RB.RhythmDBQueryModel.new_empty(db)
    entry_type = VkontakteEntryType()
    db.register_entry_type(entry_type)
    what, width, height = Gtk.icon_size_lookup(Gtk.IconSize.LARGE_TOOLBAR)
    icon = GdkPixbuf.Pixbuf.new_from_file_at_size(rb.find_plugin_file(self, "icon.ico"), width, height)
    source_group = RB.DisplayPageGroup.get_by_id("library")
    self.source = GObject.new(VkontakteSource, name=_("Vkontakte"), shell=shell, query_model=model, plugin=self, pixbuf=icon, entry_type=entry_type)
    shell.append_display_page(self.source, source_group)
    shell.register_entry_type_for_source(self.source, entry_type)
    #ui = shell.get_ui_manager()
    self.source.initialise()

  def do_deactivate(self):
    self.source.delete_thyself()
    self.source = None
