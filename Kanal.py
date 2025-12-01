import random


class Kanal:
    def przeslij(self, dane_wejsciowe: bytes) -> bytes:
        raise NotImplementedError


class BSCKanal(Kanal):
    def __init__(self, p_error: float):
        self.p_error = p_error

    def przeslij(self, dane_wejsciowe: bytes) -> bytes:
        dane_wyjsciowe = bytearray()
        for bajt in dane_wejsciowe:
            nowy_bajt = 0
            for i in range(8):
                bit = (bajt >> i) & 1
                if random.random() < self.p_error:
                    bit = 1 - bit
                if bit == 1:
                    nowy_bajt |= (1 << i)
            dane_wyjsciowe.append(nowy_bajt)
        return bytes(dane_wyjsciowe)


class GilbertElliottKanal(Kanal):
    def __init__(self, p_G: float, p_B: float, p_GB: float, p_BG: float):
        self.p_G = p_G
        self.p_B = p_B
        self.p_GB = p_GB
        self.p_BG = p_BG
        self.is_bad_state = False

    def przeslij(self, dane_wejsciowe: bytes) -> bytes:
        dane_wyjsciowe = bytearray()
        for bajt in dane_wejsciowe:
            nowy_bajt = 0
            for i in range(8):
                bit = (bajt >> i) & 1
                p_curr = self.p_B if self.is_bad_state else self.p_G

                if random.random() < p_curr:
                    bit = 1 - bit

                if bit == 1:
                    nowy_bajt |= (1 << i)

                # Zmiana stanu
                if self.is_bad_state:
                    if random.random() < self.p_BG: self.is_bad_state = False
                else:
                    if random.random() < self.p_GB: self.is_bad_state = True

            dane_wyjsciowe.append(nowy_bajt)
        return bytes(dane_wyjsciowe)