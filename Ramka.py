import struct

from KoderCRC16 import KoderCRC16

# Definicja nagłówka: 1 bajt (SEQ) + 2 bajty (CRC)
NAGLOWEK_FORMAT = '!BH'  # ! - siec, B - unsigned char (1), H - unsigned short (2)
ROZMIAR_NAGLOWKA = struct.calcsize(NAGLOWEK_FORMAT)


class Ramka:
    def __init__(self, seq_num: int, dane: bytes, crc: int = None):
        self.seq_num = seq_num & 0xFF
        self.dane = dane

        if crc is None:
            #CRC dla nowej ramki
            self.crc = KoderCRC16.oblicz(self.dane)
        else:
            # Użyj podanego CRC (rozpakowanie)
            self.crc = crc

    def pakuj(self) -> bytes:
        naglowek = struct.pack(NAGLOWEK_FORMAT, self.seq_num, self.crc)
        return naglowek + self.dane

    @staticmethod
    def rozpakuj(ramka_bajty: bytes):
        if len(ramka_bajty) < ROZMIAR_NAGLOWKA:
            raise ValueError("Ramka zbyt krótka (uszkodzony nagłówek).")

        naglowek_bajty = ramka_bajty[:ROZMIAR_NAGLOWKA]
        dane_bajty = ramka_bajty[ROZMIAR_NAGLOWKA:]

        seq_num, crc = struct.unpack(NAGLOWEK_FORMAT, naglowek_bajty)

        return Ramka(seq_num=seq_num, dane=dane_bajty, crc=crc)

    def czy_poprawna(self) -> bool:
        return KoderCRC16.weryfikuj(self.dane, self.crc)

    # debugowanie
    def __repr__(self):
        dane_str = self.dane.decode('utf-8', errors='ignore')
        if len(dane_str) > 20:
            dane_str = dane_str[:20] + "..."
        return f"Ramka(SEQ={self.seq_num}, CRC=0x{self.crc:04X}, OK={self.czy_poprawna()}, Dane='{dane_str}')"