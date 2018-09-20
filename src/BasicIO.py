import codecs


def load_data(fp):

    with codecs.open(fp, "r", encoding = "utf8") as f:
        return f.readlines()


def write_data(fp, data):

    f = codecs.open(fp, "w", encoding = "utf8")

    for line in data:
        f.write(line + "\n")

    f.close()
