import gtk


def open_file_chooser(parent):
    chooser = gtk.FileChooserDialog(
        title=None,
        parent=parent,
        action=gtk.FILE_CHOOSER_ACTION_OPEN,
        buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_OK)
    )
    try:
        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            return chooser.get_filename()
    finally:
        chooser.destroy()  
