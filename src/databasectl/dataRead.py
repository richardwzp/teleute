import yaml

from src.databasectl.postgres import PostgresQLDatabase


def readPreset(path):
    with open(path, "r") as f:
        try:
            res = yaml.safe_load(f)
            data = res['data']
            for key, val in res['override'].items():
                for point in data:
                    point[key] = val
            return data
        except yaml.YAMLError as exc:
            print(exc)


def fillDatabase(db: PostgresQLDatabase):
    with db.get_instance() as inst:
        for val in readPreset("classPreset.yaml"):
            class_name, full_name, description, school = val.values()
            inst.add_class(class_name, full_name, description, school)




if __name__ == '__main__':
    print(readPreset("classPreset.yaml"))
    #with PostgresQLDatabase() as db:
    #    fillDatabase(db)
