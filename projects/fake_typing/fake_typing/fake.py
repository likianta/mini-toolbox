class FakeType:

    def __getattr__(self, _) -> 'FakeType':
        return self    

    def __getitem__(self, _) -> 'FakeType':
        return self
