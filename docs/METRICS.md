# ReelScope Metrics Definitions & Methodology

## Core Principles
1. **No Fake Zeroes**: If a metric cannot be computed due to absent data (e.g. `completed_views` not provided by the platform export), the UI displays "Insufficient Data" rather than 0.
2. **Snapshot-Based Progression**: Rates and growth metrics are calculated relative to publication time (`published_at`) rather than static current counters.
3. **Statistical Uncertainty**: A/B experiments and cohorts report confidence intervals, sample sizes, and standard errors alongside point estimates.

## Formulas

### 1. Engagement Rate (ER)
$$\text{ER} = \frac{\text{likes} + \text{comments} + \text{shares} + \text{saves}}{\text{views}} \times 100\%$$
- Evaluated only when $\text{views} > 0$.

### 2. Completion Rate (CR)
$$\text{CR} = \frac{\text{completed\_views}}{\text{views}} \times 100\%$$
- Requires explicit `completed_views` counter. Never substituted with average watch time.

### 3. Save Rate
$$\text{Save Rate} = \frac{\text{saves}}{\text{views}} \times 100\%$$

### 4. Share Rate
$$\text{Share Rate} = \frac{\text{shares}}{\text{views}} \times 100\%$$

### 5. Follower Conversion
$$\text{Follower Conversion} = \frac{\text{followers\_gained}}{\text{views}} \times 100\%$$

### 6. 24h Velocity
$$\text{Velocity}_{24h} = \frac{\text{views at } 24\text{ hours}}{24}$$

### 7. 7d / 24h Growth Ratio
$$\text{Growth Ratio} = \frac{\text{views at } 7\text{ days}}{\text{views at } 24\text{ hours}}$$

## A/B Testing Engine
- **Binary Metrics** (e.g. Completion Rate): Two-proportion z-test with 95% Wilson confidence intervals.
- **Continuous Metrics** (e.g. Watch Time): Welch's t-test (unequal variances assumed) with Student-t confidence intervals.
- **Ratio Metrics** (e.g. Total Engagement / Views): Empirical Bootstrap with 10,000 resamples to capture correct standard errors without delta-method assumptions.
