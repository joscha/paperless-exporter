from ..utils import german_to_ascii, unidecode_filename


def test_unidecode():
    assert german_to_ascii("Geburtstagsgrüße") == "Geburtstagsgruesse"
    assert (
        unidecode_filename(
            "sparhandy 2012-05-25  BASE Internet-Flat (500MB) für effektiv 0,21€ pro Monat inkl. UMTS-Stick - myDealZ.de — myDealZ.de - 25.05.12.pdf"
        )
        == "sparhandy 2012-05-25  BASE Internet-Flat (500MB) fuer effektiv 0,21€ pro Monat inkl. UMTS-Stick - myDealZ.de — myDealZ.de - 25.05.12.pdf"
    )
