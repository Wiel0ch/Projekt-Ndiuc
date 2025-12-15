from Ramka import Ramka


class Odbiornik:
    def __init__(self, moj_adres, adres_nadajnika):
        self.adres = moj_adres
        self.adres_nadajnika = adres_nadajnika
        self.oczekiwany_seq = 0
        self.bufor_pliku = bytearray()

    def odbierz_i_odpisz(self, ramka_bajty: bytes) -> bytes:
        """
        Zwraca bajty ramki zwrotnej (ACK/NAK) lub None (cisza).
        """
        # 1. Rozpakowanie
        ramka = Ramka.rozpakuj(ramka_bajty)

        # 2. Walidacja fizyczna (CRC, Adresat)
        if ramka is None or not ramka.czy_poprawna() or ramka.addr_dst != self.adres:
            return None  # Ignorujemy śmieci
            # Opcjonalnie: Można tu odesłać NAK, jeśli CRC jest złe, ale nagłówek czytelny.

        # 3. Logika Stop-and-Wait
        response_type = Ramka.TYPE_ACK
        seq_to_ack = ramka.seq

        if ramka.seq == self.oczekiwany_seq:
            # SUKCES: Otrzymano nową, oczekiwaną ramkę
            if ramka.msg_type == Ramka.TYPE_DATA:
                self.bufor_pliku.extend(ramka.dane)

            # Przesuwamy okno
            self.oczekiwany_seq = (self.oczekiwany_seq + 1) & 0xFF

        elif ramka.seq < self.oczekiwany_seq:
            # DUPLIKAT: Nadajnik ponowił, bo nie dostał ACK.
            # Ignorujemy dane, ale musimy ponowić ACK.
            pass
        else:
            # Seq z przyszłości (błąd protokołu)
            return None

        # 4. Tworzenie odpowiedzi
        ack = Ramka(
            addr_src=self.adres,
            addr_dst=self.adres_nadajnika,
            seq_num=seq_to_ack,
            msg_type=response_type
        )
        return ack.pakuj()

    def pobierz_dane(self):
        d = bytes(self.bufor_pliku)
        self.bufor_pliku.clear()
        self.oczekiwany_seq = 0
        return d