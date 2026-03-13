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

- **Light palette:** Invert luminance. Keep semantic color meanings identical (green = gain, red = loss).

### Typography

| Element         | Font              | Weight | Size     | Line height |
|-----------------|-------------------|--------|----------|-------------|
| H1 (page title) | Inter             | 600    | 24px     | 32px        |
| H2 (section)    | Inter             | 600    | 18px     | 24px        |
| H3 (card title) | Inter             | 500    | 15px     | 20px        |
| Body             | Inter             | 400    | 14px     | 20px        |
| Caption          | Inter             | 400    | 12px     | 16px        |
| Numeric data     | JetBrains Mono    | 400    | 13px     | 18px        |
| Ticker symbol    | JetBrains Mono    | 600    | 14px     | 20px        |

- All numeric/financial data uses a **monospace font** so columns align.
- Positive deltas render in `--accent-green` with a `▲` prefix.
- Negative deltas render in `--accent-red` with a `▼` prefix.
- Zero/unchanged renders in `--text-secondary` with a `—` prefix.

### Spacing & Grid

- **Base unit:** 4px
- **Spacing scale:** 4 · 8 · 12 · 16 · 24 · 32 · 48 · 64
- **Layout grid:** 12-column CSS Grid with 16px gutters
- **Breakpoints:**

| Name     | Min width | Columns | Sidebar |
|----------|-----------|---------|---------|
| `mobile` | 0         | 4       | hidden  |
| `tablet` | 768px     | 8       | collapsed |
| `desktop`| 1280px    | 12      | visible |
| `wide`   | 1600px    | 12      | visible + expanded |

### Elevation & Borders

- No box-shadows in dark mode. Use **1px solid borders** (`--border-default`) for separation.
- Light mode may use subtle shadows: `0 1px 3px rgba(0,0,0,0.12)`.
- Border radius: `6px` for cards/panels, `4px` for inputs/buttons, `2px` for tags/badges.

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
│ • Alerts     │                                                     │
│ • Settings   │                                                     │
│          │                                                         │
├──────────┴──────────────────────────────────────────────────────────┤
│  StatusBar  [Market status: Open/Closed]  [Last updated: HH:MM]   │
└─────────────────────────────────────────────────────────────────────┘
```

### TopBar

- Fixed at top, height `48px`.
- **Search** (center): Combo search for ticker symbols and company names. Autocomplete dropdown with symbol, name, exchange, and asset type. Keyboard shortcut: `/`.
- **Alerts** (right): Bell icon with unread count badge.
- **User** (right): Avatar + dropdown (profile, preferences, sign out).

### Sidebar

- Fixed left, width `220px` (desktop) or icon-only `56px` (collapsed).
- Navigation items: icon + label. Active item uses `--accent-blue` left border + background tint.
- Collapse toggle at the bottom of the sidebar.

### StatusBar

- Fixed at bottom, height `28px`.
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
- **Compare mode:** overlay up to 4 tickers on the same normalized chart.

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

- **Charting libraries:** Use [Lightweight Charts](https://github.com/niceDev0908/lightweight-charts) for financial candlestick/OHLC charts. Use [Recharts](https://recharts.org/) for everything else (area, bar, donut, line).
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
