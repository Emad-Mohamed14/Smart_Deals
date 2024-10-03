function openUserPanel() {
    // Get the main content and user panel elements
    var mainContent = document.getElementById("main-content");
    var userPanel = document.getElementById("user-panel");

    // Toggle the panel
    if (userPanel.classList.contains("open")) {
        // Close the panel
        userPanel.classList.remove("open");
        mainContent.classList.remove("shrink");
    } else {
        // Open the panel
        userPanel.classList.add("open");
        mainContent.classList.add("shrink");
    }
}
