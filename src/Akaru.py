"""
Akaru - The Shadow Architect AI Assistant
Entry point utama.
"""

import asyncio
import sys
from typing import Optional, Tuple
from dotenv import load_dotenv

from Manager.ConfigManager import ConfigManager
from Manager.ChatManager import ChatManager
from lib.LibVoice import LibVoice


class Akaru:
    """
    Akaru AI Assistant — multi-provider, voice & text interaction.
    """

    MODES = {0: "Voice", 1: "Text"}
    EXIT_COMMANDS = {"exit", "bye", "quit", "keluar"}

    def __init__(self):
        load_dotenv()
        self.config = ConfigManager()
        self.chat_manager = ChatManager(self.config)

    def _display_welcome(self) -> None:
        provider = self.config.get_active_provider()
        model = self.config.get_model_id()
        print(f"\n{'='*40}")
        print(f"  AKARU — The Shadow Architect")
        print(f"  Provider : {provider}")
        print(f"  Model    : {model}")
        print(f"{'='*40}")
        print("  Mode:")
        for k, v in self.MODES.items():
            print(f"  [{k}] {v}")
        print()

    def _get_mode(self) -> Optional[int]:
        try:
            mode = int(input("Select mode: "))
            if mode not in self.MODES:
                print("Mode tidak valid. Pilih 0 atau 1.")
                return None
            return mode
        except (ValueError, EOFError):
            print("Input tidak valid.")
            return None

    async def _process_voice(self) -> Tuple[str, bool]:
        print("\n[Listening...]")
        question = await LibVoice.listen()
        if not question:
            return "Tidak bisa menangkap suara. Coba lagi.", True
        print(f"\nLo: {question}")
        if question.lower() in self.EXIT_COMMANDS:
            return "", False
        response = await self.chat_manager.ask(question)
        print(f"\nAkaru: {response}\n")
        await LibVoice.say(response)
        return response, True

    async def _process_text(self) -> Tuple[str, bool]:
        try:
            question = input("Lo: ").strip()
        except EOFError:
            return "", False
        if not question:
            return "Input kosong.", True
        if question.lower() in self.EXIT_COMMANDS:
            return "", False
        response = await self.chat_manager.ask(question)
        print(f"\nAkaru: {response}\n")
        return response, True

    async def _run_loop(self, mode: int) -> None:
        mode_name = self.MODES[mode]
        print(f"Mode: {mode_name}. Ketik 'exit' untuk keluar.\n")
        while True:
            try:
                if mode == 0:
                    _, should_continue = await self._process_voice()
                else:
                    _, should_continue = await self._process_text()
                if not should_continue:
                    break
            except KeyboardInterrupt:
                print("\n[Interrupted]")
                break
            except Exception as e:
                print(f"[Error] {e}")
                break

    async def run(self) -> None:
        self._display_welcome()
        mode = self._get_mode()
        if mode is None:
            return
        await self._run_loop(mode)
        print("\nSampai jumpa. — Akaru")


if __name__ == "__main__":
    akaru = Akaru()
    asyncio.run(akaru.run())
