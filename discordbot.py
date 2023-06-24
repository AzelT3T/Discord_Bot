import discord
import traceback
from discord.ext import commands
from os import getenv
import openai
from sentence_transformers import SentenceTransformer
import torch

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

# ここにFAQを定義します
faq = {
    "こんにちは。あなたは誰ですか？": "私はヘルプデスクです。なにかお手伝いできることはありますか？",
    "どういう機能がありますか？": "私は質問に答えたり、情報を提供したりします。具体的な要求があればどういった事でもお手伝いできるかもしれません。",
    # その他のFAQをここに追加できます
}

# Embedding modelの初期化
model = SentenceTransformer('paraphrase-MiniLM-L6-v2')

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

        openai_api_key = getenv('OPENAI_API_KEY')
        openai.api_key = openai_api_key

        # ユーザーのメッセージとFAQの質問の類似度を計算
        question_embeddings = model.encode(list(faq.keys()))
        message_embedding = model.encode([user_message])
        similarities = torch.nn.functional.cosine_similarity(torch.Tensor(message_embedding), torch.Tensor(question_embeddings), dim=-1)
        closest_idx = similarities.argmax().item()

        # 最も類似しているFAQの質問を見つけ、対応する回答を取得
        closest_question = list(faq.keys())[closest_idx]
        response = faq[closest_question]
        
        # メッセージを送信
        await message.channel.send(response)

bot.run(getenv('TOKEN'))
