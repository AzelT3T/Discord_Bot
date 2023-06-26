import discord
import traceback
from discord.ext import commands
from os import getenv
import openai

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

faq = {
    "どういう機能がありますか？": "私は質問に答えたり、情報を提供したりします。具体的な要求があればどういった事でもお手伝いできるかもしれません。",
    "解約方法を知りたい": "お手持ちのスマートフォンの設定を開き、自分の名前をタップします。「サブスクリプション」をタップして解約ボタンを押してください。",
}

def check_with_openai(question):
    openai_api_key = getenv('OPENAI_API_KEY')
    openai.api_key = openai_api_key
    for faq_question in faq.keys():
        prompt = f"{question}という質問がありましたが、これは '{faq_question}' の質問と一致しますか？あなたの回答は 'yes' または 'no' を指定してください。"

        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        response = completion.choices[0].message.content.lower()
        print(response)
        if "yes" in response:
            return faq[faq_question]
    return None

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
        user_message = message.content.split('>')[1].lstrip()

        # ユーザーのメッセージがFAQに一致するかどうかをチェック
        response = check_with_openai(user_message)
        
        if response is None:
            response = "Sorry, I didn't understand your question. Could you rephrase it or ask something else?"

        await message.channel.send(response)

token = getenv('DISCORD_BOT_TOKEN')
bot.run(token)
