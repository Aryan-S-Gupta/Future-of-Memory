// hooks/useTTS.js
import { useCallback, useEffect, useRef, useState } from "react";
import { useBgm } from "../../audio/AudioProvider.jsx";

const storageKey = "tts_enabled";

export default function useTTS(defaultEnabled = true, duckLevel = 0.25) {
  const synth = typeof window !== "undefined" ? window.speechSynthesis : null;
  const voicesRef = useRef([]);
  const [enabled, setEnabled] = useState(() => {
    try {
      const saved = localStorage.getItem(storageKey);
      return saved === null ? defaultEnabled : saved === "true";
    } catch {
      return defaultEnabled;
    }
  });
  const [isSpeaking, setIsSpeaking] = useState(false);

  const { isMuted, volume, setDucking } = useBgm();

  // Load voices (some browsers load asynchronously)
  useEffect(() => {
    if (!synth) return;
    const loadVoices = () => { voicesRef.current = synth.getVoices() || []; };
    loadVoices();
    synth.addEventListener?.("voiceschanged", loadVoices);
    return () => synth.removeEventListener?.("voiceschanged", loadVoices);
  }, [synth]);

  // Persist toggle
  useEffect(() => {
    try { localStorage.setItem(storageKey, String(enabled)); } catch {}
  }, [enabled]);

  const cancel = useCallback(() => {
    try { synth?.cancel(); } catch {}
    setIsSpeaking(false);
    setDucking(false);
  }, [synth, setDucking]);

  const speak = useCallback((text) => {
    if (!synth || !enabled || !text) return;
    // Stop anything currently playing and start ducking bgm
    try { synth.cancel(); } catch {}
    setDucking(true, duckLevel);

    const utter = new SpeechSynthesisUtterance(String(text));
    const v = voicesRef.current.find(v => /en-/i.test(v.lang)) || voicesRef.current[0];
    if (v) utter.voice = v;

    // Map to your app’s master volume/mute
    utter.volume = isMuted ? 0 : Math.max(0.1, Math.min(1, volume)); // keep at least audible if enabled
    utter.rate = 1;
    utter.pitch = 1;

    utter.onstart = () => setIsSpeaking(true);
    utter.onend = () => { setIsSpeaking(false); setDucking(false); };
    utter.onerror = () => { setIsSpeaking(false); setDucking(false); };

    try { synth.speak(utter); } catch { setDucking(false); }
  }, [synth, enabled, isMuted, volume, setDucking, duckLevel]);

  // Cleanup on unmount
  useEffect(() => () => cancel(), [cancel]);

  return { speak, cancel, enabled, setEnabled, isSpeaking, supported: Boolean(synth) };
}
