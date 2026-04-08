(() => {
  let mediaRecorder = null;
  let audioChunks = [];
  let isRecording = false;

  const btnRecord = document.getElementById("btn-record");
  const btnStop = document.getElementById("btn-stop");
  const btnCopy = document.getElementById("btn-copy");
  const statusEl = document.getElementById("status");
  const transcriptEl = document.getElementById("transcript");
  const refinedEl = document.getElementById("refined");
  const refinedSection = document.getElementById("refined-section");
  const presetContainer = document.getElementById("preset-buttons");
  const recordRing = document.getElementById("record-ring");
  const waveform = document.getElementById("waveform");
  const recordIcon = document.getElementById("record-icon");

  // ── Preset loading ──────────────────────────────────────────────────────────

  async function initPresets() {
    try {
      const res = await fetch("/api/presets");
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const { presets } = await res.json();

      presetContainer.innerHTML = "";
      for (const preset of presets) {
        const btn = document.createElement("button");
        btn.className = "btn btn-preset";
        btn.textContent = preset.label;
        btn.dataset.presetId = preset.id;
        btn.disabled = true;
        btn.addEventListener("click", () => refineTranscript(preset.id, btn));
        presetContainer.appendChild(btn);
      }
    } catch (err) {
      presetContainer.innerHTML = `<span class="status error">Failed to load presets: ${err.message}</span>`;
    }
  }

  function setPresetsEnabled(enabled) {
    presetContainer.querySelectorAll(".btn-preset").forEach((btn) => {
      btn.disabled = !enabled;
    });
  }

  // ── Recording ───────────────────────────────────────────────────────────────

  btnRecord.addEventListener("click", startRecording);
  btnStop.addEventListener("click", stopRecording);

  async function startRecording() {
    let stream;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    } catch (err) {
      setStatus(`Microphone access denied: ${err.message}`, "error");
      return;
    }

    audioChunks = [];

    // Prefer webm/opus; fall back gracefully
    const mimeType = ["audio/webm;codecs=opus", "audio/webm", "audio/ogg"].find(
      (m) => MediaRecorder.isTypeSupported(m)
    ) || "";

    mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : {});

    mediaRecorder.addEventListener("dataavailable", (e) => {
      if (e.data.size > 0) audioChunks.push(e.data);
    });

    mediaRecorder.addEventListener("stop", () => {
      stream.getTracks().forEach((t) => t.stop());
      const blob = new Blob(audioChunks, {
        type: mediaRecorder.mimeType || "audio/webm",
      });
      sendAudioForTranscription(blob);
    });

    mediaRecorder.start(250); // collect in 250 ms chunks
    isRecording = true;

    btnRecord.disabled = true;
    btnRecord.classList.add("recording");
    recordRing.classList.add("active");
    waveform.classList.add("active");
    recordIcon.textContent = "■";
    btnStop.disabled = false;
    setPresetsEnabled(false);
    refinedSection.hidden = true;
    setStatus("Recording…", "active");
  }

  function stopRecording() {
    if (!mediaRecorder || !isRecording) return;
    isRecording = false;
    mediaRecorder.stop();

    btnStop.disabled = true;
    btnRecord.disabled = false;
    btnRecord.classList.remove("recording");
    recordRing.classList.remove("active");
    waveform.classList.remove("active");
    recordIcon.textContent = "●";
    setStatus("Transcribing…", "active");
  }

  // ── Transcription ───────────────────────────────────────────────────────────

  async function sendAudioForTranscription(blob) {
    const formData = new FormData();
    const ext = blob.type.includes("ogg") ? "ogg" : "webm";
    formData.append("audio", blob, `recording.${ext}`);

    try {
      const res = await fetch("/api/transcribe", {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);

      transcriptEl.value = data.transcript;
      setPresetsEnabled(true);
      setStatus("Transcription complete. Edit if needed, then pick a preset.", "success");
    } catch (err) {
      setStatus(`Transcription failed: ${err.message}`, "error");
    }
  }

  // ── Refinement ──────────────────────────────────────────────────────────────

  async function refineTranscript(presetId, btn) {
    const transcript = transcriptEl.value.trim();
    if (!transcript) {
      setStatus("Nothing to refine — transcript is empty.", "error");
      return;
    }

    // Mark active preset button
    presetContainer.querySelectorAll(".btn-preset").forEach((b) =>
      b.classList.remove("active")
    );
    btn.classList.add("active");
    setPresetsEnabled(false);
    setStatus("Refining…", "active");

    try {
      const res = await fetch("/api/refine", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ transcript, preset_id: presetId }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);

      refinedEl.value = data.refined;
      refinedSection.hidden = false;
      setStatus("Done.", "success");
    } catch (err) {
      setStatus(`Refinement failed: ${err.message}`, "error");
    } finally {
      setPresetsEnabled(true);
    }
  }

  // ── Clipboard ───────────────────────────────────────────────────────────────

  btnCopy.addEventListener("click", async () => {
    const text = refinedEl.value;
    if (!text) return;
    try {
      await navigator.clipboard.writeText(text);
      const original = btnCopy.innerHTML;
      btnCopy.innerHTML = "✓ Copied!";
      setTimeout(() => (btnCopy.innerHTML = original), 1500);
    } catch {
      // Fallback for browsers without clipboard API
      refinedEl.select();
      document.execCommand("copy");
    }
  });

  // ── Helpers ─────────────────────────────────────────────────────────────────

  function setStatus(msg, type = "") {
    statusEl.textContent = msg;
    statusEl.className = "status-text" + (type ? ` ${type}` : "");
  }

  // ── Init ─────────────────────────────────────────────────────────────────────

  initPresets();
})();
