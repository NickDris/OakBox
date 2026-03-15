# Front-End Development — Market Analysis App UI/UX Guide

## Application Identity

- **App name:** OakBox Market Analyzer
- **Purpose:** Real-time and historical market data analysis — equities, indices, forex, crypto
- **Primary users:** Retail traders, portfolio managers, financial analysts
- **Core value:** Dense, actionable data presented clearly without overwhelming the user

---

## Design System

### Theme

- **Mode:** Dark-first (default), with a light mode toggle
- **Dark palette:**

| Token                  | Value       | Usage                                  |
|------------------------|-------------|----------------------------------------|
| `--bg-primary`         | `#0d1117`   | App background                         |
| `--bg-surface`         | `#161b22`   | Cards, panels, sidebar                 |
| `--bg-elevated`        | `#21262d`   | Modals, dropdowns, tooltips            |
| `--border-default`     | `#30363d`   | Dividers, card borders                 |
| `--text-primary`       | `#e6edf3`   | Body text, headings                    |
| `--text-secondary`     | `#8b949e`   | Labels, captions, muted text           |
| `--text-placeholder`   | `#484f58`   | Input placeholders                     |
| `--accent-blue`        | `#58a6ff`   | Links, active tabs, primary actions    |
| `--accent-green`       | `#3fb950`   | Positive values, gains, buy signals    |
| `--accent-red`         | `#f85149`   | Negative values, losses, sell signals  |
| `--accent-yellow`      | `#d29922`   | Warnings, neutral/hold signals         |
| `--accent-purple`      | `#bc8cff`   | Volume highlights, secondary accents   |

- **Light palette:**

| Token                  | Value       | Usage                                  |
|------------------------|-------------|----------------------------------------|
| `--bg-primary`         | `#ffffff`   | App background                         |
| `--bg-surface`         | `#f6f8fa`   | Cards, panels, sidebar                 |
| `--bg-elevated`        | `#ffffff`   | Modals, dropdowns, tooltips            |
| `--border-default`     | `#d0d7de`   | Dividers, card borders                 |
| `--text-primary`       | `#1f2328`   | Body text, headings                    |
| `--text-secondary`     | `#656d76`   | Labels, captions, muted text           |
| `--text-placeholder`   | `#6e7781`   | Input placeholders                     |
| `--accent-blue`        | `#0969da`   | Links, active tabs, primary actions    |
| `--accent-green`       | `#1a7f37`   | Positive values, gains, buy signals    |
| `--accent-red`         | `#cf222e`   | Negative values, losses, sell signals  |
| `--accent-yellow`      | `#9a6700`   | Warnings, neutral/hold signals         |
| `--accent-purple`      | `#8250df`   | Volume highlights, secondary accents   |

Semantic color meanings are identical across themes (green = gain, red = loss).
Toggle between themes by swapping the CSS custom property values on `<html data-theme="dark|light">`.

### Typography

All font sizes use `rem` relative to the 16px root.

| Token             | Element          | Font           | Weight | Size        | Line height  |
|-------------------|------------------|----------------|--------|-------------|-------------|
| `--text-h1`       | H1 (page title)  | Inter          | 600    | `1.5rem`    | `2rem`      |
| `--text-h2`       | H2 (section)     | Inter          | 600    | `1.125rem`  | `1.5rem`    |
| `--text-h3`       | H3 (card title)  | Inter          | 500    | `0.9375rem` | `1.25rem`   |
| `--text-body`     | Body             | Inter          | 400    | `0.875rem`  | `1.25rem`   |
| `--text-caption`  | Caption          | Inter          | 400    | `0.75rem`   | `1rem`      |
| `--text-numeric`  | Numeric data     | JetBrains Mono | 400    | `0.8125rem` | `1.125rem`  |
| `--text-ticker`   | Ticker symbol    | JetBrains Mono | 600    | `0.875rem`  | `1.25rem`   |

- All numeric/financial data uses a **monospace font** so columns align.
- Positive deltas render in `--accent-green` with a `▲` prefix.
- Negative deltas render in `--accent-red` with a `▼` prefix.
- Zero/unchanged renders in `--text-secondary` with a `—` prefix.

### Spacing & Grid

All spacing uses `rem` units anchored to a `1rem = 16px` root. Never use raw `px`
for spacing, padding, margins, gaps, or gutter values. This ensures the entire
UI scales uniformly when the user adjusts browser font size or when a responsive
multiplier is applied.

- **Root font-size:** `16px` (`1rem`). Set on `<html>` element. Never override.
- **Base unit:** `0.25rem` (4px equivalent)

**Spacing tokens (CSS custom properties):**

| Token           | Value       | px equiv | Usage                                    |
|-----------------|-------------|----------|------------------------------------------|
| `--space-1`     | `0.25rem`   | 4        | Inline icon gaps, tight padding          |
| `--space-2`     | `0.5rem`    | 8        | Compact element padding, chip gaps       |
| `--space-3`     | `0.75rem`   | 12       | Input padding, small card padding        |
| `--space-4`     | `1rem`      | 16       | Default card padding, grid gutters       |
| `--space-6`     | `1.5rem`    | 24       | Section gaps, card margins               |
| `--space-8`     | `2rem`      | 32       | Page section separation                  |
| `--space-12`    | `3rem`      | 48       | Major layout gaps                        |
| `--space-16`    | `4rem`      | 64       | Page-level top/bottom padding            |

Rules:
- Always reference tokens (`var(--space-4)`), never raw `rem` or `px` values.
- Compose via `calc()` only when a token does not exist (e.g. `calc(var(--space-4) + var(--space-1))`).
- The scale is intentionally non-linear. Do not invent intermediate values.

