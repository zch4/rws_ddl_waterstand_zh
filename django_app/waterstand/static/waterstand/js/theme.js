/**
 * Thema-toggle: light/dark.
 * Default is light. Als de gebruiker zelf een thema kiest, wordt die keuze
 * bewaard via localStorage en als fallback via een cookie.
 */
(function () {
  const html = document.documentElement;
  const toggle = document.querySelector('[data-theme-toggle]');
  const opslagSleutel = 'waterstand-zh-theme-v2';

  function leesCookie(naam) {
    const prefix = naam + '=';
    return document.cookie
      .split(';')
      .map(item => item.trim())
      .find(item => item.startsWith(prefix))
      ?.slice(prefix.length);
  }

  function schrijfCookie(naam, waarde) {
    document.cookie = `${naam}=${waarde}; path=/; max-age=31536000; SameSite=Lax`;
  }

  function leesOpgeslagenThema() {
    try {
      const waarde = localStorage.getItem(opslagSleutel);
      if (waarde === 'light' || waarde === 'dark') return waarde;
    } catch (e) {
      // Cookie fallback hieronder.
    }
    const cookieWaarde = leesCookie(opslagSleutel);
    return cookieWaarde === 'dark' ? 'dark' : null;
  }

  function bewaarThema(thema) {
    try {
      localStorage.setItem(opslagSleutel, thema);
    } catch (e) {
      // Cookie fallback hieronder.
    }
    schrijfCookie(opslagSleutel, thema);
  }

  let huidigThema = leesOpgeslagenThema() || 'light';
  html.setAttribute('data-theme', huidigThema);
  updateIcoon(toggle, huidigThema);

  if (toggle) {
    toggle.addEventListener('click', function () {
      huidigThema = huidigThema === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', huidigThema);
      bewaarThema(huidigThema);
      updateIcoon(toggle, huidigThema);
    });
  }

  function updateIcoon(btn, thema) {
    if (!btn) return;
    btn.setAttribute('aria-label', 'Schakel naar ' + (thema === 'dark' ? 'licht' : 'donker') + ' thema');
    btn.innerHTML = thema === 'dark'
      ? '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="5"/><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/></svg>'
      : '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
  }
})();
