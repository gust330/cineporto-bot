import pytest
from unittest.mock import patch, MagicMock
from cineporto.bot import CinePortoBot
from cineporto.models import Movie, ComparisonResult

def test_bot_command_start():
    bot = CinePortoBot(token="fake_token")
    msg = bot.handle_message("/start", chat_id="123")
    assert "CinePorto Bot" in msg
    assert "/cinemas" in msg
    assert "/estreias" in msg

def test_bot_command_cinemas():
    bot = CinePortoBot(token="fake_token")
    msg = bot.handle_message("/cinemas", chat_id="123")
    assert "Cinemas NOS NorteShopping" in msg
    assert "UCI Cinemas Arrábida 20" in msg
    assert "Cinema Trindade" in msg
    assert "Distrito do Porto" in msg

def test_bot_movie_query_found():
    bot = CinePortoBot(token="fake_token")
    fake_comp = ComparisonResult(
        movie=Movie(id="1", title_pt="Clayface"),
        grouped_by_cinema={"Cinemas NOS NorteShopping": []},
        cheapest_cinema="Cinemas NOS NorteShopping",
        cheapest_price=7.90
    )
    with patch.object(bot.service, "query_movie", return_value=fake_comp):
        with patch.object(bot.service, "format_comparison", return_value="<b>Clayface</b>\nSessões: 18:00"):
            msg = bot.handle_message("Clayface", chat_id="123")
            assert "Clayface" in msg
            assert "Sessões: 18:00" in msg

def test_bot_movie_query_not_found():
    bot = CinePortoBot(token="fake_token")
    with patch.object(bot.service, "query_movie", return_value=None):
        msg = bot.handle_message("FilmeInexistenteXYZ", chat_id="123")
        assert "Não encontrei" in msg


def test_bot_query_escapes_special_characters():
    bot = CinePortoBot(token="fake_token")
    with patch.object(bot.service, "query_movie", return_value=None):
        msg = bot.handle_message("Tom & <Jerry>", chat_id="123")
        assert "Tom &amp; &lt;Jerry&gt;" in msg
        assert "<Jerry>" not in msg


def test_bot_process_updates_once(tmp_path):
    state_file = str(tmp_path / "state.json")
    bot = CinePortoBot(token="fake_token")
    fake_updates_payload = {
        "ok": True,
        "result": [
            {
                "update_id": 100,
                "message": {
                    "chat": {"id": 12345},
                    "text": "/cinemas"
                }
            }
        ]
    }
    with patch.object(bot, "_fetch_updates", return_value=fake_updates_payload.get("result")):
        with patch.object(bot, "send_message") as mock_send:
            count = bot.process_updates_once(state_file=state_file)
            assert count == 1
            mock_send.assert_called_once()
            args, _ = mock_send.call_args
            assert args[0] == "12345"
            assert "Cinemas NOS NorteShopping" in args[1]

            # Verify state was saved
            import json
            with open(state_file, "r") as f:
                state = json.load(f)
                assert state.get("last_offset") == 101
