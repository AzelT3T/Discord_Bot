import discord
import traceback
from discord.ext import commands
from os import getenv
import openai
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
import nltk

nltk.download('punkt')
nltk.download('wordnet')

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

def word_similarity(word1, word2):
    word1 = wn.synsets(word1)
    word2 = wn.synsets(word2)
    if word1 and word2:  # if word1 and word2 are not empty
        return word1[0].wup_similarity(word2[0])
    else:
        return None

def sentence_similarity(sentence1, sentence2):
    words1 = word_tokenize(sentence1.lower())
    words2 = word_tokenize(sentence2.lower())
    score = 0
    count = 0
    for word1 in words1:
        max_score = 0
        for word2 in words2:
            sim = word_similarity(word1, word2)
            if sim is not None and sim > max_score:
                max_score = sim
        if max_score is not None:
            score += max_score
            count += 1
    if count != 0:  # Prevent division by zero
        return score / count
    else:
        return None

@bot.event
async def on_command_error(ctx, error):
    orig_error = getattr(error, "original", error)
    error_msg = ''.join(traceback.TracebackException.from_exceptionorig_error).format())
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

        response = None
        max_sim = 0.8  # similarity threshold
        for question in faq:
            sim = sentence_similarity(user_message, question)
            if sim is not None and sim > max_sim:
                response = faq[question]
                max_sim = sim

        if response is None:
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
