import struct
import sys
from pathlib import Path

from PySide6.QtCore import QBuffer, QIODevice, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QIcon,
    QImage,
    QLinearGradient,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)


def _draw_logo(painter: QPainter, size: int) -> None:
    scale = size / 128
    painter.scale(scale, scale)
    gradient = QLinearGradient(0, 0, 128, 128)
    gradient.setColorAt(0, QColor("#176b5b"))
    gradient.setColorAt(1, QColor("#27a38b"))
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(gradient))
    painter.drawRoundedRect(QRectF(4, 4, 120, 120), 30, 30)

    pen = QPen(QColor("#ffffff"), 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawRoundedRect(QRectF(27, 24, 74, 57), 15, 15)

    tail = QPainterPath()
    tail.moveTo(43, 81)
    tail.lineTo(37, 96)
    tail.lineTo(57, 81)
    painter.drawPath(tail)
    painter.drawLine(43, 43, 85, 43)
    painter.drawLine(43, 58, 73, 58)


def create_app_icon() -> QIcon:
    icon = QIcon()
    for size in (16, 24, 32, 48, 64, 128, 256):
        image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        _draw_logo(painter, size)
        painter.end()
        icon.addPixmap(QPixmap.fromImage(image))
    return icon


def create_action_icon(name: str, color: str = "#49665e", size: int = 24) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(QPen(QColor(color), 1.8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
    painter.setBrush(Qt.BrushStyle.NoBrush)

    if name == "book":
        path = QPainterPath()
        path.moveTo(3, 4)
        path.lineTo(9, 4)
        path.quadTo(10.5, 4, 12, 6)
        path.quadTo(13.5, 4, 15, 4)
        path.lineTo(21, 4)
        path.lineTo(21, 19)
        path.lineTo(15, 19)
        path.quadTo(13.5, 19, 12, 21)
        path.quadTo(10.5, 19, 9, 19)
        path.lineTo(3, 19)
        path.closeSubpath()
        painter.drawPath(path)
        painter.drawLine(12, 6, 12, 20)
    elif name == "export":
        painter.drawLine(12, 3, 12, 14)
        painter.drawLine(8, 7, 12, 3)
        painter.drawLine(16, 7, 12, 3)
        painter.drawRoundedRect(QRectF(4, 13, 16, 7), 2, 2)
        painter.drawLine(8, 16, 8, 17)
        painter.drawLine(16, 16, 16, 17)
    elif name == "settings":
        for y, knob_x in ((5, 9), (12, 15), (19, 7)):
            painter.drawLine(3, y, 21, y)
            painter.setBrush(QColor("#ffffff"))
            painter.drawEllipse(QRectF(knob_x - 2.2, y - 2.2, 4.4, 4.4))
            painter.setBrush(Qt.BrushStyle.NoBrush)
    elif name == "refresh":
        painter.drawArc(QRectF(4, 4, 16, 16), 35 * 16, 290 * 16)
        painter.drawLine(17, 3, 21, 4)
        painter.drawLine(21, 4, 20, 8)
    elif name == "trash":
        painter.drawRoundedRect(QRectF(6, 7, 12, 14), 2, 2)
        painter.drawLine(4, 5, 20, 5)
        painter.drawLine(9, 3, 15, 3)
        painter.drawLine(10, 10, 10, 18)
        painter.drawLine(14, 10, 14, 18)
    painter.end()
    return QIcon(pixmap)


def _png_bytes(image: QImage) -> bytes:
    buffer = QBuffer()
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    if not image.save(buffer, "PNG"):
        raise RuntimeError("Could not encode application icon.")
    return bytes(buffer.data())


def write_ico(path: Path) -> None:
    images = []
    for size in (16, 32, 48, 64, 128, 256):
        image = QImage(size, size, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        _draw_logo(painter, size)
        painter.end()
        images.append(_png_bytes(image))

    directory_size = 6 + 16 * len(images)
    offset = directory_size
    entries = []
    for size, image_data in zip((16, 32, 48, 64, 128, 256), images):
        dimension = 0 if size == 256 else size
        entries.append(struct.pack(
            "<BBBBHHII", dimension, dimension, 0, 0, 1, 32, len(image_data), offset
        ))
        offset += len(image_data)
    path.write_bytes(struct.pack("<HHH", 0, 1, len(images)) + b"".join(entries) + b"".join(images))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python app_icon.py <output.ico>")
    write_ico(Path(sys.argv[1]))
