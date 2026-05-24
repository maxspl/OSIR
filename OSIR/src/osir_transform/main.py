from osir_transform.OsirTransform import OsirTransform

test = OsirTransform.from_yaml("/home/typ/Desktop/OSIR/OSIR/configs/dependencies/transform/windows/evtx.yml")

test.save_vrl("/home/typ/Desktop/OSIR/OSIR/configs/dependencies/ecs_normalize/evtx.vrl")

