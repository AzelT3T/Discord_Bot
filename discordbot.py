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
    "保証内容を教えてください": "最短期間での再発送などのサポート体制で対応させていただいております。また、必要に応じて分析や調査を行い、お客様に結果をご報告させていただくとともに再発防止も徹底してまいります。",
    "クレジットカードは使えますか？": "VISA、MasterCard、JCB、AMEXなどのクレジットカードをご利用いただけます。一部、利用できないカードがございますので、お問い合わせの際に確認させていただきます。",
}

def check_with_openai(question):
    openai_api_key = getenv('OPENAI_API_KEY')
    openai.api_key = openai_api_key
    matched_questions = []
    for faq_question in faq.keys():
        prompt = f"user asked a question called '{question}', does this match the question '{faq_question}'? Your answer should be 'yes' or 'no' only."

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
            matched_questions.append(faq_question)

    if len(matched_questions) > 1:
        prompt = f"次の質問の中で、ユーザーの質問 '{question}' に最も一致しているのはどれですか？ {', '.join(matched_questions)}"
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        best_match_full = completion.choices[0].message.content
        best_match = next((q for q in matched_questions if q in best_match_full), None)
        return faq[best_match] if best_match else None
    elif matched_questions:
        return faq[matched_questions[0]]
    else:
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
        response = check_with_openai(user_message)
        if response is None:
            response = "該当するfaqが見つかりません。"

        await message.channel.send(response)

token = getenv('DISCORD_BOT_TOKEN')
bot.run(token)
