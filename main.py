from decouple import config
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = config("TOKEN")
records_file = "run_records.json"


async def my_score_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows the runner score when the command /my_score is issued."""
    with open(records_file, "r") as read_file:
        records = json.load(read_file)
        user = update.effective_user
        runner_id = update.message.from_user.id
        if records == []:
            await update.message.reply_html("Не має жодного запису про бігунів!😔\nНапиши команду /help щоб дізнатися як додати свої результати!")
        else:
            for record in records:
                if record["runner_id"] == runner_id:
                    this_user_score = record["runner_score"]
                    answer = rf"Привіт {user.mention_html()}!" + "\nТвій загальний результат : " + rf"{this_user_score} км!💪"
                    await update.message.reply_html(answer)
                    break
            else:
                answer = rf"Привіт {user.mention_html()}!" + "\nНе маю записів про тебе!😔\nНапиши команду /help щоб дізнатися як додати свої результати!"
                await update.message.reply_html(answer)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows the help message when the command /help is issued."""
    await update.message.reply_text("Привіт! Цей бот записує відстань яку ти пробіг!\nЩоб записати відстань треба написати повідомлення типу:\nПробіг 10.0 (10.0 - відстань у км)\nЩоб подивитися свій загальний результат треба написати команду /my_score\nПобігли?😎")


async def record_distance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Records runners score."""
    user_input = update.message.text
    if "Пробіг" in user_input:
        user_input = user_input.replace("Пробіг", "")
        user_input = user_input.replace(" ", "")
        if user_input[0] == "0" and not user_input[1] == ".":
            pass
        else:
            try:
                user_input = float(user_input)
            except:
                pass
            else:
                with open(records_file, "r") as read_file:
                    records = json.load(read_file)
                    runner_name = update.message.from_user.full_name
                    runner_id = update.message.from_user.id
                    runner_score = user_input
                    if records == []:
                        new_record = {
                            "runner_name" : runner_name,
                            "runner_id" : runner_id,
                            "runner_score" : runner_score
                        }
                        records.append(new_record)
                    else:
                        for record in records:
                            if record["runner_id"] == runner_id:
                                record["runner_score"] += runner_score
                                break
                with open(records_file, "w") as write_file:
                    json.dump(records, write_file)
                await update.message.reply_text("Результат записано!😌")


def main() -> None:
    """Start the bot."""

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("my_score", my_score_command))
    application.add_handler(CommandHandler("help", help_command))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, record_distance))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()