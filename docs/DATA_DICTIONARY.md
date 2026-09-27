# ReelScope Data Dictionary

## Tables

### 1. `platforms`
| Column | Type | Description | Example |
|---|---|---|---|
| `platform_id` | VARCHAR (PK) | Platform unique ID | `plat_tiktok` |
| `code` | VARCHAR (Unique) | System platform slug | `tiktok`, `reels`, `shorts` |
| `name` | VARCHAR | User-facing display name | `TikTok`, `Instagram Reels` |

### 2. `accounts`
| Column | Type | Description | Example |
|---|---|---|---|
| `account_id` | VARCHAR (PK) | Creator account identifier | `acc_alexcreates` |
| `platform_id` | VARCHAR (FK) | Reference to platforms table | `plat_tiktok` |
| `external_key` | VARCHAR | Platform handle or channel ID | `@alexcreates` |
| `display_name` | VARCHAR | Creator profile name | `Alex Creates` |

### 3. `posts`
| Column | Type | Description | Example |
|---|---|---|---|
| `post_id` | VARCHAR (PK) | Unique post identifier | `reel_9834721` |
| `account_id` | VARCHAR (FK) | Reference to creator account | `acc_alexcreates` |
| `platform` | VARCHAR | Platform code | `reels` |
| `title` | VARCHAR | Title or caption lead | `The 5 AM Mindset` |
| `published_at` | TIMESTAMP | Publication timestamp (UTC) | `2024-05-30 07:14:00` |
| `duration_sec` | DOUBLE | Content duration in seconds | `28.0` |
| `content_type` | VARCHAR | Format archetype | `Talking Head`, `B-Roll` |
| `caption_len` | INTEGER | Caption character count | `142` |
| `hashtags_count` | INTEGER | Number of hashtags in caption | `5` |
| `tags` | VARCHAR | Comma-separated category tags | `Mindset,Productivity` |
| `thumbnail_url`| VARCHAR | Optional local/remote thumbnail | `assets/thumb_01.jpg` |

### 4. `post_snapshots`
| Column | Type | Description | Example |
|---|---|---|---|
| `post_id` | VARCHAR (PK) | Post identifier | `reel_9834721` |
| `captured_at` | TIMESTAMP (PK) | Timestamp when snapshot was measured | `2024-05-31 07:14:00` |
| `views` | BIGINT | Cumulative view count | `248000` |
| `likes` | BIGINT | Cumulative like count | `18400` |
| `comments` | BIGINT | Cumulative comment count | `342` |
| `shares` | BIGINT | Cumulative share count | `1200` |
| `saves` | BIGINT | Cumulative save / bookmark count | `12400` |
| `completed_views` | BIGINT | Full completions | `178560` |
| `watch_time_sec` | DOUBLE | Total watch time accumulated | `5208000.0` |
| `followers_gained` | BIGINT | New followers attributed | `892` |

### 5. `experiments`
| Column | Type | Description |
|---|---|---|
| `experiment_id` | VARCHAR (PK) | Unique experiment ID |
| `name` | VARCHAR | Experiment descriptive name |
| `metric` | VARCHAR | Primary target metric (`completion_rate`, etc.) |
| `control_label` | VARCHAR | Label for Control A variant |
| `treatment_label`| VARCHAR | Label for Treatment B variant |
| `created_at` | TIMESTAMP | Creation timestamp |

### 6. `experiment_observations`
| Column | Type | Description |
|---|---|---|
| `observation_id`| VARCHAR (PK) | Unique observation record |
| `experiment_id` | VARCHAR (FK) | Reference to experiments |
| `variant` | VARCHAR | `control` or `treatment` |
| `value` | DOUBLE | Unit observation value (0/1 or numeric) |
| `subject_key` | VARCHAR | Optional user or session identifier |
| `captured_at` | TIMESTAMP | Observation timestamp |
