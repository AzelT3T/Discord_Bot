import discord
import traceback
from discord.ext import commands
from os import getenv
import openai

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

# ここにFAQを定義します
faq = {
    "こんにちは。あなたは誰ですか？": "私は AI アシスタントの AI Qiitan です。なにかお手伝いできることはありますか？",
    "どういう機能がありますか？": "私は質問に答えたり、情報を提供したりします。具体的な要求があればどういった事でもお手伝いできるかもしれません。",
    # その他のFAQをここに追加できます
}

messages = [
    {"role": "system", "content": "You are a helpful assistant. The AI assistant's name is AI Qiitan."},
    {"role": "user", "content": "こんにちは。あなたは誰ですか？"},
    {"role": "assistant", "content": "私はヘルプデスクです。なにかお手伝いできることはありますか？"}
]

@bot.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = ''.join(traceback.TracebackException.from_exception(orig_error).format())
    await ctx.send(error_msg)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if bot.user.id in [member.id for member in message.mentions]:
        print(message.content)
        user_message = message.content.split('>')[1].lstrip()
        print(user_message)
        messages.append({"role": "user", "content": user_message})

        # 新たに追加された部分: ユーザーのメッセージがFAQに一致するかどうかをチェック
        if user_message in faq:
            response = faq[user_message]
        else:
            openai_api_key = getenv('OPENAI_API_KEY')
            openai.api_key = openai_api_key

            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages
            )

            response = completion.choices[0].message.content

        print(response)
        await message.channel.send(response)

token = getenv('DISCORD_BOT_TOKEN')
bot.run(token)
