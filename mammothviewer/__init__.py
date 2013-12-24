import collections

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


def view_model(attr_names):
    return ViewModel(attr_names)


class ViewModel(object):
    def __init__(self, attr_names):
        self._attrs = dict((name, None) for name in attr_names)
        self._listeners = collections.defaultdict(lambda: [])

    def __setattr__(self, key, value):
        if key.startswith("_"):
            object.__setattr__(self, key, value)
        else:
            if key in self._attrs:
                self._attrs[key] = value
                self._notify(key, value)
            else:
                raise ValueError("Cannot set {0}".format(key))
    
    def __getattr__(self, key):
        return self._attrs[key]
    
    def on_change(self, key, listener):
        if key in self._attrs:
            self._listeners[key].append(listener)
        else:
            raise ValueError("Cannot listen for {0}".format(key))
    
    def _notify(self, key, value):
        for listener in self._listeners[key]:
            listener(value)


def mammoth_view_model():
    return view_model(["docx_path", "messages"])


class MammothViewerGui(object):
    def __init__(self):
        self._view_model = mammoth_view_model()
        self._set_up_watcher()
        self._create_main_window()

    def _set_up_watcher(self):
        self._view_model.on_change("docx_path", lambda x: self._restart_docx_watcher())
        self._docx_watcher = None

    def close(self):
        self._stop_docx_watcher()

    def _start_docx_watcher(self):
        if self._docx_watcher is not None:
            raise ValueError("watcher is already running")
        
        def convert_file(docx_path):
            with open(docx_path, "rb") as docx_file:
                result = mammoth.convert_to_html(docx_file)
                glib.idle_add(self._web_view.set_html_fragment, result.value, "")
                self._view_model.messages = result.messages
            
        watched_paths = [self._view_model.docx_path]
        self._docx_watcher = FileWatcher(
            paths=watched_paths,
            func=lambda: convert_file(*watched_paths)
        )
        self._docx_watcher.trigger()
        self._docx_watcher.start()

    def _stop_docx_watcher(self):
        if self._docx_watcher is not None:
            self._docx_watcher.stop()
            self._docx_watcher.join()
            self._docx_watcher = None

    def _restart_docx_watcher(self):
        self._stop_docx_watcher()
        self._start_docx_watcher()
        
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
        docx_path_display = gtk.Entry()
        docx_path_display.set_property("editable", False)
        docx_path_display.unset_flags(gtk.CAN_FOCUS)
        docx_path_display.set_has_frame(False)
        
        self._view_model.on_change("docx_path", docx_path_display.set_text)
        
        return docx_path_display


    def _create_docx_path_updater(self):
        button = gtk.Button(label="Select .docx file")
        button.connect("clicked", self._choose_docx_path)
        return button


    def _choose_docx_path(self, widget):
        path = open_file_chooser(parent=self._main_window)
        if path is not None:
            self._update_docx_path(path)

    def _update_docx_path(self, path):
        self._view_model.docx_path = path

    def _create_messages_display(self):
        message_list = MessageList()
        self._view_model.on_change("messages", message_list.set_messages)
        return message_list
        
    def _create_web_view(self):
        self._web_view = HtmlDisplay()
        return self._web_view  
