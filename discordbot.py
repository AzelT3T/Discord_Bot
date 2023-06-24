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

messages = [
    {"role": "system", "content": "You are a helpful assistant. The AI assistant's name is AI Qiitan."},
    {"role": "user", "content": "こんにちは。あなたは誰ですか？"},
    {"role": "assistant", "content": "私はヘルプデスクです。なにかお手伝いできることはありますか？"}
]

def check_with_openai(question):
    openai_api_key = getenv('OPENAI_API_KEY')
    openai.api_key = openai_api_key

    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Does this question: '{}' match with any questions in the FAQ?".format(question)}
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
        print(message.content)
        user_message = message.content.split('>')[1].lstrip()
        print(user_message)
        messages.append({"role": "user", "content": user_message})

        # If the user message is in the FAQ, return the answer
        if user_message in faq:
            response = faq[user_message]
        else:
            # If not, check with OpenAI if the question matches any in the FAQ
            openai_response = check_with_openai(user_message)
            if "yes" in openai_response.lower():
                matched_question = openai_response.split(":")[-1].strip()  # Get the matched question from OpenAI's response
                response = faq[matched_question]
            else:
                response = "Sorry, I didn't understand your question. Could you rephrase it or ask something else?"

        print(response)
        await message.channel.send(response)

token = getenv('DISCORD_BOT_TOKEN')
bot.run(token)
