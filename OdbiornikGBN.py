from Ramka import Ramka


class OdbiornikGBN:
    def __init__(self, moj_adres, adres_nadajnika):
        self.adres = moj_adres
        self.adres_nadajnika = adres_nadajnika
        self.oczekiwany_seq = 0
        self.bufor_pliku = bytearray()

    def odbierz_i_odpisz(self, ramka_bajty: bytes) -> bytes:
        """
        Logika GBN:
        1. Jeśli ramka uszkodzona -> Ignoruj (Nadajnik ponowi po timeout).
        2. Jeśli ramka poprawna i SEQ == oczekiwany -> Zapisz, zwiększ licznik, wyślij ACK(SEQ).
        3. Jeśli ramka poprawna, ale SEQ != oczekiwany -> Ignoruj dane, wyślij ACK(ostatni_poprawny).
        """
        ramka = Ramka.rozpakuj(ramka_bajty)

        # 1. Walidacja fizyczna (CRC, Adresat)
        if ramka is None or not ramka.czy_poprawna() or ramka.addr_dst != self.adres:
            return None

        # 2. Sprawdzenie kolejności
        seq_odebrany = ramka.seq

        if seq_odebrany == self.oczekiwany_seq:
            # SUKCES: To jest ramka, na którą czekamy
            if ramka.msg_type == Ramka.TYPE_DATA:
                self.bufor_pliku.extend(ramka.dane)

            # Przesuwamy okno oczekiwania
            self.oczekiwany_seq = (self.oczekiwany_seq + 1) & 0xFF

            # Potwierdzamy TĘ ramkę
            seq_to_ack = seq_odebrany
        else:
            # BŁĄD KOLEJNOŚCI: Otrzymano ramkę z przyszłości lub duplikat
            # W GBN odsyłamy ACK dla ostatniej poprawnie odebranej ramki (czyli oczekiwany - 1)
            seq_to_ack = (self.oczekiwany_seq - 1) & 0xFF

        # Jeśli jesteśmy na samym początku (oczekiwany=0) i dostaliśmy złą ramkę,
        # to seq_to_ack wyjdzie 255. Możemy to wysłać, nadajnik to zignoruje,
        # albo możemy zwrócić None (cisza), wymuszając timeout u nadajnika.
        # Dla uproszczenia symulacji:
        ack = Ramka(
            addr_src=self.adres,
            addr_dst=self.adres_nadajnika,
            seq_num=seq_to_ack,
            msg_type=Ramka.TYPE_ACK
        )
        return ack.pakuj()

    def pobierz_dane(self):
        d = bytes(self.bufor_pliku)
        self.bufor_pliku.clear()
        self.oczekiwany_seq = 0
        return d