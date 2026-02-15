import os
import discord
from discord.ext import tasks
from googleapiclient.discovery import build

# ====== 設定 ======
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_CHANNEL_ID = "UCgYCMluaLpERsyNXlPOvBtA"
DISCORD_CHANNEL_ID = 1379815933379481644
# ==================

intents = discord.Intents.default()
client = discord.Client(intents=intents)

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

notified_video_id = None  # 重複通知防止

@tasks.loop(minutes=5)
async def check_live():
    global notified_video_id

    request = youtube.search().list(
        part="snippet",
        channelId=YOUTUBE_CHANNEL_ID,
        eventType="live",
        type="video"
    )

    response = request.execute()

    if response["items"]:
        video = response["items"][0]
        video_id = video["id"]["videoId"]
        title = video["snippet"]["title"]
        url = f"https://www.youtube.com/watch?v={video_id}"

        if video_id != notified_video_id:
            notified_video_id = video_id
            channel = client.get_channel(DISCORD_CHANNEL_ID)
            await channel.send(
                f"🔴 **配信開始！**\n{title}\n{url}"
            )

@client.event
async def on_ready():
    print(f"ログイン完了：{client.user}")
    check_live.start()

client.run(DISCORD_TOKEN)
import os

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
