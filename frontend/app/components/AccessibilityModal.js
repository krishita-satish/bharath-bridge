"use client";
import { useAccessibility } from "../context/AccessibilityContext";
import { useEffect } from "react";

export default function AccessibilityModal() {
    const {
        dyslexiaFriendly, setDyslexiaFriendly,
        adhdFriendly, setAdhdFriendly,
        fontSize, setFontSize,
        textSpacing, setTextSpacing,
        lineHeight, setLineHeight,
        saturation, cycleSaturation,
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

        isModalOpen, closeModal
    } = useAccessibility();

    // Close on Escape key
    useEffect(() => {
        const handleEsc = (e) => {
            if (e.key === "Escape") closeModal();
        };
        window.addEventListener("keydown", handleEsc);
        return () => window.removeEventListener("keydown", handleEsc);
    }, [closeModal]);

    if (!isModalOpen) return null;

    // SVGs
    const Icons = {
        ReadableFont: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20" /></svg>,
        ReadingMask: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M2 12h20" /><path d="M2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6" /><path d="M2 12V6a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v6" /></svg>,
        Saturation: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z" /></svg>,
        Theme: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="5" /><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" /></svg>,
        Invert: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10" /><path d="M12 2a10 10 0 0 1 0 20z" fill="currentColor" /></svg>,
        Link: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" /><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" /></svg>,
        Speaker: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5" /><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07" /></svg>,
        Cursor: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 3l7.07 16.97 2.51-7.39 7.39-2.51L3 3z" /><path d="M13 13l6 6" /></svg>,
        HideImage: <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2" /><circle cx="8.5" cy="8.5" r="1.5" /><polyline points="21 15 16 10 5 21" /><line x1="3" y1="3" x2="21" y2="21" /></svg>
    };

    const features = [
        {
            label: "Bigger Text",
            icon: "Tᵀ",
            action: () => setFontSize(fontSize === "medium" ? "large" : fontSize === "large" ? "x-large" : "medium"),
            isActive: fontSize === "large" || fontSize === "x-large",
            desc: "Increase text size"
        },
        {
            label: "Smaller Text",
            icon: "ᵀT",
            action: () => setFontSize(fontSize === "medium" ? "small" : "medium"),
            isActive: fontSize === "small",
            desc: "Decrease text size"
        },
        {
            label: "Text Spacing",
            icon: "↔",
            action: () => setTextSpacing(!textSpacing),
            isActive: textSpacing,
            desc: "Increase space between letters"
        },
        {
            label: "Line Height",
            icon: "↕",
            action: () => setLineHeight(!lineHeight),
            isActive: lineHeight,
            desc: "Increase space between lines"
        },
        {
            label: "Dyslexia Friendly",
            icon: Icons.ReadableFont,
            action: () => setDyslexiaFriendly(!dyslexiaFriendly),
            isActive: dyslexiaFriendly,
            desc: "Use open-dyslexic font"
        },
        {
            label: "ADHD Mode",
            icon: Icons.ReadingMask,
            action: () => setAdhdFriendly(!adhdFriendly),
            isActive: adhdFriendly,
            desc: "Reading Mask / Focus"
        },
        {
            label: "Saturation",
            icon: Icons.Saturation,
            action: cycleSaturation,
            isActive: saturation !== 1,
            desc: saturation === 0 ? "Grayscale" : saturation === 2 ? "High Saturation" : "Normal"
        },
        {
            label: "Light-Dark",
            icon: Icons.Theme,
            action: () => setTheme(theme === "light" ? "dark" : "light"),
            isActive: theme === "dark",
            desc: "Toggle theme"
        },
        {
            label: "Invert Colors",
            icon: Icons.Invert,
            action: () => setInvertColors(!invertColors),
            isActive: invertColors,
            desc: "Invert all colors"
        },
        {
            label: "Highlight Links",
            icon: Icons.Link,
            action: () => setHighlightLinks(!highlightLinks),
            isActive: highlightLinks,
            desc: "High contrast links"
        },
        {
            label: "Text To Speech",
            icon: Icons.Speaker,
            action: () => setScreenReaderMode(!screenReaderMode),
            isActive: screenReaderMode,
            desc: screenReaderMode ? "Reading Enabled" : "Read aloud"
        },
        {
            label: "Cursor",
            icon: Icons.Cursor,
            action: () => setCursorType(cursorType === "default" ? "big" : "default"),
            isActive: cursorType === "big",
            desc: "Big cursor"
        },
        {
            label: "Pause Animation",
            icon: "⏸",
            action: () => setPauseAnimations(!pauseAnimations),
            isActive: pauseAnimations,
            desc: "Stop moving elements"
        },
        {
            label: "Hide Images",
            icon: Icons.HideImage,
            action: () => setHideImages(!hideImages),
            isActive: hideImages,
            desc: "Hide all images"
        },
    ];

    return (
        <div className="modal-overlay" onClick={closeModal}>
            <div className="modal-content" onClick={e => e.stopPropagation()}>
                {/* Header Overlay Style */}
                <div className="umang-header">
                    <div>
                        <h1>Accessibility Options</h1>
                        <p>Customize your viewing experience</p>
                    </div>
                    <div style={{ display: 'flex', gap: 10, alignItems: 'center' }}>
                        <button className="reset-btn" onClick={resetSettings}>
                            ↺ Reset
                        </button>
                        <button className="close-btn" onClick={closeModal}>
                            ✕
                        </button>
                    </div>

                </div>

                {/* Screen Reader Active Controls */}
                {screenReaderMode && (
                    <div className="reader-controls-fixed card-glow">
                        <div style={{ display: "flex", gap: 12, alignItems: 'center' }}>
                            <span className="reader-status-text">
                                {isReading ? (isPaused ? "Paused" : "Reading...") : "Ready to Read"}
                            </span>
                            {!isReading ? (
                                <button className="btn btn-primary btn-sm" onClick={readPageContent}>▶ Read Page</button>
                            ) : (
                                <>
                                    <button className="btn btn-secondary btn-sm" onClick={isPaused ? resumeReading : pauseReading}>
                                        {isPaused ? "▶ Resume" : "⏸ Pause"}
                                    </button>
                                    <button className="btn btn-danger btn-sm" onClick={stopReading}>⏹ Stop</button>
                                </>
                            )}
                        </div>
                    </div>
                )}

                {/* Grid Layout */}
                <div className="access-grid">
                    {features.map((f, i) => (
                        <button
                            key={i}
                            className={`access-card ${f.isActive ? "active" : ""}`}
                            onClick={f.action}
                            title={f.desc}
                        >
                            <div className="icon">{f.icon}</div>
                            <div className="label">{f.label}</div>
                        </button>
                    ))}
                </div>
            </div>

            <style jsx>{`
                .modal-overlay {
                    position: fixed;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: rgba(0, 0, 0, 0.7);
                    z-index: 9999; /* Highest Z-Index */
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    backdrop-filter: blur(5px);
                    animation: fadeIn 0.2s ease-out;
                    padding: 20px;
                }

                .modal-content {
                    background: var(--bg-card);
                    border: 1px solid var(--border);
                    border-radius: 20px;
                    width: 100%;
                    max-width: 900px;
                    max-height: 90vh;
                    overflow-y: auto;
                    padding: 24px;
                    box-shadow: 0 10px 40px rgba(0,0,0,0.5);
                    animation: slideUp 0.3s ease-out;
                    position: relative;
                }

                @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
                @keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }

                .umang-header {
                    background: var(--bg-secondary);
                    padding: 20px;
                    border-radius: 16px;
                    margin-bottom: 24px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border: 1px solid var(--border);
                }

                .umang-header h1 {
                    font-size: 1.5rem;
                    margin-bottom: 4px;
                }
                
                .umang-header p {
                    color: var(--text-secondary);
                    font-size: 0.9rem;
                    margin: 0;
                }

                .close-btn {
                    background: transparent;
                    border: none;
                    color: var(--text-muted);
                    font-size: 1.5rem;
                    cursor: pointer;
                    width: 36px;
                    height: 36px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: 0.2s;
                }
                .close-btn:hover {
                    background: var(--bg-card-hover);
                    color: var(--text-primary);
                }

                .reset-btn {
                    background: rgba(239, 68, 68, 0.1);
                    color: var(--accent-red);
                    border: 1px solid rgba(239, 68, 68, 0.2);
                    padding: 8px 16px;
                    border-radius: var(--radius-full);
                    font-weight: 600;
                    cursor: pointer;
                    transition: 0.2s;
                    font-size: 0.85rem;
                }
                
                .reset-btn:hover {
                    background: var(--accent-red);
                    color: #fff;
                }

                .access-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
                    gap: 12px;
                }

                .access-card {
                    background: var(--bg-secondary);
                    border: 2px solid var(--border);
                    border-radius: 12px;
                    padding: 16px 12px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    gap: 10px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    aspect-ratio: 1;
                    height: 100%;
                }

                .access-card:hover {
                    transform: translateY(-2px);
                    box-shadow: var(--shadow-card);
                    border-color: var(--border-hover);
                }

                .access-card.active {
                    background: rgba(91, 141, 239, 0.1);
                    border-color: var(--accent-blue);
                    box-shadow: 0 0 0 2px var(--accent-blue-glow);
                }
                
                .access-card.active .icon, .access-card.active .label {
                    color: var(--accent-blue);
                    font-weight: 700;
                }

                .icon {
                    font-size: 2rem;
                    color: var(--text-primary);
                    line-height: 1;
                    /* Ensure SVGs inherit color */
                }
                .icon svg {
                    width: 32px;
                    height: 32px;
                }

                .label {
                    font-size: 0.85rem;
                    color: var(--text-secondary);
                    font-weight: 500;
                    text-align: center;
                }

                .reader-controls-fixed {
                    position: sticky;
                    top: 0;
                    z-index: 100;
                    background: var(--bg-card);
                    padding: 12px 20px;
                    border-radius: var(--radius-full);
                    margin-bottom: 24px;
                    display: flex;
                    justify-content: center;
                    border: 1px solid var(--accent-green);
                    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
                }

                .reader-status-text {
                    font-weight: 600;
                    color: var(--accent-green);
                    font-size: 0.9rem;
                    margin-right: 12px;
                }
                
                @media (max-width: 600px) {
                    .access-grid {
                         grid-template-columns: repeat(2, 1fr);
                    }
                    .umang-header {
                        flex-direction: column;
                        align-items: flex-start;
                        gap: 12px;
                    }
                }
            `}</style>
        </div>
    );
}
