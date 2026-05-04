"""Quick preview: render only the JPEG snapshot, skip the MP4 encode."""
import build_billboard as b


def main():
    img = b.compose_frame(4.5)
    img.save(b.OUT_JPG, "JPEG", quality=92, optimize=True)
    print("wrote", b.OUT_JPG)


if __name__ == "__main__":
    main()
