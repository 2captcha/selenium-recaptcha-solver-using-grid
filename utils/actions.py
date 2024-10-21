from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class PageActions:
    """
    The PageActions class provides methods for interacting with page elements via Selenium WebDriver.
    Used to perform actions such as switching to an iframe, clicking on elements and checking their state.
    """
    def __init__(self, browser):
        """
        Initializing PageActions.

        :param browser: Selenium WebDriver object for interacting with the browser.
        """
        self.browser = browser

    def get_clickable_element(self, locator, timeout=30):
        """
        Waits until the element is clickable and returns it.

        :param locator: XPath element locator.
        :param timeout: Timeout in seconds (default 30).
        :return: Clickable element.
        """
        return WebDriverWait(self.browser, timeout).until(EC.element_to_be_clickable((By.XPATH, locator)))

    def get_presence_element(self, locator, timeout=30):
        """
        Waits until the element appears in the DOM and returns it.

        :param locator: XPath element locator.
        :param timeout: Timeout in seconds (default 30).
        :return: Found element.
        """
        return WebDriverWait(self.browser, timeout).until(EC.presence_of_element_located((By.XPATH, locator)))

    def switch_to_iframe(self, iframe_locator):
        """
        Switches focus to the iframe of the captcha.

        :param iframe_locator: XPath locator of the iframe.
        """
        iframe = self.get_presence_element(iframe_locator)
        self.browser.switch_to.frame(iframe)
        print("Switched to captcha widget")

    def click_checkbox(self, checkbox_locator):
        """
        Clicks on the checkbox element of the captcha.

        :param checkbox_locator: XPath locator of the captcha checkbox
        """
        checkbox = self.get_clickable_element(checkbox_locator)
        checkbox.click()
        print("Checked the checkbox")

    def switch_to_default_content(self):
        """Returns focus to the main page content from the iframe."""
        self.browser.switch_to.default_content()
        print("Returned focus to the main page content")

    def clicks(self, answer_list):
        """
        Clicks on the image cells in the captcha in accordance with the transmitted list of cell numbers.

        :param answer_list: List of cell numbers to click.
        """
        for i in answer_list:
            self.get_presence_element(f"//table//td[@tabindex='{i}']").click()
        print("Cells are marked")

    def click_check_button(self, locator):
        """
        Clicks on the "Check" button on the captcha after selecting images.

        :param locator: XPath locator for the "Check" button.
        """
        time.sleep(1)
        self.get_clickable_element(locator).click()
        print("Pressed the Check button")

    def check_for_image_updates(self):
        """
        Checks if captcha images have been updated using JavaScript.

        :return: Returns True if the images have been updated, False otherwise.
        """
        print("Images updated")
        return self.browser.execute_script("return monitorRequests();")