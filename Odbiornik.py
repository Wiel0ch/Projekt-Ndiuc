from Ramka import Ramka


class Odbiornik:
    def __init__(self, moj_adres, adres_nadajnika):
        self.adres = moj_adres
        self.adres_nadajnika = adres_nadajnika
        self.oczekiwany_seq = 0
        self.bufor_pliku = bytearray()

    def odbierz_i_odpisz(self, ramka_bajty: bytes) -> bytes:
        """
        1. Odbiera ramkę.
        2. Jeśli poprawna i nowa -> zapisuje.
        3. Odsyła ACK (nawet jeśli to duplikat).
        Zwraca: bajty ramki ACK lub None (gdy nic nie wysyła).
        """
        # Próba dekodowania
        ramka = Ramka.rozpakuj(ramka_bajty)

        # Jeśli ramka uszkodzona fizycznie lub logicznie (zły adres)
        if ramka is None or not ramka.czy_poprawna() or ramka.addr_dst != self.adres:
            return None  # Symulacja: "nie zrozumiałem", milczę

        # Logika Stop-and-Wait
        seq_do_potwierdzenia = ramka.seq

        if ramka.seq == self.oczekiwany_seq:
            # SUKCES: To jest nowa ramka
            if ramka.msg_type == Ramka.TYPE_DATA:
                print(f" [ODBIORNIK] Odebrano DANE Seq={ramka.seq}. Zapisuję.")
                self.bufor_pliku.extend(ramka.dane)

            # Przesuwamy okno
            self.oczekiwany_seq = (self.oczekiwany_seq + 1) & 0xFF

        elif ramka.seq < self.oczekiwany_seq:
            # DUPLIKAT (Nadajnik nie dostał ACK i ponowił)
            print(f" [ODBIORNIK] Duplikat Seq={ramka.seq}. Ignoruję dane, ponawiam ACK.")
            seq_do_potwierdzenia = ramka.seq  # Potwierdzamy to co przyszło
        else:
            return None  # Dziwna sytuacja w S&W

        # Generowanie ACK
        ack = Ramka(self.adres, self.adres_nadajnika, seq_do_potwierdzenia,
                    msg_type=Ramka.TYPE_ACK)
        return ack.pakuj()

    def pobierz_dane(self):
        d = bytes(self.bufor_pliku)
        self.bufor_pliku.clear()
        self.oczekiwany_seq = 0
        return d