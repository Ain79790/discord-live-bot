import os
import discord
from discord.ext import tasks
from googleapiclient.discovery import build
from flask import Flask
import threading

# ===== 環境変数 =====
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN が設定されていません")

if not YOUTUBE_API_KEY:
    raise ValueError("YOUTUBE_API_KEY が設定されていません")

# ===== 設定 =====
YOUTUBE_CHANNEL_IDS = [
    "UCSFCh5NL4qXrAy9u-u2lX3g",
    "UCgYCMluaLpERsyNXlPOvBtA",
    "UC5LyYg6cCA4yHEYvtUsir3g",
    "UCvUc0m317LWTTPZoBQV479A",
]

DISCORD_CHANNEL_ID = 1379815933379481644

# ===== Discord設定 =====
intents = discord.Intents.default()
client = discord.Client(intents=intents)

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

already_notified = {}

# ===== ライブチェック処理 =====
@tasks.loop(minutes=5)
async def check_live():
    global already_notified

    for yt_channel_id in YOUTUBE_CHANNEL_IDS:
        request = youtube.search().list(
            part="snippet",
            channelId=yt_channel_id,
            eventType="live",
            type="video"
        )
        response = request.execute()

        if response["items"]:
            video = response["items"][0]
            video_id = video["id"]["videoId"]
            title = video["snippet"]["title"]
            channel_name = video["snippet"]["channelTitle"]

            if already_notified.get(yt_channel_id) != video_id:
                already_notified[yt_channel_id] = video_id

                channel = client.get_channel(DISCORD_CHANNEL_ID)

                if channel:
                    await channel.send(
                        f"🔴 **{channel_name}** が配信開始！\n"
                        f"📺 {title}\n"
                        f"https://www.youtube.com/watch?v={video_id}"
                    )

@client.event
async def on_ready():
    print("Discordログイン成功")
    check_live.start()

# ===== Flask（メインで起動）=====
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_discord():
    client.run(DISCORD_TOKEN)

# Discordを別スレッドで起動
threading.Thread(target=run_discord).start()

# Flaskをメインで起動（Render用）
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
