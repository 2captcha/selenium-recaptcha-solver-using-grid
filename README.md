# reCAPTCHA Solver Using 2Captcha and Selenium

This project automates solving Google reCAPTCHA v2 with image challenges (3x3 and 4x4) using the 2Captcha service and Selenium WebDriver. The script programmatically interacts with reCAPTCHA, retrieves data for solving, sends it to 2Captcha for processing, and then submits the solution.

## Features

- Uses **Selenium WebDriver** to interact with the browser and manipulate elements on the reCAPTCHA page.
- **2Captcha API** helps solve image-based captchas using artificial intelligence.
- Handles both **3x3** and **4x4** captchas with custom logic for each.
- Tracks image updates and handles captcha error messages efficiently.

## Usage

### Clone:

```
git clone git@github.com:2captcha/recaptcha-solver-using-grid.git
cd recaptcha-solver-using-grid
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

### Example Command
```bash
python solve_recaptcha.py
```

## How It Works

1. Browser Initialization: A browser is opened using Selenium WebDriver.
2. Captcha Data Retrieval: JavaScript extracts the image tiles from reCAPTCHA and sends them to the 2Captcha service for solving.
3. Captcha Submission: Once a solution is received from 2Captcha, Selenium simulates clicking on the correct image tiles based on the solution.
4. Captcha Submission: The solution is submitted once the captcha is solved.

## Captcha Solving Logic

- For 3x3 captchas, the previous captcha ID (previousID) is saved to speed up solving when images are updated.
- For 4x4 captchas, no previousID is saved, and each solution is processed from scratch.
- Error messages, such as “Please try again” are handled, and the solving process is retried if needed.

<!-- Shared links -->
[2captcha-demo]: https://2captcha.com/demo
[recaptcha-v2-demo]: https://2captcha.com/demo/recaptcha-v2
[2captcha]: https://2captcha.com
[selenium]: https://pypi.org/project/selenium/
[2captcha-python]: https://github.com/2captcha/2captcha-python


