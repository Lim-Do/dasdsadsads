import discord
from discord.ext import commands
from discord import app_commands
import aiohttp 
import os # os 모듈 임포트했는지 다시 한번 확인!

# ★★★ 중요! BOT_TOKEN과 WEBHOOK_URL은 환경 변수로 바꿔야 안전해! ★★★
# Railway에서 설정한 환경 변수 이름을 여기에 넣어줘야 해!
# 만약 Railway 환경 변수에 DISCORD_BOT_TOKEN / DISCORD_WEBHOOK_URL로 설정했다면 아래처럼!
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN") 
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# ★★★ ALLOWED_ROLE_ID와 MENTION_ROLE_ID도 여기에 정의되어 있어야 해! ★★★
# 맨 위, os.environ.get 아래에 확실하게 있어야 해!
ALLOWED_ROLE_ID = 1399635802035585116 
MENTION_ROLE_ID = 1399635652194209905 

# ★★★ intents 중복 정의 제거! ★★★
intents = discord.Intents.default()
intents.message_content = True 
intents.members = True # 이 줄 꼭 있어야 하고, Discord 개발자 포털에서도 활성화해야 해!

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'와! {bot.user.name} 봇이 드디어 움직인다! 신난다! ✨')
    await bot.tree.sync()
    print("슬래시 명령어 동기화 완료!")
    await bot.change_presence(activity=discord.Game(name="칙령반포")) # 봇 상태 메시지


@bot.tree.command(name="천황칙령", description="황국신민들에게 천황의 칙령을 공포합니다.")
@app_commands.describe(
    칙령_번호="칙령의 번호를 입력해주세요 (예: 001)",
    내용="칙령의 본문 내용을 입력해주세요."
)
@app_commands.checks.has_role(ALLOWED_ROLE_ID) # 여기서 ALLOWED_ROLE_ID를 사용!
async def decree(interaction: discord.Interaction, 칙령_번호: str, 내용: str):
    await interaction.response.defer(ephemeral=True) 

    separator = 'ㅡ' * 9 
    content_parts = 내용.split(separator)

    korean_part = content_parts[0].strip()
    japanese_part = ""

    if len(content_parts) > 1:
        japanese_part = content_parts[1].strip()

    embed = discord.Embed(
        title=f"천황칙령 {칙령_번호}호", 
        description=f"{korean_part}\n\n{japanese_part}\n\n본 칙령은 공포 일부터 시행한다.",
        color=discord.Color.dark_red() 
    )

    embed.set_thumbnail(url="https://i.imgur.com/xdwJ9QJ.png") 

    role_mention_text = f"[ ||<@&{MENTION_ROLE_ID}> || ]" # 여기서 MENTION_ROLE_ID를 사용!

    try:
        # ★★★ WEBHOOK_URL이 제대로 설정되었는지 확인하는 로직 추가! ★★★
        if not WEBHOOK_URL:
            # Railway에서 환경 변수가 제대로 설정되지 않았을 때 이 에러가 뜰 수 있음.
            await interaction.followup.send("오류: 웹훅 URL이 설정되지 않았습니다. Railway 환경 변수를 확인해주세요.", ephemeral=True)
            return # 오류 메시지를 보냈으니 함수 종료

        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(WEBHOOK_URL, session=session)
            
            await webhook.send(
                content=role_mention_text,
                embed=embed,
                username="天皇詔勅", 
                avatar_url="https://i.imgur.com/xdwJ9QJ.png"
            )
        await interaction.followup.send("칙령이 성공적으로 공포되었습니다.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"칙령 공포에 실패했습니다. 오류: {e}", ephemeral=True)

@decree.error
async def decree_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingRole):
        await interaction.response.send_message("칙령을 작성할 권한이 없습니다.", ephemeral=True)
    else:
        await interaction.response.send_message(f"오류가 발생했습니다. {error}", ephemeral=True)

# ★★★ 봇 실행 전에 토큰이 제대로 불러와졌는지 확인하는 게 좋아! ★★★
if BOT_TOKEN is None:
    print("오류: DISCORD_BOT_TOKEN 환경 변수가 설정되지 않았습니다. 봇을 실행할 수 없습니다.")
else:
    bot.run(BOT_TOKEN)
