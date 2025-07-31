import discord
from discord.ext import commands
from discord import app_commands
import aiohttp 
import os # ★★★ os 모듈 임포트! ★★★

# ★★★ BOT_TOKEN과 WEBHOOK_URL을 환경 변수에서 불러오도록 변경! ★★★
# 실행할 때 운영체제에 설정된 환경 변수를 가져오는 방식이야.
# 만약 환경 변수가 없으면 None이 되거나 오류가 나니까, 꼭 설정해줘야 해!
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN") 
WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

# ★★★ intents 정의가 중복되어 있어서 하나로 합쳤어! ★★★
intents = discord.Intents.default()
intents.message_content = True 
intents.members = True 

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'와! {bot.user.name} 봇이 드디어 움직인다! 신난다! ✨')
    await bot.tree.sync()
    print("슬래시 명령어 동기화 완료!")
    # ★★★ 봇 상태 메시지도 여기다 넣어줄게! ★★★
    await bot.change_presence(activity=discord.Game(name="칙령반포"))


@bot.tree.command(name="천황칙령", description="황국신민들에게 천황의 칙령을 공포합니다.")
@app_commands.describe(
    칙령_번호="칙령의 번호를 입력해주세요 (예: 001)",
    내용="칙령의 본문 내용을 입력해주세요."
)
@app_commands.checks.has_role(ALLOWED_ROLE_ID) 
async def decree(interaction: discord.Interaction, 칙령_번호: str, 내용: str):
    # 'interaction.response.defer'는 봇이 '생각 중...'인 상태를 보여주는 거였지?
    # 일단 사용자가 명령어를 입력하면 봇이 즉시 응답을 준비하도록 지연시켜.
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

    role_mention_text = f"[ ||<@&{MENTION_ROLE_ID}> || ]" 

    try:
        # 웹훅 URL이 유효한지 먼저 확인!
        if not WEBHOOK_URL:
            raise ValueError("WEBHOOK_URL 환경 변수가 설정되지 않았습니다.")

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

# 봇 실행 전에 토큰이 있는지 확인하는 게 좋아!
if BOT_TOKEN is None:
    print("오류: DISCORD_BOT_TOKEN 환경 변수가 설정되지 않았습니다. 봇을 실행할 수 없습니다.")
else:
    bot.run(BOT_TOKEN)
