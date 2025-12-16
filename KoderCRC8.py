class KoderCRC8:
    """
    CRC-8: wielomian 0x07 (x^8 + x^2 + x + 1)
    """
    _wielomian = 0x07
    _init_val = 0x00

    @staticmethod
    def oblicz(dane: bytes) -> int:
        crc = KoderCRC8._init_val
        for bajt in dane:
            crc ^= bajt
            for _ in range(8):
                if crc & 0x80:
                    crc = ((crc << 1) ^ KoderCRC8._wielomian) & 0xFF
                else:
                    crc = (crc << 1) & 0xFF
        return crc

    @staticmethod
    def weryfikuj(dane: bytes, otrzymane_crc: int) -> bool:
        return KoderCRC8.oblicz(dane) == otrzymane_crc
