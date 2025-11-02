import random


class Kanal:

    def przeslij(self, dane_wejsciowe: bytes) -> bytes:
        """Symuluje przesłanie danych przez kanał. Musi być zaimplementowane."""
        raise NotImplementedError("Klasa pochodna musi implementować tę metodę.")


class BSCKanal(Kanal):
    """Implementacja kanału Binary Symmetric Channel (BSC)."""

    def __init__(self, p_error: float):
        if not (0.0 <= p_error <= 1.0):
            raise ValueError("Prawdopodobieństwo błędu musi być w zakresie [0, 1]")
        self.p_error = p_error
        print(f"INFO: Utworzono kanał BSC z p(błędu bitu) = {p_error}")

    def przeslij(self, dane_wejsciowe: bytes) -> bytes:
        """
        Symuluje BSC. Każdy BIT ma prawdopodobieństwo `p_error` na zamianę.
        """
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