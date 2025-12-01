from KoderCRC16 import KoderCRC16

# Stałe dla pola LEN/TYPE
TYPE_DATA = 0x00  # 0-254 bajtów danych
TYPE_ACK = 0xFF  # Ramka sterująca


class Ramka:
    """
    Struktura ramki: [ADDR_SRC (1)] [ADDR_DST (1)] [SEQ (1)] [LEN/TYPE (1)] [DANE (...)] [CRC16 (2)]
    """

    def __init__(self, addr_src: int, addr_dst: int, seq_num: int, dane: bytes = b'', is_ack=False):
        self.addr_src = addr_src & 0xFF
        self.addr_dst = addr_dst & 0xFF
        self.seq = seq_num & 0xFF
        self.dane = dane
        self.is_ack = is_ack

        self.len_type = TYPE_ACK if is_ack else (len(dane) & 0xFE)  # Długość <= 254

        # Obliczenie CRC na nagłówku i danych
        self.crc = KoderCRC16.oblicz(self._get_data_to_crc())

    def _get_data_to_crc(self) -> bytes:
        """Dane do obliczenia CRC (nagłówek + dane/typ)"""
        # Używamy wszystkich stałych pól nagłówka (4 bajty)
        naglowek = bytes([self.addr_src, self.addr_dst, self.seq, self.len_type])

        if self.is_ack:
            # Dla ACK CRC tylko z nagłówka
            return naglowek
        else:
            # Dla DANYCH CRC z nagłówka i payloadu
            return naglowek + self.dane

    def pakuj(self) -> bytes:
        ramka = bytearray()
        ramka.append(self.addr_src)
        ramka.append(self.addr_dst)
        ramka.append(self.seq)
        ramka.append(self.len_type)

        if not self.is_ack:
            ramka.extend(self.dane)

        ramka.extend(self.crc.to_bytes(2, byteorder="big"))
        return bytes(ramka)

    @staticmethod
    def rozpakuj(ramka_bajty: bytes):
        if len(ramka_bajty) < 6:
            raise IndexError("Ramka jest za krótka.")

        addr_src = ramka_bajty[0]
        addr_dst = ramka_bajty[1]
        seq = ramka_bajty[2]
        len_type = ramka_bajty[3]

        is_ack = (len_type == TYPE_ACK)

        if is_ack:
            dane = b''
            crc_odebrane = int.from_bytes(ramka_bajty[4:6], "big")
        else:
            length = len_type
            dane = ramka_bajty[4:4 + length]
            crc_odebrane = int.from_bytes(ramka_bajty[4 + length:4 + length + 2], "big")

        r = Ramka(addr_src, addr_dst, seq, dane, is_ack=is_ack)
        r.crc = crc_odebrane
        return r

    def czy_poprawna(self) -> bool:
        obliczone_crc = KoderCRC16.oblicz(self._get_data_to_crc())
        return self.crc == obliczone_crc

    def __str__(self):
        typ = "ACK" if self.is_ack else "DATA"
        dane_len = len(self.dane)
        # Zabezpieczenie przed błędem, jeśli odebrana ramka jest uszkodzona
        dane_info = self.dane[:10] if self.dane else b''
        return f"TYPE={typ} SEQ={self.seq} LEN={dane_len} CRC={hex(self.crc)} DANE={dane_info}..."


def utworz_ramke_ack(nadawca_addr, odbiorca_addr, seq_num):
    return Ramka(nadawca_addr, odbiorca_addr, seq_num, is_ack=True)