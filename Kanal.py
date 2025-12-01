import random


class Kanal:

    def przeslij(self, dane_wejsciowe: bytes) -> bytes:
        raise NotImplementedError("Klasa pochodna musi implementować tę metodę.")


class BSCKanal(Kanal):
    def __init__(self, p_error: float):
        if not (0.0 <= p_error <= 1.0):
            raise ValueError("Prawdopodobieństwo błędu musi być w przedziale [0, 1]")
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

    def test_ber(self, dlugosc_testu_bajty: int = 100000):
        """
        Generuje dlugi ciag zer i przesyla przez kanal, zliczajac bledy
        w celu weryfikacji zadanej wartosci BER.
        """
        # Dane testowe to same zera
        dane_testowe = b'\x00' * dlugosc_testu_bajty

        calkowita_liczba_bitow = dlugosc_testu_bajty * 8
        zmierzone_bledy = 0

        for bajt_oryginalny in dane_testowe:
            for i in range(8):
                # Symulacja błędu
                if random.random() < self.p_error:
                    zmierzone_bledy += 1

        ber_measured = zmierzone_bledy / calkowita_liczba_bitow

        print("\n--- TEST STATYSTYCZNY KANAŁU BSC ---")
        print(f"Oczekiwany BER (p): {self.p_error}")
        print(f"Długość testu: {dlugosc_testu_bajty} bajtów ({calkowita_liczba_bitow} bitów)")
        print(f"Zmierzone błędy: {zmierzone_bledy}")
        print(f"Zmierzone BER: {ber_measured:.6f}")

        margin = 0.05
        if self.p_error > 0:
            is_accurate = abs(ber_measured - self.p_error) / self.p_error < margin
        else:
            is_accurate = zmierzone_bledy == 0

        print("Weryfikacja: OK" if is_accurate else "Weryfikacja: UWAGA - ODBIEGA")
        print("-------------------------------------")


class GilbertElliottKanal(Kanal):
    # ... (klasa GilbertElliottKanal bez zmian) ...
    def __init__(self, p_G: float, p_B: float, p_GB: float, p_BG: float):
        if not all(0.0 <= p <= 1.0 for p in [p_G, p_B, p_GB, p_BG]):
            raise ValueError("Wszystkie prawdopodobieństwa muszą być w przedziale [0, 1]")

        self.p_G = p_G
        self.p_B = p_B
        self.p_GB = p_GB  # P(G -> B)
        self.p_BG = p_BG  # P(B -> G)

        self.p_GG = 1.0 - p_GB
        self.p_BB = 1.0 - p_BG

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
                aktualne_p_error = self.p_B if self.is_bad_state else self.p_G

                if random.random() < aktualne_p_error:
                    bit = 1 - bit

                if bit == 1:
                    nowy_bajt |= (1 << i)

                if self.is_bad_state:
                    if random.random() < self.p_BG:
                        self.is_bad_state = False
                else:
                    if random.random() < self.p_GB:
                        self.is_bad_state = True

            dane_wyjsciowe.append(nowy_bajt)

        return bytes(dane_wyjsciowe)