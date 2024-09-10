import click

from bobik.bobik import Bobik
from bobik.util import print_events


@click.command()
@click.option("--plec-pacjenta", default="mezczyzna")
@click.option("--wiek-pacjenta", default="45")
@click.option("--tryb-zabiegu", default="planowy")
@click.option("--rodzaj-zabiegu", default="cholecystektomia")
@click.option("--email-to", default="admin@foobar.pl")
@click.option("--db-url", default="memory://")
@click.option("--model", default="claude-3-5-sonnet-20240620")
def main(
    plec_pacjenta, wiek_pacjenta, tryb_zabiegu, rodzaj_zabiegu, email_to, db_url, model
):
    bobik = Bobik(
        plec_pacjenta=plec_pacjenta,
        wiek_pacjenta=wiek_pacjenta,
        tryb_zabiegu=tryb_zabiegu,
        rodzaj_zabiegu=rodzaj_zabiegu,
        email_to=email_to,
        db_url=db_url,
        model=model,
    )
    for event in bobik.send_message():
        print_events(event)

    while True:
        i = input("> ").strip()
        if not i:
            continue

        for event in bobik.send_message(i):
            print_events(event)


if __name__ == "__main__":
    main()
