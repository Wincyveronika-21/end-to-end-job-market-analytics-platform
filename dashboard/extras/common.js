window.Extras = {
    async request(url, options = {}) {
        const response = await fetch(url, {
            headers: { "Content-Type": "application/json", ...(options.headers || {}) },
            ...options
        });
        const payload = await response.json();
        if (!response.ok) {
            throw new Error(payload.detail || `Request failed (${response.status}).`);
        }
        return payload;
    },
    bind(formId, action, messageId) {
        const form = document.getElementById(formId);
        const message = document.getElementById(messageId);
        form.addEventListener("submit", async event => {
            event.preventDefault();
            const button = form.querySelector("button[type=submit]");
            button.disabled = true;
            message.textContent = "";
            try {
                await action(new FormData(form));
            } catch (error) {
                message.textContent = error.message;
            } finally {
                button.disabled = false;
            }
        });
    },
    showJson(elementId, value) {
        document.getElementById(elementId).textContent = JSON.stringify(value, null, 2);
    }
};
