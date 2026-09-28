# ReelScope Metrics & Data Dictionary

This document defines the canonical metrics, mathematical formulas, statistical tests, and platform-specific mapping rules implemented in **ReelScope**.

---

## 1. Canonical Schema

All imported datasets (TikTok, Instagram Reels, YouTube Shorts) are normalized into the following unified schema before storage into DuckDB:

| Canonical Field | Type | Description |
|---|---|---|
| `post_id` | `VARCHAR` | Unique identifier (e.g. `post_100001`) |
| `platform` | `VARCHAR` | `tiktok`, `reels`, or `shorts` |
| `published_at` | `TIMESTAMP` | UTC publication timestamp |
| `duration_sec` | `DOUBLE` | Video duration in seconds |
| `content_type` | `VARCHAR` | Content format (e.g. `Talking Head`, `B-Roll`, `POV`) |
| `caption_len` | `BIGINT` | Caption length in characters |
| `hashtags_count` | `BIGINT` | Number of hashtags in caption |
| `views` | `BIGINT` | Total accumulated impressions / views |
| `likes` | `BIGINT` | Total likes / hearts / diggs |
| `comments` | `BIGINT` | Total comments |
| `shares` | `BIGINT` | Total external and internal shares |
| `saves` | `BIGINT` | Total bookmarks / collections / saves |
| `completed_views` | `BIGINT` | Total views watched to 100% completion |
| `watch_time_sec` | `DOUBLE` | Cumulative watch time in seconds |
| `followers_gained` | `BIGINT` | Net new followers attributed to post |

---

## 2. Core Metric Formulas

### Engagement Rate (ER)
Measures the depth of audience interaction relative to reach:
$$\text{ER} = \frac{\text{likes} + \text{comments} + \text{shares} + \text{saves}}{\max(\text{views}, 1)} \times 100\%$$

*Note: In ReelScope, engagement rate never produces division by zero ($NULLIF(\text{views}, 0)$).*

### Completion Rate (CR)
Measures video retention and algorithmic hook effectiveness:
$$\text{CR} = \frac{\text{completed\_views}}{\max(\text{views}, 1)} \times 100\%$$

### Save Rate & Share Rate
Algorithmic signals indicating high information density or viral spread:
$$\text{Save Rate} = \frac{\text{saves}}{\max(\text{views}, 1)} \times 100\%$$
$$\text{Share Rate} = \frac{\text{shares}}{\max(\text{views}, 1)} \times 100\%$$

### 24h Velocity
Measures early breakout traction within the first 24 hours:
$$\text{Velocity}_{24h} = \frac{\text{views}_{24h}}{24.0} \quad \text{[views/hour]}$$

### 7d / 24h Growth Ratio
Identifies "slow-burners" vs. algorithmic spikes:
$$\text{Growth Ratio}_{7d/24h} = \frac{\text{views}_{7d}}{\max(\text{views}_{24h}, 1)}$$
- **Ratio $\approx 1.0 - 1.2$**: Front-loaded spike (most views gained on day 1).
- **Ratio $> 2.5$**: Strong algorithmic evergreen recommendation.

---

## 3. Platform Field Mappings

ReelScope's CSV importer automatically recognizes standard column headers across the major short-form networks:

| Canonical Field | TikTok Export | Instagram Reels Export | YouTube Shorts Analytics |
|---|---|---|---|
| `views` | `video_views`, `play_count` | `plays`, `impressions` | `views` |
| `likes` | `digg_count`, `likes` | `likes` | `likes` |
| `comments` | `comment_count`, `comments`| `comments` | `comments` |
| `shares` | `share_count`, `shares` | `shares`, `reshares` | `shares` |
| `saves` | `collect_count`, `favorites`| `saves`, `saved` | `saved_to_playlist` |
| `completed_views` | `full_watched_views` | `completed_plays` | `completions` |
| `watch_time_sec` | `total_play_time` | `watch_time_seconds` | `watch_time_hours * 3600` |
| `duration_sec` | `duration` | `video_length` | `content_duration` |

---

## 4. Statistical Testing (Experiment Lab)

### Binary Metrics (Two-Proportion Z-Test)
For metrics with binary outcomes (e.g. video completed or not):
$$\hat{p}_{\text{pool}} = \frac{x_c + x_t}{n_c + n_t}$$
$$\text{SE}_{\text{pool}} = \sqrt{\hat{p}_{\text{pool}} (1 - \hat{p}_{\text{pool}}) \left(\frac{1}{n_c} + \frac{1}{n_t}\right)}$$
$$z = \frac{\hat{p}_t - \hat{p}_c}{\text{SE}_{\text{pool}}}$$
$$95\% \text{ CI} = (\hat{p}_t - \hat{p}_c) \pm 1.96 \cdot \sqrt{\frac{\hat{p}_c(1-\hat{p}_c)}{n_c} + \frac{\hat{p}_t(1-\hat{p}_t)}{n_t}}$$

### Continuous Metrics (Welch's T-Test)
For watch time and view counts where group variances may differ:
$$t = \frac{\bar{x}_t - \bar{x}_c}{\sqrt{\frac{s_c^2}{n_c} + \frac{s_t^2}{n_t}}}$$
$$\nu \approx \frac{\left(\frac{s_c^2}{n_c} + \frac{s_t^2}{n_t}\right)^2}{\frac{(s_c^2 / n_c)^2}{n_c - 1} + \frac{(s_t^2 / n_t)^2}{n_t - 1}}$$

### Non-Parametric Bootstrap
10,000 Monte Carlo resamples with replacement compute the empirical lift distribution and the 95% quantile confidence interval: $[Q_{0.025}, Q_{0.975}]$.

### Sample Size & MDE Planning
Sample size required per variant for relative MDE $\delta_{\text{rel}}$ at power $1 - \beta$ and significance $\alpha$:
$$n = \frac{(Z_{\alpha/2} + Z_\beta)^2 \cdot \left[p(1-p) + (p + \delta)(1 - (p + \delta))\right]}{\delta^2}$$

---

## 5. Machine Learning & Anomaly Detection

### Feature Vector for Segmentation
1. `duration_sec`
2. `caption_len`
3. `hashtags_count`
4. `hour_of_day_sin` / `hour_of_day_cos`
5. `views` (log-transformed)
6. `engagement_rate`
7. `completion_rate`
8. `save_rate`
9. `share_rate`

Pipeline: `StandardScaler` $\rightarrow$ `KMeans(k=2..8)` $\rightarrow$ Silhouette score evaluation $\rightarrow$ Centroid interpretation.

### Robust Anomaly Detection
Uses the Median Absolute Deviation (MAD) to detect viral outliers and anomalies without susceptibility to extreme skewness:
$$\text{MAD} = \text{median}(|x_i - \text{median}(X)|)$$
$$\text{Robust Z-Score} = \frac{0.6745 \cdot (x_i - \text{median}(X))}{\text{MAD}}$$
A post is flagged as an anomaly if $|\text{Robust Z-Score}| \ge 3.0$.
