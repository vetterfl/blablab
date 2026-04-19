(() => {
  const TOKEN_KEY = "blablab_token";
  const overlay   = document.getElementById("auth-overlay");
  const form      = document.getElementById("auth-form");
  const errorEl   = document.getElementById("auth-error");
  const submitBtn = document.getElementById("auth-submit");
  const logoutBtn = document.getElementById("btn-logout");

  // ── Token helpers ───────────────────────────────────────────────────────────

  function getToken() { return localStorage.getItem(TOKEN_KEY); }
  function setToken(t) { localStorage.setItem(TOKEN_KEY, t); }
  function clearToken() { localStorage.removeItem(TOKEN_KEY); }

  window.getAuthHeaders = () => {
    const t = getToken();
    return t ? { Authorization: `Bearer ${t}` } : {};
  };

  // ── Show/hide overlay ───────────────────────────────────────────────────────

  function showOverlay() {
    overlay.hidden = false;
    logoutBtn.hidden = true;
  }

  function hideOverlay() {
    overlay.hidden = true;
    logoutBtn.hidden = false;
  }

  // ── Authenticated fetch wrapper ─────────────────────────────────────────────

  window.authFetch = async (url, options = {}) => {
    const res = await fetch(url, {
      ...options,
      headers: { ...options.headers, ...window.getAuthHeaders() },
    });
    if (res.status === 401) {
      clearToken();
      showOverlay();
      throw new Error("Session expired. Please sign in again.");
    }
    return res;
  };

  // ── Login ───────────────────────────────────────────────────────────────────

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    errorEl.hidden = true;
    submitBtn.disabled = true;
    submitBtn.textContent = "Signing in…";

    const username = document.getElementById("auth-username").value.trim();
    const password = document.getElementById("auth-password").value;

    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Login failed");

      setToken(data.access_token);
      form.reset();
      hideOverlay();
    } catch (err) {
      errorEl.textContent = err.message;
      errorEl.hidden = false;
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Sign in";
    }
  });

  // ── Logout ──────────────────────────────────────────────────────────────────

  logoutBtn.addEventListener("click", () => {
    clearToken();
    showOverlay();
  });

  // ── Init ────────────────────────────────────────────────────────────────────

  if (getToken()) {
    hideOverlay();
  } else {
    showOverlay();
  }
})();
