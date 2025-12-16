from Ramka import Ramka


class Nadajnik:
    def __init__(self, moj_adres, adres_celu, mtu=20):
        self.addr_src = moj_adres
        self.addr_dst = adres_celu
        self.mtu = mtu
        self.seq = 0

        # Statystyki
        self.total_transmissions = 0
        self.retransmissions = 0
        self.failed_frames = 0  # Licznik ramek odrzuconych przez limit
        self.attempts_history = []  # Lista: ile prób zajęło wysłanie każdej ramki

    def wyslij_plik(self, kanal_tam, kanal_powrot, dane: bytes, odbiornik_obj, max_retries=10):
        """
        Wysyła plik metodą Stop-and-Wait z limitem retransmisji.
        :param max_retries: Maksymalna liczba powtórzeń (np. 10). Jeśli None, brak limitu.
        """
        # Podział na kawałki
        chunks = [dane[i:i + self.mtu] for i in range(0, len(dane), self.mtu)]
        print(f"\n[NADAJNIK] Start. Do wysłania: {len(chunks)} ramek. Limit retransmisji: {max_retries}")

        for i, chunk in enumerate(chunks):
            is_last = (i == len(chunks) - 1)
            sukces = False
            attempts = 0  # Licznik prób dla bieżącej ramki

            while not sukces:
                attempts += 1
                self.total_transmissions += 1

                # Sprawdzenie limitu retransmisji
                # attempts > max_retries + 1, ponieważ 1. próba to nie retransmisja
                if max_retries is not None and attempts > (max_retries + 1):
                    print(f"[NADAJNIK] BŁĄD: Przekroczono limit prób dla ramki SEQ={self.seq}")
                    self.failed_frames += 1
                    break  # Przerywamy pętlę while, ramka uznana za utraconą

                # 1. Budowa ramki
                ramka = Ramka(self.addr_src, self.addr_dst, self.seq, chunk,
                              msg_type=Ramka.TYPE_DATA, is_eof=is_last)

                # Przesłanie przez kanał
                dane_w_kanale = kanal_tam.przeslij(ramka.pakuj())

                # 2. Odbiór (symulacja blokująca)
                odpowiedz_bajty = odbiornik_obj.odbierz_i_odpisz(dane_w_kanale)

                if odpowiedz_bajty is None:
                    # Timeout (brak odpowiedzi)
                    self.retransmissions += 1
                    continue

                # 3. Kanał zwrotny
                ack_po_kanale = kanal_powrot.przeslij(odpowiedz_bajty)

                # 4. Weryfikacja ACK
                ack_ramka = Ramka.rozpakuj(ack_po_kanale)

                if (ack_ramka and ack_ramka.czy_poprawna() and
                        ack_ramka.msg_type == Ramka.TYPE_ACK and ack_ramka.seq == self.seq):
                    sukces = True
                else:
                    # Błędne ACK lub NAK
                    self.retransmissions += 1

            # Zapisz liczbę prób do statystyk (nawet jeśli zakończono porażką)
            self.attempts_history.append(attempts)

            # Przechodzimy do kolejnego numeru sekwencyjnego
            self.seq = (self.seq + 1) & 0xFF

        print("[NADAJNIK] Koniec transmisji.")