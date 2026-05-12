from osir_transform.OsirTransform import OsirTransform

test = OsirTransform.from_yaml("/home/typ/Desktop/OSIR/OSIR/configs/dependencies/transform/linux/mactime.yml")

test.save_vrl("/home/typ/Desktop/OSIR/OSIR/configs/dependencies/transform/linux/mactime.vrl")

