// Track recaptcha image replacement requests by patching
// fetch and XMLHttpRequest. This is more reliable than
// relying on PerformanceObserver entry types.
(function initRecaptchaRequestTracking() {
    if (window.__recaptchaRequestTrackingInitialized) {
        return;
    }

    window.__recaptchaRequestTrackingInitialized = true;
    window.__recaptchaImagesUpdated = false;
    window.__recaptchaReplaceImageCount = 0;

    const markIfReplaceImage = (url) => {
        try {
            const href = typeof url === 'string' ? url : (url && url.toString()) || '';
            if (href.includes('recaptcha/api2/replaceimage')) {
                window.__recaptchaImagesUpdated = true;
                window.__recaptchaReplaceImageCount =
                    (window.__recaptchaReplaceImageCount || 0) + 1;
            }
        } catch (e) {
            // ignore
        }
    };

    // Patch fetch
    try {
        const originalFetch = window.fetch;
        if (typeof originalFetch === 'function') {
            window.fetch = function () {
                const args = Array.prototype.slice.call(arguments);
                const resource = args[0];
                const url = (resource && resource.url) || resource;
                markIfReplaceImage(url);
                return originalFetch.apply(this, args);
            };
        }
    } catch (e) {
        console.error('recaptcha fetch patch error:', e);
    }

    // Patch XMLHttpRequest
    try {
        const originalOpen = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function (method, url) {
            markIfReplaceImage(url);
            return originalOpen.apply(this, arguments);
        };
    } catch (e) {
        console.error('recaptcha XHR patch error:', e);
    }
})();

// Reset observation flag: start a new "window".
window.resetImageUpdateFlag = () => {
    window.__recaptchaImagesUpdated = false;
    window.__recaptchaReplaceImageCount = 0;
};

// Synchronous checker used from Python.
// If expectedCount is provided and > 0, returns true only when
// at least that many replaceimage requests were observed since
// the last reset. Otherwise, keeps the old behaviour: any activity.
window.monitorRequests = (expectedCount) => {
    const count = window.__recaptchaReplaceImageCount || 0;

    if (typeof expectedCount === 'number' && expectedCount > 0) {
        if (count >= expectedCount) {
            window.__recaptchaImagesUpdated = false;
            window.__recaptchaReplaceImageCount = 0;
            return true;
        }
        return false;
    }

    if (window.__recaptchaImagesUpdated) {
        window.__recaptchaImagesUpdated = false;
        window.__recaptchaReplaceImageCount = 0;
        return true;
    }
    return false;
};
