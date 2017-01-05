from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# Enable browser logging (requires Chrome).
d = DesiredCapabilities.CHROME
d['loggingPrefs'] = {'browser': 'ALL'}
#driver = webdriver.Chrome(desired_capabilities=d)

driver = webdriver.Chrome()
driver.get("http://0.0.0.0:8000")


failures = None
try:
    element = WebDriverWait(driver, 1).until(
        EC.presence_of_element_located((By.ID, "myDynamicElement"))
    )
    failures = int(element.text)
finally:
    # for entry in driver.get_log('browser'):
    #     print(entry)
    driver.quit()


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


# Travis setup:
# https://github.com/kmee/odoo-travis-robotframework/blob/master/.travis.yml
# https://github.com/travis-ci/travis-ci/issues/272#issuecomment-266001631


if failures is None:
    print('Test timed out')
    failures = 1
elif failures:
    print('%s Test(s) failed!' % failures)
else:
    print('Tests passed!')

if failures:
    import sys
    sys.exit(1)


