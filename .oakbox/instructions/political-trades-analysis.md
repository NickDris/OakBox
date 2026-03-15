# Political Portfolio Tracker — Advanced Analysis Tools Guide

## Purpose

This guide defines the architecture, data models, analysis tools, and UI
integration for tracking publicly disclosed financial transactions of political
figures (e.g. US Congress members under the STOCK Act) as market signals.

All data sourced in this feature is **public disclosure data**. This system
aggregates, normalizes, and surfaces information that is already legally
required to be published. It does not access private data.

---

## Legal & Compliance Context

### Data Sources (Public Only)

| Source                         | Authority                  | Format        | Update frequency  |
|--------------------------------|----------------------------|---------------|-------------------|
| US Senate Financial Disclosures | Senate Office of Public Records | PDF / HTML | As filed (30–45 day lag) |
| US House Financial Disclosures  | Clerk of the House         | PDF / XML     | As filed (30–45 day lag) |
| STOCK Act Electronic Filing     | efd.senate.gov / efds.house.gov | Structured XML | As filed       |
| SEC EDGAR (for cross-reference) | SEC                        | XBRL / JSON   | Real-time         |
| OpenSecrets / Quiver Quant APIs | Third-party aggregators    | REST JSON     | Daily             |

### Compliance Rules

- **Display attribution:** Every data point must link back to the original
  public disclosure filing. Show the filing date, report date, and source URL.
- **Lag disclaimer:** Always display: "Disclosure filings may be delayed up to
  45 days from the transaction date per STOCK Act requirements."
- **Not financial advice:** Every page in this feature must include a footer
  disclaimer: "Political trading data is provided for informational purposes
  only and does not constitute investment advice."
- **No insider trading facilitation:** The system surfaces public data after
  disclosure — it does not predict or enable front-running of undisclosed trades.

---

## Data Architecture

### Database Schema (PostgreSQL)

