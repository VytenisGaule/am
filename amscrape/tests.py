from django.test import TestCase
from .models import Rule
from unittest.mock import patch


class RuleTestCase(TestCase):
    def setUp(self):
        super().setUp()
        Rule.objects.create(passive_function='send_warning')

    @patch('amscrape.discord_bot.send_warning')
    def test_perform_reaction(self, mock_send_warning):
        print("Performing reaction...")
        rule = Rule.objects.first()
        print(rule.passive_function)
        print(rule.conditions)
        discord_ids = []

        def store_discord_id(discord_id):
            discord_ids.append(discord_id)
        mock_send_warning.side_effect = store_discord_id
        rule.perform_reaction()

        print("Discord IDs:", discord_ids)
