import struct
from KoderCRC16 import KoderCRC16


class Ramka:
    # Stałe definicje
    FLAG_BYTE = 0x7E  # Flaga początku/końca
    ESCAPE_BYTE = 0x7D  # Znak ucieczki
    XOR_KEY = 0x20  # Klucz do XORowania przy escapingu

    # Typy ramek
    TYPE_DATA = 0x00
    TYPE_ACK = 0x01
    TYPE_NAK = 0x02

    def __init__(self, addr_src: int, addr_dst: int, seq_num: int, dane: bytes = b'', msg_type=TYPE_DATA, is_eof=False):
        self.addr_src = addr_src & 0xFF
        self.addr_dst = addr_dst & 0xFF
        self.seq = seq_num & 0xFF
        self.dane = dane
        self.msg_type = msg_type
        self.is_eof = is_eof
        self.len = len(dane)
        self.crc = 0
        self._calculated_crc = 0  # Do weryfikacji po odbiorze

    def pakuj(self) -> bytes:
        """Tworzy ramkę z flagami i bytestuffingiem."""
        # 1. Nagłówek: DST(1B), SRC(1B), CTRL(1B), SEQ(1B), LEN(2B)
        ctrl_byte = (self.msg_type << 6) | (int(self.is_eof) << 5)
        header = struct.pack('!BBBBH', self.addr_dst, self.addr_src, ctrl_byte, self.seq, self.len)

        # 2. Payload do CRC (Nagłówek + Dane)
        raw_payload = header + self.dane

        # 3. Obliczenie i doklejenie CRC
        self.crc = KoderCRC16.oblicz(raw_payload)
        crc_bytes = self.crc.to_bytes(2, byteorder='big')
        frame_content = raw_payload + crc_bytes

        # 4. Byte Stuffing
        stuffed_content = self._byte_stuffing(frame_content)

        # 5. Dodanie flag
        return bytes([self.FLAG_BYTE]) + stuffed_content + bytes([self.FLAG_BYTE])

    @staticmethod
    def rozpakuj(ramka_bajty: bytes):
        """Odtwarza obiekt Ramka z ciągu bajtów."""
        if len(ramka_bajty) < 2:
            return None  # Zbyt krótka na cokolwiek

        # 1. Usunięcie flag (zakładamy, że dostajemy ramkę od flagi do flagi)
        temp_bytes = ramka_bajty
        if temp_bytes[0] == Ramka.FLAG_BYTE:
            temp_bytes = temp_bytes[1:]
        if len(temp_bytes) > 0 and temp_bytes[-1] == Ramka.FLAG_BYTE:
            temp_bytes = temp_bytes[:-1]

        # 2. Byte Unstuffing
        try:
            raw_content = Ramka._byte_unstuffing(temp_bytes)
        except ValueError:
            return None  # Błąd formatu

        # Min. rozmiar: 6B nagłówka + 2B CRC = 8B
        if len(raw_content) < 8:
            return None

        # 3. Wyodrębnienie CRC
        received_crc = int.from_bytes(raw_content[-2:], byteorder='big')
        data_to_check = raw_content[:-2]

        # 4. Parsowanie nagłówka
        header = data_to_check[:6]
        payload = data_to_check[6:]

        dst, src, ctrl, seq, length = struct.unpack('!BBBBH', header)

        if len(payload) != length:
            return None  # Uszkodzona długość

        msg_type = (ctrl >> 6) & 0x03
        is_eof = bool((ctrl >> 5) & 0x01)

        # 5. Tworzenie obiektu
        r = Ramka(src, dst, seq, payload, msg_type, is_eof)
        r.crc = received_crc
        r._calculated_crc = KoderCRC16.oblicz(data_to_check)

        return r

    def czy_poprawna(self) -> bool:
        return self.crc == self._calculated_crc

    @staticmethod
    def _byte_stuffing(data: bytes) -> bytes:
        res = bytearray()
        for b in data:
            if b == Ramka.FLAG_BYTE or b == Ramka.ESCAPE_BYTE:
                res.append(Ramka.ESCAPE_BYTE)
                res.append(b ^ Ramka.XOR_KEY)
            else:
                res.append(b)
        return bytes(res)

    @staticmethod
    def _byte_unstuffing(data: bytes) -> bytes:
        res = bytearray()
        skip_next = False
        for i in range(len(data)):
            if skip_next:
                skip_next = False
                continue
            b = data[i]
            if b == Ramka.ESCAPE_BYTE:
                if i + 1 >= len(data):
                    raise ValueError("Escape na końcu")
                res.append(data[i + 1] ^ Ramka.XOR_KEY)
                skip_next = True
            else:
                res.append(b)
        return bytes(res)

    def __str__(self):
        typ_str = {0: "DATA", 1: "ACK", 2: "NAK"}.get(self.msg_type, "?")
        return f"[Ramka {typ_str} SEQ={self.seq}]"