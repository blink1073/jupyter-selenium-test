
from __future__ import print_function, absolute_import

import json
import os
import sys
import time
import threading

from tornado import ioloop
from jinja2 import FileSystemLoader
from notebook.base.handlers import IPythonHandler, FileFindHandler
from notebook.notebookapp import NotebookApp
from traitlets import Bool, Unicode

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

try:
    import coloroma
    coloroma.init()
    COLOR = True
except ImportError:
    COLOR = os.name != 'nt'


LOADER = FileSystemLoader(os.path.dirname(__file__))


def green(text):
    if not COLOR:
        return text
    return '\033[32m%s\033[0m' % text


def red(text):
    if not COLOR:
        return text
    return '\033[31m%s\033[0m' % text


PASS = green('\u221A')  # check mark
FAIL = red('\u00D7')  # x mark


class TestHandler(IPythonHandler):
    """Handle requests between the main app page and notebook server."""

    def get(self):
        """Get the main page for the application's interface."""
        return self.write(self.render_template("index.html",
            static=self.static_url, base_url=self.base_url,
            token=self.settings['token']))

    def get_template(self, name):
        return LOADER.load(self.settings['jinja2_env'], name)


class TestApp(NotebookApp):

    default_url = Unicode('/test')
    open_browser = Bool(False)

    def start(self):
        self.io_loop = ioloop.IOLoop.current()
        default_handlers = [
            (r'/test/?', TestHandler),
            (r"/test/(.*)", FileFindHandler,
                {'path': ''}),
        ]
        self.web_app.add_handlers(".*$", default_handlers)
        self.io_loop.call_later(1, self._run_selenium)
        super(TestApp, self).start()

    def _run_selenium(self):
        thread = threading.Thread(target=run_selenium,
            args=(self.display_url, self._selenium_finished))
        thread.start()

    def _selenium_finished(self, result):
        self.io_loop.add_callback(lambda: sys.exit(result))


def run_selenium(url, callback):
    """Run the selenium test and call the callback with the exit code.exit
    """

    # Enable browser logging (requires Chrome).
    d = DesiredCapabilities.CHROME
    d['loggingPrefs'] = {'browser': 'ALL'}

    print('Starting Chrome Driver')
    driver = webdriver.Chrome(desired_capabilities=d)

    print('Navigating to page:', url)
    driver.get(url)

    failures = []
    passes = 0
    completed = False

    # Start a poll loop.
    t0 = time.time()
    tlast = t0
    while time.time() < tlast + 10:
        for entry in driver.get_log('browser'):
            tlast = time.time()
            # Parse the log entry.
            msg = ' '.join(entry['message'].split()[2:])
            try:
                msg = json.loads(msg)
                # This is the end message.
                if msg.startswith('stdout: '):
                    msg = msg[len('stdout: '):]
                msg = json.loads(msg)
                if msg[0] == 'pass':
                    msg = '%s %s (%dms)' % (PASS,
                                            msg[1]['fullTitle'],
                                            msg[1]['duration'])
                    passes += 1
                elif msg[0] == 'fail':
                    failures.append(msg[1])
                    msg = '%s %s' % (FAIL, red(msg[1]['fullTitle']))
            except Exception:
                pass
            print(msg)

        if 'Test completed' in driver.title:
            completed = True
            break

        # Avoid hogging the main thread.
        time.sleep(0.5)

    duration = time.time() - t0
    driver.quit()

    # Handle the test results.
    print('\n\n')
    if not completed:
        print('Test timed out')
    elif failures:
        total = len(failures) + passes
        errmsg = '%s of %s tests failed' % (len(failures), total)
        print('%s %s:' % (FAIL, red(errmsg)))
        for failure in failures:
            print('\n%s: %s' % (failure['fullTitle'], red(failure['err'])))
            print('\n%s' % failure['stack'])
    else:
        print('%s %s (%dms)' % (
            PASS, green('%d tests completed' % passes), duration * 1000))
    print('\n\n')

    # Return the exit code.
    if not completed or failures:
        callback(1)
    else:
        callback(0)


# Coverage handling.
#
# istanbul instrument src.original.js --output src.js --embed-source true
#
# https://github.com/gotwarlost/istanbul/issues/16#issuecomment-9879731
#
# driver.executeScript("return window.__coverage__;").then(function (obj) {
#     fs.writeFile('coverage/coverage.json', JSON.stringify(obj));
#     driver.quit();
# });


if __name__ == '__main__':
    TestApp.launch_instance()
