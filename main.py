from decouple import config
import json
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

SCORE = range(1)
TOKEN = config("TOKEN")
records_file = "run_records.json"


def get_keyboard1():
    reply_keyboard = [
        ["Записати відстань"],
        ["Результат"],
        ["Рейтингова таблиця"],
        ["Про бота"]
    ]
    return ReplyKeyboardMarkup(reply_keyboard)


def get_keyboard2():
    reply_keyboard = [
        ["Відмінити"]
    ]
    return ReplyKeyboardMarkup(reply_keyboard)


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
    await update.message.reply_html(
        "Привіт! Цей бот записує відстань яку ти пробіг!\nЩоб додати відстань яку ви пробігли натисніть 'Записати відстань'\nЩоб дізнатися про можливості бота натисніть 'Про бота'\nПобігли?😎",
        reply_markup=get_keyboard1()
    )


async def my_score_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows the runner score when the command /my_score is issued."""
    with open(records_file, "r") as read_file:
        records = json.load(read_file)
        user = update.effective_user
        runner_id = update.message.from_user.id
        if records == []:
            await update.message.reply_html(
                "Не має жодного запису про бігунів!😔\nЩоб дізнатися про можливості бота натисніть 'Про бота'",
                reply_markup=get_keyboard1()
            )
        else:
            for record in records:
                if record["runner_id"] == runner_id:
                    this_user_week_score = record["week_score"]
                    this_user_month_score = record["month_score"]
                    answer = rf"Привіт {user.mention_html()}!" + "\nТвій результат за тиждень : " + str(this_user_week_score) + " км!\nТвій результат за місяць : " + rf"{this_user_month_score} км!💪"+ "\nНаш Інстаграм: https://www.instagram.com/southrunners2025?igsh=MW1xcGJ1eGdkbThyag==\nІнстаграм розробника: https://www.instagram.com/kalika_perehoji/"
                    await update.message.reply_photo(
                        photo="image.jpg",
                        caption=answer,
                        parse_mode="HTML",
                        reply_markup=get_keyboard1()
                    )
                    break
            else:
                answer = rf"Привіт {user.mention_html()}!" + "\nНе маю записів про тебе!😔\nЩоб дізнатися про можливості бота натисніть 'Про бота'"
                await update.message.reply_html(
                    answer,
                    reply_markup=get_keyboard1()
                )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows the help message when the command /help is issued."""
    await update.message.reply_text(
        "Привіт! Цей бот записує відстань яку ти пробіг!\nЩоб додати відстань яку ви пробігли натисніть 'Записати відстань'\nЩоб подивитися свій поточний результат натисніть 'Результат'\nЩоб подивитися рейтингову таблицю натисніть 'Рейтингова таблиця'\nЩоб дізнатися про можливості бота натисніть 'Про бота'",
        reply_markup=get_keyboard1()
    )


async def runners_score_table(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    with open(records_file, "r") as read_file:
        records = json.load(read_file)
        sorted_records = merge_sort(records)
    result = "РЕЙТИНГОВА ТАБЛИЦЯ\n"
    for i, record in enumerate(sorted_records):
        if i == 0:
            result += str(i + 1) + " " + record["runner_name"] + " " + str(record["month_score"]) + " км " + "🥇\n"
        elif i == 1:
            result += str(i + 1) + " " + record["runner_name"] + " " + str(record["month_score"]) + " км " + "🥈\n"
        elif i == 2:
            result += str(i + 1) + " " + record["runner_name"] + " " + str(record["month_score"]) + " км " + "🥉\n"
        else:
            result += str(i + 1) + " " + record["runner_name"] + " " + str(record["month_score"]) + " км\n"
    if result == "РЕЙТИНГОВА ТАБЛИЦЯ\n":
        await update.message.reply_text(
            "Таблиця ще пуста!",
            reply_markup=get_keyboard1()
        )
    else:
        await update.message.reply_text(
            result,
            reply_markup=get_keyboard1()
        )


async def record_distance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Щоб записати відстань треба написати повідомлення типу:\n+ 10.0\n(замість + можна написати також run, біг, Пробіг, бег)\n(10.0 - відстань у км, можна писати і 10 без крапки)\nЯкщо не хочете записувати результат натисніть 'Відмінити'",
        reply_markup=get_keyboard2()
    )
    return SCORE


