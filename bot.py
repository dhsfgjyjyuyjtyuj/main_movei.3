import os
import json
import random
import time
from instagrapi import Client
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip

# --- Random Delay (0 से 10 मिनट का वेट टाइम) ---
random_wait = random.randint(0, 600)
print(f"Bot start ho gaya hai, random lagne ke liye {random_wait} seconds wait kar raha hai...")
time.sleep(random_wait)

# --- CONFIGURATION ---
SESSION_ID = os.environ.get("INSTA_SESSION_ID", "").strip()
STATE_FILE = "trading_state.json"
MOVIE_FOLDER = "./movies"  # यहाँ अपनी 1-1 मिनट की क्लिप्स रखें
PROCESSED_FOLDER = "./processed_videos"
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

def load_state():
    if not os.path.exists(STATE_FILE):
        return {"movie_index": 0, "part_number": 1}
    with open(STATE_FILE, "r") as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=4)

print("Session ID se Instagram login ho raha hai...")
cl = Client()
try:
    cl.login_by_sessionid(SESSION_ID)
    print("Login Successful!")
except Exception as e:
    print(f"Login Failed: {e}")
    exit(1)

# मूवी लिस्ट निकालें
movies = sorted([f for f in os.listdir(MOVIE_FOLDER) if f.endswith((".mp4", ".mkv", ".avi"))])

if not movies:
    print("❌ Error: Movies folder khali hai! Clips upload karein.")
    exit(1)

state = load_state()
m_idx = state["movie_index"] % len(movies)
part_num = state["part_number"]

current_movie_path = os.path.join(MOVIE_FOLDER, movies[m_idx])
processed_video_path = os.path.join(PROCESSED_FOLDER, "final_reel.mp4")

print(f"Processing Clip: {movies[m_idx]} | Assigned Part: {part_num}")

try:
    # 1. Video Loading and Resolution Fix
    video_clip = VideoFileClip(current_movie_path)
    w, h = video_clip.w, video_clip.h
    if w % 2 != 0: w -= 1
    if h % 2 != 0: h -= 1
    video_clip = video_clip.resize((w, h))

    # 🌟 एडिटिंग: वीडियो के ऊपर "पैसे कमाने का पार्ट X" लिखना
    text_str = f"MUSCLE BUILDING - PART {part_num}"
    
    # ऊपरी हिस्से में ब्लैक बार के साथ टेक्स्ट ओवरले सेट करना
    txt_clip = TextClip(text_str, fontsize=32, color='yellow', font='Arial-Bold', bg_color='black')
    txt_clip = txt_clip.set_pos(('center', 20)).set_duration(video_clip.duration)
    
    # मर्ज करें
    final_clip = CompositeVideoClip([video_clip, txt_clip])
    final_clip.write_videofile(
        processed_video_path,
        codec="libx264",
        audio_codec="aac",
        fps=24,
        logger=None,
        threads=4
    )

    video_clip.close()
    txt_clip.close()
    final_clip.close()

    # 2. प्रीमियम और वायरल कैप्शंस की लिस्ट
    viral_captions = [
        f"Don't miss this part! 🔥 Watch till the end. | Part {part_num}",
        f"The ultimate guide to financial freedom. 📈 | Part {part_num}",
        f"Make your money work for you. 🧠 Save this reel! | Part {part_num}",
        f"Mindset changes everything. 💸 Follow for next part! | Part {part_num}"
    ]
    
    hashtags = f"\n\n#financialfreedom #moneytips #businessgrowth #paisa #investing #part{part_num} #viralreels #foryou"
    selected_caption = random.choice(viral_captions) + hashtags

    # 3. Instagram Upload
    print(f"Instagram par Part {part_num} upload ho raha hai...")
    media = cl.clip_upload(processed_video_path, caption=selected_caption)
    print(f"✅ Upload Successful! Media ID: {media.pk}")

    # 4. State Management (अगली रन के लिए इंडेक्स और पार्ट अपडेट करें)
    state["movie_index"] = m_idx + 1  # अगली क्लिप पर जाएँ
    state["part_number"] = part_num + 1  # पार्ट नंबर 1 बढ़ाएं
    save_state(state)

    # Cleanup
    if os.path.exists(processed_video_path):
        os.remove(processed_video_path)

except Exception as e:
    print(f"❌ Error aaya: {e}")
    exit(1)
