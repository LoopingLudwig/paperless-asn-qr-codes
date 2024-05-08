import argparse
import re

from reportlab.lib.units import mm

from paperless_asn_qr_codes import avery_labels
from paperless_asn_qr_codes.render_qr import LabelRenderer


def main():
    # Match the starting position parameter. Allow x:y or n
    def _start_position(arg):
        if mat := re.match(r"^(\d{1,2}):(\d{1,2})$", arg):
            return (int(mat.group(1)), int(mat.group(2)))
        elif mat := re.match(r"^\d+$", arg):

            return int(arg)
        else:
            raise argparse.ArgumentTypeError("invalid value")

    parser = argparse.ArgumentParser(
        prog="paperless-asn-qr-codes",
        description="CLI Tool for generating paperless ASN labels with QR codes",
    )
    parser.add_argument("start_asn", type=int, help="The value of the first ASN")
    parser.add_argument(
        "output_file",
        type=str,
        default="labels.pdf",
        help="The output file to write to (default: labels.pdf)",
    )
    parser.add_argument(
        "--format", "-f", choices=avery_labels.labelInfo.keys(), default="averyL4731"
    )
    parser.add_argument(
        "--digits",
        "-d",
        default=7,
        help="Number of digits in the ASN (default: 7, produces 'ASN0000001')",
        type=int,
    )
    parser.add_argument("-b",
        "--border",
        action="store_true",
        help="Display borders around labels, useful for debugging the printer alignment",
    )
    parser.add_argument("-r",
       "--row-wise",
        action="store_false",
        help="Increment the ASNs row-wise, go from left to right",
    )
    parser.add_argument("-n",
        "--num-labels",
        type=int,
        help="Number of labels to be printed on the sheet",
    )
    parser.add_argument("-p",
        "--pages",
        type=int,
        default=1,
        help="Number of pages to be printed, ignored if NUM_LABELS is set (default: 1)",
    )
    parser.add_argument("-s",
        "--start-position",
        type=_start_position,
        help="Define the starting position on the sheet, eighter as ROW:COLUMN or COUNT, both starting from 1 (default: 1:1 or 1)",
    )
    parser.add_argument("-m",
        "--micro-qr",
        action="store_true",
        help="Create Micro-QR-Codes, if possible",
    )
    parser.add_argument(
        "--qr-code-prefix",
        type=str,
        default="ASN",
        help="Prefix coded in QR-Code (default: ASN)",
    )
    parser.add_argument(
        "--text-prefix",
        type=str,
        help="Prefix used in text (default: same as --qr-code-prefix)",
    )

    args = parser.parse_args()

    label = avery_labels.AveryLabel(args.format, args.border,
                                    topDown=args.row_wise,
                                    start_pos=args.start_position)
    label.open(args.output_file)

    # If defined use parameter for number of labels
    if args.num_labels:
        count = args.num_labels
    else:
        # Otherwise number of pages*labels - offset
        count = args.pages * label.across * label.down - label.position

    #Prefixes
    text_prefix = args.qr_code_prefix if args.text_prefix is None else args.text_prefix

    renderer = LabelRenderer(args.start_asn, args.digits, args.micro_qr,
                             barcode_prefix=args.qr_code_prefix, text_prefix=text_prefix)

    label.render(renderer.render, count)
    label.close()