```sql
-- Political figures tracked by the system
CREATE TABLE political_persons (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name       TEXT NOT NULL,
    slug            TEXT NOT NULL UNIQUE,           -- URL-friendly: "nancy-pelosi"
    chamber         TEXT NOT NULL CHECK (chamber IN ('senate', 'house')),
    state           TEXT NOT NULL,                  -- Two-letter state code
    party           TEXT NOT NULL CHECK (party IN ('D', 'R', 'I')),
    district        TEXT,                           -- NULL for senators
    in_office       BOOLEAN NOT NULL DEFAULT TRUE,
    committee_seats TEXT[] NOT NULL DEFAULT '{}',   -- e.g. {"Finance", "Armed Services"}
    photo_url       TEXT,
    first_elected   DATE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_political_persons_slug ON political_persons (slug);
CREATE INDEX idx_political_persons_chamber ON political_persons (chamber);

-- Individual disclosed transactions
CREATE TABLE political_trades (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id           UUID NOT NULL REFERENCES political_persons(id),
    disclosure_date     DATE NOT NULL,       -- When the filing was made public
    transaction_date    DATE NOT NULL,       -- When the trade actually occurred
    ticker              TEXT NOT NULL,        -- Stock symbol, e.g. "AAPL"
    asset_name          TEXT NOT NULL,        -- Full asset description from filing
    asset_type          TEXT NOT NULL CHECK (asset_type IN (
                            'stock', 'stock_option', 'etf', 'bond',
                            'mutual_fund', 'crypto', 'other'
                        )),
    transaction_type    TEXT NOT NULL CHECK (transaction_type IN (
                            'purchase', 'sale_full', 'sale_partial', 'exchange'
                        )),
    amount_range_low    NUMERIC NOT NULL,    -- Lower bound of reported range
    amount_range_high   NUMERIC NOT NULL,    -- Upper bound of reported range
    owner               TEXT NOT NULL CHECK (owner IN (
                            'self', 'spouse', 'dependent', 'joint'
                        )),
    filing_url          TEXT NOT NULL,        -- Link to original public filing
    source              TEXT NOT NULL CHECK (source IN (
                            'senate_efd', 'house_efd', 'opensecrets', 'quiver_quant'
                        )),
    price_at_trade      NUMERIC,             -- Looked up from market data (nullable)
    price_at_disclosure NUMERIC,             -- Price when filing went public
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_political_trades_person ON political_trades (person_id);
CREATE INDEX idx_political_trades_ticker ON political_trades (ticker);
CREATE INDEX idx_political_trades_date ON political_trades (transaction_date DESC);
CREATE INDEX idx_political_trades_disclosure ON political_trades (disclosure_date DESC);

-- Precomputed performance metrics per person
CREATE TABLE person_performance (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    person_id       UUID NOT NULL REFERENCES political_persons(id),
    period          TEXT NOT NULL CHECK (period IN (
                        '30d', '90d', '1y', '2y', 'all_time'
                    )),
    total_trades    INT NOT NULL,
    win_rate        NUMERIC NOT NULL,        -- % of trades that were profitable
    avg_return      NUMERIC NOT NULL,        -- Average return per trade
    total_volume    NUMERIC NOT NULL,        -- Sum of midpoint estimates
    top_sector      TEXT,                    -- Most traded GICS sector
    computed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (person_id, period)
);

-- Aggregated signal scores per ticker
CREATE TABLE ticker_political_signals (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    ticker          TEXT NOT NULL,
    signal_date     DATE NOT NULL,
    buy_count       INT NOT NULL DEFAULT 0,    -- Purchases in last 90 days
    sell_count      INT NOT NULL DEFAULT 0,    -- Sales in last 90 days
    net_sentiment   NUMERIC NOT NULL,          -- Range -1.0 (all sell) to +1.0 (all buy)
    notable_traders TEXT[] NOT NULL DEFAULT '{}', -- Person slugs with recent activity
    cluster_score   NUMERIC NOT NULL,          -- 0.0–1.0, how many persons are trading same direction
    computed_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (ticker, signal_date)
);

CREATE INDEX idx_ticker_signals_ticker ON ticker_political_signals (ticker);
CREATE INDEX idx_ticker_signals_date ON ticker_political_signals (signal_date DESC);
```

### Alembic Migration Rules

- One migration per table. Name format: `NNNN_create_<table_name>.py`.
- Enums use `CHECK` constraints (not Postgres `ENUM` types) for easier migration.
- All `NUMERIC` financial columns default to no precision constraint — store exact values.

---

## Data Ingestion Pipeline

### Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  Source Fetchers │────▶│   Normalizer    │────▶│   PostgreSQL     │
│  (scheduled)    │     │   (validation)  │     │   (write layer)  │
└─────────────────┘     └─────────────────┘     └──────────────────┘
        │                       │                        │
        │                       ▼                        ▼
        │               ┌─────────────────┐     ┌──────────────────┐
        │               │  Price Enricher │     │ Signal Aggregator│
        │               │  (market data)  │     │ (scoring engine) │
        │               └─────────────────┘     └──────────────────┘
```

### Pipeline Stages

| Stage              | Module                                  | Schedule         | Description |
|--------------------|-----------------------------------------|------------------|-------------|
| **1. Fetch**       | `src/backend/services/political/fetchers/` | Every 6 hours  | Pull new filings from each data source |
| **2. Normalize**   | `src/backend/services/political/normalizer.py` | On new data | Parse PDF/XML, extract structured trade records |
| **3. Deduplicate** | `src/backend/services/political/dedup.py` | On new data     | Match against existing records by (person, ticker, transaction_date, amount_range) |
| **4. Enrich**      | `src/backend/services/political/enricher.py` | On new data   | Look up `price_at_trade` and `price_at_disclosure` from market data |
| **5. Score**       | `src/backend/services/political/scorer.py` | Daily at 00:00 UTC | Recompute `person_performance` and `ticker_political_signals` |

### Fetcher Interface

Every data source implements this interface:

```python
from abc import ABC, abstractmethod
from datetime import date

