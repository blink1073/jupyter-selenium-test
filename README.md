# Jupyter Selenium Test Proof of Concept

Runs a test against a Jupyter Notebook server using Selenium,
which allows an actual browser to be scripted on the same origin
as the server.

Requires `selenium` (`pip install selenium`) and [ChromeDriver](https://sites.google.com/a/chromium.org/chromedriver/) installed on your `PATH`.

Run the example as `python test.py`.


Findings:

- This approach is too brittle for full unit testing do to
  inability to get proper console output
    - Firefox >48: https://github.com/mozilla/geckodriver/issues/284
    - Chrome: https://bugs.chromium.org/p/chromedriver/issues/detail?id=669
    - No other browsers support it at all: https://seleniumhq.github.io/selenium/docs/api/javascript/module/selenium-webdriver/lib/logging.html
- This approach complicates dev installs by requiring a separate
binary to be downloaded and installed on `PATH`.
- However, this is a good approach to making sure a given 
page loads properly in a notebook app.
