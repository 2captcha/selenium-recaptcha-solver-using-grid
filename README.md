# reCAPTCHA Solver Using 2Captcha and Selenium

This project automates [bypass Google reCAPTCHA] v2 with image challenges (3x3 and 4x4) using the 2Captcha service 
([captcha solver]) and Selenium WebDriver. The script programmatically interacts with reCAPTCHA, retrieves data for 
solving, sends it to [reCAPTCHA solver] for processing, and then submits the solution.

![bypass_recaptcha_v2_selenium_final2.gif](media%2Fbypass_recaptcha_v2_selenium_final2.gif)

2Captcha service allows you to bypass any CAPTCHA using Selenium. You can find more details on [Selenium captcha solver] page.

If you are using JavaScript, we also have a similar example for JavaScript Puppeteer, the example is in the [reCAPTCHA Solver using 2Captcha and Puppeteer] repository.


## Features

- **Selenium WebDriver**: Interacts with the browser and manipulates elements on the reCAPTCHA page.
- **2Captcha API**: Solves image-based captchas using artificial intelligence.
- Handles both **3x3** and **4x4** captchas with custom logic for each.
- Modular design with separated logic into helper classes for easy code maintenance and future expansion.
- Tracks image updates and handles captcha error messages efficiently using custom error handling.

## Code Structure

The project is structured as follows:

- **`utils/actions.py`**: Contains the `PageActions` class, which encapsulates common browser actions (clicking, switching frames, etc.).
- **`utils/helpers.py`**: Contains the `CaptchaHelper` class, responsible for solving captchas, executing JS, and handling captcha error messages.
- **`js_scripts/`**: JavaScript files that extract captcha data and track image updates.

## Usage

### Clone:

```
git clone git@github.com:2captcha/selenium-recaptcha-solver-using-grid.git
cd selenium-recaptcha-solver-using-grid
```

### Requirements

- Python >= 3.6
- Installed Selenium WebDriver (for Chrome)
- [2Captcha account][2captcha] and API key
- Required Python libraries:
  - `selenium`
  - `twocaptcha-python`
```bash
pip install -r requirements.txt
```

### Configure:

Set the `APIKEY` environment variable. You can get the `APIKEY` value in your personal [2captcha account][2captcha].

`export APIKEY=your_api_key`

You can also set the value of `APIKEY` directly in the code. To do this, modify the `apikey` value in the following file: [main.py, line 10].

### Example Command
```bash
python main.py
```

## How It Works

1. **Browser Initialization:** A browser is opened using Selenium WebDriver.
2. **Captcha Data Retrieval:** JavaScript extracts the image tiles from reCAPTCHA and sends them to the 2Captcha service for solving.
3. **Captcha Submission:** Once a solution is received from 2Captcha, Selenium simulates clicking on the correct image tiles based on the solution.
4. **Final Submission:** The solution is submitted once the captcha is solved.

## Captcha Solving Logic

- **3x3 Captchas:** Previous captcha ID (previousID) is saved to speed up solving when images are updated.
- **4x4 Captchas:** No previousID is saved, and each solution is processed from scratch.
- **Error Handling:** Messages like “Please try again” are handled, and the solving process is retried if needed.

## Modular Design

The project follows a modular design for better maintainability:

- **PageActions Class:** Handles general browser interactions like switching to iframes, clicking elements, and returning focus to the main content.
- **CaptchaHelper Class:** Encapsulates captcha-specific logic, such as solving the captcha via 2Captcha API, handling error messages, and executing JavaScript in the browser.

## JavaScript Scripts

- `get_captcha_data.js`: Extracts captcha image tiles for solving. The source code of the script is located here https://gist.github.com/kratzky/20ea5f4f142cec8f1de748b3f3f84bfc
- `track_image_updates.js`: Monitors requests to check if captcha images are updated.

<!-- Shared links -->
[2captcha-demo]: https://2captcha.com/demo
[recaptcha-v2-demo]: https://2captcha.com/demo/recaptcha-v2
[selenium]: https://pypi.org/project/selenium/
[2captcha-python]: https://github.com/2captcha/2captcha-python
[reCAPTCHA Solver using 2Captcha and Puppeteer]: https://github.com/2captcha/puppeteer-recaptcha-solver-using-clicks
[main.py, line 10]: ./main.py#L10
[bypass Google reCAPTCHA]: https://2captcha.com/p/bypass-recaptcha
[captcha solver]: https://2captcha.com/
[reCAPTCHA solver]:https://2captcha.com/
[Selenium captcha solver]: https://2captcha.com/p/selenium-captcha-solver
