
import os
import sys
import threading

from tornado import ioloop
from jinja2 import FileSystemLoader
from notebook.base.handlers import IPythonHandler, FileFindHandler
from notebook.notebookapp import NotebookApp
from traitlets import Bool, Unicode

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


LOADER = FileSystemLoader(os.path.dirname(__file__))


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
                {'path': 'build'}),
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
    # Enable browser logging (requires Chrome).
    d = DesiredCapabilities.CHROME
    d['loggingPrefs'] = {'browser': 'ALL'}

    print('Starting Chrome Driver')
    driver = webdriver.Chrome(desired_capabilities=d)

    print('Navigating to page', url)
    driver.get(url)

    failures = None
    try:
        print('Running Tests')
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "myDynamicElement"))
        )
        failures = int(element.text)
    finally:
        for entry in driver.get_log('browser'):
            print(entry)
        driver.quit()

    if failures is None:
        print('Test timed out')
        failures = 1
    elif failures:
        print('%s Test(s) failed!' % failures)
    else:
        print('Tests passed!')

    if failures:
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
