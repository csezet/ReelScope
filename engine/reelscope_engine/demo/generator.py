import random
import uuid
import math
from datetime import datetime, timedelta

PLATFORMS = [
    {"code": "tiktok", "name": "TikTok", "share": 0.52},
    {"code": "reels", "name": "Instagram Reels", "share": 0.28},
    {"code": "shorts", "name": "YouTube Shorts", "share": 0.20}
]

CREATORS = [
    ("acc_alexcreates", "@alexcreates", "Alex Creates"),
    ("acc_sarahvids", "@sarahvids", "Sarah Tech"),
    ("acc_marcusfit", "@marcusfit", "Marcus Fitness"),
    ("acc_elenacook", "@elenacook", "Elena Kitchen"),
    ("acc_davidgrowth", "@davidgrowth", "David Growth Lab")
]

CONTENT_FORMATS = [
    "Talking Head",
    "B-Roll",
    "Text/Caption",
    "Screen Record",
    "POV"
]

TOPICS = [
    ("Mindset", ["Mindset", "Productivity", "Habits", "Morning Routine"]),
    ("Tech & Setup", ["Productivity", "Setup", "Tech", "Workflow"]),
    ("Lifestyle", ["Lifestyle", "Travel", "Vlog", "Daily"]),
    ("Fitness", ["Fitness", "Health", "Workout", "Routine"]),
    ("Advice", ["Advice", "Career", "Motivation", "Finance"])
]

SAMPLE_TITLES = [
    "The 5 AM Mindset Changed My Life",
    "You're Closer Than You Think",
    "A Day in My Life as a Creator",
    "This Changed Everything",
    "My Productivity Setup (2024)",
    "Why Consistency Always Wins",
    "Stop Overthinking (Here's How)",
    "My Full Workout Routine",
    "3 Habits That Save 10 Hours a Week",
    "The Truth About Content Creation",
    "How to Double Your Output in 30 Days",
    "Simple Rule for Mental Clarity",
    "The Secret to Better Hooks",
    "5 Books That Actually Matter",
    "What Nobody Tells You About Burnout"
]

SNAPSHOT_DELTAS = [
    ("1h", timedelta(hours=1)),
    ("6h", timedelta(hours=6)),
    ("24h", timedelta(hours=24)),
    ("3d", timedelta(days=3)),
    ("7d", timedelta(days=7)),
    ("14d", timedelta(days=14)),
    ("21d", timedelta(days=21)),
    ("30d", timedelta(days=30))
]


