# Copyright 2018 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import joblib
import fairing
import numpy as np

MODEL_FILE = 'trained_ames_model.dat'

import sys
sys.path.insert(0,"/home/jovyan/fairing")
print(sys.path)

#fairing.config.set_builder('docker', registry='index.docker.io/m1st3rb3an', base_image="seldonio/seldon-core-s2i-python3:0.4")
#fairing.config.set_builder('append', registry='index.docker.io/m1st3rb3an', base_image="seldonio/seldon-core-s2i-python3:0.4")
fairing.config.set_builder('cluster', registry='index.docker.io/m1st3rb3an', base_image="seldonio/seldon-core-s2i-python3:0.4")

fairing.config.set_deployer('serving', serving_class="HousingServe")

class HousingServe(object):
  def __init__(self, model_file=MODEL_FILE):
    """Load the housing model using joblib."""
    self.model = joblib.load(model_file)


  def predict(self, X, feature_names):
    """Predict using the model for given ndarray."""
    prediction = self.model.predict(data=X)
    return [[prediction.item(0), prediction.item(0)]]


if __name__ == '__main__':
  fairing.config.run()
  serve = HousingServe()
  print(serve.predict(np.ndarray([1, 37]), None))
