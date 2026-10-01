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

});
