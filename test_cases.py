import main
import unittest

class TestMusterPoint(unittest.TestCase):

    def test_class_user(self):
        # Test User Class
        # Test Instantiation
        test_correct_params  = main.User('Testname', 'testID', 'testID')
        test_no_params = main.User()
        test_wrong_type_params = main.User(True, 1, False)
        test_too_few_params = main.User('test', 'test')
        self.assertIsInstance(test_correct_params, main.User)
        self.assertEqual(test_correct_params.name, 'Testname')
        self.assertEqual(test_correct_params.badge_id, 'testID')
        self.assertEqual(test_correct_params.face_coords, 'testID')
        self.assertIsInstance(test_no_params, main.User)
        self.assertIsInstance(test_wrong_type_params, main.User)
        self.assertIsInstance(test_too_few_params, main.User)

    def test_class_zone(self):
        # Test Zone Class
        # Test Instantiation
        test_correct_params  = main.Zone('Testname', 'testID', 'testID')
        test_no_params = main.Zone()
        test_wrong_type_params = main.Zone(True, 1, False)
        test_too_few_params = main.Zone('test', 'test')
        self.assertIsInstance(test_correct_params, main.Zone)
        self.assertEqual(test_correct_params.name, 'Testname')
        self.assertEqual(test_correct_params.cctv_sensorid, 'testID')
        self.assertEqual(test_correct_params.door_sensorid, 'testID')
        self.assertIsInstance(test_no_params, main.Zone)
        self.assertIsInstance(test_wrong_type_params, main.Zone)
        self.assertIsInstance(test_too_few_params, main.Zone)

    def test_class_cctvsensor(self):
        # Test CCTVSensor Class
        # Test Instantiation
        test_correct_params = main.CCTVSensor('123', 'Zone9999')
        test_no_params = main.CCTVSensor()
        test_wrong_type_params = main.CCTVSensor(True, 1, False)
        test_too_few_params = main.CCTVSensor('test', 'test')
        self.assertIsInstance(test_correct_params, main.CCTVSensor)
        self.assertEqual(test_correct_params.id, '123')
        self.assertEqual(test_correct_params.zone, 'Zone9999')
        self.assertIsInstance(test_no_params, main.CCTVSensor)
        self.assertIsInstance(test_wrong_type_params, main.CCTVSensor)
        self.assertIsInstance(test_too_few_params, main.CCTVSensor)

    def test_class_doorsensor(self):
        # Test DoorSensor Class
        # Test Instantiation
        test_correct_params = main.DoorSensor('123', 'Zone9999')
        test_no_params = main.DoorSensor()
        test_wrong_type_params = main.DoorSensor(True, 1, False)
        test_too_few_params = main.DoorSensor('test', 'test')
        self.assertIsInstance(test_correct_params, main.DoorSensor)
        self.assertEqual(test_correct_params.id, '123')
        self.assertEqual(test_correct_params.zone, 'Zone9999')
        self.assertIsInstance(test_no_params, main.DoorSensor)
        self.assertIsInstance(test_wrong_type_params, main.DoorSensor)
        self.assertIsInstance(test_too_few_params, main.DoorSensor)
    

if __name__ == '__main__':
    unittest.main()