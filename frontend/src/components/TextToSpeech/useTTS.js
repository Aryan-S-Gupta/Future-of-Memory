// hooks/useTTS.js
import { useCallback, useEffect, useRef, useState } from "react";
import { useBgm } from "../../audio/AudioProvider.jsx";

const storageKey = "tts_enabled";

export default function useTTS(defaultEnabled = true, duckLevel = 0.25) {
    // browser speech synth (null if not supported)
    const synth = typeof window !== "undefined" ? window.speechSynthesis : null;

    // voices list + preload flag
    const voicesRef = useRef([]);
    const preloadedRef = useRef(false);

    // TTS on/off, saved in localStorage
    const [enabled, setEnabled] = useState(() => {
        try {
            const saved = localStorage.getItem(storageKey);
            return saved === null ? defaultEnabled : saved === "true";
        } catch {
            return defaultEnabled;
        }
    });

    // speaking status
    const [isSpeaking, setIsSpeaking] = useState(false);

    // bgm controls
    const { isMuted, volume, setDucking } = useBgm();

    // load voices + do a silent warmup once
    useEffect(() => {
        if (!synth) return;

        const loadVoices = () => {
            voicesRef.current = synth.getVoices() || [];

            // one-time preload so first real speak isn’t delayed
            if (voicesRef.current.length && !preloadedRef.current) {
                try {
                    const u = new SpeechSynthesisUtterance(" ");
                    u.volume = 0; // silent
                    u.rate = 1;
                    u.pitch = 1;

                    // try to pick a nice clear english voice
                    const warmup =
                        voicesRef.current.find(v =>
                            /Microsoft (Sonia|Jenny|Aria).*Online|Google UK English Female|Samantha|Victoria|Serena|Daniel/i.test(v.name)
                        ) || voicesRef.current[0];

                    if (warmup) u.voice = warmup;

                    synth.speak(u); // silent speak
                    preloadedRef.current = true;
                } catch { }
            }
        };

        loadVoices();
        synth.addEventListener?.("voiceschanged", loadVoices);
        return () => synth.removeEventListener?.("voiceschanged", loadVoices);
    }, [synth]);

    // save enabled flag
    useEffect(() => {
        try { localStorage.setItem(storageKey, String(enabled)); } catch { }
    }, [enabled]);

    // stop current speech
    const cancel = useCallback(() => {
        try { synth?.cancel(); } catch { }
        setIsSpeaking(false);
        setDucking(false);
    }, [synth, setDucking]);

    // speak some text
    const speak = useCallback((text) => {
        if (!synth || !enabled || !text) return;

        // stop any old speech + lower bgm
        try { synth.cancel(); } catch { }
        setDucking(true, duckLevel);

        const utter = new SpeechSynthesisUtterance(String(text));

        // pick english voice if possible
        const v = voicesRef.current.find(v => /en-/i.test(v.lang)) || voicesRef.current[0];
        if (v) utter.voice = v;

        // sync with app volume/mute
        utter.volume = isMuted ? 0 : Math.max(0.1, Math.min(1, volume));
        utter.rate = 1;
        utter.pitch = 1;

        // update state on start/stop
        utter.onstart = () => setIsSpeaking(true);
        utter.onend = () => { setIsSpeaking(false); setDucking(false); };
        utter.onerror = () => { setIsSpeaking(false); setDucking(false); };

        try { synth.speak(utter); } catch { setDucking(false); }
    }, [synth, enabled, isMuted, volume, setDucking, duckLevel]);

    // cleanup on unmount
    useEffect(() => () => cancel(), [cancel]);

    // return stuff for outside use
    return {
        speak, cancel, enabled, setEnabled, isSpeaking, supported: Boolean(synth)
    };
}
