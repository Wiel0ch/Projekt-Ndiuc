import random


class Kanal:

    def przeslij(self, dane_wejsciowe: bytes) -> bytes:
        #Symuluje przesłanie danych przez kanał
        raise NotImplementedError("Klasa pochodna musi implementować tę metodę.")


class BSCKanal(Kanal):
    def __init__(self, p_error: float):
        if not (0.0 <= p_error <= 1.0):
            raise ValueError("Prawdopodobieństwo błędu musi być w przedziale (0,1)")
        self.p_error = p_error
        print(f"INFO: Utworzono kanał BSC z p(błędem bitu) = {p_error}")

    def przeslij(self, dane_wejsciowe: bytes) -> bytes:
        dane_wyjsciowe = bytearray()

        for bajt in dane_wejsciowe:
            nowy_bajt = 0
            for i in range(8):
                bit = (bajt >> i) & 1

                # Symulacja błędu
                if random.random() < self.p_error:
                    bit = 1 - bit  # Odwróć bit

                if bit == 1:
                    nowy_bajt |= (1 << i)

            dane_wyjsciowe.append(nowy_bajt)

        return bytes(dane_wyjsciowe)