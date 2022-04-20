# Copyright (C) 2022 Indoc Research
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import random

from fastapi.testclient import TestClient

from app.app_utils import decode_path_from_ltree
from app.app_utils import encode_path_for_ltree
from app.main import app


class TestUtils:
    app = TestClient(app)

    def generate_random_label(self) -> str:
        random_label = ''
        label_length = random.randint(4, 20)
        for _ in range(label_length):
            random_label += chr(random.randint(32, 126))
        return random_label

    def generate_random_path(self) -> str:
        random_path = ''
        labels = random.randint(1, 8)
        for _ in range(labels):
            random_path += f'{self.generate_random_label()}.'
        return random_path[:-1]

    def test_01_encode_decode_paths(self):
        random_paths = []
        paths_to_test = 100
        for _ in range(paths_to_test):
            random_paths.append(self.generate_random_path())
        for path in random_paths:
            encoded = encode_path_for_ltree(path)
            decoded = decode_path_from_ltree(encoded)
            assert decoded == path
