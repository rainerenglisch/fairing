import logging

import fairing
import json
import numpy as np
from fairing.deployers.job.job import Job
from fairing.deployers.serving.serving import Serving
from fairing.backends import KubernetesBackend
from .utils import guess_preprocessor

import requests

logger = logging.getLogger(__name__)


class BaseTask:
    """
    Base class for handling high level ML tasks.
    args:
        entry_point: An object or reference to the source code that has to be deployed.
        base_docker_image: Name of the base docker image that should be used as a base image
            when building a new docker image as part of an ML task deployment.
        docker_registry: Docker registry to store output docker images.
        input_files: list of files that needs to be packaged along with the entry point.
            E.g. local python modules, trained model weigths, etc.
    """
    def __init__(self, entry_point, base_docker_image, docker_registry, input_files=None, backend=None):
        self._backend = backend or KubernetesBackend()
        input_files = input_files or []
        preprocessor = guess_preprocessor(entry_point, input_files=input_files)
        logger.warn("Using preprocessor: {}".format(type(preprocessor)))

        self.docker_registry = docker_registry
        logger.warn("Using docker registry: {}".format(self.docker_registry))

        self.builder = backend.get_builder(preprocessor=preprocessor,
                                           base_image=base_docker_image,
                                           registry=self.docker_registry)
        #rainer
        from fairing.builders.append.append import AppendBuilder

        self.builder = AppendBuilder(preprocessor=preprocessor,
                                 base_image=base_docker_image,
                                 registry=self.docker_registry)
        #end
        logger.warn("Using builder: {}".format(type(self.builder)))

    def _build(self):
        logging.info("Building the docker image.")
        self.builder.build()
        self.pod_spec = self.builder.generate_pod_spec()


class TrainJob(BaseTask):

    def __init__(self, entry_point, base_docker_image, docker_registry, input_files=None, backend=None):
        super().__init__(entry_point, base_docker_image, docker_registry, input_files, backend)

    def submit(self):
        self._build()
        deployer = self._backend.get_training_deployer()
        return deployer.deploy(self.pod_spec)


class PredictionEndpoint(BaseTask):

    def __init__(self, model_class, base_docker_image, docker_registry, input_files=None, backend=None):
        self.model_class = model_class
        super().__init__(model_class, base_docker_image, docker_registry, input_files, backend=backend)

    def create(self):
        self._build()
        logging.info("Deploying the endpoint.")
        self._deployer = self._backend.get_serving_deployer(self.model_class.__name__)
        self.url = self._deployer.deploy(self.pod_spec)
        logger.warning("Prediction endpoint: {}".format(self.url))

    def predict_nparray(self, data, feature_names=None):
        #rainer start
        import requests
        import json
        import time
        logging.info("PredictionEndpoint.predict_nparray: Start")
        #rainer ende
        pdata={
            "data": {
                "names":feature_names,
                "tensor": {
                    "shape": np.asarray(data.shape).tolist(),
                    "values": data.flatten().tolist(),
                },
            }
        }
        
        serialized_data = json.dumps(pdata)
        
        #rainer_start
        url_prediction = self.url + "/predict"
        logging.info("self.url: {}".format(url_prediction))
        #logging.info("pdata: {}".format(pdata))
        #logging.info("serialized data: {}".format(serialized_data))
        #r = requests.post(url_prediction, data={'json':serialized_data})
        #headers = {'content-type': 'application/json'}
        
        #try:
        r = requests.post(url_prediction, data={'json':serialized_data},timeout=1)#, headers=headers)
        #except Exception as e:
            #print(e)
            #time.sleep(10)
            #r = requests.post(url_prediction, data={'json':serialized_data})
        
        response = r.json()
        #logger.info("Response: {}".format(response))
        logging.info("PredictionEndpoint.predict_nparray: End")
        return r.json()
        #rainer_end

    def delete(self):
        self._deployer.delete()
