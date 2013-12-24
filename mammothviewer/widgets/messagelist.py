import gtk
import gobject


class MessageList(gtk.ScrolledWindow):
    def __init__(self):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        
        message_list = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        message_list_view = gtk.TreeView(message_list)
        
        message_list_view.append_column(gtk.TreeViewColumn("Severity", gtk.CellRendererText(), text=0))
        message_list_view.append_column(gtk.TreeViewColumn("Message", gtk.CellRendererText(), text=1))
        
        self.add_with_viewport(message_list_view)
        
        self._message_list = message_list
    
    def set_messages(self, messages):
        self._message_list.clear()
        for message in messages:
            self._message_list.append([message.type, message.message])
