import struct
from KoderCRC16 import KoderCRC16
from KoderCRC8 import KoderCRC8


class Ramka:
    # Stałe fizyczne
    FLAG_BYTE = 0x7E
    ESCAPE_BYTE = 0x7D
    XOR_KEY = 0x20

    # Typy ramek
    TYPE_DATA = 0x00
    TYPE_ACK = 0x01
    TYPE_NAK = 0x02

    # Typy CRC
    CRC8 = 8
    CRC16 = 16

    def __init__(self, addr_src, addr_dst, seq_num,
                 dane=b'', msg_type=TYPE_DATA, is_eof=False,
                 crc_type=CRC16):

        self.addr_src = addr_src & 0xFF
        self.addr_dst = addr_dst & 0xFF
        self.seq = seq_num & 0xFF
        self.dane = dane
        self.msg_type = msg_type
        self.is_eof = is_eof
        self.len = len(dane)

        self.crc_type = crc_type
        self.crc = 0
        self._calculated_crc = 0

    def pakuj(self) -> bytes:
        # Nagłówek
        ctrl_byte = (self.msg_type << 6) | (int(self.is_eof) << 5)
        header = struct.pack('!BBBBH',
                              self.addr_dst,
                              self.addr_src,
                              ctrl_byte,
                              self.seq,
                              self.len)

        raw_payload = header + self.dane

        # CRC
        if self.crc_type == Ramka.CRC8:
            self.crc = KoderCRC8.oblicz(raw_payload)
            crc_bytes = self.crc.to_bytes(1, 'big')
        else:
            self.crc = KoderCRC16.oblicz(raw_payload)
            crc_bytes = self.crc.to_bytes(2, 'big')

        frame_content = raw_payload + crc_bytes
        stuffed = self._byte_stuffing(frame_content)

        return bytes([self.FLAG_BYTE]) + stuffed + bytes([self.FLAG_BYTE])

    @staticmethod
    def rozpakuj(ramka_bajty: bytes):
        if len(ramka_bajty) < 7:  # Minimum: 6 nagłówka + 1 CRC
            return None

        temp = ramka_bajty
        # Usuwanie flag (byte unstuffing robi to w środku, ale tu usuwamy skrajne)
        if temp[0] == Ramka.FLAG_BYTE:
            temp = temp[1:]
        if temp and temp[-1] == Ramka.FLAG_BYTE:
            temp = temp[:-1]

        try:
            raw = Ramka._byte_unstuffing(temp)
        except ValueError:
            return None

        if len(raw) < 7:  # Nagłówek(6) + CRC(min 1)
            return None

        # Odczytujemy nagłówek, żeby poznać długość danych
        header_part = raw[:6]
        dst, src, ctrl, seq, declared_len = struct.unpack('!BBBBH', header_part)

        # Sprawdzamy ile bajtów zostało na CRC
        # Cała ramka (raw) = Nagłówek (6) + Dane (declared_len) + CRC (X)
        expected_total_len_without_crc = 6 + declared_len
        crc_len = len(raw) - expected_total_len_without_crc

        # Rozpoznawanie typu CRC po długości reszty
        if crc_len == 1:
            detected_crc_type = Ramka.CRC8
        elif crc_len == 2:
            detected_crc_type = Ramka.CRC16
        else:
            return None  # Błędna długość ramki (nie pasuje ani do CRC8 ani CRC16)

        # Wyodrębnienie CRC i weryfikacja
        received_crc = int.from_bytes(raw[-crc_len:], 'big')
        data_to_check = raw[:-crc_len]
        payload = data_to_check[6:]  # Dane zaczynają się po 6 bajcie nagłówka

        # Wstępna weryfikacja długości payloadu
        if len(payload) != declared_len:
            return None

        # Parsowanie pól sterujących
        msg_type = (ctrl >> 6) & 0x03
        is_eof = bool((ctrl >> 5) & 0x01)

        # Tworzymy obiekt ramki
        r = Ramka(src, dst, seq, payload, msg_type, is_eof, crc_type=detected_crc_type)
        r.crc = received_crc

        # Obliczamy CRC właściwym algorytmem
        if detected_crc_type == Ramka.CRC8:
            r._calculated_crc = KoderCRC8.oblicz(data_to_check)
        else:
            r._calculated_crc = KoderCRC16.oblicz(data_to_check)

        return r
    def czy_poprawna(self) -> bool:
        return self.crc == self._calculated_crc

    @staticmethod
    def _byte_stuffing(data: bytes) -> bytes:
        res = bytearray()
        for b in data:
            if b in (Ramka.FLAG_BYTE, Ramka.ESCAPE_BYTE):
                res.append(Ramka.ESCAPE_BYTE)
                res.append(b ^ Ramka.XOR_KEY)
            else:
                res.append(b)
        return bytes(res)

    @staticmethod
    def _byte_unstuffing(data: bytes) -> bytes:
        res = bytearray()
        skip = False
        for i in range(len(data)):
            if skip:
                skip = False
                continue
            if data[i] == Ramka.ESCAPE_BYTE:
                if i + 1 >= len(data):
                    raise ValueError("Błędne escape")
                res.append(data[i + 1] ^ Ramka.XOR_KEY)
                skip = True
            else:
                res.append(data[i])
        return bytes(res)
