class KoderCRC16:
    """
    Statyczna klasa narzędziowa do obliczania i weryfikacji
    sum kontrolnych CRC-16-CCITT (Wielomian: 0x1021, Init: 0xFFFF).
    """
    _wielomian = 0x1021
    _init_val = 0xFFFF

    @staticmethod
    def oblicz(dane: bytes) -> int:
        """Oblicza sumę kontrolną CRC-16-CCITT."""
        crc = KoderCRC16._init_val

        for bajt in dane:
            crc ^= (bajt << 8)
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ KoderCRC16._wielomian
                else:
                    crc = crc << 1
                crc &= 0xFFFF
        return crc

    @staticmethod
    def weryfikuj(dane: bytes, otrzymane_crc: int) -> bool:
        """Sprawdza, czy obliczone CRC zgadza się z otrzymanym."""
        return KoderCRC16.oblicz(dane) == otrzymane_crc