**Layout grid:**

| Property     | Value            |
|--------------|------------------|
| Type         | CSS Grid         |
| Columns      | breakpoint-dependent (see below) |
| Gutter       | `var(--space-4)` (1rem) |
| Page margin  | `var(--space-6)` (1.5rem) on mobile, `var(--space-8)` (2rem) on desktop |
| Max width    | `90rem` (1440px equiv), centered |

**Breakpoints:**

| Name     | Min width  | Columns | Sidebar     | Page margin        |
|----------|------------|---------|-------------|--------------------|
| `mobile` | 0          | 4       | hidden      | `var(--space-4)`   |
| `tablet` | `48rem`    | 8       | collapsed   | `var(--space-6)`   |
| `desktop`| `80rem`    | 12      | visible     | `var(--space-8)`   |
| `wide`   | `100rem`   | 12      | expanded    | `var(--space-8)`   |

Breakpoints use `rem` so they respect the user's root font-size preference.

**Component-specific spacing:**

| Context                  | Padding               | Gap between children    |
|--------------------------|-----------------------|-------------------------|
| Card (default)           | `var(--space-4)`      | `var(--space-3)`        |
| Card (compact / table)   | `var(--space-3)`      | `var(--space-2)`        |
| Modal                    | `var(--space-6)`      | `var(--space-4)`        |
| TopBar                   | `0 var(--space-4)`    | `var(--space-3)`        |
| Sidebar (expanded)       | `var(--space-3)`      | `var(--space-1)`        |
| StatusBar                | `0 var(--space-4)`    | `var(--space-4)`        |
| Form fields (label→input)| —                     | `var(--space-2)`        |
| Button padding           | `var(--space-2) var(--space-4)` | —             |

### Elevation & Borders

- No box-shadows in dark mode. Use `1px solid var(--border-default)` for separation.
- Light mode may use subtle shadows: `0 0.0625rem 0.1875rem rgba(0,0,0,0.12)`.
- Border radius tokens:

| Token              | Value        | Usage                     |
|--------------------|-------------|---------------------------|
| `--radius-sm`      | `0.125rem`  | Tags, badges              |
| `--radius-md`      | `0.25rem`   | Inputs, buttons           |
| `--radius-lg`      | `0.375rem`  | Cards, panels             |
| `--radius-full`    | `9999px`    | Avatars, pills            |

---

## Application Shell

```
┌─────────────────────────────────────────────────────────────────────┐
│  TopBar  [Logo]  [Search: ticker/company]    [Alerts 🔔]  [User]  │
├──────────┬──────────────────────────────────────────────────────────┤
│          │  BreadcrumbBar / Tab Navigation                         │
│ Sidebar  ├──────────────────────────────────────────────────────────┤
│          │                                                         │
│ • Dashboard  │              Main Content Area                      │
│ • Watchlist  │     (routed views rendered here)                    │
│ • Screener   │                                                     │
│ • Portfolio  │                                                     │
│ • Analysis   │                                                     │
│ • Political  │                                                     │
│ • Alerts     │                                                     │
│ • Settings   │                                                     │
│          │                                                         │
├──────────┴──────────────────────────────────────────────────────────┤
│  StatusBar  [Market status: Open/Closed]  [Last updated: HH:MM]   │
└─────────────────────────────────────────────────────────────────────┘
```

### TopBar

- Fixed at top, height `3rem`.
- **Search** (center): Combo search for ticker symbols and company names. Autocomplete dropdown with symbol, name, exchange, and asset type. Keyboard shortcut: `/`.
- **Alerts** (right): Bell icon with unread count badge.
- **User** (right): Avatar + dropdown (profile, preferences, sign out).

### Sidebar

- Fixed left, width `13.75rem` (desktop) or icon-only `3.5rem` (collapsed).
- Navigation items: icon + label. Active item uses `--accent-blue` left border (`3px`) + background tint at 10% opacity.
- Collapse toggle at the bottom of the sidebar.
- **Mobile:** sidebar is hidden. Replaced by a bottom tab bar (see Responsive Behavior).

### StatusBar

- Fixed at bottom, height `1.75rem`.
- Shows: market open/close status, last data refresh timestamp, connection indicator.

---

## Page Layouts & Wireframes

### 1. Dashboard

The default landing page. Dense overview of the user's most important data.

```
┌──────────────────────────────────────────────────────────────┐
│  Market Summary Bar                                          │
│  [S&P 500 ▲0.42%] [NASDAQ ▲0.67%] [DOW ▼0.11%] [VIX 14.2] │
├──────────────────────┬───────────────────────────────────────┤
│  Watchlist (card)    │   Portfolio Performance (card)        │
│  ┌────┬──────┬─────┐ │   ┌─────────────────────────────┐    │
│  │Tick│Price │Chg% │ │   │  Area chart: total value     │    │
│  │AAPL│189.2 │▲1.2%│ │   │  over selected time range    │    │
│  │MSFT│378.9 │▼0.3%│ │   │  [1D] [1W] [1M] [3M] [1Y]   │    │
│  │GOOG│141.5 │▲0.8%│ │   └─────────────────────────────┘    │
│  └────┴──────┴─────┘ │   Total: $124,502  |  Day: ▲$1,204   │
├──────────────────────┼───────────────────────────────────────┤
│  Top Movers (card)   │   Recent Alerts (card)                │
│  Gainers | Losers    │   • AAPL crossed above 50-day MA      │
│  ┌────┬──────┬─────┐ │   • Portfolio up 5% this week         │
│  │NVDA│▲ 4.2%│$875 │ │   • TSLA RSI above 70 (overbought)   │
│  │AMD │▲ 3.1%│$162 │ │                                       │
│  └────┴──────┴─────┘ │                                       │
└──────────────────────┴───────────────────────────────────────┘
```

