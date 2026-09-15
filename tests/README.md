# Offline tests

From the project root after installing requirements, run:

```powershell
py -m unittest discover -s tests -v
```

The 24 tests use mocked AI responses. They test application behavior and failure handling, not legal accuracy. See TEST_RESULTS.md in the project root.
