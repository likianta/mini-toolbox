class _FakeType:
    
    def __getattr__(self, _) -> '_FakeType':
        return self
    
    def __getitem__(self, _) -> '_FakeType':
        return self
    
    def __call__(self) -> '_FakeType':
        import warnings
        warnings.warn(
            '`FakeType()` is deprecated, use `FakeType` directly.',
            DeprecationWarning
        )
        return self


# singleton
FakeType = _FakeType()
