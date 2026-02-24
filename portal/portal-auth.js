/**
 * Portal Auth — JWT Fail-Closed Authentication
 *
 * Sources JWT from:
 *   1. URL fragment: #token=<jwt>
 *   2. sessionStorage: pmoves_jwt
 *
 * Fail-closed: No token = no WebRTC connection.
 * Token is cleared from URL fragment after extraction (security).
 */

(function () {
  'use strict';

  const AUTH_STORAGE_KEY = 'pmoves_jwt';

  /**
   * Extract JWT from URL fragment (#token=...) or sessionStorage.
   * Returns null if no token found.
   */
  function extractToken() {
    // 1. Check URL fragment
    const hash = window.location.hash;
    if (hash) {
      const params = new URLSearchParams(hash.substring(1));
      const fragmentToken = params.get('token');
      if (fragmentToken) {
        // Store and clear from URL
        sessionStorage.setItem(AUTH_STORAGE_KEY, fragmentToken);
        // Remove token from URL without reload
        history.replaceState(null, '', window.location.pathname + window.location.search);
        return fragmentToken;
      }
    }

    // 2. Check sessionStorage
    const storedToken = sessionStorage.getItem(AUTH_STORAGE_KEY);
    if (storedToken) {
      return storedToken;
    }

    return null;
  }

  /**
   * Decode JWT payload (no verification — server verifies).
   * Returns null on parse failure.
   */
  function decodePayload(token) {
    try {
      const parts = token.split('.');
      if (parts.length !== 3) return null;

      // base64url → base64
      const payload = parts[1]
        .replace(/-/g, '+')
        .replace(/_/g, '/');
      const decoded = atob(payload);
      return JSON.parse(decoded);
    } catch {
      return null;
    }
  }

  /**
   * Check if token is expired.
   */
  function isExpired(payload) {
    if (!payload || !payload.exp) return true;
    return Date.now() / 1000 > payload.exp;
  }

  // --- Initialize ---
  const token = extractToken();
  const authOverlay = document.getElementById('auth-overlay');
  const connectBtn = document.getElementById('btn-connect');

  if (!token) {
    // Fail-closed: show auth overlay, disable controls
    if (authOverlay) authOverlay.classList.remove('hidden');
    if (connectBtn) connectBtn.disabled = true;
    window.PORTAL_AUTH = { authenticated: false, token: null, payload: null };
    return;
  }

  const payload = decodePayload(token);

  if (!payload || payload.role === 'anon') {
    // Reject anonymous tokens
    if (authOverlay) authOverlay.classList.remove('hidden');
    if (connectBtn) connectBtn.disabled = true;
    window.PORTAL_AUTH = { authenticated: false, token: null, payload: null };
    return;
  }

  if (isExpired(payload)) {
    sessionStorage.removeItem(AUTH_STORAGE_KEY);
    if (authOverlay) authOverlay.classList.remove('hidden');
    if (connectBtn) connectBtn.disabled = true;
    window.PORTAL_AUTH = { authenticated: false, token: null, payload: null };
    return;
  }

  // Authenticated — hide overlay, enable controls
  if (authOverlay) authOverlay.classList.add('hidden');
  if (connectBtn) connectBtn.disabled = false;

  window.PORTAL_AUTH = {
    authenticated: true,
    token: token,
    payload: payload,
  };
})();
