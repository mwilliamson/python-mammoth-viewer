import gtk 
import glib
import mammoth

from .viewmodels import create_view_model
from .filewatch import FileWatcher
from .widgets.filechooser import open_file_chooser
from .widgets.messagelist import MessageList
from .widgets.html import HtmlDisplay


_DEFAULT_WIDTH = 600
_PADDING = 5


def start():
    view_model = mammoth_view_model()
    with MammothFilesWatcher(view_model) as watcher:
        gui = MammothViewerGui(view_model)
        gtk.main()



def mammoth_view_model():
    return create_view_model(["docx_path", "styles_path", "html", "messages"])


class MammothFilesWatcher(object):
    def __init__(self, view_model):
        self._watcher = None
        self._view_model = view_model
        for attr_name in ["docx_path", "styles_path"]:
            view_model.on_change(
                attr_name,
                lambda x: self._restart_watcher()
            )
    
    def close(self):
        self._stop_watcher()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()

    def _start_watcher(self):
        if self._watcher is not None:
            raise ValueError("watcher is already running")
        
        def convert_file(docx_path, styles_path):
            if styles_path is not None:
                with open(styles_path) as styles_file:
                    styles = styles_file.read()
            else:
                styles = None
            
            with open(docx_path, "rb") as docx_file:
                result = mammoth.convert_to_html(docx_file, styles=styles)
                self._view_model.html = result.value
                self._view_model.messages = result.messages
            
        watched_paths = [self._view_model.docx_path, self._view_model.styles_path]
        self._watcher = FileWatcher(
            paths=filter(None, watched_paths),
            func=lambda: convert_file(*watched_paths)
        )
        self._watcher.trigger()
        self._watcher.start()

    def _stop_watcher(self):
        if self._watcher is not None:
            self._watcher.stop()
            self._watcher.join()
            self._watcher = None

    def _restart_watcher(self):
        self._stop_watcher()
        self._start_watcher()


class MammothViewerGui(object):
    def __init__(self, view_model):
        self._view_model = view_model
        self._create_main_window()
        
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
        box = gtk.VBox()
        
        box.pack_start(
            self._create_heading(".docx file"),
            padding=_PADDING, fill=False, expand=False
        )
        box.pack_start(
            self._create_docx_selection_controls(),
            padding=_PADDING, fill=False, expand=False
        )
        
        box.pack_start(
            self._create_heading("Styles file"),
            padding=_PADDING, fill=False, expand=False
        )
        box.pack_start(
            self._create_styles_selection_controls(),
            padding=_PADDING, fill=False, expand=False
        )
        
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
        return self._create_file_selection_controls("docx_path", "Select .docx file")
        
    def _create_styles_selection_controls(self):
        return self._create_file_selection_controls("styles_path", "Select styles file")
        
    def _create_file_selection_controls(self, attr_name, label):
        table = gtk.Table(rows=1, columns=2)
        table.set_col_spacings(_PADDING)
        table.set_row_spacings(_PADDING)
        table.attach(self._create_path_display(attr_name), left_attach=0, right_attach=1, top_attach=0, bottom_attach=1)
        table.attach(self._create_path_updater(attr_name, label), left_attach=1, right_attach=2, top_attach=0, bottom_attach=1, xoptions=0, yoptions=0)
        return table


    def _create_path_display(self, attr_name):
        docx_path_display = gtk.Entry()
        docx_path_display.set_property("editable", False)
        docx_path_display.unset_flags(gtk.CAN_FOCUS)
        docx_path_display.set_has_frame(False)
        
        self._view_model.on_change(attr_name, docx_path_display.set_text)
        
        return docx_path_display


    def _create_path_updater(self, attr_name, label):
        button = gtk.Button(label=label)
        button.connect("clicked", lambda widget: self._choose_path(attr_name))
        return button


    def _choose_path(self, attr_name):
        path = open_file_chooser(parent=self._main_window)
        if path is not None:
            setattr(self._view_model, attr_name, path)

    def _create_messages_display(self):
        message_list = MessageList()
        self._view_model.on_change("messages", message_list.set_messages)
        return message_list
        
    def _create_web_view(self):
        web_view = HtmlDisplay()
        self._view_model.on_change(
            "html",
            lambda html: glib.idle_add(web_view.set_html_fragment, html, "")
        )
        return web_view  
