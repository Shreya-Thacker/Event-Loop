/* =============================================================================
   EventLoop – main.js
   Client-side form validation & interactions
   ============================================================================= */

document.addEventListener('DOMContentLoaded', () => {

    // ── Password show/hide toggle ─────────────────────────────────────────────
    const toggleBtns = document.querySelectorAll('.toggle-pw');
    toggleBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const input = btn.closest('.input-icon-wrap').querySelector('input');
            if (input.type === 'password') {
                input.type = 'text';
                btn.innerHTML = '&#128683;'; // closed eye
            } else {
                input.type = 'password';
                btn.innerHTML = '&#128065;'; // open eye
            }
        });
    });

    // ── Password strength meter ───────────────────────────────────────────────
    const pwInput      = document.getElementById('password');
    const strengthBar  = document.getElementById('strengthBar');
    const strengthLbl  = document.getElementById('strengthLabel');

    if (pwInput && strengthBar && strengthLbl) {
        pwInput.addEventListener('input', () => {
            const val   = pwInput.value;
            const score = getStrengthScore(val);
            const info  = strengthInfo(score);
            strengthBar.style.width      = info.width;
            strengthBar.style.background = info.color;
            strengthLbl.textContent      = val.length > 0 ? info.label : '';
            strengthLbl.style.color      = info.color;
        });
    }

    function getStrengthScore(pw) {
        let score = 0;
        if (pw.length >= 6)                          score++;
        if (pw.length >= 10)                         score++;
        if (/[A-Z]/.test(pw))                        score++;
        if (/[0-9]/.test(pw))                        score++;
        if (/[^A-Za-z0-9]/.test(pw))                 score++;
        return score;
    }

    function strengthInfo(score) {
        if (score <= 1) return { width: '20%', color: '#eb5757', label: 'Very Weak'  };
        if (score === 2) return { width: '40%', color: '#f2994a', label: 'Weak'       };
        if (score === 3) return { width: '60%', color: '#f2c94c', label: 'Fair'       };
        if (score === 4) return { width: '80%', color: '#6fcf97', label: 'Strong'     };
        return              { width: '100%', color: '#27ae60', label: 'Very Strong' };
    }

    // ── Register form client-side validation ──────────────────────────────────
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', (e) => {
            let valid = true;

            const username = document.getElementById('username');
            const email    = document.getElementById('email');
            const password = document.getElementById('password');
            const confirm  = document.getElementById('confirm_password');

            clearErrors();

            if (username.value.trim().length < 3) {
                showError(username, 'usernameError', 'Username must be at least 3 characters.');
                valid = false;
            }

            if (!isValidEmail(email.value.trim())) {
                showError(email, 'emailError', 'Please enter a valid email address.');
                valid = false;
            }

            if (password.value.length < 6) {
                showError(password, 'passwordError', 'Password must be at least 6 characters.');
                valid = false;
            }

            if (password.value !== confirm.value) {
                showError(confirm, 'confirmError', 'Passwords do not match.');
                valid = false;
            }

            if (!valid) e.preventDefault();
        });
    }

    // ── Login form client-side validation ─────────────────────────────────────
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            let valid = true;

            const email    = document.getElementById('email');
            const password = document.getElementById('password');

            clearErrors();

            if (!isValidEmail(email.value.trim())) {
                showError(email, 'emailError', 'Please enter a valid email address.');
                valid = false;
            }

            if (password.value.length === 0) {
                showError(password, 'passwordError', 'Please enter your password.');
                valid = false;
            }

            if (!valid) e.preventDefault();
        });
    }

    // ── Helpers ───────────────────────────────────────────────────────────────
    function showError(inputEl, errorId, message) {
        inputEl.classList.add('input-error');
        inputEl.classList.remove('input-valid');
        const errEl = document.getElementById(errorId);
        if (errEl) errEl.textContent = message;
    }

    function clearErrors() {
        document.querySelectorAll('.form-input').forEach(el => {
            el.classList.remove('input-error', 'input-valid');
        });
        document.querySelectorAll('.field-error').forEach(el => {
            el.textContent = '';
        });
    }

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    // ── Auto-dismiss flash messages after 4 seconds ───────────────────────────
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(flash => {
        setTimeout(() => {
            flash.style.transition = 'opacity 0.5s ease';
            flash.style.opacity = '0';
            setTimeout(() => flash.remove(), 500);
        }, 4000);
    });

    // ── Events list: category filter buttons ──────────────────────────────────
    const filterBtns    = document.querySelectorAll('.filter-btn');
    const hiddenCat     = document.getElementById('hiddenCategory');
    const searchForm    = document.getElementById('searchForm');

    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            filterBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            if (hiddenCat) hiddenCat.value = btn.dataset.category;
            if (searchForm) searchForm.submit();
        });
    });

    // ── Events list: clear search ─────────────────────────────────────────────
    const clearSearchBtn = document.getElementById('clearSearch');
    const searchInput    = document.getElementById('searchInput');

    if (clearSearchBtn && searchInput) {
        clearSearchBtn.addEventListener('click', () => {
            searchInput.value = '';
            if (searchForm) searchForm.submit();
        });
    }

    // ── Events list: live search on Enter key ─────────────────────────────────
    if (searchInput) {
        searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                if (searchForm) searchForm.submit();
            }
        });
    }

    // ════════════════════════════════════════════════════════════════════════
    // STAGE 4 – Create / Edit Event form
    // ════════════════════════════════════════════════════════════════════════

    // ── Set minimum date to today ─────────────────────────────────────────────
    const dateInput = document.getElementById('date');
    if (dateInput && !dateInput.value) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.min = today;
    }

    // ── Description character counter ─────────────────────────────────────────
    const descTextarea = document.getElementById('description');
    const charCount    = document.getElementById('charCount');
    const MAX_DESC     = 500;

    if (descTextarea && charCount) {
        const update = () => {
            const len = descTextarea.value.length;
            charCount.textContent = `${len} / ${MAX_DESC}`;
            charCount.style.color = len > MAX_DESC ? '#eb5757' : 'var(--text-muted)';
        };
        descTextarea.addEventListener('input', update);
        update(); // run on page load (for edit pre-fill)
    }

    // ── Event form validation ─────────────────────────────────────────────────
    const eventForm = document.getElementById('eventForm');
    if (eventForm) {
        eventForm.addEventListener('submit', (e) => {
            let valid = true;
            clearErrors();

            const title    = document.getElementById('title');
            const desc     = document.getElementById('description');
            const category = document.getElementById('category');
            const location = document.getElementById('location');
            const date     = document.getElementById('date');
            const time     = document.getElementById('time');
            const capacity = document.getElementById('capacity');

            if (!title || title.value.trim().length < 5) {
                showError(title, 'titleError', 'Title must be at least 5 characters.');
                valid = false;
            }
            if (!desc || desc.value.trim().length < 20) {
                showError(desc, 'descError', 'Description must be at least 20 characters.');
                valid = false;
            }
            if (!category || !category.value) {
                showError(category, 'categoryError', 'Please select a category.');
                valid = false;
            }
            if (!location || location.value.trim() === '') {
                showError(location, 'locationError', 'Location is required.');
                valid = false;
            }
            if (!date || !date.value) {
                showError(date, 'dateError', 'Please select a date.');
                valid = false;
            } else {
                const chosen = new Date(date.value);
                const today  = new Date(); today.setHours(0,0,0,0);
                if (chosen < today) {
                    showError(date, 'dateError', 'Date must be today or in the future.');
                    valid = false;
                }
            }
            if (!time || !time.value) {
                showError(time, 'timeError', 'Please select a time.');
                valid = false;
            }
            if (!capacity || capacity.value === '') {
                showError(capacity, 'capacityError', 'Capacity is required.');
                valid = false;
            } else if (parseInt(capacity.value) < 1 || parseInt(capacity.value) > 5000) {
                showError(capacity, 'capacityError', 'Capacity must be between 1 and 5000.');
                valid = false;
            }

            if (!valid) e.preventDefault();
        });
    }

    // ════════════════════════════════════════════════════════════════════════
    // STAGE 4 – Delete confirmation modal
    // ════════════════════════════════════════════════════════════════════════

    const deleteBtn  = document.getElementById('deleteBtn');
    const deleteForm = document.getElementById('deleteForm');

    if (deleteBtn && deleteForm) {
        deleteBtn.addEventListener('click', () => {
            const title = deleteBtn.dataset.title || 'this event';
            showDeleteModal(title);
        });
    }

    function showDeleteModal(title) {
        // Build modal markup
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.id = 'deleteModal';
        overlay.innerHTML = `
            <div class="modal-box" role="dialog" aria-modal="true">
                <div class="modal-icon">&#128465;</div>
                <h3>Delete Event?</h3>
                <p>You are about to permanently delete<br>
                   <strong>"${escapeHtml(title)}"</strong>.<br>
                   This action cannot be undone.</p>
                <div class="modal-actions">
                    <button class="btn-modal-cancel" id="modalCancel">Keep Event</button>
                    <button class="btn-modal-delete" id="modalConfirm">Yes, Delete</button>
                </div>
            </div>`;

        document.body.appendChild(overlay);
        document.getElementById('modalCancel').focus();

        // Cancel
        document.getElementById('modalCancel').addEventListener('click', () => overlay.remove());
        overlay.addEventListener('click', (e) => { if (e.target === overlay) overlay.remove(); });

        // Confirm → submit the hidden form
        document.getElementById('modalConfirm').addEventListener('click', () => {
            deleteForm.submit();
        });

        // Escape key closes modal
        document.addEventListener('keydown', function onEsc(e) {
            if (e.key === 'Escape') { overlay.remove(); document.removeEventListener('keydown', onEsc); }
        });
    }

    function escapeHtml(str) {
        return str.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
    }

    // ════════════════════════════════════════════════════════════════════════
    // STAGE 5 – Profile tab switching
    // ════════════════════════════════════════════════════════════════════════

    const tabBtns   = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const target = btn.dataset.tab;

            // Update buttons
            tabBtns.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Update panels
            tabPanels.forEach(p => p.classList.remove('active'));
            const panel = document.getElementById(`tab-${target}`);
            if (panel) panel.classList.add('active');
        });
    });

    // ════════════════════════════════════════════════════════════════════════
    // NEW FEATURE – Not Interested (hide cards)
    // ════════════════════════════════════════════════════════════════════════
    const notInterestedBtns = document.querySelectorAll('.btn-not-interested');
    
    // Check local storage on load
    const hiddenEvents = JSON.parse(localStorage.getItem('hiddenEvents') || '[]');
    hiddenEvents.forEach(id => {
        const card = document.getElementById(`event-card-${id}`);
        if (card) {
            card.style.display = 'none';
        }
    });

    notInterestedBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const eventId = btn.getAttribute('data-id');
            const card = document.getElementById(`event-card-${eventId}`);
            
            // Hide visually
            if (card) {
                card.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                card.style.opacity = '0';
                card.style.transform = 'scale(0.9)';
                setTimeout(() => card.style.display = 'none', 300);
            }
            
            // Save to local storage
            if (!hiddenEvents.includes(eventId)) {
                hiddenEvents.push(eventId);
                localStorage.setItem('hiddenEvents', JSON.stringify(hiddenEvents));
            }
        });
    });

});
