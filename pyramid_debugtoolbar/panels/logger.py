import datetime
import logging
try:
    import threading
except ImportError:
    threading = None

from pyramid_debugtoolbar.panels import DebugPanel
from pyramid_debugtoolbar.utils import format_fname

_ = lambda x: x

class ThreadTrackingHandler(logging.Handler):
    def __init__(self):
        if threading is None:
            raise NotImplementedError(
                "threading module is not available, "
                "the logging panel cannot be used without it")
        logging.Handler.__init__(self)
        self.records = {} # a dictionary that maps threads to log records

    def emit(self, record):
        self.get_records().append(record)

    def get_records(self, thread=None):
        """
        Returns a list of records for the provided thread, of if none is
        provided, returns a list for the current thread.
        """
        if thread is None:
            thread = threading.currentThread()
        if thread not in self.records:
            self.records[thread] = []
        return self.records[thread]

    def clear_records(self, thread=None):
        if thread is None:
            thread = threading.currentThread()
        if thread in self.records:
            del self.records[thread]

handler = ThreadTrackingHandler()
logging.root.addHandler(handler)

class LoggingPanel(DebugPanel):
    name = 'Logging'
    has_content = True

    def __init__(self, request):
        self.request = request
        handler.clear_records()

    def get_and_delete(self):
        records = handler.get_records()
        handler.clear_records()
        return records

    def nav_title(self):
        return _("Logging")

    def nav_subtitle(self):
        records = handler.get_records()
        num = len(records)
        return '%d %s' % (num, self.pluralize("message", "messages", num))

    def title(self):
        return _('Log Messages')

    def url(self):
        return ''

    def content(self):
        records = []
        for record in self.get_and_delete():
            records.append({
                'message': record.getMessage(),
                'time': datetime.datetime.fromtimestamp(record.created),
                'level': record.levelname,
                'file': format_fname(record.pathname),
                'file_long': record.pathname,
                'line': record.lineno,
            })

        vars = {'records': records}

        return self.render(
            'pyramid_debugtoolbar.panels:templates/logger.dbtmako',
            vars,
            request=self.request)


