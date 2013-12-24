import gtk 
import glib
import mammoth

from .filewatch import FileWatcher
from .widgets.filechooser import open_file_chooser
from .widgets.messagelist import MessageList
from .widgets.html import HtmlDisplay


_DEFAULT_WIDTH = 600
_PADDING = 5


def start():
    gui = MammothViewerGui()
    try:
        gtk.main()
    finally:
        gui.close()


class MammothViewerGui(object):
    def __init__(self):
        self._docx_watcher = None
        self._create_main_window()

    def close(self):
        self._stop_docx_watcher()

    def _stop_docx_watcher(self):
        if self._docx_watcher is not None:
            self._docx_watcher.stop()
            self._docx_watcher.join()
            self._docx_watcher = None
        
    def _create_main_window(self):
        self._main_window = window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_size_request(width=_DEFAULT_WIDTH, height=400)
        paned = gtk.HPaned()
        paned.add1(self._create_controls())
        paned.add2(self._create_web_view())
        paned.set_position(_DEFAULT_WIDTH / 2)
        window.add(paned)
        window.show_all() 
        window.connect("destroy", gtk.main_quit)
        
        return window
        

    def _create_controls(self):
        controls = self._create_docx_selection_controls()
        box = gtk.VBox()
        
        box.pack_start(self._create_heading(".docx file"), padding=_PADDING, fill=False, expand=False)
        box.pack_start(controls, padding=_PADDING, fill=False, expand=False)
        
        box.pack_start(self._create_heading("Messages"), padding=_PADDING, fill=False, expand=False)
        box.pack_start(self._create_messages_display(), padding=_PADDING)
        
        alignment = gtk.Alignment(0, 0, 1, 1)
        alignment.set_property("left-padding", _PADDING)
        alignment.set_property("right-padding", _PADDING)
        alignment.set_property("top-padding", _PADDING)
        alignment.add(box)
        return alignment
    
    
    def _create_heading(self, text):
        heading = gtk.Label()
        heading.set_alignment(0, 0.5)
        heading.set_markup("<b>{0}</b>".format(text))
        return heading


    def _create_docx_selection_controls(self):
        table = gtk.Table(rows=1, columns=2)
        table.set_col_spacings(_PADDING)
        table.set_row_spacings(_PADDING)
        table.attach(self._create_docx_path_display(), left_attach=0, right_attach=1, top_attach=0, bottom_attach=1)
        table.attach(self._create_docx_path_updater(), left_attach=1, right_attach=2, top_attach=0, bottom_attach=1, xoptions=0, yoptions=0)
        return table


    def _create_docx_path_display(self):
        self._docx_path_display = gtk.Entry()
        self._docx_path_display.set_property("editable", False)
        self._docx_path_display.unset_flags(gtk.CAN_FOCUS)
        self._docx_path_display.set_has_frame(False)
        return self._docx_path_display


    def _create_docx_path_updater(self):
        button = gtk.Button(label="Select .docx file")
        button.connect("clicked", self._choose_docx_path)
        return button


    def _choose_docx_path(self, widget):
        path = open_file_chooser(parent=self._main_window)
        if path is not None:
            self._update_docx_path(path)

    def _update_docx_path(self, path):
        self._docx_path_display.set_text(path)
        self._stop_docx_watcher()
        
        def convert_file():
            with open(path, "rb") as docx_file:
                result = mammoth.convert_to_html(docx_file)
                glib.idle_add(self._web_view.set_html_fragment, result.value, "")
                self._message_list.set_messages(result.messages)
            
        convert_file()
        self._docx_watcher = FileWatcher([path], convert_file)
        self._docx_watcher.start()


    def _create_messages_display(self):
        self._message_list = MessageList()
        return self._message_list
        
    def _create_web_view(self):
        self._web_view = HtmlDisplay()
        return self._web_view  
