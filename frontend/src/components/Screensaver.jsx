import { useEffect, useLayoutEffect, useState } from "react";
import useIdle from "../components/useIdle";
import "../styles/tokens.css";
import { motion, AnimatePresence } from "framer-motion";

/**
 * Screensaver Component
 * ---------------------
 * Displays an animated idle screen with rotating text rings and a central logo.
 * Automatically appears after a period of inactivity and disappears on interaction.
 * Built with Framer Motion for smooth fade/scale transitions and accessible keyboard input.
 */
export default function Screensaver({
    idleMs = 600000, // default: 10 minutes before screensaver activates
    initialShow = true, // whether to show screensaver on first load
    onDismiss, // callback when user interacts and screensaver hides
    onShow, // callback when screensaver activates due to idleness
    title = "30B", // main title text
    subtitle = "Speculative Futures of Memory", // subtitle text
    hint = "Tap anywhere to begin", // hint for user to exit
    tagline = "• NAVIGATING THE FUTURE • ETHICS • IDENTITY • SPECULATION • TECH • ",
}) {
    const [visible, setVisible] = useState(initialShow);

    // Store phrases for inner and outer text rings
    const [outerPhrase, setOuterPhrase] = useState(tagline);
    const [innerPhrase, setInnerPhrase] = useState(tagline);

    // Ring geometry (in SVG coordinate units)
    const OUTER_RADIUS = 80;
    const INNER_RADIUS = 65;

    // Disable page scrolling when screensaver is active
    useEffect(() => {
        if (!visible) return;
        const prev = document.body.style.overflow;
        document.body.style.overflow = "hidden";
        return () => {
            document.body.style.overflow = prev;
        };
    }, [visible]);

    // Trigger the screensaver after being idle for the specified duration
    useIdle({
        idleMs,
        onIdle: () => {
            setVisible(true);
            onShow?.();
        },
    });

    // Dismiss screensaver (on click/tap/keyboard)
    const dismiss = (e) => {
        e?.preventDefault?.();
        e?.stopPropagation?.();
        setVisible(false);
        onDismiss?.();
    };

    // Allow dismissal using Enter, Space, or Escape keys
    const onKeyDown = (e) => {
        if (["Enter", " ", "Escape"].includes(e.key)) dismiss(e);
    };

    /**
     * Dynamically adjust the number of repeated tagline phrases
     * to perfectly wrap around the circular SVG paths.
     */
    useLayoutEffect(() => {
        const avgChar = 6.5; // average character width (approximation)

        const fit = (pathEl, base, padPx = 0) => {
            if (!pathEl) return base.repeat(4).trim();
            const L = pathEl.getTotalLength() - padPx; // total path length
            const w = base.length * avgChar; // estimated total text width
            const n = Math.max(2, Math.ceil(L / w) + 1); // ensure full wrap
            return ((base + "   ").repeat(n)).trim(); // add spacing for clarity
        };

        const outerPath = document.querySelector("#halo-outer");
        const innerPath = document.querySelector("#halo-inner-rev");

        setOuterPhrase(fit(outerPath, tagline, 1000));
        setInnerPhrase(fit(innerPath, tagline, 850));
    }, [tagline]);

    return (
        <AnimatePresence>
            {visible && (
                <motion.div
                    className="screensaver"
                    role="dialog"
                    aria-modal="true"
                    aria-label="Screensaver — press Enter to begin"
                    tabIndex={0}
                    onKeyDown={onKeyDown}
                    onClick={dismiss}
                    onTouchStart={dismiss}
                    initial={{ opacity: 1, scale: 1 }}
                    exit={{ scale: 1.3, opacity: 0 }}
                    transition={{
                        scale: { duration: 0.8, ease: "easeOut" },
                        opacity: { duration: 3, ease: "easeInOut" },
                    }}
                >
                    {/* Animated circular text halos */}
                    <motion.svg
                        className="halo"
                        viewBox="0 0 200 200"
                        aria-hidden="true"
                        initial={{ scale: 1, opacity: 1 }}
                        exit={{ scale: 2, opacity: 0 }}
                        transition={{ duration: 1.4, ease: "easeInOut" }}
                    >
                        <defs>
                            {/* OUTER circle (clockwise direction) */}
                            <path
                                id="halo-outer"
                                d={`M100,100 m-${OUTER_RADIUS},0 a${OUTER_RADIUS},${OUTER_RADIUS} 0 1,1 ${OUTER_RADIUS * 2
                                    },0 a${OUTER_RADIUS},${OUTER_RADIUS} 0 1,1 -${OUTER_RADIUS * 2},0`}
                                pathLength="1000"
                            />
                            {/* INNER circle (counter-clockwise for baseline alignment) */}
                            <path
                                id="halo-inner-rev"
                                d={`M100,100 m${INNER_RADIUS},0 a${INNER_RADIUS},${INNER_RADIUS} 0 1,0 -${INNER_RADIUS * 2
                                    },0 a${INNER_RADIUS},${INNER_RADIUS} 0 1,0 ${INNER_RADIUS * 2},0`}
                                pathLength="860"
                            />
                        </defs>

                        {/* OUTER text ring */}
                        <g className="ring ring--outer">
                            <text className="txt txt--outer" textRendering="optimizeLegibility">
                                <textPath
                                    href="#halo-outer"
                                    startOffset="3%"
                                    lengthAdjust="spacing"
                                    textLength="1000"
                                >
                                    {outerPhrase}
                                </textPath>
                            </text>
                        </g>

                        {/* INNER text ring (reverse direction for variation) */}
                        <g className="ring ring--inner">
                            <text className="txt txt--inner" textRendering="optimizeLegibility">
                                <textPath
                                    href="#halo-inner-rev"
                                    startOffset="10%"
                                    lengthAdjust="spacing"
                                    textLength="810"
                                >
                                    {innerPhrase}
                                </textPath>
                            </text>
                        </g>
                    </motion.svg>

                    {/* Central logo and labels */}
                    <motion.div
                        className="center"
                        aria-hidden="true"
                        initial={{ opacity: 1, scale: 1 }}
                        exit={{ opacity: 0, scale: 1.2 }}
                        transition={{ duration: 1.4, ease: "easeInOut" }}
                    >
                        <div className="logo">{title}</div>
                        <p className="subtitle">{subtitle}</p>
                        <br />
                        <p className="hint">{hint}</p>
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}