- **Market Summary Bar:** Horizontal scrollable strip of major indices. Always visible.
- **Watchlist card:** Compact table, sortable by column, click row → navigate to ticker detail.
- **Portfolio Performance card:** Area/line chart with time-range selector buttons.
- **Top Movers card:** Toggle between gainers/losers tab. Top 5 each.
- **Recent Alerts card:** Chronological list of triggered alerts, click → alert detail.

### 2. Ticker Detail (`/ticker/:symbol`)

Deep-dive view for a single security.

```
┌──────────────────────────────────────────────────────────────┐
│  AAPL — Apple Inc.         $189.24  ▲$2.31 (+1.24%)         │
│  Exchange: NASDAQ  |  Sector: Technology  |  Mkt Cap: $2.9T │
├──────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────┐  │
│  │              Interactive Candlestick Chart             │  │
│  │  [1D] [1W] [1M] [3M] [6M] [1Y] [5Y] [Max]           │  │
│  │  Overlays: [SMA] [EMA] [Bollinger]  |  [Volume on/off]│  │
│  │                                                        │  │
│  │  ████████                                              │  │
│  │  █      █   ██                                         │  │
│  │  █  ██  █  █  █  ████                                  │  │
│  │  ████████  █  █  █  █                                  │  │
│  │            ████  ████                                  │  │
│  │  ▁▃▅▇▅▃▁▂▄▆▄▂ (volume bars)                           │  │
│  └────────────────────────────────────────────────────────┘  │
├────────────────────┬─────────────────────────────────────────┤
│  Key Stats (card)  │  Technical Indicators (card)            │
│  Open:    $187.10  │  RSI (14):     62.4                     │
│  High:    $190.05  │  MACD:         ▲ Bullish crossover      │
│  Low:     $186.80  │  50-day MA:    $182.50                  │
│  Volume:  48.2M    │  200-day MA:   $175.30                  │
│  Avg Vol: 52.1M    │  ATR (14):     3.21                     │
│  P/E:     29.8     │  52W High:     $199.62                  │
│  EPS:     $6.35    │  52W Low:      $143.90                  │
├────────────────────┴─────────────────────────────────────────┤
│  News & Sentiment (card)                                     │
│  [▓▓▓▓▓▓▓░░░] 72% Bullish  (based on 48 articles, 7 days)  │
│  • "Apple Vision Pro sales exceed expectations" — Reuters    │
│  • "iPhone 17 supply chain ramp-up confirmed" — Bloomberg    │
└──────────────────────────────────────────────────────────────┘
```

- **Header:** Symbol, full name, current price, daily change (color-coded), metadata.
- **Chart:** Candlestick by default. Overlay toggles for moving averages, Bollinger bands. Volume sub-chart below. Time-range selector as pill buttons.
- **Key Stats:** Two-column key-value layout. Numbers right-aligned, monospace.
- **Technical Indicators:** Signal labels color-coded (green=bullish, red=bearish, yellow=neutral).
- **News & Sentiment:** Sentiment bar + scrollable headline list. Each links to source.

### 3. Screener (`/screener`)

Filter and discover securities by criteria.

```
┌──────────────────────────────────────────────────────────────┐
│  Screener                                        [Save] [Reset] │
├──────────────────────────────────────────────────────────────┤
│  Filters (collapsible panel)                                 │
│  [Market Cap ▼] [Sector ▼] [P/E Range ▼] [Volume ▼]        │
│  [RSI Range ▼]  [52W % ▼]  [Dividend ▼]  [+ Add Filter]    │
├──────────────────────────────────────────────────────────────┤
│  Results: 142 matches                     [Sort: Mkt Cap ▼] │
│  ┌──────┬──────────────┬─────────┬───────┬───────┬────────┐ │
│  │ Tick │ Name         │ Price   │ Chg%  │ MktCp │ P/E    │ │
│  ├──────┼──────────────┼─────────┼───────┼───────┼────────┤ │
│  │ AAPL │ Apple Inc.   │ $189.24 │ ▲1.2% │ 2.9T  │ 29.8   │ │
│  │ MSFT │ Microsoft    │ $378.91 │ ▼0.3% │ 2.8T  │ 34.2   │ │
│  │ GOOG │ Alphabet     │ $141.50 │ ▲0.8% │ 1.8T  │ 24.1   │ │
│  │ ...  │              │         │       │       │        │ │
│  └──────┴──────────────┴─────────┴───────┴───────┴────────┘ │
│  [◀ Prev]  Page 1 of 8  [Next ▶]                            │
└──────────────────────────────────────────────────────────────┘
```

- Filters use **dropdown chips** that expand into range sliders or multi-select lists.
- Results table is sortable by any column (click header). Sticky header on scroll.
- Click any row → navigates to ticker detail.
- **Save** persists the current filter set as a named screen.

### 4. Portfolio (`/portfolio`)

