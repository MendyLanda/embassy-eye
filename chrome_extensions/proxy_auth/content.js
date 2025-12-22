// Content script to receive credentials from page and pass to background
// This script is injected into pages to communicate with the extension

// Listen for messages from the page (injected via CDP)
window.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SET_PROXY_CREDENTIALS') {
    // Forward to background script
    chrome.runtime.sendMessage({
      action: 'setCredentials',
      username: event.data.username,
      password: event.data.password
    });
  }
});
