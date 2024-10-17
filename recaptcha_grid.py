import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
from twocaptcha import TwoCaptcha

# CONFIGURATION
url = "https://2captcha.com/demo/recaptcha-v2"
apikey = os.getenv('APIKEY_2CAPTCHA')  # Get the API key for the 2Captcha service from environment variables
solver = TwoCaptcha(apikey)

# JavaScript script to get captcha data
script_get_data_captcha = """
const getCaptchaData = () => {
    return new Promise((resolve, reject)=>{
        let canvas = document.createElement('canvas')
        let ctx = canvas.getContext('2d')
        let comment = document.querySelector('.rc-imageselect-desc-wrapper').innerText.replace(/\\n/g, ' ')

        let img4x4 = document.querySelector('img.rc-image-tile-44')
        if (!img4x4) {
            let table3x3 = document.querySelector('table.rc-imageselect-table-33 > tbody')
            if (!table3x3) {
                reject('Can not find reCAPTCHA elements')
            }

            let initial3x3img = table3x3.querySelector('img.rc-image-tile-33')

            canvas.width = initial3x3img.naturalWidth
            canvas.height = initial3x3img.naturalHeight
            ctx.drawImage(initial3x3img, 0, 0)

            let updatedTiles = document.querySelectorAll('img.rc-image-tile-11')

            if (updatedTiles.length > 0) {
                const pos = [
                    { x: 0, y: 0 }, { x: ctx.canvas.width / 3, y: 0 }, { x: ctx.canvas.width / 3 * 2, y: 0 },
                    { x: 0, y: ctx.canvas.height / 3 }, { x: ctx.canvas.width / 3, y: ctx.canvas.height / 3 }, { x: ctx.canvas.width / 3 * 2, y: ctx.canvas.height / 3 },
                    { x: 0, y: ctx.canvas.height / 3 * 2 }, { x: ctx.canvas.width / 3, y: ctx.canvas.height / 3 * 2 }, { x: ctx.canvas.width / 3 * 2, y: ctx.canvas.height / 3 * 2 }
                ]
                updatedTiles.forEach((t) => {
                    const ind = t.parentElement.parentElement.parentElement.tabIndex - 3
                    ctx.drawImage(t, pos[ind - 1].x, pos[ind - 1].y)
                })
            }
            resolve({
                rows: 3,
                columns: 3,
                type: 'GridTask',
                comment,
                body: canvas.toDataURL().replace(/^data:image\/?[A-z]*;base64,/, '')
            })
        } else {
            canvas.width = img4x4.naturalWidth
            canvas.height = img4x4.naturalHeight
            ctx.drawImage(img4x4, 0, 0)
            resolve({
                rows: 4,
                columns: 4,
                comment,
                body: canvas.toDataURL().replace(/^data:image\/?[A-z]*;base64,/, ''),
                type: 'GridTask'
            })
        }
    })
};
return getCaptchaData();
"""

# JavaScript to track network requests to update images
script_change_tracking = """
const monitorRequests = () => {
    let found = false;

    const observer = new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
            if (entry.initiatorType === 'xmlhttprequest' || entry.initiatorType === 'fetch') {
                const url = new URL(entry.name);
                if (url.href.includes("recaptcha/api2/replaceimage")) {
                    found = true;  // If the request is found, set the flag to true
                }
            }
        });
    });

    observer.observe({ entryTypes: ['resource'] });

    // We return the result after 10 seconds
    return new Promise((resolve) => {
        setTimeout(() => resolve(found), 10000);
    });
};

return monitorRequests();
"""

# LOCATORS
locator_iframe_captcha = "//iframe[@title='reCAPTCHA']"
locator_checkbox_captcha = "//span[@role='checkbox']"
locator_popup_captcha = "//iframe[contains(@title, 'two minutes')]"
locator_verify_button = "//button[@id='recaptcha-verify-button']"
locator_submit_button_captcha_locator = "//button[@type='submit']"
locator_try_again = "//div[@class='rc-imageselect-incorrect-response']"
locator_select_more = "//div[@class='rc-imageselect-error-select-more']"
locator_dynamic_more = "//div[@class='rc-imageselect-error-dynamic-more']"
locator_select_something = "//div[@class='rc-imageselect-error-select-something']"

# GETTERS
def get_clickable_element(locator, timeout=30):
    """Waits until the element is clickable and returns it."""
    return WebDriverWait(browser, timeout).until(EC.element_to_be_clickable((By.XPATH, locator)))


def get_presence_element(locator, timeout=30):
    """Waits until the element appears in the DOM and returns it."""
    return WebDriverWait(browser, timeout).until(EC.presence_of_element_located((By.XPATH, locator)))


# ACTIONS
def switch_to_iframe(iframe_locator):
    """Switches focus to the iframe of the captcha."""
    iframe = get_presence_element(iframe_locator)
    browser.switch_to.frame(iframe)
    print("Switched to captcha widget")


