# Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy, modify,
# merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
from elasticsearch import Elasticsearch, RequestsHttpConnection, NotFoundError
from elasticsearch import SerializationError, ConflictError, RequestError


class ElasticsearchClient:
    """
    Elasticsearch wrapper
    """
    es_client = None

    def __init__(self, host, awsauth):
        self.es_client = Elasticsearch(
            hosts=[{'host': host, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection,
            retry_on_timeout=True,
            max_retries=3
        )

    # def index(self, index, id, body, version):
    def index(self, index, id, body):
        """
        Indexes documents to elasticsearch.
        Uses external version support to handle duplicates.
        https://www.elastic.co/blog/elasticsearch-versioning-support
        https://www.elastic.co/guide/en/elasticsearch/reference/current/docs-index_.html#index-version-types
        """
        try:
            # response = self.es_client.index(index=index, id=id,
            #                                 body=body, version=version, version_type="external")
            # print("Indexed document with id: {id}, body: {body}"
            #       " and version: {version}".format(id=id, body=body,
            #                                        version=version))
            response = self.es_client.index(index=index, id=id, body=body)

            print("Indexed document with id: {id}, body: {body}".format(id=id, body=body))

            return response

        except (SerializationError, ConflictError,
                RequestError) as e:  # https://elasticsearch-py.readthedocs.io/en/master/exceptions.html#elasticsearch.ElasticsearchException
            # print("Elasticsearch Exception occured while indexing id={id}, body={body} and"
            #       "version={version}. Error: {error}".format(id=id, body=body, version=version,
            #                                                  error=str(e)))
            print("Elasticsearch Exception occured while indexing id={id}, body={body} and"
                    "Error: {error}".format(id=id, body=body, error=str(e)))
            return None

    # def delete(self, index, id, version):
    def delete(self, index, id):

        try:

            # response = self.es_client.delete(index=index, id=id, version=version, version_type="external")
            response = self.es_client.delete(index=index, id=id)
            print("Deleted document with id: {id}".format(id=id))

            return response

        except (SerializationError, ConflictError,
                RequestError, NotFoundError) as e:  # https://elasticsearch-py.readthedocs.io/en/master/exceptions.html#elasticsearch.ElasticsearchException
            print("Elasticsearch Exception occured while deleting id={id}. Error: {error}"
                  .format(id=id, error=str(e)))
            return None

    # @JM Elasticsearch get document API calls
    def get(self, index, id):

        try:

            response = self.es_client.get(index=index, id=id)
            print("Get document with id: {id}".format(id=id))

            return response

        except (SerializationError, ConflictError,
                RequestError, NotFoundError) as e:  # https://elasticsearch-py.readthedocs.io/en/master/exceptions.html#elasticsearch.ElasticsearchException
            print("Elasticsearch Exception occured while getting id={id}. Error: {error}"
                  .format(id=id, error=str(e)))
            return None

    # @JM Elasticsearch search document API calls
    def search(self, index, body):

        try:
            response = self.es_client.search(index=index, body=body)
            print("Search document with query: {}".format(body))

            return response

        except (SerializationError, ConflictError,
                RequestError, NotFoundError) as e:  # https://elasticsearch-py.readthedocs.io/en/master/exceptions.html#elasticsearch.ElasticsearchException
            print("Elasticsearch Exception occured while searching body={body}. Error: {error}"
                  .format(body=body, error=str(e)))
            return None
        