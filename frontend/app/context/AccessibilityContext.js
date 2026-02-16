"use client";
import { createContext, useContext, useState, useEffect, useRef } from "react";
import { usePathname } from "next/navigation";

const AccessibilityContext = createContext();

export function AccessibilityProvider({ children }) {
    // Existing states
    const [dyslexiaFriendly, setDyslexiaFriendly] = useState(false);
    const [adhdFriendly, setAdhdFriendly] = useState(false);
    const [fontSize, setFontSize] = useState("medium"); // small, medium, large, x-large

    // New UMANG-style states
    const [textSpacing, setTextSpacing] = useState(false);
    const [lineHeight, setLineHeight] = useState(false);
    const [saturation, setSaturation] = useState(1); // 0 (grayscale), 1 (normal), 2 (high saturation)
    const [invertColors, setInvertColors] = useState(false);
    const [theme, setTheme] = useState("light"); // light, dark (acts as Light/Dark toggle)
    const [highlightLinks, setHighlightLinks] = useState(false);
    const [cursorType, setCursorType] = useState("default"); // default, big
    const [pauseAnimations, setPauseAnimations] = useState(false);
    const [hideImages, setHideImages] = useState(false);

    // Screen Reader State
    const [screenReaderMode, setScreenReaderMode] = useState(false);
    const [isReading, setIsReading] = useState(false);
    const [isPaused, setIsPaused] = useState(false);

    // Modal State
    const [isModalOpen, setIsModalOpen] = useState(false);
    const openModal = () => setIsModalOpen(true);
    const closeModal = () => setIsModalOpen(false);
    const toggleModal = () => setIsModalOpen((prev) => !prev);

    const pathname = usePathname();
    const utteranceRef = useRef(null);

    // Apply classes/styles to HTML/Body
    useEffect(() => {
        const body = document.body;
        const html = document.documentElement;

        // Font Family
        if (dyslexiaFriendly) body.classList.add("dyslexia-font");
        else body.classList.remove("dyslexia-font");

        // ADHD Mode
        if (adhdFriendly) body.classList.add("adhd-focus");
        else body.classList.remove("adhd-focus");

        // Font Size
        html.classList.remove("font-sm", "font-md", "font-lg", "font-xl");
        html.classList.add(`font-${fontSize === "small" ? "sm" : fontSize === "large" ? "lg" : fontSize === "x-large" ? "xl" : "md"}`);

        // Text Spacing
        if (textSpacing) html.classList.add("text-spacing");
        else html.classList.remove("text-spacing");

        // Line Height
        if (lineHeight) html.classList.add("line-height-lg");
        else html.classList.remove("line-height-lg");

        // Saturation
        html.style.filter = `saturate(${saturation})`;
        // Invert acts on top of saturation usually, or we can combine filters
        // Using a class for invert might be safer for specific exclusions, but simple filter is okay
        if (invertColors) {
            html.style.filter = `saturate(${saturation}) invert(1)`;
        } else {
            html.style.filter = `saturate(${saturation})`;
        }

        // Theme
        html.setAttribute("data-theme", theme);
        if (theme === "dark") body.classList.add("dark-theme");
        else body.classList.remove("dark-theme");

        // Highlight Links
        if (highlightLinks) body.classList.add("highlight-links");
        else body.classList.remove("highlight-links");

        // Cursor
        if (cursorType === "big") body.classList.add("big-cursor");
        else body.classList.remove("big-cursor");

        // Pause Animations
        if (pauseAnimations) body.classList.add("pause-animations");
        else body.classList.remove("pause-animations");

        // Hide Images
        if (hideImages) body.classList.add("hide-images");
        else body.classList.remove("hide-images");


    }, [dyslexiaFriendly, adhdFriendly, fontSize, textSpacing, lineHeight, saturation, invertColors, theme, highlightLinks, cursorType, pauseAnimations, hideImages]);

    // ADHD Reading Mask Logic
    const [maskY, setMaskY] = useState(0);
    const maskHeight = 120; // Height of the clear Area

    useEffect(() => {
        if (!adhdFriendly) return;

        const handleMouseMove = (e) => {
            setMaskY(e.clientY);
        };

        window.addEventListener("mousemove", handleMouseMove);
        return () => window.removeEventListener("mousemove", handleMouseMove);
    }, [adhdFriendly]);


    // Reset Function
    const resetSettings = () => {
        setDyslexiaFriendly(false);
        setAdhdFriendly(false);
        setFontSize("medium");
        setTextSpacing(false);
        setLineHeight(false);
        setSaturation(1);
        setInvertColors(false);
        setTheme("light");
        setHighlightLinks(false);
        setCursorType("default");
        setPauseAnimations(false);
        setHideImages(false);
        setScreenReaderMode(false);
        stopReading();
    };

    // Cycle Saturation
    const cycleSaturation = () => {
        if (saturation === 1) setSaturation(2); // High Sat
        else if (saturation === 2) setSaturation(0); // Grayscale
        else setSaturation(1); // Normal
    };


    // Screen Reader Logic (Existing)
    useEffect(() => { stopReading(); }, [pathname]);
    useEffect(() => { if (!screenReaderMode) stopReading(); }, [screenReaderMode]);

    const speak = (text) => {
        if (!screenReaderMode) return;
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(text);
        utteranceRef.current = utterance;
        utterance.onend = () => { setIsReading(false); setIsPaused(false); };
        window.speechSynthesis.speak(utterance);
        setIsReading(true); setIsPaused(false);
    };

    const stopReading = () => {
        window.speechSynthesis.cancel();
        setIsReading(false); setIsPaused(false);
    };

    const pauseReading = () => {
        if (window.speechSynthesis.speaking && !window.speechSynthesis.paused) {
            window.speechSynthesis.pause();
            setIsPaused(true);
        }
    };

    const resumeReading = () => {
        if (window.speechSynthesis.paused) {
            window.speechSynthesis.resume();
            setIsPaused(false);
        }
    };

    const readPageContent = () => {
        if (!screenReaderMode) return;
        const elements = document.querySelectorAll('h1, h2, h3, h4, p, li, button, a, [aria-label]');
        let textContent = "";
        elements.forEach(el => {
            if (el.offsetParent === null) return;
            let text = el.innerText || el.getAttribute("aria-label") || el.alt;
            if (text && text.trim().length > 0) {
                text = text.replace(/\s+/g, ' ').trim();
                if (!textContent.includes(text)) textContent += text + ". ";
            }
        });
        if (textContent) speak(textContent);
        else speak("No content found to read.");
    };

    return (
        <AccessibilityContext.Provider
            value={{
                dyslexiaFriendly, setDyslexiaFriendly,
                adhdFriendly, setAdhdFriendly,
                fontSize, setFontSize,
                textSpacing, setTextSpacing,
                lineHeight, setLineHeight,
                saturation, setSaturation, cycleSaturation,
                invertColors, setInvertColors,
                theme, setTheme,
                highlightLinks, setHighlightLinks,
                cursorType, setCursorType,
                pauseAnimations, setPauseAnimations,
                hideImages, setHideImages,

                resetSettings,

                screenReaderMode, setScreenReaderMode,
                isReading, isPaused,
                readPageContent, stopReading, pauseReading, resumeReading,

                isModalOpen, openModal, closeModal, toggleModal
            }}
        >
            {children}
            {/* ADHD Reading Mask Overlay */}
            {adhdFriendly && (
                <>
                    <div style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        width: '100%',
                        height: Math.max(0, maskY - maskHeight / 2),
                        background: 'rgba(0, 0, 0, 0.6)',
                        zIndex: 9999,
                        pointerEvents: 'none',
                        transition: 'height 0.1s linear'
                    }} />
                    <div style={{
                        position: 'fixed',
                        top: maskY + maskHeight / 2,
                        left: 0,
                        width: '100%',
                        bottom: 0,
                        background: 'rgba(0, 0, 0, 0.6)',
                        zIndex: 9999,
                        pointerEvents: 'none',
                        transition: 'top 0.1s linear'
                    }} />
                    {/* Optional: Guide Line */}
                    <div style={{
                        position: 'fixed',
                        top: maskY,
                        left: 0,
                        width: '100%',
                        height: 2,
                        background: 'rgba(255, 0, 0, 0.5)',
                        zIndex: 10000,
                        pointerEvents: 'none',
                        transform: 'translateY(-50%)'
                    }} />
                </>
            )}
        </AccessibilityContext.Provider>
    );
}

export function useAccessibility() {
    return useContext(AccessibilityContext);
}
