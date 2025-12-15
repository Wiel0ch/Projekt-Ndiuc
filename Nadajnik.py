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

    def wyslij_plik(self, kanal_tam, kanal_powrot, dane: bytes, odbiornik_obj):
        """Wysyła plik metodą Stop-and-Wait."""
        # Podział na kawałki
        chunks = [dane[i:i + self.mtu] for i in range(0, len(dane), self.mtu)]
        print(f"\n[NADAJNIK] Start. Do wysłania: {len(chunks)} ramek (MTU={self.mtu}).")

        for i, chunk in enumerate(chunks):
            is_last = (i == len(chunks) - 1)
            sukces = False

            while not sukces:
                self.total_transmissions += 1

                # 1. Budowa ramki
                ramka = Ramka(self.addr_src, self.addr_dst, self.seq, chunk,
                              msg_type=Ramka.TYPE_DATA, is_eof=is_last)
                dane_w_kanale = kanal_tam.przeslij(ramka.pakuj())

                # 2. Symulacja przesyłu i odbioru (blokująca)
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

            # Po sukcesie przechodzimy do kolejnego numeru
            self.seq = (self.seq + 1) & 0xFF

        print("[NADAJNIK] Koniec transmisji.")