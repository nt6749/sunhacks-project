// Regex to check for Amazon product pages
const amazonProductRegex = /^https:\/\/www\.amazon\.com\/.*\/(dp|gp\/product)\/([A-Z0-9]{10})/;

// This function runs our main logic
function handleTabLogic(tabId, url) {
    // Check if the tab's URL is a valid Amazon product page
    if (url && amazonProductRegex.test(url)) {
        console.log("Amazon page detected. Executing content script.");
        chrome.scripting.executeScript({
            target: { tabId: tabId },
            files: ['content.js']
        });
    } else {
        console.log("Not an Amazon product page. Clearing old data.");
        chrome.storage.local.remove('ecoData');
    }
}

// Listen for when the user switches to a different tab
chrome.tabs.onActivated.addListener((activeInfo) => {
    chrome.tabs.get(activeInfo.tabId, (tab) => {
        if (chrome.runtime.lastError) {
            console.warn("Could not get tab info:", chrome.runtime.lastError.message);
            return;
        }
        handleTabLogic(tab.id, tab.url);
    });
});

// Listen for when a tab is updated (user navigates to a new URL in the same tab)
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.url && tab.active) {
        handleTabLogic(tabId, changeInfo.url);
    }
});