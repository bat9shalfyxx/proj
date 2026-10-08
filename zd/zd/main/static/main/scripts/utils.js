(function () {
  'use strict';

  window.escapeHtml = function (text) {
    if (text === null || text === undefined) return '';
    const div = document.createElement('div');
    div.textContent = String(text);
    return div.innerHTML;
  };

  window.getDeclension = function (number, one, two, five) {
    const n = Math.abs(number) % 100;
    if (n >= 5 && n <= 20) return five;
    const m = n % 10;
    if (m === 1) return one;
    if (m >= 2 && m <= 4) return two;
    return five;
  };
})();
