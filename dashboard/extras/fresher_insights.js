document.getElementById("load-insights").addEventListener("click", async event => {
    const button = event.currentTarget;
    const message = document.getElementById("message");
    button.disabled = true;
    message.textContent = "";
    try {
        const result = await Extras.request("/extras/fresher-insights");
        Extras.showJson("result", result);
    } catch (error) {
        message.textContent = error.message;
    } finally {
        button.disabled = false;
    }
});