class BaseFetcher(ABC):
    """Base class for political disclosure data fetchers."""

    @abstractmethod
    async def fetch_new_filings(
        self,
        since: date,
    ) -> list[RawFiling]:
        """Fetch filings published since the given date."""
        ...

    @abstractmethod
    def source_name(self) -> str:
        """Return the source identifier (e.g. 'senate_efd')."""
        ...
```

```python
from pydantic import BaseModel
from datetime import date

class RawFiling(BaseModel):
    """Unprocessed filing record from a data source."""
    person_name: str
    transaction_date: date
    disclosure_date: date
    ticker: str | None         # None if asset is not publicly traded
    asset_description: str
    asset_type: str
    transaction_type: str      # 'purchase', 'sale_full', 'sale_partial', 'exchange'
    amount_range_low: float
    amount_range_high: float
    owner: str
    filing_url: str
    source: str
```

### Scoring Algorithm

The **cluster score** for a ticker measures coordinated political trading:

```
cluster_score = (unique_persons_trading_same_direction / total_unique_persons_with_any_trade) ^ 0.5
```

The **net sentiment** for a ticker:

```
net_sentiment = (buy_volume - sell_volume) / (buy_volume + sell_volume)
```

Where `volume` is the midpoint of each trade's amount range.

The **win rate** for a person:

```
win_rate = trades_with_positive_return / total_trades_with_known_return
```

A trade's return is measured from `price_at_trade` to the price 30 days after
`transaction_date`. If price data is unavailable, the trade is excluded from
win rate (not counted as a loss).

---

## Backend API Endpoints

| Method | Path                                           | Purpose                              | Response type              |
|--------|------------------------------------------------|--------------------------------------|----------------------------|
| GET    | `/api/v1/political/persons`                    | List all tracked political figures   | `PoliticalPerson[]`        |
|        | `?chamber=senate|house&party=D|R|I&sort=win_rate|total_trades|name&order=asc|desc` | | |
| GET    | `/api/v1/political/persons/:slug`              | Single person detail                 | `PoliticalPersonDetail`    |
| GET    | `/api/v1/political/persons/:slug/trades`       | Person's trade history               | `PoliticalTrade[]`         |
|        | `?ticker=<sym>&type=purchase|sale_full|sale_partial&since=<date>&page=<n>&limit=<n>` | | |
| GET    | `/api/v1/political/persons/:slug/performance`  | Person's performance metrics         | `PersonPerformance[]`      |
| GET    | `/api/v1/political/trades/recent`              | Latest trades across all persons     | `PoliticalTrade[]`         |
|        | `?days=<n>&ticker=<sym>&type=purchase|sale_full|sale_partial&page=<n>&limit=<n>` | | |
| GET    | `/api/v1/political/trades/ticker/:symbol`      | All political trades for a ticker    | `PoliticalTrade[]`         |
| GET    | `/api/v1/political/signals`                    | Ticker signal rankings               | `TickerPoliticalSignal[]`  |
|        | `?min_cluster=<0-1>&direction=buy|sell|any&sort=cluster_score|net_sentiment&limit=<n>` | | |
| GET    | `/api/v1/political/signals/:symbol`            | Signal detail for a single ticker    | `TickerPoliticalSignal`    |
| GET    | `/api/v1/political/dashboard`                  | Pre-composed dashboard payload       | `PoliticalDashboard`       |

**Pagination:** All list endpoints follow the project standard:
`{ results: T[], total: number, page: number, limit: number }`.

---

## TypeScript Data Types

```typescript
interface PoliticalPerson {
  id: string;
  fullName: string;
  slug: string;
  chamber: 'senate' | 'house';
  state: string;
  party: 'D' | 'R' | 'I';
  district: string | null;
  inOffice: boolean;
  committeeSeats: string[];
  photoUrl: string | null;
  firstElected: string | null;    // ISO date
}

