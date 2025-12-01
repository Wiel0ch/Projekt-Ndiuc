from Ramka import Ramka, utworz_ramke_ack


class Nadajnik:
    # Maksymalna liczba retransmisji
    TIMEOUT = 5

    def __init__(self, addr_src=1, addr_dst=2):
        self.seq = 0
        self.addr_src = addr_src
        self.addr_dst = addr_dst
        # Referencja do odbiornika do symulacji ACK
        self.odbiornik_dla_ack = None
        self.ostatnia_transmisja_prob = 0  # Licznik prób na potrzeby statystyk

    def ustaw_odbiornik_dla_ack(self, odbiornik):
        self.odbiornik_dla_ack = odbiornik

    def wyslij(self, kanal, dane: bytes):

        attempts = 0

        while attempts < self.TIMEOUT:

            # Ramka DANYCH tworzona jest z aktualnym numerem SEQ
            ramka_danych = Ramka(self.addr_src, self.addr_dst, self.seq, dane)
            ramka_bajty = ramka_danych.pakuj()

            print(f"[NADAJNIK] Wysyłam (próba {attempts + 1}, SEQ={self.seq})")

            # Krok 1: Wysłanie ramki danych
            ramka_danych_po_kanale = kanal.przeslij(ramka_bajty)

            # Krok 2: Odbiór przez Odbiornik (Odbiornik przetwarza dane i zwraca ACK)
            ramka_ack_bajty = self.odbiornik_dla_ack.odbierz_i_zwroc_ack(
                ramka_danych_po_kanale, kanal, self.addr_src
            )

            # Krok 3: Transmisja ACK z powrotem do Nadawcy
            if ramka_ack_bajty:

                # Ramka ACK jest przesyłana przez ten sam kanał
                ramka_ack_po_kanale = kanal.przeslij(ramka_ack_bajty)

                try:
                    ramka_ack_odebrana = Ramka.rozpakuj(ramka_ack_po_kanale)
                except IndexError:
                    print("[NADAJNIK] BŁĄD: Otrzymano niepoprawny pakiet ACK (uszkodzony format). Retransmisja...")
                    attempts += 1
                    continue

                # Krok 4: Weryfikacja ACK
                if ramka_ack_odebrana.czy_poprawna() and ramka_ack_odebrana.seq == self.seq:

                    # Poprawne ACK dla aktualnego SEQ!
                    print(f"[NADAJNIK] Odebrano poprawne ACK dla SEQ={self.seq}. Zakończono.")

                    self.ostatnia_transmisja_prob = attempts + 1
                    self.seq = (self.seq + 1) & 0xFF
                    return True

                else:
                    # ACK uszkodzone CRC lub potwierdza stary numer
                    print("[NADAJNIK] BŁĄD: Otrzymano uszkodzone CRC ACK lub zły SEQ. Retransmisja...")
                    attempts += 1
            else:
                # Brak ACK (Timeout - Odbiornik nie wysłał ACK z powodu BŁĘDU DANYCH)
                print("[NADAJNIK] Brak ACK (Timeout). Retransmisja...")
                attempts += 1

        self.ostatnia_transmisja_prob = attempts
        print(f"[NADAJNIK] PRZERWANIE: Przekroczono limit {self.TIMEOUT} retransmisji dla SEQ={self.seq}.")
        return False