async def save_distance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Records runners score."""
    user_input = update.message.text
    current_month = update.message.date.month
    current_day = update.message.date.day
    if "Пробіг" in user_input or "біг" in user_input or "run" in user_input or "+" in user_input or "бег" in user_input:
        user_input = user_input.replace("Пробіг", "")
        user_input = user_input.replace("біг", "")
        user_input = user_input.replace("run", "")
        user_input = user_input.replace("+", "")
        user_input = user_input.replace("бег", "")
        user_input = user_input.replace(" ", "")
        if user_input[0] == "0" and not user_input[1] == ".":
            await update.message.reply_text(
                "Результат введено не вірно!\nЩоб записати відстань треба написати повідомлення типу:\n+ 10.0\n(замість + можна написати також run, біг, Пробіг, бег)\n(10.0 - відстань у км, можна писати і 10 без крапки)",
                reply_markup=get_keyboard1()
            )
            return ConversationHandler.END
        else:
            try:
                user_input = float(user_input)
            except:
                await update.message.reply_text(
                    "Результат введено не вірно!\nЩоб записати відстань треба написати повідомлення типу:\n+ 10.0\n(замість + можна написати також run, біг, Пробіг, бег)\n(10.0 - відстань у км, можна писати і 10 без крапки)",
                    reply_markup=get_keyboard1()
                )
                return ConversationHandler.END
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
                            "week_score" : runner_score,
                            "month_score" : runner_score,
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
                                        record["week_score"] = runner_score
                                        record["month_score"] += runner_score
                                        record["week_day"] = current_day
                                        this_user_week_score = record["week_score"]
                                        this_user_month_score = record["month_score"]
                                        break
                                    else:
                                        record["week_score"] += runner_score
                                        record["month_score"] += runner_score
                                        this_user_week_score = record["week_score"]
                                        this_user_month_score = record["month_score"]
                                        break
                        else:
                            new_record = {
                                "runner_name" : runner_name,
                                "runner_id" : runner_id,
                                "week_score" : runner_score,
                                "month_score" : runner_score,
                                "week_day" : current_day,
                                "current_month" : current_month
                            }
                            records.append(new_record)
                            this_user_week_score = new_record["week_score"]
                            this_user_month_score = new_record["month_score"]
                with open(records_file, "w") as write_file:
                    json.dump(records, write_file)
                await update.message.reply_photo(
                    photo="image.jpg",
                    caption="Результат записано!😌\nТвій результат : " + str(runner_score) + " км!\nТвій результат за тиждень : " + str(this_user_week_score) + " км!\nТвій результат за місяць : " + rf"{this_user_month_score} км!💪"+ "\nІнстаграм: https://www.instagram.com/southrunners2025?igsh=MW1xcGJ1eGdkbThyag==\nІнстаграм розробника: https://www.instagram.com/kalika_perehoji/",
                    reply_markup=get_keyboard1()
                )
                return ConversationHandler.END
    else:
        await update.message.reply_text(
            "Результат введено не вірно!\nЩоб записати відстань треба написати повідомлення типу:\n+ 10.0\n(замість + можна написати також run, біг, Пробіг, бег)\n(10.0 - відстань у км, можна писати і 10 без крапки)",
            reply_markup=get_keyboard1()
        )
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await update.message.reply_text(
        "Результат не збережено", reply_markup=get_keyboard1()
    )

    return ConversationHandler.END


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shows the help message when the command /help is issued."""
    await update.message.reply_text(
        "Невідома команда",
        reply_markup=get_keyboard1()
    )


def main() -> None:
    """Start the bot."""

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Результат$"), my_score_command))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Рейтингова таблиця$"), runners_score_table))
    application.add_handler(MessageHandler(filters.TEXT & filters.Regex("^Про бота$"), help_command))

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Записати відстань$"), record_distance)],
        states={
            SCORE: [MessageHandler(filters.TEXT & ~filters.COMMAND, save_distance)],
        },
        fallbacks=[MessageHandler(filters.Regex("^Відмінити$"), cancel)],
    )

    application.add_handler(conv_handler)

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_command))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()