```
┌──────────────────────────────────────────────────────────────┐
│  Portfolio Overview                                          │
│  Total Value: $124,502.18    Day: ▲$1,204 (+0.97%)          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Area chart — portfolio value over time                │  │
│  │  [1D] [1W] [1M] [3M] [YTD] [1Y] [All]                │  │
│  └────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────┬───────────────────────┤
│  Holdings Table                      │  Allocation (donut)  │
│  ┌──────┬────┬────────┬───────┬────┐ │  ┌──────────────┐    │
│  │ Tick │ Qty│ Value  │ Gain  │ %  │ │  │   ◉ Tech 48% │    │
│  │ AAPL │ 50 │$9,462  │▲$812 │+9% │ │  │  Health 22%  │    │
│  │ MSFT │ 25 │$9,473  │▲$1.1k│+13%│ │  │  Finance 18% │    │
│  │ VTI  │120 │$28,440 │▲$3.2k│+13%│ │  │  Other 12%   │    │
│  └──────┴────┴────────┴───────┴────┘ │  └──────────────┘    │
└──────────────────────────────────────┴───────────────────────┘
```

- **Donut chart:** Sector allocation breakdown. Hover segment → tooltip with exact %.
- **Holdings table:** Sortable. Inline sparkline optional for each ticker.
- Gain/loss columns color-coded.

### 5. Analysis (`/analysis/:symbol`)

Technical and fundamental analysis workspace.

```
┌──────────────────────────────────────────────────────────────┐
│  Analysis: AAPL         [Technical] [Fundamental] [Compare]  │
├──────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────┐  │
│  │  Full-width chart with drawing tools sidebar           │  │
│  │  Tools: [Line] [Fib] [Trendline] [Rect] [Text]       │  │
│  │  Indicators panel (add/remove):                        │  │
│  │    ✓ RSI  ✓ MACD  ☐ Stochastic  ☐ OBV  ☐ ADX        │  │
│  └────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────┤
│  Signal Summary                                              │
│  ┌───────────┬───────────┬───────────┐                       │
│  │  SHORT    │  MEDIUM   │  LONG     │                       │
│  │  ▲ Buy    │  — Hold   │  ▲ Buy    │                       │
│  │  (3 of 5) │  (2 of 5) │  (4 of 5) │                       │
│  └───────────┴───────────┴───────────┘                       │
└──────────────────────────────────────────────────────────────┘
```

- Tab navigation for Technical / Fundamental / Compare views.
- **Compare mode:** overlay up to 4 tickers on the same normalized chart (percentage-based Y axis).

#### Fundamental Tab (`/analysis/:symbol?tab=fundamental`)

```
┌──────────────────────────────────────────────────────────────┐
│  Financials          [Annual] [Quarterly]                    │
│  ┌───────────────┬──────────┬──────────┬──────────┐         │
│  │ Metric        │ 2025     │ 2024     │ 2023     │         │
│  ├───────────────┼──────────┼──────────┼──────────┤         │
│  │ Revenue       │ $394.3B  │ $383.3B  │ $383.0B  │         │
│  │ Net Income    │ $101.2B  │ $97.0B   │ $97.0B   │         │
│  │ EPS           │ $6.75    │ $6.35    │ $6.13    │         │
│  │ Gross Margin  │ 46.2%    │ 45.6%    │ 44.1%    │         │
│  │ Debt/Equity   │ 1.51     │ 1.79     │ 1.99     │         │
│  └───────────────┴──────────┴──────────┴──────────┘         │
├──────────────────────────────────────────────────────────────┤
│  Valuation Metrics                                           │
│  ┌────────────┬────────────┬──────────────────────┐         │
│  │ P/E        │ 29.8       │ Sector avg: 25.4     │         │
│  │ P/S        │ 7.6        │ Sector avg: 5.2      │         │
│  │ P/B        │ 48.2       │ Sector avg: 8.7      │         │
│  │ PEG        │ 2.1        │                      │         │
│  │ EV/EBITDA  │ 22.3       │ Sector avg: 18.9     │         │
│  └────────────┴────────────┴──────────────────────┘         │
├──────────────────────────────────────────────────────────────┤
│  Dividends                                                   │
│  Yield: 0.56%  |  Annual: $1.00  |  Payout Ratio: 15.7%    │
│  Ex-Date: Feb 7, 2026  |  Frequency: Quarterly              │
└──────────────────────────────────────────────────────────────┘
```

- **Financials table:** Toggle between Annual (last 3 years) and Quarterly (last 4 quarters). Right-aligned numeric cells.
- **Valuation Metrics:** Compare the ticker's multiples against sector averages. Highlight when significantly above (red text) or below (green text) sector average.
- **Dividends:** Single row of key-value stats. Show "N/A" if the security pays no dividend.

### 6. Alerts (`/alerts`)

```
┌──────────────────────────────────────────────────────────────┐
│  Alerts                                    [+ Create Alert]  │
├──────────────────────────────────────────────────────────────┤
│  Active Alerts (list)                                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ ● AAPL — Price above $195.00          [Edit] [Delete] │  │
│  │ ● TSLA — RSI crosses above 70         [Edit] [Delete] │  │
│  │ ● Portfolio — Daily loss exceeds 2%   [Edit] [Delete] │  │
│  └────────────────────────────────────────────────────────┘  │
├──────────────────────────────────────────────────────────────┤
│  Alert History (collapsible)                                 │
│  │ ✓ AAPL crossed 50-day MA — triggered Mar 12, 09:42 AM │  │
│  │ ✓ NVDA price above $850 — triggered Mar 11, 02:15 PM  │  │
└──────────────────────────────────────────────────────────────┘
```

- **Create Alert modal:** Ticker selector → condition type (price, indicator, portfolio) → threshold → notification channel (in-app, email).
- Active alerts show a colored dot: green = active, yellow = paused, gray = expired.

### 7. Settings (`/settings`)