interface PoliticalPersonDetail extends PoliticalPerson {
  performance: PersonPerformance[];
  recentTrades: PoliticalTrade[];  // Last 10
  topTickers: { symbol: string; tradeCount: number }[];
}

interface PoliticalTrade {
  id: string;
  person: {
    slug: string;
    fullName: string;
    party: 'D' | 'R' | 'I';
    chamber: 'senate' | 'house';
  };
  disclosureDate: string;          // ISO date
  transactionDate: string;         // ISO date
  ticker: string;
  assetName: string;
  assetType: 'stock' | 'stock_option' | 'etf' | 'bond' | 'mutual_fund' | 'crypto' | 'other';
  transactionType: 'purchase' | 'sale_full' | 'sale_partial' | 'exchange';
  amountRangeLow: number;
  amountRangeHigh: number;
  owner: 'self' | 'spouse' | 'dependent' | 'joint';
  filingUrl: string;
  source: string;
  priceAtTrade: number | null;
  priceAtDisclosure: number | null;
}

interface PersonPerformance {
  period: '30d' | '90d' | '1y' | '2y' | 'all_time';
  totalTrades: number;
  winRate: number;                 // 0.0–1.0
  avgReturn: number;               // Percentage, e.g. 12.5
  totalVolume: number;
  topSector: string | null;
}

interface TickerPoliticalSignal {
  ticker: string;
  signalDate: string;              // ISO date
  buyCount: number;
  sellCount: number;
  netSentiment: number;            // -1.0 to +1.0
  notableTraders: string[];        // Person slugs
  clusterScore: number;            // 0.0–1.0
}

