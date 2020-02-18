import gzip
import json
from typing import Union

from google.protobuf.json_format import Parse

from . import BaseIndexer
from ...proto import jina_pb2


class MetaProtoIndexer(BaseIndexer):
    """Storing and querying protobuf chunk/document using gzip and Python dict. """

    compress_level = 1  #: The compresslevel argument is an integer from 0 to 9 controlling the level of compression

    def get_query_handler(self):
        r = {}
        with gzip.open(self.index_abspath, 'rt') as fp:
            for l in fp:
                if l:
                    tmp = json.loads(l)
                    for k, v in tmp.items():
                        _parser = jina_pb2.Chunk if k[0] == 'c' else jina_pb2.Document
                        r[int(k[1:])] = Parse(v, _parser())
        return r

    def get_add_handler(self):
        """Append to the existing gzip file using text appending mode """

        # note this write mode must be append, otherwise the index will be overwrite in the search time
        return gzip.open(self.index_abspath, 'at', compresslevel=self.compress_level)

    def get_create_handler(self):
        """Creat a new gzip file"""
        return self.get_add_handler()

    def add(self, obj):
        """Add a JSON-friendly object to the indexer

        :param obj: an object can be jsonify
        """
        json.dump(obj, self.write_handler)
        self.write_handler.write('\n')

    def query(self, key: int) -> Union['jina_pb2.Chunk', 'jina_pb2.Document']:
        """ Find the protobuf chunk/doc using id

        :param key: ``chunk_id`` or ``doc_id``
        :return: protobuf chunk or protobuf document
        """
        return self.query_handler[key]
