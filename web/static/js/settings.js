/**
 * Camera Settings & Navigation Toolbar Controller
 */
(function() {
  'use strict';

  let isAudioEnabled = false;
  let isFlashlightEnabled = false;

  async function apiRequest(url, method = 'GET', body = null) {
    const options = {
      method,
      headers: { 'Content-Type': 'application/json' }
    };
    if (body) {
      options.body = JSON.stringify(body);
    }
    const res = await fetch(url, options);
    if (!res.ok) {
      const data = await res.json().catch(() => ({}));
      throw new Error(data.error || 'Request failed');
    }
    return res.json();
  }

  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch((err) => {
        console.warn('Fullscreen request failed:', err);
      });
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
  }

  async function restartStream() {
    const btn = document.getElementById('btn-restart');
    if (btn) btn.disabled = true;
    try {
      await apiRequest('/api/camera/restart', 'POST');
      const img = document.getElementById('camera-feed');
      if (img) {
        // Force refresh image stream
        setTimeout(() => {
          img.src = '/api/stream?t=' + Date.now();
        }, 1000);
      }
    } catch (err) {
      alert('Erro ao reiniciar conexão: ' + err.message);
    } finally {
      if (btn) btn.disabled = false;
    }
  }

  async function toggleAudio() {
    const btn = document.getElementById('btn-audio');
    isAudioEnabled = !isAudioEnabled;
    try {
      await apiRequest('/api/camera/audio', 'POST', { enabled: isAudioEnabled });
      if (btn) {
        btn.classList.toggle('active', isAudioEnabled);
        btn.setAttribute('title', isAudioEnabled ? 'Áudio: Ativo' : 'Áudio: Mudo');
      }
    } catch (err) {
      isAudioEnabled = !isAudioEnabled;
      console.warn('Failed to toggle audio:', err);
    }
  }

  async function toggleFlashlight() {
    const btn = document.getElementById('btn-flashlight');
    isFlashlightEnabled = !isFlashlightEnabled;
    try {
      const res = await apiRequest('/api/camera/flashlight', 'POST', { enabled: isFlashlightEnabled });
      if (!res.supported) {
        alert('Esta câmera não suporta controle de lanterna/iluminador auxiliar.');
        isFlashlightEnabled = false;
      }
      if (btn) {
        btn.classList.toggle('active', isFlashlightEnabled);
      }
    } catch (err) {
      isFlashlightEnabled = !isFlashlightEnabled;
      console.warn('Failed to toggle flashlight:', err);
    }
  }

  async function loadResolutions() {
    const select = document.getElementById('select-resolution');
    if (!select) return;

    try {
      const data = await apiRequest('/api/camera/resolutions');
      select.innerHTML = '';
      data.available.forEach((res) => {
        const opt = document.createElement('option');
        opt.value = `${res.width}x${res.height}`;
        opt.textContent = res.label;
        if (data.current.width === res.width && data.current.height === res.height) {
          opt.selected = true;
        }
        select.appendChild(opt);
      });

      select.addEventListener('change', async () => {
        const [w, h] = select.value.split('x').map(Number);
        await apiRequest('/api/camera/resolution', 'POST', { width: w, height: h });
        const img = document.getElementById('camera-feed');
        if (img) {
          setTimeout(() => {
            img.src = '/api/stream?t=' + Date.now();
          }, 1000);
        }
      });
    } catch (err) {
      console.warn('Failed to load resolutions:', err);
    }
  }

  async function handleLogout() {
    try {
      await apiRequest('/api/auth/logout', 'POST');
      window.location.href = '/login';
    } catch (err) {
      window.location.href = '/login';
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('btn-fullscreen')?.addEventListener('click', toggleFullscreen);
    document.getElementById('btn-restart')?.addEventListener('click', restartStream);
    document.getElementById('btn-audio')?.addEventListener('click', toggleAudio);
    document.getElementById('btn-flashlight')?.addEventListener('click', toggleFlashlight);
    document.getElementById('btn-logout')?.addEventListener('click', handleLogout);

    const toggleSettings = document.getElementById('btn-toggle-settings');
    const settingsPanel = document.getElementById('settings-panel');
    if (toggleSettings && settingsPanel) {
      toggleSettings.addEventListener('click', () => {
        settingsPanel.classList.toggle('open');
      });
    }

    loadResolutions();
  });
})();
