---
name: DineAI Design System
colors:
  surface: '#fcf9f8'
  surface-dim: '#dcd9d9'
  surface-bright: '#fcf9f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f2'
  surface-container: '#f0eded'
  surface-container-high: '#eae7e7'
  surface-container-highest: '#e5e2e1'
  on-surface: '#1b1b1b'
  on-surface-variant: '#5b403f'
  inverse-surface: '#313030'
  inverse-on-surface: '#f3f0ef'
  outline: '#8f6f6e'
  outline-variant: '#e4bebc'
  surface-tint: '#bb162c'
  primary: '#b7122a'
  on-primary: '#ffffff'
  primary-container: '#db313f'
  on-primary-container: '#fffbff'
  inverse-primary: '#ffb3b1'
  secondary: '#8e4e14'
  on-secondary: '#ffffff'
  secondary-container: '#ffab69'
  on-secondary-container: '#783d01'
  tertiary: '#625a5a'
  on-tertiary: '#ffffff'
  tertiary-container: '#7b7373'
  on-tertiary-container: '#fffbff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdad8'
  primary-fixed-dim: '#ffb3b1'
  on-primary-fixed: '#410007'
  on-primary-fixed-variant: '#92001c'
  secondary-fixed: '#ffdcc4'
  secondary-fixed-dim: '#ffb780'
  on-secondary-fixed: '#2f1400'
  on-secondary-fixed-variant: '#6f3800'
  tertiary-fixed: '#ebe0e0'
  tertiary-fixed-dim: '#cfc4c4'
  on-tertiary-fixed: '#201a1b'
  on-tertiary-fixed-variant: '#4c4545'
  background: '#fcf9f8'
  on-background: '#1b1b1b'
  surface-variant: '#e5e2e1'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 26px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 12px
  md: 16px
  lg: 24px
  xl: 32px
  gutter: 16px
  margin-mobile: 16px
  margin-desktop: 40px
---

## Brand & Style

The design system is centered on a "food-forward" philosophy, prioritizing high-quality imagery and clarity to facilitate effortless restaurant discovery. The aesthetic is **Corporate / Modern** with a lean towards minimalism, ensuring the AI-driven recommendations feel reliable and professional rather than experimental.

The target audience consists of urban professionals and food enthusiasts who value efficiency and trust. The UI evokes a sense of curated expertise through a disciplined use of whitespace, crisp typography, and a "Warm Minimalist" approach that balances clinical utility with the vibrant energy of the culinary world.

## Colors

The palette is anchored by a high-energy **Zomato Red** (#E23744), specifically reserved for critical action points and brand presence. This is balanced against a sophisticated off-white background to reduce eye strain during long browsing sessions.

- **Primary Accent:** Used for Primary CTAs, active navigation states, and ranking indicators.
- **Secondary Accent:** A **Warm Amber** (#F4A261) dedicated exclusively to social proof and star ratings to ensure semantic clarity.
- **AI Summary Banner:** A soft **Light Pink Tint** (#FEF2F2) provides a distinct but non-intrusive container for machine-generated insights, separating algorithmic content from user-generated data.
- **Neutral Scales:** Near-Black for maximum legibility on headings, and Cool Gray for metadata and secondary labels to maintain a clean visual hierarchy.

## Typography

This design system utilizes **Inter** for its systematic, utilitarian nature and exceptional legibility at small sizes. The hierarchy is established through weight rather than dramatic size shifts, utilizing **Semibold (600)** for all structural headings to convey authority.

- **Headlines:** Use tight letter-spacing (-0.02em) on larger sizes to maintain a "tucked" professional look.
- **Body Text:** Always uses **Regular (400)** weight to ensure maximum readability in long restaurant descriptions or reviews.
- **Labels:** Small labels and captions use **Medium (500)** or **Semibold (600)** to remain legible against varied image backgrounds or within dense data displays.

## Layout & Spacing

The design system employs a **Fluid Grid** model based on a 4px baseline rhythm. This ensures a mathematical harmony across all components.

- **Mobile:** 4-column layout with 16px side margins and 16px gutters.
- **Desktop:** 12-column layout with a maximum container width of 1200px.
- **Touch Targets:** A strict 44px minimum height is enforced for all interactive elements (buttons, list items, toggles) to meet accessibility standards.
- **Spacing Principle:** Use `md` (16px) for standard internal padding and `lg` (24px) to separate distinct sections of content.

## Elevation & Depth

Visual hierarchy is achieved through **Tonal Layers** and subtle **Ambient Shadows**. This design system avoids heavy gradients, preferring flat surfaces that appear to float slightly above the off-white background.

- **Default State:** Most cards use a subtle shadow: `0 1px 3px rgba(0,0,0,0.08)`.
- **Active/Hover State:** Elements should "lift" using a secondary shadow: `0 4px 12px rgba(0,0,0,0.12)`, creating a tactile response.
- **Borders:** Low-contrast 1px strokes (#E5E7EB) are used for secondary buttons and inactive input fields to maintain structure without adding visual noise.

## Shapes

The shape language balances friendliness with modern structure. 
- **Standard UI (Cards/Inputs):** Use a 12px (`rounded-lg`) corner radius to soften the interface while maintaining a professional grid.
- **Buttons:** Use a slightly tighter 8px (`rounded-md`) radius to indicate firmness and action.
- **Chips & Badges:** Utilize `rounded-full` (pill-shaped) geometry to distinguish them from interactive buttons and structural containers.

## Components

### Buttons
- **Primary:** Solid Primary Red (#E23744) with White text. 8px radius. Minimum 44px height.
- **Secondary:** Outline Cool Gray (#D1D5DB) with Text Secondary (#6B7280). 8px radius.
- **Icon Buttons:** Circular or 8px radius, used for "Favorite" (Heart) or "Share" actions.

### Cards
- **Restaurant Card:** White background, 12px radius, subtle shadow. Images should have a 0px top radius if they bleed to the edge, otherwise maintain 12px.
- **Hover Effect:** Apply a -4px Y-axis translation and enhanced shadow on desktop hover.

### Form Elements
- **Input Fields:** 8px radius, 1px Gray-200 border. Focused state uses 1px Primary Red border with a subtle 2px Red glow (10% opacity).
- **Checkboxes/Radios:** Primary Red for active states.

### Chips & Badges
- **Cuisine Chips:** Light Gray background with Text Secondary. `rounded-full`.
- **Rank Badge:** Solid Primary Red, white text, positioned in the top-left of restaurant cards.

### Icons
- Use consistent **Line-style icons** (2px stroke width).
- **AI Sparkles:** Reserved for the AI Summary Banner and "Smart Search" features.
- **Star Rating:** Always solid fill in Warm Amber (#F4A261).