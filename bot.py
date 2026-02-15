import os
import discord
from discord.ext import tasks
from googleapiclient.discovery import build

# ===== 環境変数 =====
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not DISCORD_TOKEN:
    raise ValueError("DISCORD_TOKEN が設定されていません")

if not YOUTUBE_API_KEY:
    raise ValueError("YOUTUBE_API_KEY が設定されていません")

# ===== 設定 =====
YOUTUBE_CHANNEL_ID = "UCgYCMluaLpERsyNXlPOvBtA"
YOUTUBE_CHANNEL_IDS = [
    "UCSFCh5NL4qXrAy9u-u2lX3g",
    "UCgYCMluaLpERsyNXlPOvBtA",
    "UC5LyYg6cCA4yHEYvtUsir3g",
    "UCvUc0m317LWTTPZoBQV479A",
]

# ===== Discord設定 =====
intents = discord.Intents.default()
client = discord.Client(intents=intents)

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
DISCORD_CHANNEL_ID = 1379815933379481644

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


# ===== 起動時 =====
@client.event
async def on_ready():
    print("起動成功")
    check_live.start()

client.run(DISCORD_TOKEN)
@tasks.loop(minutes=1)
async def check_live():
    print("チェック中")

    for yt_channel_id in YOUTUBE_CHANNEL_IDS:
        print("確認:", yt_channel_id)

        request = youtube.search().list(
            part="snippet",
            channelId=yt_channel_id,
            eventType="live",
            type="video"
        )
        response = request.execute()

        print(response)