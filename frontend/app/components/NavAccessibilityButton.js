"use client";
import { useAccessibility } from "../context/AccessibilityContext";

export default function NavAccessibilityButton() {
    const { toggleModal } = useAccessibility();

    return (
        <button
            className="nav-link btn-ghost"
            onClick={toggleModal}
            style={{
                background: 'transparent',
                border: 'none',
                cursor: 'pointer',
                fontFamily: 'inherit'
            }}
        >
            Accessibility
        </button>
    );
}
