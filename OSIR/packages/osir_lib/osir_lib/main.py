from core.model.OsirModuleModel import OsirModuleModel

print(OsirModuleModel.from_yaml('/home/typ/Desktop/OSIR/OSIR/configs/modules/network/zeek.yml').model_dump())