import unittest

import pb_test_pb2
import simple_convert

class TestPb2Json(unittest.TestCase):
    def setUp(self):
        self.pbobj = pb_test_pb2.m1()
        self.pbobj.int1 = 1
        self.pbobj.arr1.extend([11, 33, 55, 77])

        a2_1 = self.pbobj.arr2.add()
        a2_1.int2 = 2
        a3_1 = a2_1.arr3.add()
        a3_1.int3 = 88
        a3_2 = a2_1.arr3.add()
        a3_2.int3 = 99

        a2_2 = self.pbobj.arr2.add()
        a2_2.int2 = 3
        a3_1 = a2_2.arr3.add()
        a3_1.int3 = 1000
        a3_2 = a2_2.arr3.add()
        a3_2.int3 = 2000

        self.jsonobj = {
            "int1": 1,
            "arr1": [11, 33, 55, 77],
            "arr2": [{"int2": 2, "arr3": [{"int3": 88}, {"int3": 99}]},
                        {"int2": 3, "arr3": [{"int3": 1000}, {"int3": 2000}]}]}

    def runTest(self):
        self.assertEqual(simple_convert.pb2json(self.pbobj), self.jsonobj)

class TestJson2pb(unittest.TestCase):
    def setUp(self):
        self.jsonobj = {
            "int1": 1,
            "arr1": [11, 33, 55, 77],
            "arr2": [{"int2": 2, "arr3": [{"int3": 88}, {"int3": 99}]},
                        {"int2": 3, "arr3": [{"int3": 1000}, {"int3": 2000}]}]}

    def runTest(self):
        pb = simple_convert.json2pb("pb_test_pb2", "m1").get_pb(self.jsonobj)
        pbstr = pb.SerializeToString()
        m = pb_test_pb2.m1()
        m.ParseFromString(pbstr)

        self.assertEqual(m.int1, self.jsonobj["int1"])
        self.assertEqual(m.arr1._values, self.jsonobj["arr1"])
        for ind, item in enumerate(m.arr2._values):
            self.assertEqual(item.int2, self.jsonobj["arr2"][ind]["int2"])
            for ind2, item2 in enumerate(item.arr3._values):
                self.assertEqual(item2.int3, 
                    self.jsonobj["arr2"][ind]["arr3"][ind2]["int3"])

if __name__ == "__main__":
    unittest.main()

