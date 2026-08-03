# telegram_bot/management/commands/run_bot.py

from django.core.management.base import BaseCommand
from telegram_bot.bot import telegram_bot


class Command(BaseCommand):
    help = 'Запускает Telegram бота'

    def handle(self, *args, **options):
        self.stdout.write('🤖 Запуск Telegram бота...')
        telegram_bot.setup()
        telegram_bot.run()