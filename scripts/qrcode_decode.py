#!/usr/bin/env pipenv-shebang
import click
from PIL import Image
from pyzbar import pyzbar


@click.command(help="Decode a QRCode image into a text and print it")
@click.argument('file_name')
def decode_qrcode(file_name):
    click.echo(f'Decoding qrcode {file_name}')

    with open(file_name, mode='rb') as fd:
        # image = io.BytesIO(response.data)
        data = pyzbar.decode(Image.open(fd))
        qrcode_decoded = data[0].data.decode('utf-8')

    click.echo('QRCode decoded to:')
    click.echo(qrcode_decoded)


if __name__ == '__main__':
    decode_qrcode()  # pylint: disable=no-value-for-parameter
