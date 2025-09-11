from decouple import config
import json
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

TOKEN = config("TOKEN")
records_file = "run_records.json"


def merge_sort(records):
    if len(records) <= 1:
        return records

    mid = len(records) // 2
    left_half = merge_sort(records[:mid])
    right_half = merge_sort(records[mid:])

    return merge(left_half, right_half)


def merge(left, right):
    result = []
    i = j = 0

    while i < len(left) and j < len(right):
        if left[i]["month_score"] >= right[j]["month_score"]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    answer = """Привіт! Цей бот записує відстань яку ти пробіг!
Щоб додати відстань яку ви пробігли надішліть 
повідомлення зі скріншотом з додатку де показано
відстань, яку ви пробігли та підписом + 10.0
(замість + можна писати - Пробіг, Біг, Бег, Run)
(10.0 - відстань у кілометрах, якщо чило кругле 
можна писати і без крапки - 10)
Щоб дізнатися про можливості бота напишіть /help
Щоб подивитися таблицю результатів напишіть /table
Побігли?😎"""
    await update.message.reply_html(
        answer
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows the help message when the command /help is issued."""
    await update.message.reply_text(
        "Приклад повідомлення з відстанню"
    )
    await update.message.reply_photo(
        photo="screen_sample.jpg",
        caption="+10.15",
    )


async def runners_score_table(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows runners table"""
    with open(records_file, "r") as read_file:
        records = json.load(read_file)
        sorted_records = merge_sort(records)
    result = "РЕЙТИНГОВА ТАБЛИЦЯ\n"
    for i, record in enumerate(sorted_records):
        if i == 0:
            result += str(i + 1) + " " + record["runner_name"] + " " + str(round(record["month_score"], 3)) + " км " + "🥇\n"
        elif i == 1:
            result += str(i + 1) + " " + record["runner_name"] + " " + str(round(record["month_score"], 3)) + " км " + "🥈\n"
        elif i == 2:
            result += str(i + 1) + " " + record["runner_name"] + " " + str(round(record["month_score"], 3)) + " км " + "🥉\n"
        else:
            result += str(i + 1) + " " + record["runner_name"] + " " + str(round(record["month_score"], 3)) + " км\n"
    if result == "РЕЙТИНГОВА ТАБЛИЦЯ\n":
        await update.message.reply_text(
            "Таблиця ще пуста!"
        )
    else:
        await update.message.reply_text(
            result
        )

async def record_distance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Records runners score."""
    user_input = update.message.caption
    current_month = update.message.date.month
    current_day = update.message.date.day
    if "Пробіг" in user_input or "біг" in user_input or "run" in user_input or "+" in user_input or "бег" in user_input or "пробіг" in user_input or "Біг" in user_input or "Run" in user_input or "Бег" in user_input:
        user_input = user_input.replace("Пробіг", "")
        user_input = user_input.replace("пробіг", "")
        user_input = user_input.replace("Біг", "")
        user_input = user_input.replace("біг", "")
        user_input = user_input.replace("Run", "")
        user_input = user_input.replace("run", "")
        user_input = user_input.replace("Бег", "")
        user_input = user_input.replace("бег", "")
        user_input = user_input.replace("+", "")
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
                            "week_score" : round(runner_score,3),
                            "month_score" : round(runner_score,3),
                            "week_day" : current_day,
                            "current_month" : current_month
                        }
                        records.append(new_record)
                        this_user_week_score = new_record["week_score"]
                        this_user_month_score = new_record["month_score"]
                    else:
                        for record in records:
                            if record["runner_id"] == runner_id:
                                if record["current_month"] != current_month:
                                    record["week_score"] = 0.0
                                    record["month_score"] = 0.0
                                    record["week_day"] = current_day
                                    record["current_month"] = current_month
                                    this_user_week_score = record["week_score"]
                                    this_user_month_score = record["month_score"]
                                    break
                                else:
                                    if current_day - record["week_day"] == 7:
                                        record["week_score"] = round(runner_score,3)
                                        record["month_score"] += round(runner_score,3)
                                        record["week_day"] = current_day
                                        this_user_week_score = record["week_score"]
                                        this_user_month_score = record["month_score"]
                                        break
                                    else:
                                        record["week_score"] += round(runner_score,3)
                                        record["month_score"] += round(runner_score,3)
                                        this_user_week_score = record["week_score"]
                                        this_user_month_score = record["month_score"]
                                        break
                        else:
                            new_record = {
                                "runner_name" : runner_name,
                                "runner_id" : runner_id,
                                "week_score" : round(runner_score,3),
                                "month_score" : round(runner_score,3),
                                "week_day" : current_day,
                                "current_month" : current_month
                            }
                            records.append(new_record)
                            this_user_week_score = new_record["week_score"]
                            this_user_month_score = new_record["month_score"]
                with open(records_file, "w") as write_file:
                    json.dump(records, write_file)
                await update.message.reply_text(
                    "Результат записано!😌\nТвій результат : " + str(round(runner_score,3)) + " км!\nТвій результат за тиждень : " + str(round(this_user_week_score, 3)) + " км!\nТвій результат за місяць : " + rf"{round(this_user_month_score, 3)} км!💪"+ "\nІнстаграм: https://www.instagram.com/southrunners2025?igsh=MW1xcGJ1eGdkbThyag==\nІнстаграм розробника: https://www.instagram.com/kalika_perehoji/",
                )


def main() -> None:
    """Start the bot."""

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("table", runners_score_table))

    application.add_handler(MessageHandler(filters.PHOTO & filters.CAPTION, record_distance))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()