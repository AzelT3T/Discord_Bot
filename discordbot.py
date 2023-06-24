import discord
import traceback
from discord.ext import commands
from os import getenv
import openai

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

faq = {
    "こんにちは。あなたは誰ですか？": "私はヘルプデスクです。なにかお手伝いできることはありますか？",
    "どういう機能がありますか？": "私は質問に答えたり、情報を提供したりします。具体的な要求があればどういった事でもお手伝いできるかもしれません。",
}

def check_with_openai(question):
    openai_api_key = getenv('OPENAI_API_KEY')
    openai.api_key = openai_api_key
    question_list = ", ".join(faq.keys())
    print(question_list)
    prompt = f"{question}という質問がありましたが、これは {question_list} のいずれかの質問と一致しますか？回答は"'yes OR no','一致している質問','一致している質問に対応する回答'"のプロンプトにしたがってください。"

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    response = completion.choices[0].message.content
    return response

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
        
        # gpt-3.5-turboの回答が"yes"を含むならば、それに関連するFAQの回答を返す
        if "yes" in response.lower():
            matched_question = response.split(",")[1].strip()  # Assuming the second part of the response is the matching question
            if matched_question in faq:
                response = faq[matched_question]
        else:
            response = "Sorry, I didn't understand your question. Could you rephrase it or ask something else?"
        
        await message.channel.send(response)

token = getenv('DISCORD_BOT_TOKEN')
bot.run(token)
