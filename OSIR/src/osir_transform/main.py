from osir_transform.osir_transform import OsirTransform


def main():
    test = OsirTransform.from_yaml("/home/typ/Desktop/OSIR/OSIR/configs/dependencies/transform/windows/evtx.yml")
    test.save_vrl("/home/typ/Desktop/OSIR/OSIR/configs/dependencies/ecs_normalize/evtx.vrl")


if __name__ == "__main__":
    main()