interface PoliticalDashboard {
  recentTrades: PoliticalTrade[];           // Last 20
  topBuySignals: TickerPoliticalSignal[];   // Top 10 by cluster_score, buy direction
  topSellSignals: TickerPoliticalSignal[];  // Top 10 by cluster_score, sell direction
  mostActivePersons: (PoliticalPerson & {
    tradeCount30d: number;
    winRate: number;
  })[];
  bipartisanPicks: TickerPoliticalSignal[]; // Tickers bought by both parties
}
```

---

## Frontend Feature Module

### Route Structure

| Route                              | Page                     |
|------------------------------------|--------------------------|
| `/political`                       | Political Dashboard      |
| `/political/persons`               | All Persons list         |
| `/political/persons/:slug`         | Person Detail            |
| `/political/trades`                | Trade Feed               |
| `/political/signals`               | Signal Rankings          |
| `/ticker/:symbol` (existing)       | Integrates political tab |

### File Structure

```
src/frontend/features/
  political/
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
```

### Page Wireframes

#### Political Dashboard (`/political`)

```
┌──────────────────────────────────────────────────────────────┐
│  Political Tracker                                           │
│  ⚖️ Tracking 535 members  |  Last updated: Mar 15, 2026     │
├──────────────────────────────────────────────────────────────┤
│  Disclaimer: Political trading data is provided for          │
│  informational purposes only. Not investment advice.         │
├────────────────────────────┬─────────────────────────────────┤
│  Recent Trades (card)      │  Top Buy Signals (card)         │
│  ┌─────┬─────┬─────┬─────┐│  ┌──────┬───────┬───────┬─────┐│
│  │ Who │Tick │ Type│ Amt ││  │ Tick │ Buyers│ Clstr │ Net ││
│  │Pelosi│NVDA│ Buy │$1-5M││  │ NVDA │  8    │ 0.82  │+0.91││
│  │Tubrvl│MSFT│ Sell│$250K││  │ LMT  │  5    │ 0.74  │+0.68││
│  │Cruz  │AAPL│ Buy │$15K ││  │ PLTR │  4    │ 0.71  │+0.85││
│  └─────┴─────┴─────┴─────┘│  └──────┴───────┴───────┴─────┘│
├────────────────────────────┼─────────────────────────────────┤
│  Most Active (card)        │  Bipartisan Picks (card)        │
│  ┌──────────┬─────┬──────┐│  ┌──────┬───────┬──────┬──────┐│
│  │ Name     │Trades│WinR ││  │ Tick │ D Buy │ R Buy│ Clstr││
│  │ Pelosi   │ 12  │ 68% ││  │ MSFT │  3    │  4   │ 0.78 ││
│  │ Tubervlle│ 9   │ 71% ││  │ UNH  │  2    │  3   │ 0.65 ││
│  │ Crenshaw │ 7   │ 55% ││  │ JPM  │  2    │  2   │ 0.60 ││
│  └──────────┴─────┴──────┘│  └──────┴───────┴──────┴──────┘│
├──────────────────────────────────────────────────────────────┤
│  Top Sell Signals (card)                                     │
│  ┌──────┬────────┬──────────┬───────────┐                   │
│  │ Tick │ Sellers│ Cluster  │ Net Sent. │                   │
│  │ TSLA │   6    │  0.77    │  -0.83    │                   │
│  │ META │   4    │  0.65    │  -0.72    │                   │
│  └──────┴────────┴──────────┴───────────┘                   │
├──────────────────────────────────────────────────────────────┤
│  Disclaimer footer (always visible)                          │
└──────────────────────────────────────────────────────────────┘
```

#### Person Detail (`/political/persons/:slug`)

```
┌──────────────────────────────────────────────────────────────┐
│  [Photo] Nancy Pelosi (D-CA)                                 │
│  House  |  Speaker Emerita  |  In office since 1987          │
│  Committees: Financial Services, Intelligence                │
├──────────────────────────────────────────────────────────────┤
│  Performance Summary                                         │
│  ┌───────────┬───────────┬───────────┬───────────┐          │
│  │  30 Day   │  90 Day   │  1 Year   │ All Time  │          │
│  │  Trades: 3│  Trades: 8│ Trades: 24│Trades: 142│          │
│  │  Win: 67% │  Win: 71% │  Win: 68% │  Win: 65% │          │
│  │  Avg: +8% │  Avg: +12%│  Avg: +15%│  Avg: +11%│          │
│  │  Vol: $2M │  Vol: $8M │  Vol: $22M│  Vol:$140M│          │
│  └───────────┴───────────┴───────────┴───────────┘          │
├──────────────────────────────────────────────────────────────┤
│  Trade History                        [Filter ▼] [Export CSV]│
│  ┌──────┬──────────┬──────────┬──────┬──────────┬──────────┐│
│  │ Date │ Ticker   │ Type     │Amount│ Price@   │ Filing   ││
│  │      │          │          │      │ Trade    │          ││
│  │ 3/10 │ NVDA     │ Purchase │$1-5M │ $872.50  │ [Link]   ││
│  │ 3/02 │ AAPL     │ Sale     │$500K │ $188.90  │ [Link]   ││
│  │ 2/15 │ RBLX     │ Purchase │$1-5M │ $52.30   │ [Link]   ││
│  └──────┴──────────┴──────────┴──────┴──────────┴──────────┘│
│  [◀ Prev]  Page 1 of 12  [Next ▶]                           │
├──────────────────────────────────────────────────────────────┤
│  Top Tickers (horizontal bar chart)                          │
│  NVDA  ████████████████████  12 trades                       │
│  AAPL  ████████████████      10 trades                       │
│  MSFT  ███████████           7 trades                        │
│  RBLX  ████████              5 trades                        │
├──────────────────────────────────────────────────────────────┤
│  Disclaimer footer                                           │
└──────────────────────────────────────────────────────────────┘
```

#### Signal Rankings (`/political/signals`)

```
┌──────────────────────────────────────────────────────────────┐
│  Political Signal Rankings       [Buy Signals] [Sell Signals]│
├──────────────────────────────────────────────────────────────┤
│  Filters: [Min Cluster ▼] [Direction ▼] [Time Range ▼]      │
├──────────────────────────────────────────────────────────────┤
│  ┌──────┬────────┬────────┬──────────┬──────────┬──────────┐│
│  │ Tick │ Buyers │ Sellers│ Net Sent │ Cluster  │ Traders  ││
│  │ NVDA │   8    │   1    │  +0.91   │ ████ 0.82│ Pelosi.. ││
│  │ LMT  │   5    │   0    │  +1.00   │ ███▓ 0.74│ Inhofe.. ││
│  │ PLTR │   4    │   0    │  +1.00   │ ███▓ 0.71│ Tubervl..││
│  │ TSLA │   1    │   6    │  -0.83   │ ███▓ 0.77│ multiple ││
│  └──────┴────────┴────────┴──────────┴──────────┴──────────┘│
│  [◀ Prev]  Page 1 of 5  [Next ▶]                            │
├──────────────────────────────────────────────────────────────┤
│  Disclaimer footer                                           │
└──────────────────────────────────────────────────────────────┘
```

---

## Integration With Existing Market Analysis UI

The political tracker integrates into the existing app shell defined in
`frontend-market-analysis.md`:

### Sidebar Addition

Add below "Analysis" in the sidebar navigation:

| Icon    | Label           | Route        |
|---------|-----------------|--------------|
| Capitol | Political       | `/political` |

Mobile bottom tab bar: Political goes inside the **More** drawer alongside
Watchlist, Analysis, and Settings.

### Ticker Detail Integration

Add a **Political** tab to the existing ticker detail page (`/ticker/:symbol`):

```
┌──────────────────────────────────────────────────────────────┐
│  NVDA — NVIDIA Corp         [Chart] [Stats] [Political] ... │
├──────────────────────────────────────────────────────────────┤
│  Political Activity for NVDA                                 │
│  Signal: ▲ Strong Buy  |  Cluster: 0.82  |  Net: +0.91     │
│                                                              │
│  Recent Political Trades                                     │
│  ┌─────────┬──────────┬──────────┬──────────┬──────────┐    │
│  │ Person  │ Date     │ Type     │ Amount   │ Filing   │    │
│  │ Pelosi  │ Mar 10   │ Purchase │ $1-5M    │ [Link]   │    │
│  │ Cruz    │ Mar 08   │ Purchase │ $50-100K │ [Link]   │    │
│  │ Crenshaw│ Feb 28   │ Purchase │ $15-50K  │ [Link]   │    │
│  └─────────┴──────────┴──────────┴──────────┴──────────┘    │
├──────────────────────────────────────────────────────────────┤
│  Disclaimer footer                                           │
└──────────────────────────────────────────────────────────────┘
```

### Dashboard Integration

Add a **Political Signals** card to the main Dashboard page (bottom row,
alongside existing cards):

| Component                | Content                                           |
|--------------------------|---------------------------------------------------|
| `PoliticalSignalsCard`   | Top 3 buy signals + top 3 sell signals by cluster score. Click → `/political/signals` |

---

## Component Specifications

### New Shared Components

| Component           | Props                                             | Usage                              |
|---------------------|---------------------------------------------------|------------------------------------|
| `PartyBadge`        | `party: 'D' | 'R' | 'I'`                        | Colored pill: blue (D), red (R), gray (I) |
| `ClusterScoreBar`   | `score: number` (0–1)                             | Horizontal fill bar with numeric label |
| `SentimentGauge`    | `value: number` (-1 to +1)                        | Centered gauge: red←neutral→green  |
| `SignalBadge`       | `direction: 'buy' | 'sell' | 'neutral'`, `strength: 'strong' | 'moderate' | 'weak'` | "▲ Strong Buy" colored badge |
| `CommitteeTag`      | `name: string`                                    | Gray chip: "Finance", "Intelligence" |
| `FilingSourceLink`  | `url: string`, `source: string`                   | External link icon + source name   |
| `DisclaimerFooter`  | none                                              | Standard legal disclaimer text     |
| `AmountRange`       | `low: number`, `high: number`                     | Formatted range: "$1M–$5M"         |

### Color Conventions (Political)

| Element              | Color token                              |
|----------------------|------------------------------------------|
| Democratic (D)       | `--accent-blue` (`#58a6ff` dark / `#0969da` light) |
| Republican (R)       | `--accent-red` (`#f85149` dark / `#cf222e` light)  |
| Independent (I)      | `--text-secondary`                       |
| Buy signal           | `--accent-green`                         |
| Sell signal          | `--accent-red`                           |
| Neutral signal       | `--accent-yellow`                        |
| Cluster score fill   | `--accent-purple`                        |

