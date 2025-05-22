import discord
from discord.ext import commands
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.members = True
intents.voice_states = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

USER_1_ID = "USER_ID"  # ч1

@bot.event
async def on_ready():
    print(f"✅ Бот запущен как {bot.user}")

@bot.event
async def on_voice_state_update(member, before, after):
    if member.id != USER_1_ID:
        return

    # Слежение за изменением mute/deaf или киком из войса
    mute_changed = before.mute != after.mute
    deaf_changed = before.deaf != after.deaf
    left_channel = before.channel and after.channel is None

    if not (mute_changed or deaf_changed or left_channel):
        return

    try:
        await asyncio.sleep(1.5)  # Дать Discord время записать аудит-лог

        guild = member.guild

        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.member_update):
            if entry.target.id == USER_1_ID:
                actor = entry.user
                if actor.bot:
                    return  # не трогаем ботов

                print(f"🔍 Найден нарушитель: {actor.display_name}")

                # Проверка — в голосовом ли канале
                if actor.voice and actor.voice.channel:
                    await actor.edit(mute=True, deafen=True)
                    await actor.move_to(None)
                    print(f"❌ {actor.display_name} кикнут и замучен за вмешательство в голос ч1.")
                else:
                    print(f"{actor.display_name} не в голосе — пропущен.")
                return

        print("⚠️ Не удалось найти подходящую запись в аудит-логах.")

    except Exception as e:
        print(f"Ошибка: {e}")

bot.run("YOUR_DISCORD_BOT_TOKEN")