```
┌──────────────────────────────────────────────────────────────┐
│  Settings                                                    │
├──────────────────────────────────────────────────────────────┤
│  Appearance                                                  │
│  Theme:          [Dark ▼]                                    │
│  Default page:   [Dashboard ▼]                               │
├──────────────────────────────────────────────────────────────┤
│  Market Data                                                 │
│  Default exchange:   [All ▼]                                 │
│  Refresh interval:   [15s ▼]  (market hours only)            │
│  Currency display:   [USD ▼]                                 │
├──────────────────────────────────────────────────────────────┤
│  Notifications                                               │
│  In-app alerts:   [On]                                       │
│  Email alerts:    [Off]     Email: [user@example.com]        │
├──────────────────────────────────────────────────────────────┤
│  Account                                                     │
│  Display name:    [____________]                             │
│  [Save Changes]                              [Delete Account]│
└──────────────────────────────────────────────────────────────┘
```

- Grouped into sections with clear headings.
- All changes require an explicit **Save** action (no auto-save) except theme toggle which applies immediately.
- **Delete Account** uses a `Button` (Danger variant) with a confirmation modal.

---

## Shared Component Library

Agents must use these components consistently. No one-off variants.

### Data Display

| Component           | Usage                                              |
|---------------------|----------------------------------------------------|
| `PriceDisplay`      | Formatted price with currency symbol, delta color  |
| `ChangeIndicator`   | `▲ +1.24%` or `▼ -0.83%` with semantic color      |
| `TickerChip`        | Inline badge: `[AAPL]` — clickable, links to detail|
| `DataTable`         | Sortable, paginated table with sticky header       |
| `Sparkline`         | Inline mini line chart (no axes) for table cells   |
| `StatCard`          | Label + large value + optional delta subtitle      |
| `SentimentBar`      | Horizontal bar: green/red proportional fill         |

### Charts

| Component           | Library          | Usage                             |
|---------------------|------------------|-----------------------------------|
| `CandlestickChart`  | Lightweight Charts (TradingView) | Ticker detail, analysis |
| `AreaChart`         | Recharts          | Portfolio value over time          |
| `DonutChart`        | Recharts          | Allocation breakdowns              |
| `BarChart`          | Recharts          | Volume, screener distributions     |
| `Sparkline`         | Custom SVG        | Inline table mini-charts           |

