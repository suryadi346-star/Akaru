"""
LibVoice — Termux TTS & STT wrapper.
Fix: shell injection patched via shlex.quote
"""

import asyncio
import shlex
from typing import Optional


class LibVoice:

    @staticmethod
    async def _is_available(cmd: str) -> bool:
        proc = await asyncio.create_subprocess_shell(
            f"command -v {cmd} > /dev/null 2>&1",
            stdout=asyncio.subprocess.DEVNULL,
            stderr=asyncio.subprocess.DEVNULL,
        )
        await proc.wait()
        return proc.returncode == 0

    @staticmethod
    async def say(msg: str) -> None:
        """
        Text-to-speech via Termux.
        FIX: shlex.quote mencegah shell injection dari user input.
        """
        if not await LibVoice._is_available("termux-tts-speak"):
            print("[TTS] termux-tts-speak tidak tersedia.")
            return
        try:
            safe_msg = shlex.quote(msg.lower())
            proc = await asyncio.create_subprocess_shell(
                f"termux-tts-speak {safe_msg}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await proc.communicate()
        except Exception as e:
            print(f"[TTS Error] {e}")

    @staticmethod
    async def listen() -> Optional[str]:
        """
        Speech-to-text via Termux.
        """
        if not await LibVoice._is_available("termux-speech-to-text"):
            print("[STT] termux-speech-to-text tidak tersedia.")
            print("Install: pkg install termux-api")
            return None
        try:
            proc = await asyncio.create_subprocess_shell(
                "termux-speech-to-text",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0 and stdout:
                return stdout.decode().strip()
            if stderr:
                print(f"[STT Error] {stderr.decode().strip()}")
        except Exception as e:
            print(f"[STT Error] {e}")
        return None