### Amount Range Formatting

Filings report trade amounts as ranges. Format them consistently:

| Range                 | Display         |
|-----------------------|-----------------|
| $1,001–$15,000        | `$1K–$15K`     |
| $15,001–$50,000       | `$15K–$50K`    |
| $50,001–$100,000      | `$50K–$100K`   |
| $100,001–$250,000     | `$100K–$250K`  |
| $250,001–$500,000     | `$250K–$500K`  |
| $500,001–$1,000,000   | `$500K–$1M`    |
| $1,000,001–$5,000,000 | `$1M–$5M`      |
| $5,000,001–$25,000,000| `$5M–$25M`     |
| $25,000,001–$50,000,000| `$25M–$50M`   |
| Over $50,000,000      | `$50M+`         |

These ranges match the STOCK Act disclosure brackets exactly.

---

## Error & Empty States

| Page / Card                    | Empty state message                                | CTA             |
|--------------------------------|----------------------------------------------------|-----------------|
| Political Dashboard            | "No political trading data available yet."         | —               |
| Person Detail → Trade History  | "No disclosed trades found for this member."       | —               |
| Signal Rankings → Results      | "No signals match your filters."                   | "Reset filters" |
| Ticker → Political tab         | "No political trades found for this ticker."       | —               |
| Trade Feed                     | "No trades in the selected time range."            | "Expand range"  |

