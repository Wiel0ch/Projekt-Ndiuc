from KoderCRC16 import KoderCRC16

class Ramka:
    """
    Struktura ramki:
    [ADDR_SRC (1)] [ADDR_DST (1)] [SEQ (1)] [LEN (1)] [DANE (...)] [CRC16 (2)]
    """

    def __init__(self, addr_src: int, addr_dst: int, seq_num: int, dane: bytes):
        self.addr_src = addr_src & 0xFF
        self.addr_dst = addr_dst & 0xFF
        self.seq = seq_num & 0xFF
        self.dane = dane
        self.len = len(dane)
        self.crc = KoderCRC16.oblicz(self.dane)

    def pakuj(self) -> bytes:
        ramka = bytearray()
        ramka.append(self.addr_src)
        ramka.append(self.addr_dst)
        ramka.append(self.seq)
        ramka.append(self.len)
        ramka.extend(self.dane)
        ramka.extend(self.crc.to_bytes(2, byteorder="big"))
        return bytes(ramka)

    @staticmethod
    def rozpakuj(ramka_bajty: bytes):
        addr_src = ramka_bajty[0]
        addr_dst = ramka_bajty[1]
        seq = ramka_bajty[2]
        length = ramka_bajty[3]
        dane = ramka_bajty[4:4+length]
        crc_odebrane = int.from_bytes(ramka_bajty[4+length:4+length+2], "big")

        r = Ramka(addr_src, addr_dst, seq, dane)
        r.crc = crc_odebrane
        return r

    def czy_poprawna(self) -> bool:
        return self.crc == KoderCRC16.oblicz(self.dane)

    def __str__(self):
        return f"ADDR_SRC={self.addr_src} ADDR_DST={self.addr_dst} SEQ={self.seq} LEN={self.len} CRC={hex(self.crc)} DANE={self.dane}"
