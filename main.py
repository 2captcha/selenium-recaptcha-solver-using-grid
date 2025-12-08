import time
import os
import base64
from pathlib import Path
from seleniumbase import Driver
from twocaptcha import TwoCaptcha
from utils.actions import PageActions
from utils.helpers import CaptchaHelper

# CONFIGURATION
url = "https://2captcha.com/demo/recaptcha-v2"
apikey = os.getenv('APIKEY_2CAPTCHA')  # Get the API key for the 2Captcha service from environment variables
solver = TwoCaptcha(apikey, pollingInterval=1)

# LOCATORS

# CAPTCHA LOCATORS
c_iframe_captcha = "//iframe[@title='reCAPTCHA']"
c_checkbox_captcha = "//span[@role='checkbox']"
c_popup_captcha = "//iframe[contains(@title, 'two minutes')]"
c_verify_button = "//button[@id='recaptcha-verify-button']"
c_reload_button = "//button[@id='recaptcha-reload-button']"
c_try_again = "//div[@class='rc-imageselect-incorrect-response']"
c_select_more = "//div[@class='rc-imageselect-error-select-more']"
c_dynamic_more = "//div[@class='rc-imageselect-error-dynamic-more']"
c_select_something = "//div[@class='rc-imageselect-error-select-something']"

# PAGE LOCATORS (For another page the value of this locator needs to be changed)
p_submit_button_captcha = "//button[@type='submit']"

# MAIN LOGIC
with Driver(browser="chrome", locale_code="en") as browser:
    # images_dir = Path("downloaded_files")
    # images_dir.mkdir(exist_ok=True)
    iteration = 0
    last_body = None
    unchanged_count = 0
    select_something_errors = 0

    browser.get(url)
    print("Started")

    # Instantiate helper classes
    page_actions = PageActions(browser)
    captcha_helper = CaptchaHelper(browser, solver)

    # We start by clicking on the captcha checkbox
    page_actions.switch_to_iframe(c_iframe_captcha)
    page_actions.click_checkbox(c_checkbox_captcha)
    page_actions.switch_to_default_content()
    page_actions.switch_to_iframe(c_popup_captcha)
    time.sleep(1)

    # Load JS files
    script_get_data_captcha = captcha_helper.load_js_script('js_scripts/get_captcha_data.js')
    script_change_tracking = captcha_helper.load_js_script('js_scripts/track_image_updates.js')

    # Inject JS once
    captcha_helper.execute_js(script_get_data_captcha)
    captcha_helper.execute_js(script_change_tracking)

    id = None  # Initialize the id variable for captcha

    while True:
        # Get captcha data by calling the JS function directly
        captcha_data = browser.execute_script("return getCaptchaData();")

        iteration += 1

        # Skip sending to 2captcha if image didn't change
        body = captcha_data.get("body")
        if body == last_body:
            unchanged_count += 1
            if unchanged_count < 5:
                print(f"Iteration {iteration}: captcha image unchanged ({unchanged_count} in a row), skipping send to 2captcha")
                time.sleep(1)
                continue
            else:
                print(f"Iteration {iteration}: captcha image unchanged ({unchanged_count} in a row), forcing send to 2captcha once")
                unchanged_count = 0
        else:
            unchanged_count = 0

        last_body = body

        print(f"Iteration {iteration}: rows={captcha_data.get('rows')}, cols={captcha_data.get('columns')}")

        # Forming parameters for solving captcha
        params = {
            "method": "base64",
            "img_type": "recaptcha",
            "recaptcha": 1,
            "cols": captcha_data['columns'],
            "rows": captcha_data['rows'],
            "textinstructions": captcha_data['comment'],
            "lang": "en",
            "can_no_answer": 1
        }

        # If the 3x3 captcha is an id, add previousID to the parameters
        if params['cols'] == 3 and id:
            params["previousID"] = id

        print("Params before solving captcha:", params)

        # Send captcha for solution
        result = captcha_helper.solver_captcha(file=captcha_data['body'], **params)

        if result is None:
            print("Captcha solving failed or timed out. Stopping the process.")
            break

        # If 2captcha reports that this captcha is unsolvable,
        # just retry in the next loop iteration with the same images.
        if isinstance(result, dict) and result.get("unsolvable"):
            print("2Captcha returned ERROR_CAPTCHA_UNSOLVABLE, retrying the same captcha")
            time.sleep(1)
            continue

        # Check if the captcha was solved successfully
        elif result and 'No_matching_images' not in result['code']:
            # We save the id only on the first successful iteration for 3x3 captcha
            if id is None and params['cols'] == 3 and result['captchaId']:
                id = result['captchaId']  # Save id for subsequent iterations

            answer = result['code']
            number_list = captcha_helper.pars_answer(answer)

            # Processing for 3x3
            if params['cols'] == 3:
                # Start new observation window for image updates
                page_actions.reset_image_update_flag()

                # Click on the answers found
                page_actions.clicks(number_list)

                # Wait until all clicked tiles have been updated
                image_update = page_actions.check_for_image_updates(
                    expected_updates=len(number_list)
                )

                if image_update:
                    # If the images have been updated, continue with the saved id
                    print(f"Images updated, continuing with previousID: {id}")
                    continue  # Continue the loop

                # Press the check button after clicks
                page_actions.click_check_button(c_verify_button)

            # Processing for 4x4
            elif params['cols'] == 4:
                # Start new observation window for image updates
                page_actions.reset_image_update_flag()

                # Click on the answers found and immediately press the check button
                page_actions.clicks(number_list)
                page_actions.click_check_button(c_verify_button)

                # After clicking, we check for errors and image updates.
                # For 4x4 we keep original behaviour: any update is enough.
                image_update = page_actions.check_for_image_updates()

                if image_update:
                    print(f"Images updated, continuing without previousID")
                    continue  # Continue the loop

            # If the images are not updated, check the error messages
            if captcha_helper.handle_error_messages(c_try_again, c_select_more, c_dynamic_more, c_select_something):
                # Special handling for "Please select all matching images"
                if captcha_helper.is_message_visible(c_select_something):
                    select_something_errors += 1
                    print(f'"Select all matching images" error #{select_something_errors}')

                    if select_something_errors >= 2:
                        print('Too many "select all matching images" errors, reloading captcha')
                        # Click reload button inside captcha iframe
                        page_actions.click_check_button(c_reload_button)
                        # Reset state for a fresh captcha
                        id = None
                        last_body = None
                        unchanged_count = 0
                        select_something_errors = 0
                        time.sleep(2)
                else:
                    # Other error types reset this specific counter
                    select_something_errors = 0
                continue  # If an error is visible, restart the loop

            # If there are no errors, send the captcha
            page_actions.switch_to_default_content()
            page_actions.click_check_button(p_submit_button_captcha)
            break  # Exit the loop if the captcha is solved

        elif 'No_matching_images' in result['code']:
            # If the captcha returned the code "no_matching_images", check the errors
            page_actions.click_check_button(c_verify_button)
            if captcha_helper.handle_error_messages(c_try_again, c_select_more, c_dynamic_more, c_select_something):
                continue  # Restart the loop if an error is visible
            else:
                page_actions.switch_to_default_content()
                page_actions.click_check_button(p_submit_button_captcha)
                break  # Exit loop

    time.sleep(10)
