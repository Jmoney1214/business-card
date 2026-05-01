"""Quick preview: render only the JPEG snapshot, skip the MP4 encode."""
import build_billboard as b


def main():
    qr_side = b.qr_card(b.make_qr(b.QR_URL, 220), pad=12)
    qr_rear = b.qr_card(b.make_qr(b.QR_URL, 220), pad=12)
    img = b.compose_frame(4.5, qr_side, qr_rear)
    img.save(b.OUT_JPG, "JPEG", quality=92, optimize=True)
    print("wrote", b.OUT_JPG)


if __name__ == "__main__":
    main()
