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


class GilbertElliottKanal(Kanal):
    def __init__(self, p_G: float, p_B: float, p_GB: float, p_BG: float):
        if not all(0.0 <= p <= 1.0 for p in [p_G, p_B, p_GB, p_BG]):
            raise ValueError("Wszystkie prawdopodobieństwa muszą być w przedziale [0, 1]")

        self.p_G = p_G
        self.p_B = p_B
        self.p_GB = p_GB  # P(G -> B)
        self.p_BG = p_BG  # P(B -> G)

        # Prawdopodobieństwa pozostania w stanach
        self.p_GG = 1.0 - p_GB
        self.p_BB = 1.0 - p_BG

        # Kanał startuje w stanie DOBRYM
        self.is_bad_state = False

        print(f"INFO: Utworzono kanał G-E:")
        print(f"      Stan G: p(błąd) = {p_G}, p(G->B) = {p_GB}")
        print(f"      Stan B: p(błąd) = {p_B}, p(B->G) = {p_BG}")

    def przeslij(self, dane_wejsciowe: bytes) -> bytes:
        dane_wyjsciowe = bytearray()

        for bajt in dane_wejsciowe:
            nowy_bajt = 0
            for i in range(8):
                bit = (bajt >> i) & 1
                #Określenie p(błędu) na podstawie obcengo stanu
                aktualne_p_error = self.p_B if self.is_bad_state else self.p_G

                #Symuloawnie błędu bitu
                if random.random() < aktualne_p_error:
                    bit = 1 - bit

                if bit == 1:
                    nowy_bajt |= (1 << i)

                #przejście do następnego stanu
                if self.is_bad_state:
                    #stan  zły(B)
                    if random.random() < self.p_BG:
                        self.is_bad_state = False  # Przejście B -> G
                else:
                    #stan dobry(G)
                    if random.random() < self.p_GB:
                        self.is_bad_state = True  # Przejście G -> B

            dane_wyjsciowe.append(nowy_bajt)

        return bytes(dane_wyjsciowe)