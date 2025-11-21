"""Quick test to verify refactored code works correctly."""

from tests import volume_tester, log_console_and_file

# Run a quick test with just 2 tests
volume_tester(
    num_tests=2,
    min_vertices=10,
    max_vertices=20,
    r=0,
    peso_min=1,
    peso_max=20,
    log_csv_path="test_quick.csv",
    log_txt_path="test_quick.txt",
    family="random",
    draw_fn=None,
    log=log_console_and_file,
    boilerplate=True,
    lang="pt",
)
