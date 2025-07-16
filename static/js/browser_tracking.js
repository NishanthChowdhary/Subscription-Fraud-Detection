let tabSwitches = 0;

// Detect tab switching
window.onblur = function() {
    tabSwitches++;
    // Store the count in sessionStorage so it persists across pages
    sessionStorage.setItem('tabSwitches', tabSwitches);
};

// When page loads, retrieve the previous tabSwitches count from sessionStorage
window.onload = function() {
    const previousSwitches = parseInt(sessionStorage.getItem('tabSwitches')) || 0;
    tabSwitches = previousSwitches;
};
