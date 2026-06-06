// Main JavaScript file
document.addEventListener('DOMContentLoaded', function () {
    // Auto-hide alerts after 4 seconds
    document.querySelectorAll('.alert').forEach(function (alert) {
        setTimeout(function () {
            alert.classList.remove('show');
        }, 4000);
    });
});