def click_checkbox(checkbox_locator):
    """Clicks on the reCAPTCHA checkbox."""
    checkbox = get_clickable_element(checkbox_locator)
    checkbox.click()
    print("Checked the checkbox")


def execute_js(script):
    """Executes JavaScript code in the browser."""
    return browser.execute_script(script)


def switch_to_default_content():
    """Returns focus to the main page content."""
    browser.switch_to.default_content()
    print("Returned focus to the main page content")



def solver_captcha(**kwargs):
    """Solves reCAPTCHA using the 2Captcha service."""
    try:
        result = solver.grid(**kwargs)
        print(f"Captcha solved")
        return result
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def pars_answer(answer):
    """Parses the response from 2Captcha and returns a list of numbers for clicks."""
    numbers_str = answer.split(":")[1]
    number_list = list(map(int, numbers_str.split("/")))
    new_number_list = [i + 3 for i in number_list]
    print("Parsed the response to a list of cell numbers")
    return new_number_list


def clicks(answer_list):
    """Clicks on image cells based on a list of numbers."""
    for i in answer_list:
        get_presence_element(f"//table//td[@tabindex='{i}']").click()
    print("Сells are marked")


def is_message_visible(locator):
    """Checks the visibility of an element with a captcha error message"""
    try:
        element = get_presence_element(locator)
        is_visible = browser.execute_script("""
            var elem = arguments[0];
            var style = window.getComputedStyle(elem);
            return !(style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0');
        """, element)
        return is_visible
    except Exception as e:
        print(f"Error: {e}")
        return False

def handle_error_messages():
    """
    Checks for error messages on the captcha and returns True if they are visible.
    """
    time.sleep(1)
    if is_message_visible(locator_try_again):
        return True
    elif is_message_visible(locator_select_more):
        return True
    elif is_message_visible(locator_dynamic_more):
        return True
    elif is_message_visible(locator_select_something):
        return True
    print("No error messages")
    return False

def click_check_button(locator):
    """Clicks on the captcha check button"""
    time.sleep(1)
    get_clickable_element(locator).click()
    print("Pressed the Check button")


def check_for_image_updates(script):
    """Checks captcha images update via JavaScript."""
    print("Images updated")
    return execute_js(script)


# MAIN LOGIC
options = webdriver.ChromeOptions()
options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})

# Basic program logic
with webdriver.Chrome(options=options) as browser:
    browser.get(url)
    print("Started")

    # We start by clicking on the captcha checkbox
    switch_to_iframe(locator_iframe_captcha)
    click_checkbox(locator_checkbox_captcha)
    switch_to_default_content()
    time.sleep(1)
    switch_to_iframe(locator_popup_captcha)
    time.sleep(1)

    id = None  # Initialize the id variable for captcha

    while True:
        # Get captcha data
        captcha_data = execute_js(script_get_data_captcha)

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
        result = solver_captcha(file=captcha_data['body'], **params)

        if result is None:
            print("Captcha solving failed or timed out. Stopping the process.")
            break

        # Check if the captcha was solved successfully
        elif result and 'no_matching_images' not in result['code']:
            # We save the id only on the first successful iteration for 3x3 captcha
            if id is None and params['cols'] == 3 and result['captchaId']:
                id = result['captchaId']  # Save id for subsequent iterations

            answer = result['code']
            number_list = pars_answer(answer)

            # Processing for 3x3
            if params['cols'] == 3:
                # Click on the answers found
                clicks(number_list)

                # Check if the images have been updated
                image_update = check_for_image_updates(script_change_tracking)

                if image_update:
                    # If the images have been updated, continue with the saved id
                    print(f"Images updated, continuing with previousID: {id}")
                    continue  # Continue the loop

                # Press the check button after clicks
                click_check_button(locator_verify_button)

            # Processing for 4x4
            elif params['cols'] == 4:
                # Click on the answers found and immediately press the check button
                clicks(number_list)
                click_check_button(locator_verify_button)

                # After clicking, we check for errors and image updates
                image_update = check_for_image_updates(script_change_tracking)

                if image_update:
                    print(f"Images updated, continuing without previousID")
                    continue  # Continue the loop

            # If the images are not updated, check the error messages
            if handle_error_messages():
                continue  # If an error is visible, restart the loop

            # If there are no errors, send the captcha
            switch_to_default_content()
            click_check_button(locator_submit_button_captcha_locator)
            break  # Exit the loop if the captcha is solved

        elif 'no_matching_images' in result['code']:
            # If the captcha returned the code "no_matching_images", check the errors
            click_check_button(locator_verify_button)
            if handle_error_messages():
                continue  # Restart the loop if an error is visible
            else:
                switch_to_default_content()
                click_check_button(locator_submit_button_captcha_locator)
                break  # Exit loop
    print("Finished")
    time.sleep(10)