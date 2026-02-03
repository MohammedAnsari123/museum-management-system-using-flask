// Main JavaScript for PixelPast

document.addEventListener('DOMContentLoaded', () => {
    // User Navbar Toggle
    const navToggle = document.getElementById('nav-toggle');
    const navLinks = document.getElementById('nav-links');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }

    // Admin Sidebar Toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const adminSidebar = document.querySelector('.admin-sidebar');

    if (sidebarToggle && adminSidebar) {
        sidebarToggle.addEventListener('click', () => {
            adminSidebar.classList.toggle('active');
        });

        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', (e) => {
            if (window.innerWidth <= 1024 &&
                !adminSidebar.contains(e.target) &&
                !sidebarToggle.contains(e.target) &&
                adminSidebar.classList.contains('active')) {
                adminSidebar.classList.remove('active');
            }
        });
    }
});


document.addEventListener('DOMContentLoaded', () => {
    // Set min date for date pickers if present
    const visitDateInput = document.getElementById('visitDate');
    if (visitDateInput) {
        const today = new Date().toISOString().split('T')[0];
        visitDateInput.setAttribute('min', today);
    }

    // Modal close on click outside
    window.onclick = function (event) {
        const bookingModal = document.getElementById('bookingModal');
        const reviewModal = document.getElementById('reviewModal');

        if (event.target == bookingModal) {
            closeBookingModal();
        }
        if (event.target == reviewModal) {
            closeReviewModal();
        }
    }
});

function openBookingModal(museumId, museumName, museumIdStr) {
    document.getElementById('modalMuseumId').value = museumId;
    document.getElementById('modalMuseumName').innerText = museumName;

    // Reset form
    document.getElementById('bookingForm').reset();

    // Ensure min date is set
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('visitDate').setAttribute('min', today);

    document.getElementById('bookingModal').style.display = 'block';
}

function closeBookingModal() {
    const modal = document.getElementById('bookingModal');
    if (modal) modal.style.display = 'none';
}

function openReviewModal(museumId, museumName) {
    document.getElementById('reviewMuseumName').innerText = museumName;
    const form = document.getElementById('reviewForm');
    if (form) {
        form.action = "/review/" + museumId;
    }
    document.getElementById('reviewModal').style.display = 'block';
}

function closeReviewModal() {
    const modal = document.getElementById('reviewModal');
    if (modal) modal.style.display = 'none';
}

async function submitBooking(event) {
    event.preventDefault();

    const museumId = document.getElementById('modalMuseumId').value;
    const date = document.getElementById('visitDate').value;
    const tickets = document.getElementById('ticketCount').value;

    const btn = event.target.querySelector('button[type="submit"]');
    const originalText = btn.innerText;
    btn.innerText = "Processing...";
    btn.disabled = true;

    try {
        const formData = new FormData();
        formData.append('date', date);
        formData.append('tickets', tickets);

        const response = await fetch(`/book/${museumId}`, {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (response.ok) {
            alert("Success: " + result.message);
            closeBookingModal();
            // Refresh to update dashboard/capacity if needed, or simple redirect
            window.location.reload();
        } else {
            alert("Error: " + (result.error || "Booking failed"));
        }
    } catch (error) {
        alert("An error occurred. Please try again.");
        console.error(error);
    } finally {
        btn.innerText = originalText;
        btn.disabled = false;
    }
}
