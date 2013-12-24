import gtk
import webkit


class HtmlDisplay(gtk.ScrolledWindow):
    _TEMPLATE = """<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf8">
  </head>
  <body>
    {0}
  </body>
</html>
    """
    def __init__(self):
        gtk.ScrolledWindow.__init__(self)
        
        self._web_view = webkit.WebView()
        self.add(self._web_view)
    
    def set_html_fragment(self, fragment, base_uri):
        full_html = self._TEMPLATE.format(fragment)
        self._web_view.load_string(full_html, "text/html", "utf-8", base_uri)
