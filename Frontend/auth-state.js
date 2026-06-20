(function () {
  const AUTH_STORAGE_KEY = 'careroute_auth';

  function setCookie(name, value, days) {
    const expires = new Date(Date.now() + days * 24 * 60 * 60 * 1000).toUTCString();
    document.cookie = `${encodeURIComponent(name)}=${encodeURIComponent(value)}; expires=${expires}; path=/; SameSite=Lax`;
  }

  function getCookie(name) {
    const prefix = `${encodeURIComponent(name)}=`;
    return document.cookie.split('; ').reduce((found, part) => {
      if (part.startsWith(prefix)) {
        return decodeURIComponent(part.slice(prefix.length));
      }
      return found;
    }, '');
  }

  function writeFallbackState(authState) {
    try {
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(authState));
    } catch (error) {
      // Ignore storage failures in the demo environment.
    }

    try {
      window.name = JSON.stringify({ authState });
    } catch (error) {
      // Ignore name assignment failures in the demo environment.
    }
  }

  function readFallbackState() {
    try {
      const storedState = localStorage.getItem(AUTH_STORAGE_KEY);
      if (storedState) {
        return JSON.parse(storedState);
      }
    } catch (error) {
      // Ignore malformed or unavailable localStorage data.
    }

    try {
      const parsedWindowName = JSON.parse(window.name || '{}');
      if (parsedWindowName && parsedWindowName.authState) {
        return parsedWindowName.authState;
      }
    } catch (error) {
      // Ignore malformed window.name data.
    }

    return { role: '', username: '', password: '' };
  }

  function setAuthState(role, username, password) {
    const authState = { role, username, password };
    setCookie('careroute_role', role, 7);
    setCookie('careroute_username', username, 7);
    setCookie('careroute_password', password, 7);
    writeFallbackState(authState);
  }

  function getAuthState() {
    const cookieUsername = getCookie('careroute_username');
    if (cookieUsername) {
      return {
        role: getCookie('careroute_role'),
        username: cookieUsername,
        password: getCookie('careroute_password'),
      };
    }

    return readFallbackState();
  }

  function getSignedInUsername() {
    return getAuthState().username || '';
  }

  function clearAuthState() {
    setCookie('careroute_role', '', -1);
    setCookie('careroute_username', '', -1);
    setCookie('careroute_password', '', -1);
    try {
      localStorage.removeItem(AUTH_STORAGE_KEY);
    } catch (error) {
      // Ignore storage failures in the demo environment.
    }
    window.name = '';
  }

  window.CareRouteAuth = {
    setAuthState,
    getAuthState,
    getSignedInUsername,
    clearAuthState,
  };
})();
