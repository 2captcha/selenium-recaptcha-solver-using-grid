window.monitorRequests = () => {
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