from c20_client.do_wait import get_wait_time


def test_get_wait_time():
    assert get_wait_time() == 3.66