- **Charting libraries:** Use [Lightweight Charts](https://github.com/niceDev0908/lightweight-charts) (`lightweight-charts` npm package) for financial candlestick/OHLC charts. Use [Recharts](https://recharts.org/) (`recharts` npm package) for everything else (area, bar, donut, line).
- All charts must include a loading skeleton and an empty state.
- Charts must be responsive — resize on container change via `ResizeObserver`.

### Inputs & Actions

| Component           | Usage                                              |
|---------------------|----------------------------------------------------|
| `TickerSearch`      | Autocomplete combo input for symbol/company search |
| `TimeRangeSelector` | Pill button group: `1D 1W 1M 3M 6M 1Y 5Y Max`    |
| `FilterChip`        | Dropdown chip for screener filters                 |
| `Button`            | Primary (blue fill), Secondary (outline), Danger (red) |
| `IconButton`        | Toolbar and card actions                           |
| `Modal`             | Alert creation, settings, confirmations            |
| `Tooltip`           | Data point hover details, truncated text           |

### Feedback

| Component           | Usage                                              |
|---------------------|----------------------------------------------------|
| `Skeleton`          | Placeholder shimmer while data loads               |
| `EmptyState`        | Illustration + message when no data exists         |
| `ErrorBanner`       | Inline red banner for API/connection failures      |
| `Toast`             | Transient success/error notifications (bottom-right) |

---

## Interaction Patterns

### Data Loading

- Show `Skeleton` placeholders immediately — never a blank screen.
- Stale data stays visible while fresh data loads (stale-while-revalidate via React Query).
- If a request fails, show `ErrorBanner` with a "Retry" button. Keep stale data visible.
- Auto-refresh intervals: market data every 15s (when market is open), portfolio every 60s.

### Navigation

- **Routing:** React Router v6 with lazy-loaded route components.
- Sidebar selection updates URL. Browser back/forward must work.
- Ticker detail opens via row click in any table — consistent across all pages.

### Keyboard Shortcuts

| Shortcut    | Action                       |
|-------------|------------------------------|
| `/`         | Focus search bar             |
| `Esc`       | Close modal / blur search    |
| `j` / `k`   | Navigate table rows (vim-style) |
| `Enter`     | Open selected row            |
| `?`         | Show shortcut reference      |

### Responsive Behavior

- **Mobile (< 768px):** Single column. Sidebar replaced by bottom tab bar (5 items max). Charts shrink but remain interactive. Tables switch to card-list layout.
- **Tablet (768–1279px):** Two-column grid. Sidebar collapsed to icons.
- **Desktop (≥ 1280px):** Full layout as wireframed.

---

## Feature Module Structure

Each page maps to a feature module under `src/frontend/features/`:

```
src/frontend/features/
  dashboard/
    components/
      MarketSummaryBar.tsx
      WatchlistCard.tsx
      PortfolioSummaryCard.tsx
      TopMoversCard.tsx
      RecentAlertsCard.tsx
    hooks/
      useMarketSummary.ts
      useWatchlist.ts
    api.ts
    types.ts
    index.ts                    # Route-level component
  ticker-detail/
    components/
      TickerHeader.tsx
      PriceChart.tsx
      KeyStats.tsx
      TechnicalIndicators.tsx
      NewsSentiment.tsx
    hooks/
      useTickerData.ts
      useTechnicalIndicators.ts
    api.ts
    types.ts
    index.ts
  screener/
    components/
      FilterPanel.tsx
      ResultsTable.tsx
    hooks/
      useScreener.ts
    api.ts
    types.ts
    index.ts
  portfolio/
    components/
      PortfolioChart.tsx
      HoldingsTable.tsx
      AllocationDonut.tsx
    hooks/
      usePortfolio.ts
    api.ts
    types.ts
    index.ts
  analysis/
    components/
      AnalysisChart.tsx
      DrawingToolbar.tsx
      SignalSummary.tsx
      CompareView.tsx
    hooks/
      useAnalysis.ts
    api.ts
    types.ts
    index.ts
  alerts/
    components/
      AlertList.tsx
      AlertForm.tsx
      AlertHistory.tsx
    hooks/
      useAlerts.ts
    api.ts
    types.ts
    index.ts
  political/                       # See political-trades-analysis.md for full spec
    components/
      PoliticalDashboardPage.tsx
      PersonCard.tsx
      PersonsTable.tsx
      PersonDetailHeader.tsx
      PersonTradeHistory.tsx
      PersonPerformanceCards.tsx
      TradeFeed.tsx
      TradeRow.tsx
      SignalRankingsTable.tsx
      SignalBadge.tsx
      ClusterScoreBar.tsx
      SentimentGauge.tsx
      PartyBadge.tsx
      CommitteeTag.tsx
      FilingSourceLink.tsx
      DisclaimerFooter.tsx
    hooks/
      usePoliticalDashboard.ts
      usePoliticalPersons.ts
      usePoliticalPerson.ts
      usePoliticalTrades.ts
      usePoliticalSignals.ts
      useTickerPoliticalSignal.ts
    api.ts
    types.ts
    index.ts
  settings/
    components/
      AppearanceSection.tsx
      MarketDataSection.tsx
      NotificationsSection.tsx
      AccountSection.tsx
    hooks/
      useSettings.ts
    api.ts
    types.ts
    index.ts
```

---

## Data Types (API Contract Shapes)

These types define the frontend's expectations from the backend API. Backend
schemas must match.

```typescript
interface Ticker {
  symbol: string;          // e.g. "AAPL"
  name: string;            // e.g. "Apple Inc."
  exchange: string;        // e.g. "NASDAQ"
  assetType: 'equity' | 'etf' | 'crypto' | 'forex' | 'index';
}

interface Quote {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  open: number;
  high: number;
  low: number;
  volume: number;
  avgVolume: number;
  marketCap: number;
  pe: number | null;
  eps: number | null;
  week52High: number;
  week52Low: number;
  timestamp: string;       // ISO 8601
}

interface OHLC {
  time: string;            // ISO 8601 date
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface PortfolioHolding {
  symbol: string;
  name: string;
  quantity: number;
  avgCost: number;
  currentPrice: number;
  marketValue: number;
  gainLoss: number;
  gainLossPercent: number;
  sector: string;
}

interface Alert {
  id: string;
  symbol: string | null;   // null for portfolio-level alerts
  conditionType: 'price_above' | 'price_below' | 'rsi_above' | 'rsi_below' | 'portfolio_loss';
  threshold: number;
  status: 'active' | 'paused' | 'triggered' | 'expired';
  createdAt: string;
  triggeredAt: string | null;
}

interface ScreenerFilter {
  field: string;            // e.g. "marketCap", "pe", "rsi"
  operator: 'gt' | 'lt' | 'between' | 'eq' | 'in';
  value: number | number[] | string[];
}

interface MarketSummary {
  indices: {
    symbol: string;        // e.g. "SPX", "IXIC", "DJI"
    name: string;          // e.g. "S&P 500"
    value: number;
    change: number;
    changePercent: number;
  }[];
  marketStatus: 'pre_market' | 'open' | 'after_hours' | 'closed';
  lastUpdated: string;     // ISO 8601
}

interface Mover {
  symbol: string;
  name: string;
  price: number;
  changePercent: number;
  volume: number;
  direction: 'gainer' | 'loser';
}

interface Technicals {
  symbol: string;
  rsi14: number | null;
  macd: { value: number; signal: number; histogram: number } | null;
  sma50: number | null;
  sma200: number | null;
  ema12: number | null;
  ema26: number | null;
  bollingerUpper: number | null;
  bollingerLower: number | null;
  atr14: number | null;
  stochastic: { k: number; d: number } | null;
  obv: number | null;
  adx: number | null;
}

interface Fundamentals {
  symbol: string;
  financials: {
    period: string;        // e.g. "2025", "Q1 2026"
    revenue: number | null;
    netIncome: number | null;
    eps: number | null;
    grossMargin: number | null;
    debtToEquity: number | null;
  }[];
  valuation: {
    pe: number | null;
    ps: number | null;
    pb: number | null;
    peg: number | null;
    evToEbitda: number | null;
    sectorAvgPe: number | null;
    sectorAvgPs: number | null;
    sectorAvgPb: number | null;
    sectorAvgEvToEbitda: number | null;
  };
  dividend: {
    yield: number | null;
    annualAmount: number | null;
    payoutRatio: number | null;
    exDate: string | null;
    frequency: 'quarterly' | 'semi-annual' | 'annual' | null;
  };
}

interface NewsItem {
  id: string;
  title: string;
  source: string;
  url: string;
  publishedAt: string;     // ISO 8601
  sentiment: 'bullish' | 'bearish' | 'neutral';
}

interface UserSettings {
  theme: 'dark' | 'light';
  defaultPage: 'dashboard' | 'screener' | 'portfolio';
  defaultExchange: string | null;  // null = all
  refreshIntervalSec: number;
  currencyDisplay: string;         // ISO 4217 code, e.g. "USD"
  inAppAlerts: boolean;
  emailAlerts: boolean;
  alertEmail: string | null;
  displayName: string;
}

interface Portfolio {
  totalValue: number;
  dayChange: number;
  dayChangePercent: number;
  totalGainLoss: number;
  totalGainLossPercent: number;
}
```

---

## Accessibility Requirements

- WCAG 2.1 AA compliance minimum.
- Color is never the sole indicator — always pair with icons or text (▲/▼ for gain/loss).
- All charts must have an `aria-label` describing the data trend.
- Tables must use `<th scope="col">` and `<th scope="row">` correctly.
- Focus management: modals trap focus; closing returns to trigger element.
- Screen reader announcements for live data updates (`aria-live="polite"` on price feeds).

---

## Performance Targets

| Metric                  | Target    |
|-------------------------|-----------|
| First Contentful Paint  | < 1.2s    |
| Largest Contentful Paint| < 2.5s    |
| Time to Interactive     | < 3.5s    |
| Cumulative Layout Shift | < 0.1     |
| Bundle size (gzipped)   | < 250 KB  |
| Chart render (1Y data)  | < 200ms   |

- Lazy-load route components and chart libraries.
- Virtualize tables with > 50 rows (use `@tanstack/react-virtual`).
- Debounce search input (300ms).
- Throttle chart crosshair/tooltip updates (16ms / 60fps).

---

## Number & Currency Formatting

All numeric formatting must use a shared `formatNumber` utility. Never format
numbers with ad-hoc string interpolation.

| Data type        | Format                       | Example               |
|------------------|------------------------------|-----------------------|
| Price (< $1)     | 4 decimal places             | `$0.0034`             |
| Price (≥ $1)     | 2 decimal places             | `$189.24`             |
| Percentage       | 2 decimal places + `%`       | `+1.24%`, `-0.83%`   |
| Large numbers    | Abbreviated with suffix      | `$2.9T`, `48.2M`     |
| Volume           | Abbreviated, no decimals     | `48M`, `1.2B`         |
| Ratios (P/E etc) | 1 decimal place              | `29.8`, `1.5`         |
| EPS              | 2 decimal places             | `$6.35`               |

**Abbreviation thresholds:**

| Threshold    | Suffix | Example        |
|-------------|--------|----------------|
| ≥ 1,000,000,000,000 | `T` | `$2.9T` |
| ≥ 1,000,000,000     | `B` | `$1.2B` |
| ≥ 1,000,000         | `M` | `$48.2M`|
| ≥ 1,000             | `K` | `$4.5K` |
| < 1,000             | —   | `$892`  |

- Always prefix prices with `$` (USD assumed unless Settings overrides).
- Positive deltas always show `+` prefix: `+1.24%`, `+$2.31`.
- Negative deltas use `−` (minus sign): `−0.83%`, `−$1.50`.
- Use `Intl.NumberFormat` under the hood with `en-US` locale as default.
- `null` / missing values render as `—` (em dash) in `--text-secondary` color.

---

## API Endpoint Conventions

The frontend consumes a REST API. These are the expected endpoint shapes. The
backend (Python/FastAPI) must implement matching routes.

| Method | Path                                 | Purpose                      | Response type       |
|--------|--------------------------------------|------------------------------|---------------------|
| GET    | `/api/v1/tickers/search?q=<query>`   | Autocomplete ticker search   | `Ticker[]`          |
| GET    | `/api/v1/tickers/:symbol/quote`      | Current quote for a symbol   | `Quote`             |
| GET    | `/api/v1/tickers/:symbol/history`    | OHLC history                 | `OHLC[]`            |
|        | `?range=1d|1w|1m|3m|6m|1y|5y|max`   |                              |                     |
| GET    | `/api/v1/tickers/:symbol/technicals` | Technical indicators         | `Technicals`        |
| GET    | `/api/v1/tickers/:symbol/fundamentals`| Fundamental data            | `Fundamentals`      |
| GET    | `/api/v1/tickers/:symbol/news`       | News + sentiment             | `NewsItem[]`        |
| GET    | `/api/v1/market/summary`             | Major indices overview        | `MarketSummary`     |
| GET    | `/api/v1/market/movers`              | Top gainers/losers            | `Mover[]`           |
| GET    | `/api/v1/screener`                   | Filtered screener results     | `{ results: Quote[], total: number }` |
|        | `?filters=<JSON>&sort=<field>&order=asc|desc&page=<n>&limit=<n>` | |                  |
| GET    | `/api/v1/portfolio`                  | User portfolio overview       | `Portfolio`         |
| GET    | `/api/v1/portfolio/holdings`         | Holdings list                 | `PortfolioHolding[]`|
| GET    | `/api/v1/portfolio/history`          | Portfolio value history       | `{ time: string, value: number }[]` |
| GET    | `/api/v1/alerts`                     | User's alerts                 | `Alert[]`           |
| POST   | `/api/v1/alerts`                     | Create alert                  | `Alert`             |
| PATCH  | `/api/v1/alerts/:id`                 | Update alert                  | `Alert`             |
| DELETE | `/api/v1/alerts/:id`                 | Delete alert                  | `204 No Content`    |
| GET    | `/api/v1/user/settings`              | User preferences              | `UserSettings`      |
| PATCH  | `/api/v1/user/settings`              | Update preferences            | `UserSettings`      |

**Conventions:**
- All responses are JSON with `Content-Type: application/json`.
- Error responses use `{ "error": string, "detail": string | null }` shape.
- HTTP status codes: `200` success, `201` created, `204` no content, `400` bad request, `401` unauthorized, `404` not found, `422` validation error, `500` server error.
- Paginated endpoints return `{ results: T[], total: number, page: number, limit: number }`.

---

## Error, Empty, and Edge States

Every page and card must handle three non-happy states. Never leave these
undefined — an agent implementing a component must include all three.

### Per-component states

| State       | Display                                                   |
|-------------|-----------------------------------------------------------|
| **Loading** | `Skeleton` placeholder matching the component's layout    |
| **Empty**   | `EmptyState` with illustration, message, and CTA          |
| **Error**   | `ErrorBanner` with error message and "Retry" button       |

### Page-specific empty/zero-data messages

| Page / Card             | Empty state message                                  | CTA button          |
|-------------------------|------------------------------------------------------|---------------------|
| Dashboard → Watchlist   | "No tickers in your watchlist yet."                  | "Add tickers"       |
| Dashboard → Portfolio   | "You haven't added any holdings."                    | "Create portfolio"  |
| Dashboard → Alerts      | "No alerts have triggered recently."                 | —                   |
| Screener → Results      | "No securities match your filters."                  | "Reset filters"     |
| Portfolio → Holdings    | "Your portfolio is empty."                           | "Add a holding"     |
| Alerts → Active         | "You have no active alerts."                         | "Create alert"      |
| Alerts → History        | "No alert history yet."                              | —                   |
| Ticker → News           | "No recent news for this ticker."                    | —                   |
| Analysis → Fundamental  | "Fundamental data unavailable for this security."    | —                   |

### Network / connection states

| State                    | Display                                               |
|--------------------------|-------------------------------------------------------|
| Offline                  | StatusBar turns `--accent-yellow`, shows "Offline — displaying cached data" |
| WebSocket disconnected   | StatusBar connection indicator turns red, auto-reconnect with exponential backoff |
| API rate limited (429)   | `Toast` warning: "Data refresh paused. Retrying in Xs." |

---

## Responsive Behavior — Mobile Bottom Tab Bar

The sidebar lists 7 navigation items, but mobile allows a maximum of 5 tabs.

**Bottom tab bar items (mobile only):**

| Position | Icon     | Label      | Route         |
|----------|----------|------------|---------------|
| 1        | Grid     | Dashboard  | `/`           |
| 2        | Search   | Screener   | `/screener`   |
| 3        | Briefcase| Portfolio  | `/portfolio`  |
| 4        | Bell     | Alerts     | `/alerts`     |
| 5        | Menu     | More       | (drawer)      |

The **More** tab opens a half-sheet drawer containing links to: Watchlist, Analysis, Political, Settings.

- Active tab uses `--accent-blue` icon + label color.
- Inactive tabs use `--text-secondary`.
- Tab bar height: `3.5rem` with `env(safe-area-inset-bottom)` padding for notched devices.

---

## Animation & Transitions

Use CSS transitions and animations sparingly. Motion is functional, not decorative.

**Motion tokens:**

| Token                    | Value                | Usage                               |
|--------------------------|----------------------|-------------------------------------|
| `--duration-fast`        | `100ms`              | Hover states, active states         |
| `--duration-normal`      | `200ms`              | Panel expand/collapse, dropdowns    |
| `--duration-slow`        | `300ms`              | Modal enter/exit, page transitions  |
| `--easing-default`       | `cubic-bezier(0.4, 0, 0.2, 1)` | General transitions     |
| `--easing-enter`         | `cubic-bezier(0, 0, 0.2, 1)`   | Elements entering view  |
| `--easing-exit`          | `cubic-bezier(0.4, 0, 1, 1)`   | Elements leaving view   |

**Required animations:**

| Interaction               | Animation                                         |
|---------------------------|----------------------------------------------------|
| Sidebar collapse/expand   | Width transition, `--duration-normal`              |
| Modal open                | Fade-in backdrop + scale-up content from 95%→100%, `--duration-slow` |
| Modal close               | Reverse of open, `--duration-normal`               |
| Dropdown open             | Fade-in + slide down 4px, `--duration-normal`      |
| Toast appear              | Slide in from right, `--duration-slow`             |
| Toast dismiss             | Fade out, `--duration-fast`                        |
| Skeleton shimmer          | Infinite left-to-right gradient sweep, `1.5s` loop |
| Price update flash        | Background flash `--accent-green` or `--accent-red` at 20% opacity, fade to transparent over `600ms` |
| Tab switch (content area) | No animation — instant swap (prevents CLS)         |
| Chart crosshair           | No transition — must track cursor at 60fps          |

- Respect `prefers-reduced-motion: reduce` — disable all transitions except opacity fades.
- Never animate `layout`-triggering properties (`width`, `height`, `top`, `left`) on frequently updating elements. Use `transform` and `opacity` only.

---

## Z-Index Layering

Use named z-index tokens. Never use arbitrary numbers.

| Token              | Value | Layer                                  |
|--------------------|-------|----------------------------------------|
| `--z-base`         | `0`   | Normal document flow                   |
| `--z-sticky`       | `10`  | Sticky table headers, market summary bar |
| `--z-sidebar`      | `20`  | Sidebar navigation                     |
| `--z-topbar`       | `30`  | TopBar (above sidebar on overlap)      |
| `--z-dropdown`     | `40`  | Dropdowns, autocomplete, popovers     |
| `--z-modal-backdrop` | `50` | Modal backdrop overlay                |
| `--z-modal`        | `60`  | Modal content                          |
| `--z-toast`        | `70`  | Toast notifications (always on top)    |
| `--z-tooltip`      | `80`  | Tooltips (topmost interactive layer)   |

- Always reference tokens (`var(--z-modal)`), never raw integers.
- If two elements on the same layer conflict, restructure the DOM — do not create new z-index values.
