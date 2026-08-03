# telegram_bot/bot.py

import os
import asyncio
from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
from django.conf import settings
from django.core.management.base import BaseCommand
from users.models import User

# Токен бота
BOT_TOKEN = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')

# Хранилище chat_id пользователей (временное)
user_chats = {}


class TelegramBot:
    """Класс для работы с Telegram ботом"""

    def __init__(self):
        self.token = BOT_TOKEN
        self.application = None

    def setup(self):
        """Настройка бота"""
        if not self.token:
            print("⚠️ TELEGRAM_BOT_TOKEN не установлен в .env")
            return None

        self.application = ApplicationBuilder().token(self.token).build()

        # Команды
        self.application.add_handler(CommandHandler('start', self.start_command))
        self.application.add_handler(CommandHandler('help', self.help_command))

        # Callback для кнопок
        self.application.add_handler(CallbackQueryHandler(self.button_callback))

        return self.application

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /start"""
        user_id = update.effective_user.id
        username = update.effective_user.username or str(user_id)

        # Сохраняем chat_id
        user_chats[username] = user_id

        # Ищем пользователя в Django
        try:
            user = User.objects.filter(username=username).first()
            if user:
                user.telegram_id = user_id
                user.save()
        except:
            pass

        await update.message.reply_text(
            f"👋 Привет, {username}!\n\n"
            "Я бот ProFinder. Я буду присылать тебе уведомления о:\n"
            "💬 Новых сообщениях\n"
            "⭐ Новых отзывах\n"
            "📊 Статистике\n\n"
            "Используй /help для списка команд"
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Команда /help"""
        await update.message.reply_text(
            "📖 Помощь:\n\n"
            "/start - Начать работу\n"
            "/help - Помощь\n"
            "/stats - Моя статистика\n\n"
            "🔔 Уведомления приходят автоматически"
        )

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка нажатий на кнопки"""
        query = update.callback_query
        await query.answer()

        if query.data == 'notif_messages':
            await query.edit_message_text("💬 Уведомления о сообщениях включены")
        elif query.data == 'notif_reviews':
            await query.edit_message_text("⭐ Уведомления об отзывах включены")
        elif query.data == 'notif_stats':
            await query.edit_message_text("📊 Статистика будет приходить раз в день")
        elif query.data == 'notif_off':
            await query.edit_message_text("🔕 Все уведомления отключены")

    def send_notification(self, user_id, message, link=None):
        """Отправка уведомления пользователю"""
        if not self.application or not user_id:
            return

        try:
            keyboard = None
            if link:
                keyboard = [[InlineKeyboardButton("🔗 Перейти", url=link)]]
                reply_markup = InlineKeyboardMarkup(keyboard)
            else:
                reply_markup = None

            # Отправляем сообщение (синхронная обертка)
            import asyncio
            asyncio.run(self._send_message(user_id, message, reply_markup))
        except Exception as e:
            print(f"Ошибка отправки Telegram уведомления: {e}")

    async def _send_message(self, chat_id, message, reply_markup=None):
        """Асинхронная отправка сообщения"""
        try:
            await self.application.bot.send_message(
                chat_id=chat_id,
                text=message,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        except Exception as e:
            print(f"Ошибка отправки: {e}")

    def run(self):
        """Запуск бота"""
        if self.application:
            print("🤖 Запуск Telegram бота...")
            self.application.run_polling()


# Глобальный экземпляр бота
telegram_bot = TelegramBot()


# Функции для отправки уведомлений
def send_message_notification(message):
    """Уведомление о новом сообщении"""
    try:
        chat = message.chat
        recipient = chat.get_other_user(message.sender)

        if recipient.telegram_id and recipient.telegram_notifications:
            text = (
                f"💬 <b>Новое сообщение</b>\n\n"
                f"👤 От: {message.sender.username}\n"
                f"📝 {message.content[:200]}{'...' if len(message.content) > 200 else ''}\n\n"
                f"📅 {message.created_at.strftime('%d.%m.%Y %H:%M')}"
            )
            from django.conf import settings
            link = f"{getattr(settings, 'SITE_URL', '')}/chat/"
            telegram_bot.send_notification(recipient.telegram_id, text, link)
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")


def send_review_notification(review):
    """Уведомление о новом отзыве"""
    try:
        provider = review.provider
        owner = provider.created_by

        if owner and owner.telegram_id and owner.telegram_notifications:
            text = (
                f"⭐ <b>Новый отзыв!</b>\n\n"
                f"👤 {review.user.username}\n"
                f"📊 Оценка: {'⭐' * review.rating}\n"
                f"💬 {review.comment[:200]}{'...' if len(review.comment) > 200 else ''}\n\n"
                f"📅 {review.created_at.strftime('%d.%m.%Y %H:%M')}"
            )
            from django.conf import settings
            link = f"{getattr(settings, 'SITE_URL', '')}/provider/{provider.id}/"
            telegram_bot.send_notification(owner.telegram_id, text, link)
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")