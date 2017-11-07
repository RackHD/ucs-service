import threading
import time
import flask


class ThreadingTimer(object):
    def __init__(self, app, interval=60):
        self.interval = interval
        self.app = app
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        while True:
            with self.app.app.app_context():
                handlers = flask.current_app.config.get('handlers', {})
                for host, data in handlers.iteritems():
                    if data and time.time() - data['timestamp'] >= self.interval:
                        data['handle'].logout()
                        handlers[host] = None
            time.sleep(5)
