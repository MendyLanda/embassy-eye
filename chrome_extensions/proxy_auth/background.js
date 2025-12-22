// Proxy authentication handler for Manifest V3
// Based on Stack Overflow solution: https://stackoverflow.com/questions/17082425/running-selenium-webdriver-with-a-proxy-in-python

// Store credentials - will be set via message from content script
let proxyCredentials = null;

// Listen for messages from content script to set credentials
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'setCredentials') {
    proxyCredentials = {
      username: request.username,
      password: request.password
    };
    console.log('Proxy credentials set in extension');
    // Also store in storage as backup
    chrome.storage.local.set({
      proxyUsername: request.username,
      proxyPassword: request.password
    });
    sendResponse({ success: true });
    return true; // Keep channel open for async response
  }
  return false;
});

// Try to read from storage on startup (fallback)
chrome.storage.local.get(['proxyUsername', 'proxyPassword'], (data) => {
  if (data.proxyUsername && data.proxyPassword) {
    proxyCredentials = {
      username: data.proxyUsername,
      password: data.proxyPassword
    };
    console.log('Proxy credentials loaded from storage');
  }
});

// Also try to read from credentials.json file if available (pre-loaded by Python)
// Note: This requires the file to be in the extension directory
try {
  // In service worker context, we can't directly read files, but we can try via fetch
  // This is a fallback - the main method is via messages/storage
} catch (e) {
  // File reading not available in service worker, that's OK
}

// Handle proxy authentication requests
// This is the key handler that Chrome calls when proxy authentication is required
chrome.webRequest.onAuthRequired.addListener(
  function(details, callback) {
    console.log('Proxy authentication required for:', details.challenger?.host);
    
    // Try to get credentials from memory first
    if (proxyCredentials) {
      console.log('Providing proxy credentials from memory');
      callback({
        authCredentials: {
          username: proxyCredentials.username,
          password: proxyCredentials.password
        }
      });
      return;
    }
    
    // Fallback: try to get from storage
    chrome.storage.local.get(['proxyUsername', 'proxyPassword'], (data) => {
      if (data.proxyUsername && data.proxyPassword) {
        proxyCredentials = {
          username: data.proxyUsername,
          password: data.proxyPassword
        };
        console.log('Providing proxy credentials from storage');
        callback({
          authCredentials: {
            username: data.proxyUsername,
            password: data.proxyPassword
          }
        });
      } else {
        console.log('No proxy credentials available - Chrome will show dialog');
        // No credentials available, let Chrome handle it (will show dialog)
        callback({});
      }
    });
    return true; // Indicates we will call the callback asynchronously
  },
  { urls: ["<all_urls>"] },
  ["blocking"]
);
