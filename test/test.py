import unittest

import neo4j



class TestConnection(unittest.TestCase):

    def setUp(self):
        self.n4cm = neo4j.connect("http://localhost:7474")


    def test_request(self):

        # because sometime the previous tests fucks up
        self.n4cm.request("MATCH (n:TestCommit) DELETE n")

        # insert
        self.n4cm.request("CREATE (n:TestCommit {name:1337})")

        # query / insert check
        r = self.n4cm.request("MATCH (n:TestCommit) RETURN n.name")
        self.assertEqual(r, [[1337]] )

        # delete
        self.n4cm.request("MATCH (n:TestCommit) DELETE n")

        # query / delete check
        r = self.n4cm.request("MATCH (n:TestCommit) RETURN n.name")
        self.assertEqual(r, [] )


    def test_transaction_commit(self):

        # because sometime the previous tests fucks up
        self.n4cm.request("MATCH (n:TestCommit) DELETE n")

        with self.n4cm.transaction as t:
            t.execute("CREATE (n:TestCommit {name:1338})")
            t.execute("CREATE (n:TestCommit {name:1339})")
            t.commit()

        # query / insert check
        r = self.n4cm.request("MATCH (n:TestCommit) RETURN n.name")
        self.assertEqual(len(r), 2)
        self.assertIn([1338], r)
        self.assertIn([1339], r)

        self.n4cm.request("MATCH (n:TestCommit) DELETE n")


    def test_transaction_rollback(self):

        with self.n4cm.transaction as t:
            t.execute("CREATE (n:TestCommit {name:1338})")
            t.execute("CREATE (n:TestCommit {name:1339})")
            t.rollback()

        # query / insert check
        r = self.n4cm.request("MATCH (n:TestCommit) RETURN n.name")
        self.assertEqual(len(r), 0)




if __name__ == '__main__':
    unittest.main()
