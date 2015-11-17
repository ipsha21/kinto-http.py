import unittest2 as unittest
import mock

from kinto_client.batch import Batch, batch_requests


class BatchRequestsTest(unittest.TestCase):
    def setUp(self):
        self.client = mock.MagicMock()

    def test_requests_are_stacked(self):
        batch = Batch(self.client)
        batch.request('GET', '/foobar/baz',
                  mock.sentinel.data,
                  mock.sentinel.permissions)
        assert len(batch.requests) == 1

    def test_send_adds_data_attribute(self):
        batch = Batch(self.client)
        batch.request('GET', '/foobar/baz', data={'foo': 'bar'})
        batch.send()

        self.client.session.request.assert_called_with(
            'POST',
            self.client.endpoints.batch(),
            data={'requests': [{
                'method': 'GET',
                'path': '/foobar/baz',
                'body': {'data': {'foo': 'bar'}}
            }]}
        )

    def test_send_adds_permissions_attribute(self):
        batch = Batch(self.client)
        batch.request('GET', '/foobar/baz', permissions=mock.sentinel.permissions)
        batch.send()

        self.client.session.request.assert_called_with(
            'POST',
            self.client.endpoints.batch(),
            data={'requests': [{
                'method': 'GET',
                'path': '/foobar/baz',
                'body': {'permissions': mock.sentinel.permissions}
            }]}
        )

    def test_send_adds_headers_if_specified(self):
        batch = Batch(self.client)
        batch.request('GET', '/foobar/baz', headers={'Foo': 'Bar'})
        batch.send()

        self.client.session.request.assert_called_with(
            'POST',
            self.client.endpoints.batch(),
            data={'requests': [{
                'method': 'GET',
                'path': '/foobar/baz',
                'headers': {'Foo': 'Bar'},
                'body': {}
            }]}
        )

    def test_send_empties_the_requests_cache(self):
        batch = Batch(self.client)
        batch.request('GET', '/foobar/baz',
                      permissions=mock.sentinel.permissions)
        assert len(batch.requests) == 1
        batch.send()
        assert len(batch.requests) == 0

    def test_context_manager_works_as_expected(self):
        batcher = batch_requests
        with batcher(self.client) as batch:
            batch.request('PUT', '/records/1234', data={'foo': 'bar'})
            batch.request('PUT', '/records/5678', data={'bar': 'baz'})

        assert self.client.session.request.called
