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
            self.get_presence_element(f"//table//td[@id='{i}']").click()
        print("Cells are marked")

    def click_check_button(self, locator):
        """
        Clicks on the "Check" button on the captcha after selecting images.

        :param locator: XPath locator for the "Check" button.
        """
        time.sleep(1)
        self.get_clickable_element(locator).click()
        print("Pressed the Check button")

    def reset_image_update_flag(self):
        """
        Resets JS flag that tracks recaptcha image updates and
        starts a new observation window for network requests.
        """
        try:
            self.browser.execute_script(
                "if (typeof resetImageUpdateFlag === 'function') { resetImageUpdateFlag(); }"
            )
            print("Reset image update flag")
        except Exception as e:
            print(f"Error while resetting image update flag: {e}")

    def check_for_image_updates(self, expected_updates=None, wait_time=0.5, retries=10):
        """
        Checks if captcha images have been updated using JavaScript and
        network request monitoring. Polls the JS flag several times.

        :param expected_updates: Expected number of image replacement
                                 requests (usually equals number of clicks).
        :param wait_time: Pause between checks in seconds.
        :param retries: Number of polling attempts.
        :return: True if image update requests were detected, False otherwise.
        """
        for _ in range(retries):
            try:
                if expected_updates is not None:
                    updated = self.browser.execute_script(
                        "return (typeof monitorRequests === 'function') && monitorRequests(arguments[0]);",
                        int(expected_updates),
                    )
                else:
                    updated = self.browser.execute_script(
                        "return (typeof monitorRequests === 'function') && monitorRequests();"
                    )
                if updated:
                    print("Images updated (network requests detected)")
                    time.sleep(2)
                    return True
            except Exception as e:
                print(f"Error while checking image updates: {e}")
                break
            time.sleep(wait_time)

        print("No image updates detected")
        return False
