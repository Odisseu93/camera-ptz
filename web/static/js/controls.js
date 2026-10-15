/**
 * PTZ Dual Virtual Joysticks & Keyboard Navigation Controller
 */
(function() {
  'use strict';

  let lastMoveTime = 0;
  const MOVE_INTERVAL = 60; // ms debounce

  async function sendMove(x, y) {
    const now = Date.now();
    if (now - lastMoveTime < MOVE_INTERVAL) return;
    lastMoveTime = now;

    try {
      await fetch('/api/ptz/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ x: Number(x.toFixed(2)), y: Number(y.toFixed(2)) })
      });
    } catch (err) {
      console.warn('PTZ move error:', err);
    }
  }

  async function sendStop() {
    try {
      await fetch('/api/ptz/stop', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (err) {
      console.warn('PTZ stop error:', err);
    }
  }

  function initJoysticks() {
    if (typeof nipplejs === 'undefined') {
      console.warn('nipplejs not loaded, joysticks unavailable.');
      return;
    }

    const leftZone = document.getElementById('joystick-left-zone');
    const rightZone = document.getElementById('joystick-right-zone');

    if (leftZone) {
      const leftManager = nipplejs.create({
        zone: leftZone,
        mode: 'static',
        position: { left: '50%', top: '50%' },
        color: '#0084ff',
        size: leftZone.clientWidth * 0.75
      });

      leftManager.on('move', (evt, data) => {
        if (!data || !data.vector) return;
        // Vector X ranges -1 to 1, Vector Y inverted for camera pitch
        const vx = data.vector.x;
        const vy = data.vector.y;
        sendMove(vx, vy);
      });

      leftManager.on('end', () => {
        sendStop();
      });
    }

    if (rightZone) {
      const rightManager = nipplejs.create({
        zone: rightZone,
        mode: 'static',
        position: { left: '50%', top: '50%' },
        color: '#32d74b',
        size: rightZone.clientWidth * 0.75,
        lockY: true // Primarily for vertical or fine adjustment
      });

      rightManager.on('move', (evt, data) => {
        if (!data || !data.vector) return;
        sendMove(0, data.vector.y);
      });

      rightManager.on('end', () => {
        sendStop();
      });
    }
  }

  function initKeyboardControls() {
    const activeKeys = new Set();
    let keyLoop = null;

    function handleKeyMove() {
      let x = 0;
      let y = 0;
      if (activeKeys.has('ArrowUp') || activeKeys.has('w') || activeKeys.has('W')) y += 1;
      if (activeKeys.has('ArrowDown') || activeKeys.has('s') || activeKeys.has('S')) y -= 1;
      if (activeKeys.has('ArrowLeft') || activeKeys.has('a') || activeKeys.has('A')) x -= 1;
      if (activeKeys.has('ArrowRight') || activeKeys.has('d') || activeKeys.has('D')) x += 1;

      if (x !== 0 || y !== 0) {
        sendMove(x, y);
      }
    }

    window.addEventListener('keydown', (e) => {
      const valid = ['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'w', 'W', 'a', 'A', 's', 'S', 'd', 'D'];
      if (!valid.includes(e.key)) return;

      activeKeys.add(e.key);
      if (!keyLoop) {
        handleKeyMove();
        keyLoop = setInterval(handleKeyMove, MOVE_INTERVAL);
      }
    });

    window.addEventListener('keyup', (e) => {
      activeKeys.delete(e.key);
      if (activeKeys.size === 0 && keyLoop) {
        clearInterval(keyLoop);
        keyLoop = null;
        sendStop();
      }
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    initJoysticks();
    initKeyboardControls();
  });
})();