---

## Testing Requirements

### Backend

- **Fetcher tests:** Mock HTTP responses from each data source. Assert correct parsing of at least 3 filing formats per source.
- **Normalizer tests:** Feed known raw filings → assert correct `PoliticalTrade` output including edge cases (missing ticker, unknown asset type).
- **Dedup tests:** Insert duplicate filings → assert no duplicate rows in `political_trades`.
- **Scorer tests:** Seed trades → assert correct `win_rate`, `cluster_score`, `net_sentiment` calculations against hand-computed values.
- **API tests:** Full endpoint integration tests using `httpx.AsyncClient` against test database.

### Frontend

- **Component tests:** Render each component with mock data. Assert correct display of party colors, amount ranges, signal badges.
- **Hook tests:** Mock API responses with MSW. Assert loading/success/error states.
- **Disclaimer test:** Assert `DisclaimerFooter` is rendered on every political page.
- **Accessibility:** Assert all tables have correct `scope` attributes. Assert `PartyBadge` has `aria-label` (not color-only).

---

## Performance Considerations

- **Precompute signals daily** — do not compute cluster scores or win rates on the fly. Read from `person_performance` and `ticker_political_signals` tables.
- **Cache the dashboard payload** — `/api/v1/political/dashboard` should be cached with a 5-minute TTL at the API layer.
- **Paginate all trade lists** — default `limit=20`, max `limit=100`.
- **Index on `(ticker, transaction_date)`** — this is the most common join path when integrating with the existing ticker detail page.
