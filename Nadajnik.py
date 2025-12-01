from Ramka import Ramka


class Nadajnik:
    def __init__(self, moj_adres, adres_celu, mtu=10):
        self.addr_src = moj_adres
        self.addr_dst = adres_celu
        self.mtu = mtu
        self.seq = 0
        self.total_transmissions = 0
        self.retransmissions = 0

    def wyslij_plik(self, kanal_tam, kanal_powrot, dane: bytes, odbiornik_obj):
        """Metoda blokująca - wysyła cały plik metodą Stop-and-Wait."""
        # Dzielenie na kawałki
        chunks = [dane[i:i + self.mtu] for i in range(0, len(dane), self.mtu)]
        print(f"\n[NADAJNIK] Start transmisji. {len(chunks)} ramek do wysłania.")

        for i, chunk in enumerate(chunks):
            is_last = (i == len(chunks) - 1)
            sukces = False

            while not sukces:
                self.total_transmissions += 1

                # 1. Tworzenie i pakowanie ramki
                ramka = Ramka(self.addr_src, self.addr_dst, self.seq, chunk,
                              msg_type=Ramka.TYPE_DATA, is_eof=is_last)
                dane_w_kanale = kanal_tam.przeslij(ramka.pakuj())

                print(f"[NADAJNIK] Wysyłam Seq={self.seq} (len={len(chunk)})... ", end="")

                # 2. Odbiornik przetwarza i generuje odpowiedź
                # (Tutaj następuje "magia" symulacji - przekazujemy bajty bezpośrednio)
                odpowiedz_bajty = odbiornik_obj.odbierz_i_odpisz(dane_w_kanale)

                if odpowiedz_bajty is None:
                    # Timeout (odbiornik odrzucił ramkę)
                    print("TIMEOUT (Brak ACK)")
                    self.retransmissions += 1
                    continue

                # 3. Kanał zwrotny (psuje ACK)
                ack_po_kanale = kanal_powrot.przeslij(odpowiedz_bajty)

                # 4. Sprawdzenie ACK
                ack_ramka = Ramka.rozpakuj(ack_po_kanale)

                if (ack_ramka and ack_ramka.czy_poprawna() and
                        ack_ramka.msg_type == Ramka.TYPE_ACK and ack_ramka.seq == self.seq):
                    print("ACK OK.")
                    sukces = True
                else:
                    print("Błąd ACK (CRC lub zły Seq).")
                    self.retransmissions += 1

            # Po pętli while (sukces) -> następny numer
            self.seq = (self.seq + 1) & 0xFF

        print("[NADAJNIK] Koniec pliku.")