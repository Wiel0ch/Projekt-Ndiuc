import struct

from KoderCRC16 import KoderCRC16

# Definicja nagłówka: 1 bajt (SEQ) + 2 bajty (CRC)
NAGLOWEK_FORMAT = '!BH'  # ! - siec, B - unsigned char (1), H - unsigned short (2)
ROZMIAR_NAGLOWKA = struct.calcsize(NAGLOWEK_FORMAT)


class Ramka:
    """Definicja ramki transmisyjnej (kontener na dane)."""

    def __init__(self, seq_num: int, dane: bytes, crc: int = None):
        self.seq_num = seq_num & 0xFF  # Upewnij się, że mieści się w 1 bajcie
        self.dane = dane

        if crc is None:
            # Oblicz CRC, jeśli tworzymy nową ramkę
            self.crc = KoderCRC16.oblicz(self.dane)
        else:
            # Użyj podanego CRC (przy rozpakowywaniu)
            self.crc = crc

    def pakuj(self) -> bytes:
        """Konwertuje obiekt Ramka na ciąg bajtów do wysłania."""
        naglowek = struct.pack(NAGLOWEK_FORMAT, self.seq_num, self.crc)
        return naglowek + self.dane

    @staticmethod
    def rozpakuj(ramka_bajty: bytes):
        """Konwertuje ciąg bajtów z powrotem na obiekt Ramka."""
        if len(ramka_bajty) < ROZMIAR_NAGLOWKA:
            raise ValueError("Ramka zbyt krótka (uszkodzony nagłówek).")

        naglowek_bajty = ramka_bajty[:ROZMIAR_NAGLOWKA]
        dane_bajty = ramka_bajty[ROZMIAR_NAGLOWKA:]

        seq_num, crc = struct.unpack(NAGLOWEK_FORMAT, naglowek_bajty)

        return Ramka(seq_num=seq_num, dane=dane_bajty, crc=crc)

    def czy_poprawna(self) -> bool:
        """Sprawdza poprawność CRC tej ramki."""
        return KoderCRC16.weryfikuj(self.dane, self.crc)

    def __repr__(self):
        """Ładna reprezentacja do debugowania."""
        dane_str = self.dane.decode('utf-8', errors='ignore')
        if len(dane_str) > 20:
            dane_str = dane_str[:20] + "..."
        return f"Ramka(SEQ={self.seq_num}, CRC=0x{self.crc:04X}, OK={self.czy_poprawna()}, Dane='{dane_str}')"