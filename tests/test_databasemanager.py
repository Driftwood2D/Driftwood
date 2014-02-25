import shutil
import unittest
import unittest.mock as mock

import databasemanager

driftwood = mock.Mock()
driftwood.config = {
    'database': {
        'root': 'db.test',
        'name': 'test.db'
    }
}
driftwood.log.msg.side_effect = Exception('log.msg called')

class TestDatabaseCreation(unittest.TestCase):
    def test_create_db_dir_if_not_exist(self):
        dbm = databasemanager.DatabaseManager(driftwood)
    
    def test_create_db_file_if_not_exist(self):
        databasemanager.DatabaseManager(driftwood)

    def tearDown(self):
        shutil.rmtree('db.test', ignore_errors=False)
