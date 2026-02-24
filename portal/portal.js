/**
 * Portal WebRTC + Prosodic-Geometry Bridge
 *
 * Connects to Flute-Gateway WebSocket (port 8056) for voice sessions.
 * Maps prosodic boundaries to Three.js scene parameters via postMessage.
 *
 * Prosodic Boundary → Geometry Mapping:
 *   SENTENCE  | 60 BPM (Largo)    | #E11D48 DARKXSIDE rose  | C4
 *   CLAUSE    | 90 BPM (Andante)  | #FB7185 Rose accent     | E4
 *   PHRASE    | 120 BPM (Allegro) | #7C3AED Claude violet   | G4
 *   BREATH    | 80 BPM (Adagio)   | #0EA5E9 Crush sky       | D4
 *   NONE      | 150 BPM (Presto)  | #F59E0B POWERFULMOVES   | C5
 */

(function () {
  'use strict';

  // --- Configuration ---
  const FLUTE_WS_URL = 'ws://localhost:8056/ws/voice';
  const MINIO_UPLOAD_URL = 'http://localhost:8088/presign';

  // --- Prosodic Mapping Table ---
  const BOUNDARY_MAP = {
    SENTENCE: { bpm: 60, color: '#E11D48', note: 'C4', midi: 60, tempo: 'Largo' },
    CLAUSE:   { bpm: 90, color: '#FB7185', note: 'E4', midi: 64, tempo: 'Andante' },
    PHRASE:   { bpm: 120, color: '#7C3AED', note: 'G4', midi: 67, tempo: 'Allegro' },
    BREATH:   { bpm: 80, color: '#0EA5E9', note: 'D4', midi: 62, tempo: 'Adagio' },
    NONE:     { bpm: 150, color: '#F59E0B', note: 'C5', midi: 72, tempo: 'Presto' },
  };

  // --- Music Theory Helpers (from musicMapping.ts patterns) ---
  function midiToFreq(midi) {
    return 440 * Math.pow(2, (midi - 69) / 12);
  }

  function freqToY(freq, minFreq, maxFreq, height) {
    const logMin = Math.log2(minFreq);
    const logMax = Math.log2(maxFreq);
    const logFreq = Math.log2(freq);
    return height * (1 - (logFreq - logMin) / (logMax - logMin));
  }

  // --- State ---
  let ws = null;
  let mediaRecorder = null;
  let recordedChunks = [];
  let sessionStartTime = null;

  // --- DOM ---
  const statusEl = document.getElementById('connection-status');
  const connectBtn = document.getElementById('btn-connect');
  const disconnectBtn = document.getElementById('btn-disconnect');
  const boundaryTypeEl = document.getElementById('boundary-type');
  const boundaryBpmEl = document.getElementById('boundary-bpm');
  const beatFillEl = document.getElementById('beat-fill');
  const noteDisplayEl = document.getElementById('note-display');
  const screenshotBtn = document.getElementById('btn-screenshot');
  const recordStartBtn = document.getElementById('btn-record-start');
  const recordStopBtn = document.getElementById('btn-record-stop');
  const viewerFrame = document.getElementById('hyperdimensions-frame');

  // --- WebRTC Connection ---
  function connect() {
    if (!window.PORTAL_AUTH || !window.PORTAL_AUTH.authenticated) {
      console.error('Cannot connect: not authenticated');
      return;
    }

    setStatus('connecting');

    // Append token to WebSocket URL for auth
    const wsUrl = FLUTE_WS_URL + '?token=' + encodeURIComponent(window.PORTAL_AUTH.token);

    try {
      ws = new WebSocket(wsUrl);
    } catch (err) {
      console.error('WebSocket creation failed:', err);
      setStatus('disconnected');
      return;
    }

    ws.onopen = function () {
      setStatus('connected');
      connectBtn.disabled = true;
      disconnectBtn.disabled = false;
      sessionStartTime = new Date().toISOString();
      console.log('Portal WebSocket connected');
    };

    ws.onmessage = function (event) {
      try {
        const msg = JSON.parse(event.data);
        handleProsodicEvent(msg);
      } catch {
        // Binary audio data — ignore for prosodic bridge
      }
    };

    ws.onclose = function () {
      setStatus('disconnected');
      connectBtn.disabled = false;
      disconnectBtn.disabled = true;
      ws = null;
      console.log('Portal WebSocket closed');
    };

    ws.onerror = function (err) {
      console.error('WebSocket error:', err);
      setStatus('disconnected');
    };
  }

  function disconnect() {
    if (ws) {
      ws.close();
      ws = null;
    }
  }

  function setStatus(state) {
    statusEl.className = 'status ' + state;
    statusEl.textContent = state.charAt(0).toUpperCase() + state.slice(1);
  }

  // --- Prosodic Event Handler ---
  function handleProsodicEvent(msg) {
    // Expected shape from Flute-Gateway:
    // { type: "prosodic_boundary", boundary: "SENTENCE"|"CLAUSE"|..., text: "...", timestamp: ... }
    if (msg.type !== 'prosodic_boundary') return;

    const boundary = BOUNDARY_MAP[msg.boundary] || BOUNDARY_MAP.NONE;

    // Update UI
    boundaryTypeEl.textContent = msg.boundary || 'NONE';
    boundaryTypeEl.style.color = boundary.color;
    boundaryBpmEl.textContent = boundary.bpm + ' BPM (' + boundary.tempo + ')';

    const freq = midiToFreq(boundary.midi);
    noteDisplayEl.textContent = boundary.note + ' — ' + Math.round(freq) + ' Hz';

    // Animate beat meter
    animateBeat(boundary.bpm);

    // Post to Three.js iframe
    if (viewerFrame && viewerFrame.contentWindow) {
      viewerFrame.contentWindow.postMessage({
        type: 'prosodic_update',
        boundary: msg.boundary,
        color: boundary.color,
        bpm: boundary.bpm,
        midi: boundary.midi,
        freq: freq,
      }, '*');
    }
  }

  // --- Beat Animation ---
  let beatAnimationFrame = null;

  function animateBeat(bpm) {
    if (beatAnimationFrame) cancelAnimationFrame(beatAnimationFrame);

    const beatDuration = 60000 / bpm; // ms per beat
    const startTime = performance.now();

    function tick() {
      const elapsed = performance.now() - startTime;
      const progress = Math.min(elapsed / beatDuration, 1);
      beatFillEl.style.width = (progress * 100) + '%';

      if (progress < 1) {
        beatAnimationFrame = requestAnimationFrame(tick);
      }
    }

    beatAnimationFrame = requestAnimationFrame(tick);
  }

  // --- Capture: Screenshot ---
  function captureScreenshot() {
    if (!viewerFrame || !viewerFrame.contentWindow) return;

    // Request canvas data from iframe
    viewerFrame.contentWindow.postMessage({ type: 'capture_screenshot' }, '*');
  }

  // Listen for screenshot response from iframe
  window.addEventListener('message', function (event) {
    if (event.data && event.data.type === 'screenshot_data') {
      const blob = dataURLtoBlob(event.data.dataUrl);
      if (blob) {
        uploadCapture(blob, 'screenshot-' + Date.now() + '.png', 'image/png');
      }
    }
  });

  function dataURLtoBlob(dataUrl) {
    try {
      const parts = dataUrl.split(',');
      const mime = parts[0].match(/:(.*?);/)[1];
      const bytes = atob(parts[1]);
      const arr = new Uint8Array(bytes.length);
      for (let i = 0; i < bytes.length; i++) {
        arr[i] = bytes.charCodeAt(i);
      }
      return new Blob([arr], { type: mime });
    } catch {
      console.error('Failed to convert dataURL to Blob');
      return null;
    }
  }

  // --- Capture: Recording ---
  function startRecording() {
    if (!viewerFrame || !viewerFrame.contentWindow) return;

    // Request stream from iframe canvas
    viewerFrame.contentWindow.postMessage({ type: 'start_stream' }, '*');
    recordStartBtn.disabled = true;
    recordStopBtn.disabled = false;
  }

  function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop();
    }
    recordStartBtn.disabled = false;
    recordStopBtn.disabled = true;
  }

  window.addEventListener('message', function (event) {
    if (event.data && event.data.type === 'canvas_stream') {
      // Iframe provides a stream — but cross-origin limitations apply.
      // Fallback: use captureStream on the portal page itself.
      console.log('Canvas stream received — starting MediaRecorder');
    }
  });

  // Fallback: record the entire portal view
  function startFallbackRecording() {
    const canvas = document.createElement('canvas');
    const portalRoot = document.getElementById('portal-root');
    // Use html2canvas or manual approach — for now, use MediaRecorder on the viewport
    recordedChunks = [];

    try {
      const stream = document.getElementById('viewer-panel').querySelector('iframe')
        ? null : null; // Cross-origin restriction

      // If no stream available, notify user
      console.warn('Cross-origin recording not available. Use Screenshot instead.');
      recordStartBtn.disabled = false;
      recordStopBtn.disabled = true;
    } catch (err) {
      console.error('Recording failed:', err);
    }
  }

  // --- Upload Capture to MinIO ---
  async function uploadCapture(blob, filename, contentType) {
    if (!window.PORTAL_AUTH || !window.PORTAL_AUTH.token) {
      console.error('Cannot upload: not authenticated');
      return;
    }

    try {
      // Get presigned upload URL
      const presignRes = await fetch(MINIO_UPLOAD_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ' + window.PORTAL_AUTH.token,
        },
        body: JSON.stringify({
          bucket: 'outputs',
          key: 'portal/' + filename,
          method: 'PUT',
          content_type: contentType,
        }),
      });

      if (!presignRes.ok) {
        console.error('Presign failed:', presignRes.status);
        return;
      }

      const { url } = await presignRes.json();

      // Upload
      await fetch(url, {
        method: 'PUT',
        body: blob,
        headers: { 'Content-Type': contentType },
      });

      console.log('Capture uploaded:', filename);
    } catch (err) {
      console.error('Upload failed:', err);
    }
  }

  // --- Event Listeners ---
  if (connectBtn) connectBtn.addEventListener('click', connect);
  if (disconnectBtn) disconnectBtn.addEventListener('click', disconnect);
  if (screenshotBtn) screenshotBtn.addEventListener('click', captureScreenshot);
  if (recordStartBtn) recordStartBtn.addEventListener('click', startRecording);
  if (recordStopBtn) recordStopBtn.addEventListener('click', stopRecording);

  // Initialize beat meter
  animateBeat(10); // 10 BPM default from AGNOTE4482.BEATS

  console.log('DARKXSIDE Portal initialized');
})();
