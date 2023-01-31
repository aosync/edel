from . import consts

class Bldenv:
    def __init__(self):
        self.path = consts.CACHE / ('bldenv-%s-%s' % (consts.PID, consts.bldid()))

        self.proto = self.path / 'proto'
        self.build = self.path / 'build'
        self.manifest = self.path / 'manifest'

        self.proto.mkdir(parents=True, exist_ok=True)
        self.build.mkdir(parents=True, exist_ok=True)
