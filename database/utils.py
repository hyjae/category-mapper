import json


class DBUtils:

    @staticmethod
    def page_query(q):
        offset = 0
        while True:
            r = False
            for elem in q.limit(1000).offset(offset):
                r = True
                yield elem
            offset += 1000
            if not r:
                break


class ESUtils:

    @staticmethod
    def multi_match_query(query, query_type, fields):
        if not isinstance(fields, list):
            fields = [fields]
        return json.dump({
            "query": {
                "multi_match": {
                    "query": query,
                    "type": query_type,
                    "fields": fields
                }
            }
        }).encode('utf-8')

    @staticmethod
    def multi_search(es_conn, queries, index, doc_type, retries=0):



        None
print(ESUtils.multi_match_query(1,2,3))