def generate_demo_dataset(num_posts=300, seed=42):
    random.seed(seed)
    
    posts = []
    snapshots = []
    
    base_time = datetime(2024, 1, 1, 9, 0, 0)
    end_time = datetime(2024, 5, 31, 18, 0, 0)
    total_seconds = int((end_time - base_time).total_seconds())

    for i in range(num_posts):
        post_id = f"post_{100000 + i}"
        creator = CREATORS[0] if i < 150 else random.choice(CREATORS)
        
        r = random.random()
        if r < 0.52:
            platform = "tiktok"
        elif r < 0.80:
            platform = "reels"
        else:
            platform = "shorts"
            
        topic_name, topic_tags = random.choice(TOPICS)
        title = random.choice(SAMPLE_TITLES)
        if random.random() > 0.6:
            title = f"{title} #{random.randint(2, 9)}"
            
        format_type = random.choice(CONTENT_FORMATS)
        duration_sec = round(random.uniform(15.0, 58.0), 1)
        caption_len = random.randint(40, 280)
        hashtags_count = random.randint(2, 7)
        tags_str = ",".join(topic_tags)
        
        published_offset = random.randint(0, total_seconds)
        published_at = base_time + timedelta(seconds=published_offset)

        # Archetype: viral, high engagement, slow burner, underperformer
        archetype_roll = random.random()
        if archetype_roll < 0.15:
            target_final_views = random.randint(300_000, 1_500_000)
            eng_base = random.uniform(0.07, 0.12)
            completion_base = random.uniform(0.65, 0.85)
        elif archetype_roll < 0.45:
            target_final_views = random.randint(150_000, 400_000)
            eng_base = random.uniform(0.08, 0.14)
            completion_base = random.uniform(0.70, 0.88)
        elif archetype_roll < 0.80:
            target_final_views = random.randint(50_000, 180_000)
            eng_base = random.uniform(0.04, 0.08)
            completion_base = random.uniform(0.45, 0.65)
        else:
            target_final_views = random.randint(5_000, 40_000)
            eng_base = random.uniform(0.01, 0.04)
            completion_base = random.uniform(0.25, 0.45)

        post_record = {
            "post_id": post_id,
            "account_id": creator[0],
            "platform": platform,
            "title": title,
            "published_at": published_at.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_sec": duration_sec,
            "content_type": format_type,
            "caption_len": caption_len,
            "hashtags_count": hashtags_count,
            "tags": tags_str,
            "thumbnail_url": f"assets/thumbs/{platform}_{i % 10 + 1}.jpg"
        }
        posts.append(post_record)

        for delta_label, delta in SNAPSHOT_DELTAS:
            captured_at = published_at + delta
            if captured_at > end_time + timedelta(days=35):
                continue
                
            hours_elapsed = delta.total_seconds() / 3600.0
            progression = math.log(hours_elapsed + 1) / math.log(721)
            progression = min(1.0, max(0.02, progression))
            
            cur_views = int(target_final_views * progression * random.uniform(0.92, 1.05))
            cur_views = max(10, cur_views)
            
            cur_likes = int(cur_views * eng_base * 0.70 * random.uniform(0.9, 1.1))
            cur_comments = int(cur_views * eng_base * 0.05 * random.uniform(0.8, 1.2))
            cur_shares = int(cur_views * eng_base * 0.10 * random.uniform(0.8, 1.2))
            cur_saves = int(cur_views * eng_base * 0.15 * random.uniform(0.9, 1.1))
            cur_completed = int(cur_views * completion_base * random.uniform(0.95, 1.05))
            cur_watch_time = round(cur_views * duration_sec * (completion_base * 0.8), 1)
            cur_followers = int(cur_views * (eng_base * 0.04) * random.uniform(0.8, 1.2))
            
            snapshots.append({
                "post_id": post_id,
                "captured_at": captured_at.strftime("%Y-%m-%d %H:%M:%S"),
                "views": cur_views,
                "likes": cur_likes,
                "comments": cur_comments,
                "shares": cur_shares,
                "saves": cur_saves,
                "completed_views": cur_completed,
                "watch_time_sec": cur_watch_time,
                "followers_gained": cur_followers
            })

    experiments = [
        {
            "experiment_id": "exp_hook_length",
            "name": "Hook Duration (3s vs 1.5s)",
            "metric": "completion_rate",
            "control_label": "Standard Hook (3s)",
            "treatment_label": "Fast Punchy Hook (1.5s)",
            "control_rate": 0.421,
            "treatment_rate": 0.468,
            "n": 1500
        },
        {
            "experiment_id": "exp_thumbnail_face",
            "name": "Thumbnail: Face Close-up vs Landscape B-Roll",
            "metric": "conversion_rate",
            "control_label": "Landscape B-Roll",
            "treatment_label": "Expressive Face Close-up",
            "control_rate": 0.068,
            "treatment_rate": 0.084,
            "n": 2500
        },
        {
            "experiment_id": "exp_caption_question",
            "name": "Interactive Question Hook in Caption",
            "metric": "engagement_rate",
            "control_label": "Statement Caption",
            "treatment_label": "Provocative Question",
            "control_rate": 0.052,
            "treatment_rate": 0.076,
            "n": 2000
        },
        {
            "experiment_id": "exp_looping_ending",
            "name": "Seamless Loop Ending vs Fade Out",
            "metric": "completion_rate",
            "control_label": "Natural Fade Out",
            "treatment_label": "Seamless Seamless Loop",
            "control_rate": 0.450,
            "treatment_rate": 0.525,
            "n": 1800
        },
        {
            "experiment_id": "exp_first_frame_text",
            "name": "Frame 1 Text Overlay: High-Contrast Yellow vs White",
            "metric": "completion_rate",
            "control_label": "Clean White Text",
            "treatment_label": "High-Contrast Yellow Box",
            "control_rate": 0.380,
            "treatment_rate": 0.435,
            "n": 2200
        },
        {
            "experiment_id": "exp_share_cta",
            "name": "End Screen CTA: 'Send to a friend' vs None",
            "metric": "share_rate",
            "control_label": "No CTA",
            "treatment_label": "Direct Share Cue",
            "control_rate": 0.021,
            "treatment_rate": 0.044,
            "n": 3000
        },
        {
            "experiment_id": "exp_audio_trending",
            "name": "Trending Audio Track vs Original Voiceover",
            "metric": "conversion_rate",
            "control_label": "Original Voice Alone",
            "treatment_label": "Trending Lo-Fi Audio Bed",
            "control_rate": 0.045,
            "treatment_rate": 0.062,
            "n": 1600
        },
        {
            "experiment_id": "exp_pacing_cut_rate",
            "name": "Cut Frequency (1.5s cuts vs 4s cuts)",
            "metric": "completion_rate",
            "control_label": "Relaxed Pacing (4s cuts)",
            "treatment_label": "Fast Pacing (1.5s cuts)",
            "control_rate": 0.410,
            "treatment_rate": 0.490,
            "n": 2100
        },
        {
            "experiment_id": "exp_post_time_window",
            "name": "Publishing Time: Evening (19:00) vs Midday (12:00)",
            "metric": "conversion_rate",
            "control_label": "Midday 12:00 PM",
            "treatment_label": "Evening 7:00 PM Prime",
            "control_rate": 0.055,
            "treatment_rate": 0.071,
            "n": 1900
        },
        {
            "experiment_id": "exp_stitch_reaction",
            "name": "Content Style: Stitch Reaction vs Solo Monologue",
            "metric": "engagement_rate",
            "control_label": "Solo Monologue",
            "treatment_label": "Stitch with Trending Creator",
            "control_rate": 0.060,
            "treatment_rate": 0.088,
            "n": 1700
        },
        {
            "experiment_id": "exp_sound_effects",
            "name": "Audio Foley: Whoosh SFX on Transitions",
            "metric": "completion_rate",
            "control_label": "No Transition SFX",
            "treatment_label": "Subtle Whoosh SFX",
            "control_rate": 0.440,
            "treatment_rate": 0.475,
            "n": 1500
        },
        {
            "experiment_id": "exp_subtitle_style",
            "name": "Kinetic Animated Subtitles vs Static Subtitles",
            "metric": "completion_rate",
            "control_label": "Static Bottom Subtitles",
            "treatment_label": "Kinetic Bouncing Words",
            "control_rate": 0.480,
            "treatment_rate": 0.540,
            "n": 2400
        }
    ]

    exp_observations = []
    for exp in experiments:
        for i in range(exp["n"]):
            c_val = 1.0 if random.random() < exp["control_rate"] else 0.0
            exp_observations.append({
                "observation_id": f"{exp['experiment_id']}_c_{i}",
                "experiment_id": exp["experiment_id"],
                "variant": "control",
                "value": c_val,
                "subject_key": f"user_c_{i}"
            })
            t_val = 1.0 if random.random() < exp["treatment_rate"] else 0.0
            exp_observations.append({
                "observation_id": f"{exp['experiment_id']}_t_{i}",
                "experiment_id": exp["experiment_id"],
                "variant": "treatment",
                "value": t_val,
                "subject_key": f"user_t_{i}"
            })

    return {
        "platforms": PLATFORMS,
        "creators": CREATORS,
        "posts": posts,
        "snapshots": snapshots,
        "experiments": experiments,
        "observations": exp_observations
    }
