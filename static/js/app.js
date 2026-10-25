// PfunzoBridge Client Application Scripts
document.addEventListener('DOMContentLoaded', () => {
    // Register Service Worker for PWA
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(reg => console.log('PfunzoBridge Service Worker registered:', reg.scope))
            .catch(err => console.warn('Service Worker registration skipped:', err));
    }

    // Auto-fill prompt if navigated from APS or Quiz
    const pendingPrompt = sessionStorage.getItem('pending_agent_prompt');
    const promptInput = document.getElementById('prompt');
    if (pendingPrompt && promptInput) {
        promptInput.value = pendingPrompt;
        sessionStorage.removeItem('pending_agent_prompt');
        // If startAgent function exists, run it
        if (typeof startAgent === 'function') {
            setTimeout(() => {
                startAgent();
            }, 300);
        }
    }
});
