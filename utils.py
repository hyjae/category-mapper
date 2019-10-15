
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
    def gen_mm_query(index, fields, query, match_type='most_fields', size=1):
        """Generate ES multi-match query

        :param index: index
        :param query: a query string
        :param match_type: refer to official doc
        :param fields: a list of fields to search
        :param size: return size
        :return: query dict()
        """
        if not isinstance(fields, list):
            fields = [fields]
        return [
            {
                "index": index
            },
            {
                "query": {
                    "multi_match": {
                        "query": query,
                        "type": match_type,
                        "fields": fields
                    }
                },
                "size": size
            }
        ]
