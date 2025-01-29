from discord_webhook import DiscordWebhook
from am.settings import DISCORD_WEBHOOK_URL
from celery import shared_task


@shared_task
def send_warning(user_id, message):
    webhook = DiscordWebhook(url=DISCORD_WEBHOOK_URL, rate_limit_retry=True, content=f'<@{user_id}> - {message}')
    allowed_mentions = {"users": [user_id]}
    response = webhook.execute()
