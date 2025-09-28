/**
 * Gets the ASIN of the main product from the URL.
 */
function getMainASIN() {
    const match = window.location.href.match(/\/dp\/([A-Z0-9]{10})/);
    return match ? match[1] : null;
}

/**
 * Gets the main product title from the page.
 */
function getMainProductTitle() {
    const titleElement = document.getElementById('productTitle');
    return titleElement ? titleElement.innerText.trim() : null;
}

/**
 * Gets related ASINs by parsing the carousel's data attribute (Original Method).
 * @returns {string[]} A list of unique ASINs.
 */
function getRelatedASINs() {
    let relatedASINs = [];
    const carousels = document.querySelectorAll("div[data-a-carousel-options]");

    carousels.forEach(carousel => {
        try {
            const options = carousel.getAttribute("data-a-carousel-options");
            if (options) {
                const parsed = JSON.parse(options);
                if (parsed.initialSeenAsins) {
                    relatedASINs.push(...parsed.initialSeenAsins);
                }
            }
        } catch (err) {
            console.warn("ERROR: parsing carousel", err);
        }
    });

    // Return a unique list of ASINs
    return [...new Set(relatedASINs)];
}

/**
 * Gets a clean list of product titles from all carousels on the page.
 * @returns {string[]} A list of unique product titles.
 */
function getRelatedTitles() {
    const relatedTitles = new Set();
    const carousels = document.querySelectorAll('div[data-a-carousel-options]');
    
    const titleSelectors = [
        'span[class*="p13n-sc-truncate"]',
        'span[class*="p13n-sc-un-line-clamp"]',
        'div.p13n-sc-truncate-fallback-text-container',
        'a.a-link-normal > span.a-size-base'
    ].join(', ');

    carousels.forEach(carousel => {
        const titleElements = carousel.querySelectorAll(titleSelectors);
        titleElements.forEach(el => {
            if (el.innerText && !el.innerText.startsWith('$')) {
                relatedTitles.add(el.innerText.trim());
            }
        });
    });

    return [...relatedTitles];
}

/**
 * Mocks a backend response using the scraped data.
 */
function mockBackend(mainProduct, { relatedASINs, relatedTitles }) {
    console.log("Generating mock data for main product:", mainProduct.title);
    
    const alternatives = relatedASINs.slice(0, 3).map((asin, index) => {
        const title = relatedTitles[index];
        return {
            asin: asin,
            title: title || "Eco-Friendly Item", // Fallback title if arrays are mismatched
            score: Math.floor(Math.random() * (98 - 85 + 1)) + 85,
        };
    });

    return {
        mainProduct: {
            ...mainProduct,
            score: 80
        },
        alternatives: alternatives
    };
}

// --- Main execution logic (IIFE) ---
(function sendData() {
    const mainASIN = getMainASIN();
    const mainTitle = getMainProductTitle();

    if (!mainASIN || !mainTitle) {
        console.log("Main product ASIN or Title not found.");
        return; 
    }

    const mainProduct = { asin: mainASIN, title: mainTitle };
    const relatedASINs = getRelatedASINs();
    const relatedTitles = getRelatedTitles();

    console.log("Main Product:", mainProduct);
    console.log("Scraped Related ASINs:", relatedASINs);
    console.log("Scraped Related Titles:", relatedTitles);

    const data = mockBackend(mainProduct, { relatedASINs, relatedTitles });

    chrome.storage.local.set({ ecoData: data }, () => {
        console.log("Mock ecoData saved:", data);
    });
})();