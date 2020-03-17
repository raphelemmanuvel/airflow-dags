# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""An example DAG demonstrating Kubernetes Pod Operator."""

# [START composer_kubernetespodoperator]
import datetime
from airflow import models
from airflow.contrib.kubernetes import secret
from airflow.contrib.operators import kubernetes_pod_operator


# A Secret is an object that contains a small amount of sensitive data such as
# a password, a token, or a key. Such information might otherwise be put in a
# Pod specification or in an image; putting it in a Secret object allows for
# more control over how it is used, and reduces the risk of accidental
# exposure.

# [START composer_kubernetespodoperator_secretobject]
secret_env = secret.Secret(
    # Expose the secret as environment variable.
    deploy_type='env',
    # The name of the environment variable, since deploy_type is `env` rather
    # than `volume`.
    deploy_target='SQL_CONN',
    # Name of the Kubernetes Secret
    secret='airflow-secrets',
    # Key of a secret stored in this Secret object
    key='sql_alchemy_conn')
# [END composer_kubernetespodoperator_secretobject]

YESTERDAY = datetime.datetime.now() - datetime.timedelta(days=1)

# If a Pod fails to launch, or has an error occur in the container, Airflow
# will show the task as failed, as well as contain all of the task logs
# required to debug.
with models.DAG(
        dag_id='composer_sample_kubernetes_pod',
        schedule_interval=datetime.timedelta(days=1),
        start_date=YESTERDAY) as dag:
    # Only name, namespace, image, and task_id are required to create a
    # KubernetesPodOperator. In Cloud Composer, currently the operator defaults
    # to using the config file found at `/home/airflow/composer_kube_config if
    # no `config_file` parameter is specified. By default it will contain the
    # credentials for Cloud Composer's Google Kubernetes Engine cluster that is
    # created upon environment creation.

    # [START composer_kubernetespodoperator_minconfig]
    kubernetes_min_pod = kubernetes_pod_operator.KubernetesPodOperator(
        # The ID specified for the task.
        task_id='pod-ex-minimum',
        # Name of task you want to run, used to generate Pod ID.
        name='pod-ex-minimum',
        # Entrypoint of the container, if not specified the Docker container's
        # entrypoint is used. The cmds parameter is templated.
        cmds=['echo'],
        # The namespace to run within Kubernetes, default namespace is
        # `default`. There is the potential for the resource starvation of
        # Airflow workers and scheduler within the Cloud Composer environment,
        # the recommended solution is to increase the amount of nodes in order
        # to satisfy the computing requirements. Alternatively, launching pods
        # into a custom namespace will stop fighting over resources.
        namespace='default',
        # Docker image specified. Defaults to hub.docker.com, but any fully
        # qualified URLs will point to a custom repository. Supports private
        # gcr.io images if the Composer Environment is under the same
        # project-id as the gcr.io images and the service account that Composer
        # uses has permission to access the Google Container Registry
        # (the default service account has permission)
        is_delete_operator_pod=True,
        image='gcr.io/gcp-runtimes/ubuntu_18_0_4')
    # [END composer_kubernetespodoperator_minconfig]

# [END composer_kubernetespodoperator]
