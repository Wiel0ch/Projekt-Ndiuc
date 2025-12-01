from Ramka import Ramka, utworz_ramke_ack


class Odbiornik:
    def __init__(self, adres=2):
        self.adres = adres
        self.ostatnio_odebrany_seq = -1

    def odbierz_i_zwroc_ack(self, ramka_bajty: bytes, kanal, nadawca_addr) -> bytes or None:
        """
        Odbiera ramkę danych, przetwarza ją i zwraca spakowaną ramkę ACK
        (która jest później przesyłana przez kanał zwrotny).
        """

        try:
            ramka = Ramka.rozpakuj(ramka_bajty)
        except IndexError:
            # Ramka uszkodzona na tyle, że nie da się jej rozpakować
            print("[ODBIORNIK] BŁĄD: Otrzymano uszkodzoną ramkę (niepoprawny format). Wyciszam...")
            return None

        # Odbiornik ignoruje ACK
        if ramka.is_ack:
            return None

        print(f"[ODBIORNIK] Odebrano: {ramka}")

        if ramka.addr_dst != self.adres:
            return None

        if ramka.czy_poprawna():

            # --- Obsługa duplikatów (retransmisja) ---
            if ramka.seq == self.ostatnio_odebrany_seq:
                print(f" CRC poprawne, ale DUPLIKAT SEQ={ramka.seq}. Ponownie wysyłam ACK.")
                # Ponownie wysyłamy ACK dla tego numeru, by zresetować timeout nadawcy
                ack = utworz_ramke_ack(self.adres, nadawca_addr, ramka.seq)
                return ack.pakuj()

            # --- Nowa, poprawna ramka ---
            print(f" CRC poprawne dla SEQ={ramka.seq} → dane OK. Wysyłam ACK.")
            self.ostatnio_odebrany_seq = ramka.seq

            # ACK potwierdza numer ramki, którą właśnie odebraliśmy
            ack = utworz_ramke_ack(self.adres, nadawca_addr, ramka.seq)
            return ack.pakuj()
        else:
            print(" BŁĄD CRC! Dane uszkodzone! Wyciszam (czekam na retransmisję).")
            # Nie wysyłamy ACK, Nadawca musi osiągnąć timeout
            return None