---
name: Clinical Intelligence
colors:
  surface: '#101415'
  surface-dim: '#101415'
  surface-bright: '#363a3b'
  surface-container-lowest: '#0b0f10'
  surface-container-low: '#191c1e'
  surface-container: '#1d2022'
  surface-container-high: '#272a2c'
  surface-container-highest: '#323537'
  on-surface: '#e0e3e5'
  on-surface-variant: '#c6c6cd'
  inverse-surface: '#e0e3e5'
  inverse-on-surface: '#2d3133'
  outline: '#909097'
  outline-variant: '#45464d'
  surface-tint: '#bec6e0'
  primary: '#bec6e0'
  on-primary: '#283044'
  primary-container: '#0f172a'
  on-primary-container: '#798098'
  inverse-primary: '#565e74'
  secondary: '#4edea3'
  on-secondary: '#003824'
  secondary-container: '#00a572'
  on-secondary-container: '#00311f'
  tertiary: '#7bd0ff'
  on-tertiary: '#00354a'
  tertiary-container: '#001a27'
  on-tertiary-container: '#008abb'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#6ffbbe'
  secondary-fixed-dim: '#4edea3'
  on-secondary-fixed: '#002113'
  on-secondary-fixed-variant: '#005236'
  tertiary-fixed: '#c4e7ff'
  tertiary-fixed-dim: '#7bd0ff'
  on-tertiary-fixed: '#001e2c'
  on-tertiary-fixed-variant: '#004c69'
  background: '#101415'
  on-background: '#e0e3e5'
  surface-variant: '#323537'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: 0em
  label-caps:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.1em
  data-mono:
    fontFamily: JetBrains Mono
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 16px
  md: 24px
  lg: 40px
  xl: 64px
  gutter: 20px
  margin-mobile: 16px
  margin-desktop: 32px
---

## Brand & Style

The design system is engineered for high-stakes medical environments where clarity and perceived reliability are paramount. It adopts a **Technical Minimalism** style, blending the precision of laboratory equipment with the fluid intelligence of modern AI. 

The aesthetic focuses on "Active Assurance"—the UI should feel vigilant but never intrusive. Visual metaphors lean toward medical instrumentation: high-contrast data readouts, thin linework, and subtle glowing states that signal systemic health and background processing. The interface minimizes cognitive load by using generous whitespace and a strictly functional hierarchy, ensuring that critical safety information is never obscured by decorative elements.

## Colors

The palette is anchored in a deep-space navy to provide a stable, non-fatiguing foundation for long-duration monitoring. 

- **Primary (Deep Navy):** Used for background surfaces and structural elements to establish a sense of depth and authority.
- **Secondary (Emerald Green):** Reserved exclusively for "Safe," "Active," or "Normal" statuses. This color should pulsate or glow slightly when representing live AI monitoring.
- **Tertiary (Sky Blue):** Used for informational accents, secondary actions, and data visualization highlights.
- **Neutral (Crisp White/Slate):** Used for primary text and high-priority icons to ensure maximum legibility against the dark background.
- **System States:** High-alert situations should bypass the primary palette in favor of a specialized **#EF4444 (Emergency Red)** to break the user's focus and demand immediate action.

## Typography

The design system utilizes **Inter** for all primary communication due to its exceptional legibility in digital interfaces and neutral, professional tone. 

To reinforce the "AI/Medical" narrative, **JetBrains Mono** is introduced for labels, metadata, and numerical data points. This monospaced secondary font suggests precision, as if the data is being pulled directly from a high-speed diagnostic engine.

- Use **All-Caps JetBrains Mono** for overlines and small category labels to create a distinct visual "grid" feel.
- Maintain tight tracking on headlines but increase tracking for mono-spaced labels to ensure they remain legible at small sizes on low-resolution medical displays.

## Layout & Spacing

This design system employs a **Modular Fluid Grid** based on an 8px rhythmic scale, though it uses a 4px "half-step" for tight internal component spacing (like labels next to icons).

- **Desktop:** 12-column grid with 20px gutters. Content should be logically grouped into "Monitoring Panes" that can scale to fill the viewport.
- **Mobile:** 4-column grid with 16px margins. Primary safety status (the "Pulse") must always be pinned or prominently displayed at the top of the viewport.
- **Rhythm:** Use `lg` (40px) and `xl` (64px) spacing to separate distinct diagnostic sections, ensuring the interface feels airy and organized rather than cluttered with data.

## Elevation & Depth

Depth in the design system is communicated through **Tonal Layering** and **Luminescent Accents** rather than traditional drop shadows.

- **Level 0 (Floor):** The base background (#0F172A).
- **Level 1 (Surface):** A slightly lighter navy (#1E293B) with a subtle 1px border (#334155) to define card boundaries.
- **Active State Glow:** Elements that are "On" or "Safe" utilize an outer glow (0px 0px 12px) using the Emerald Green color at 30% opacity. This creates a "light-emitting" effect common in medical monitors.
- **Glassmorphism:** Use a light backdrop blur (8px) for persistent navigation bars or modal overlays to maintain context of the underlying data while focusing the user's attention.

## Shapes

The shape language is **Soft (0.25rem)**. While rounded corners are used to make the interface feel modern and approachable, the radius remains small to preserve a disciplined, technical appearance. 

- **Primary Buttons:** Use `rounded-lg` (0.5rem) to make them easily targetable.
- **Status Indicators:** Small circles or "pills" for status tags to provide a organic contrast to the rigid grid.
- **Dividers:** Use ultra-thin 1px lines with low-opacity gradients at the ends to fade them into the background, avoiding harsh box-like containment.

## Components

### Buttons
- **Primary:** Emerald Green background with White text. Hover state increases the "glow" intensity.
- **Ghost:** Transparent background with a 1px Slate border. Used for secondary navigation.

### Chips & Status Tags
- Used for patient status or AI confidence levels. Always pair the Emerald Green text with a 10% opacity Emerald background for a "lit-from-within" look.

### Input Fields
- Darker navy background than the card surface. The focus state should change the border to Sky Blue with a subtle outer glow. Label text always uses the **label-caps** typography style.

### Monitoring Cards
- Must include a "Last Updated" timestamp in the bottom-right corner using **data-mono** typography.
- Use a 2px vertical accent bar on the left edge of the card to denote the current status (Green for OK, Red for Alert).

### Pulse Indicator
- A specialized component representing the AI "thought" process. It is a soft-glowing circle that expands and contracts slightly, placed near the primary logo or data headers to show the system is live.
