import time

from utils.actions import PageActions

class CaptchaHelper:
    """
    The CaptchaHelper class provides methods for interacting with captchas
    and executing JavaScript code through Selenium WebDriver. Interaction
    with captchas is carried out using the 2Captcha service.
    """
    def __init__(self, browser, solver):
        """
        Initializing CaptchaHelper.

        :param browser: Selenium WebDriver object for interacting with the browser.
        :param solver: 2Captcha object for solving captchas.
        """
        self.browser = browser
        self.solver = solver
        self.page_actions = PageActions(browser)

    def execute_js(self, script):
        """Executes JavaScript code in the browser.

        :param script: A string of JavaScript code to be executed in the context of the current page.
        :return: The result of JavaScript execution.
        """
        print("Executing JS")
        return self.browser.execute_script(script)

    def solver_captcha(self, **kwargs):
        """Sends the captcha image to be solved via the 2Captcha service

        :param kwargs: Additional parameters for 2Captcha (for example, base64 image).
        :return: The result of solving the captcha or None in case of an error.
        """
        try:
            result = self.solver.grid(**kwargs)
            print(f"Captcha solved")
            return result
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def pars_answer(self, answer):
        """Parses the response from 2Captcha and returns a list of numbers for clicks.

        :param answer: Response from 2Captcha in string format (e.g. "OK: 1/2/3").
        :return: List of cell numbers to click.
        """
        numbers_str = answer.split(":")[1]
        number_list = list(map(int, numbers_str.split("/")))
        new_number_list = [i + 3 for i in number_list] # Add 3 to go to the correct index.
        print("Parsed the response to a list of cell numbers")
        return new_number_list

    def is_message_visible(self, locator):
        """Checks the visibility of an element with a captcha error message

        :param locator: XPath locator of the element to check.
        :return: True if the element is visible, otherwise False.
        """
        try:
            element = self.page_actions.get_presence_element(locator)
            is_visible = self.browser.execute_script("""
                var elem = arguments[0];
                var style = window.getComputedStyle(elem);
                return !(style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0');
            """, element)
            return is_visible
        except Exception as e:
            print(f"Error: {e}")
            return False

    def handle_error_messages(self, l_try_again, l_select_more, l_dynamic_more, l_select_something):
        """
        Checks for error messages on the captcha and returns True if they are visible.

        :param l_try_again: Locator for the "Try again" message.
        :param l_select_more: Locator for the "Select more" message.
        :param l_dynamic_more: Locator for dynamic error.
        :param l_select_something: Locator for the "Select something" message.
        :return: True if any of the error messages are visible, otherwise False.
        """
        time.sleep(1)
        if self.is_message_visible(l_try_again):
            return True
        elif self.is_message_visible(l_select_more):
            return True
        elif self.is_message_visible(l_dynamic_more):
            return True
        elif self.is_message_visible(l_select_something):
            return True
        print("No error messages")
        return False

    def load_js_script(self, file_path):
        """
        Loads JavaScript code from a file.

        :param file_path: Path to the file with JavaScript code.
        :return: A string containing the contents of the file.
        """
        with open(file_path, 'r') as file:
            return file.read()