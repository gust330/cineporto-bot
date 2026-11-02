"""Telegram bot interface for CinePorto."""
import logging
import os
import time
import urllib.request
import urllib.parse
import json
import html
from typing import Optional, Dict, Any, List
from cineporto.service import CinePortoService
from cineporto.cinemas_data import PORTO_CINEMAS

logger = logging.getLogger(__name__)


class CinePortoBot:
    def __init__(self, token: Optional[str] = None, timeout: int = 25):
        self.token = token or ""
        self.timeout = timeout
        self.service = CinePortoService()
        self.api_base = f"https://api.telegram.org/bot{self.token}"

    def send_message(self, chat_id: str, text: str, parse_mode: str = "HTML") -> Optional[Dict[str, Any]]:
        if not self.token:
            logger.warning("Telegram token missing; skipping network send.")
            return None
        url = f"{self.api_base}/sendMessage"
        payload = urllib.parse.urlencode({
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode,
            "disable_web_page_preview": "true",
        }).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode("utf-8", errors="replace"))
        except Exception as e:
            logger.error(f"Failed to send telegram message: {e}")
            return None

    def handle_message(self, text: str, chat_id: str) -> str:
        cmd = text.strip()

        if cmd in ["/start", "/iniciar"]:
            return (
                "👋 <b>Olá! Sou o CinePorto Bot</b> 🎬\n\n"
                "Envie-me o <b>nome de qualquer filme</b> (já em cartaz ou prestes a estrear) e eu mostro e comparo:\n"
                "• 📍 <b>Cinemas</b> de todo o Distrito do Porto\n"
                "• ⏰ <b>Sessões & Datas</b> em cada sala\n"
                "• 💰 <b>Preços & Descontos</b> (Standard, Estudante, Dia do Espectador, Cartão NOS 2-por-1)\n"
                "• ✨ <b>Salas Especiais</b> (IMAX, 4DX, iSense, ScreenX)\n\n"
                "💡 <i>Experimente enviar agora:</i>\n"
                "<code>Gladiator II</code>\n"
                "<code>Clayface</code>\n"
                "<code>Avatar</code>\n\n"
                "📌 <b>Outros Comandos:</b>\n"
                "/cinemas — Lista todos os cinemas cobertos no distrito\n"
                "/estreias — Próximas estreias anunciadas\n"
                "/ajuda — Dicas e preços de referência"
            )

        if cmd in ["/cinemas", "/salas"]:
            lines = [
                "🏛️ <b>Cinemas Cobertos no Distrito do Porto:</b>\n",
            ]
            by_muni = {}
            for c in PORTO_CINEMAS.values():
                by_muni.setdefault(c.municipality, []).append(c)

            for muni, c_list in sorted(by_muni.items()):
                lines.append(f"📍 <b>{html.escape(muni)}:</b>")
                for c in c_list:
                    extras = f" <i>[{', '.join(c.special_formats)}]</i>" if c.special_formats else ""
                    lines.append(f"  • {html.escape(c.name)}{extras}")
                lines.append("")

            lines.append("<i>Envie o nome de um filme para ver sessões nestas salas!</i>")
            return "\n".join(lines)

        if cmd in ["/estreias", "/brevemente"]:
            soon_movies = self.service.nos_scraper.search_movies("")
            soon_list = [m for m in soon_movies if m.status == "premiere_soon"][:8]
            if not soon_list:
                return "🚀 <b>Próximas Estreias no Porto:</b>\n\nConsulte em breve ou pesquise o título desejado!"
            lines = ["🚀 <b>Próximas Estreias Anunciadas (Cinemas do Porto):</b>\n"]
            for m in soon_list:
                date_str = m.release_date.split("T")[0] if m.release_date else "Brevemente"
                title = html.escape(m.title_pt)
                if m.title_original and m.title_original.lower() != m.title_pt.lower():
                    title += f" ({html.escape(m.title_original)})"
                lines.append(f"• <b>{title}</b> — 🗓️ {date_str}")
            lines.append("\n<i>Envie o nome de qualquer uma das estreias para verificar pré-venda e salas!</i>")
            return "\n".join(lines)

        if cmd in ["/ajuda", "/help"]:
            return (
                "ℹ️ <b>Guia CinePorto:</b>\n\n"
                "1️⃣ <b>Pesquisar Filme:</b> Basta escrever o nome do filme no chat (ex: <i>Gladiator</i>, <i>Dune</i>, <i>Clayface</i>).\n"
                "2️⃣ <b>Comparativo:</b> O bot compara automaticamente todos os cinemas do Porto com sessões marcadas, ordenados por preço e sala.\n"
                "3️⃣ <b>Dicas de Poupança no Porto:</b>\n"
                "• <b>Cartão NOS / WTF:</b> 2 bilhetes pelo preço de 1 nos Cinemas NOS (~3.95€/cada).\n"
                "• <b>Quartas-feiras:</b> Dia do Espectador na UCI Arrábida 20 (5.80€).\n"
                "• <b>Segundas-feiras:</b> Cinema Trindade a 5.00€ e 2ª feira digital NOS a 7.35€.\n"
                "• <b>Cartão Tripass:</b> Descontos no Cinema Trindade e teatros municipais."
            )

        # Natural movie search query
        comp = self.service.query_movie(cmd)
        if not comp:
            cmd_esc = html.escape(cmd)
            return (
                f"🔍 Não encontrei sessões ou estreias para '<b>{cmd_esc}</b>'.\n\n"
                "Verifique se o nome está correto (pode ser o título em português ou em inglês).\n"
                "Experimente títulos populares como <code>Gladiator II</code>, <code>Clayface</code>, ou use /estreias."
            )

        return self.service.format_comparison(comp)

    def _fetch_updates(self, offset: int, timeout: int = 20) -> List[Dict[str, Any]]:
        """Fetch pending updates from Telegram API."""
        if not self.token:
            return []
        url = f"{self.api_base}/getUpdates?offset={offset}&timeout={timeout}"
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout + 10) as resp:
                data = json.loads(resp.read().decode("utf-8", errors="replace"))
                return data.get("result", [])
        except Exception as e:
            logger.error(f"Error fetching updates from Telegram: {e}")
            return []

    def process_updates_once(self, state_file: Optional[str] = None) -> int:
        """
        Polls pending updates once, handles incoming messages, acknowledges the offset,
        and persists state. Ideal for serverless, cron jobs, and CI workflows.
        """
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN is not configured.")

        offset = 0
        state = {}
        if state_file and os.path.exists(state_file):
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    state = json.load(f)
                    offset = state.get("last_offset", 0)
            except Exception as e:
                logger.warning(f"Could not load state file {state_file}: {e}")

        updates = self._fetch_updates(offset=offset, timeout=5)
        processed_count = 0

        for u in updates:
            update_id = u.get("update_id", 0)
            offset = max(offset, update_id + 1)
            msg = u.get("message", {})
            chat_id = str(msg.get("chat", {}).get("id", ""))
            text = msg.get("text", "")

            if chat_id and text:
                logger.info(f"Processing message from chat {chat_id}: {text}")
                reply = self.handle_message(text, chat_id)
                self.send_message(chat_id, reply)
                processed_count += 1

        if state_file:
            state["last_offset"] = offset
            try:
                with open(state_file, "w", encoding="utf-8") as f:
                    json.dump(state, f, indent=2)
            except Exception as e:
                logger.error(f"Failed to write state file {state_file}: {e}")

        return processed_count

    def run_polling(self):
        """Starts continuous long polling loop for incoming Telegram updates."""
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN is not configured.")

        offset = 0
        logger.info("CinePortoBot polling started...")
        print("🤖 CinePortoBot está ativo e a escutar mensagens no Telegram...")

        while True:
            try:
                updates = self._fetch_updates(offset=offset, timeout=20)
                for u in updates:
                    offset = max(offset, u["update_id"] + 1)
                    msg = u.get("message", {})
                    chat_id = str(msg.get("chat", {}).get("id", ""))
                    text = msg.get("text", "")

                    if chat_id and text:
                        logger.info(f"Received query from chat {chat_id}: {text}")
                        reply = self.handle_message(text, chat_id)
                        self.send_message(chat_id, reply)

            except KeyboardInterrupt:
                print("\nEncerrando bot...")
                break
            except Exception as e:
                logger.error(f"Polling error: {e}")
                time.sleep(3)
