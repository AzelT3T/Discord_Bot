import discord
import traceback
from discord.ext import commands
from os import getenv
import openai
from sentence_transformers import SentenceTransformer
import numpy as np

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

# ここにFAQを定義します
faq = {
    "こんにちは。あなたは誰ですか？": "私はヘルプデスクです。なにかお手伝いできることはありますか？",
    "どういう機能がありますか？": "私は質問に答えたり、情報を提供したりします。具体的な要求があればどういった事でもお手伝いできるかもしれません。",
    # その他のFAQをここに追加できます
}

messages = [
    {"role": "system", "content": "You are a helpful assistant. The AI assistant's name is AI Qiitan."},
    {"role": "user", "content": "こんにちは。あなたは誰ですか？"},
    {"role": "assistant", "content": "私はヘルプデスクです。なにかお手伝いできることはありますか？"}
]

# SentenceTransformerのモデルをロード
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# FAQの質問をベクトル化
faq_questions = list(faq.keys())
faq_embeddings = model.encode(faq_questions)

def find_closest_question(user_question):
    user_embedding = model.encode([user_question])
    distances = np.linalg.norm(faq_embeddings - user_embedding, axis=1)
    closest_idx = np.argmin(distances)
    return faq_questions[closest_idx]

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

        closest_question = find_closest_question(user_message)
        if np.linalg.norm(model.encode([user_message]) - model.encode([closest_question])) < 0.5:
            response = faq[closest_question]
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

