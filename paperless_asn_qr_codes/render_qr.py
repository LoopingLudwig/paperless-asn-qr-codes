import segno
from reportlab.lib.units import mm
from reportlab.platypus import Flowable


class QRCodeImage(Flowable):
    # This class is based on reportlab-qrcode (https://github.com/hprid/reportlab-qrcode)
    #
    # Copyright 2020 Henning Pridöhl <dev@hprid.de>

    # Permission is hereby granted, free of charge, to any person obtaining a copy of
    # this software and associated documentation files (the "Software"), to deal in
    # the Software without restriction, including without limitation the rights to
    # use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
    # of the Software, and to permit persons to whom the Software is furnished to do
    # so, subject to the following conditions:

    # The above copyright notice and this permission notice shall be included in all
    # copies or substantial portions of the Software.

    # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    # SOFTWARE.


    def __init__(self, data, size=25 * mm, fill_color='black',
                 back_color='white', border=None, **kwargs):
        Flowable.__init__(self)
        self.x = 0
        self.y = 0
        self.size = size
        self.border = border
        self.fill_color = fill_color
        self.back_color = back_color
        self.data = data
        self.qr_kwargs = kwargs

    def draw(self):

        qr = segno.make(self.data, **self.qr_kwargs)
        border = self.border if self.border else qr.default_border_size

        active_positions = []
        for y, row in enumerate(qr.matrix):
            for x, is_active in enumerate(row):
                if is_active:
                    active_positions.append((y, x))
        box_size = self.size / (len(qr.matrix) + 2 * border)
        self.canv.saveState()
        if self.back_color is not None:
            self.canv.setFillColor(self.back_color)
            self.canv.rect(self.x, self.y, self.size, self.size, stroke=0, fill=1)
        self.canv.setFillColor(self.fill_color)
        for row, col in active_positions:
            xr = (col + border) * box_size
            yr = (row + border) * box_size
            yr = -yr
            yr += self.size - box_size
            self.canv.rect(xr + self.x, yr + self.y, box_size, box_size, stroke=0, fill=1)
        self.canv.restoreState()


class LabelRenderer:

    def __init__(self, start, digits, micro_qr=False,
                 barcode_prefix="ASN", text_prefix="ASN"):

        self.value = start
        self.digits = digits
        self.micro_qr = micro_qr
        self.barcode_prefix=barcode_prefix
        self.text_prefix=text_prefix

    def render(self, c, x, y):
        barcode_value = f"{self.barcode_prefix}{self.value:0{self.digits}d}"
        text_value = f"{self.text_prefix}{self.value:0{self.digits}d}"
        self.value += 1

        qr = QRCodeImage(barcode_value, size=y * 0.9, micro=self.micro_qr)
        qr.drawOn(c, 1 * mm, y * 0.05)
        c.setFont("Helvetica", 2 * mm)
        c.drawString(y, (y - 2 * mm) / 2, text_value)

