#!/usr/bin/python


import click
import json
import yaml

from collections import defaultdict


RKE_IMAGES = {
    'etcd': 'quay.io/coreos/etcd:latest',
    'kube-api': 'rancher/k8s:v1.8.3-rancher2',
    'kube-controller': 'rancher/k8s:v1.8.3-rancher2',
    'scheduler': 'rancher/k8s:v1.8.3-rancher2',
    'kubelet': 'rancher/k8s:v1.8.3-rancher2',
    'kubeproxy': 'rancher/k8s:v1.8.3-rancher2'
}


@click.command()
@click.option('--terraform-state-file', required=True)
@click.option('--cluster-manifest-file', default='cluster.yml')
def main(terraform_state_file=None, cluster_manifest_file=None):
    '''
    Generate RKE cluster configuration from Terraform outputs.

    The following outputs must be defined:
        - rke_control_plane_nodes
        - rke_etcd_nodes
        - rke_worker_nodes

    The outputs must be lists of node IP addresses
    (SSH-accessible from the system where RKE will be run).
    '''

    print("Terraform state file is '{0}'.".format(
        terraform_state_file
    ))

    with open(terraform_state_file) as state_file:
        terraform_state = json.load(state_file)

    outputs = {
        output_name: output['value']
        for module in terraform_state['modules']
        for (output_name, output) in module['outputs'].items()
    }

    rke_control_plane_nodes = []
    rke_etcd_nodes = []
    rke_worker_nodes = []
    for output in outputs.keys():
        if not output.startswith('rke_'):
            continue

        value = outputs[output]
        if not isinstance(value, list):
            value = [value]

        if output == 'rke_control_plane_nodes':
            rke_control_plane_nodes.extend(value)
        if output == 'rke_etcd_nodes':
            rke_etcd_nodes.extend(value)
        if output == 'rke_worker_nodes':
            rke_worker_nodes.extend(value)

    print('rke_control_plane_nodes = {0}'.format(
        repr(rke_control_plane_nodes)
    ))
    print('rke_etcd_nodes = {0}'.format(
        repr(rke_etcd_nodes)
    ))
    print('rke_worker_nodes = {0}'.format(
        repr(rke_worker_nodes)
    ))

    node_roles = defaultdict(set)
    for node_ip in rke_control_plane_nodes:
        node_roles[node_ip].add('controlplane')
    for node_ip in rke_etcd_nodes:
        node_roles[node_ip].add('etcd')
    for node_ip in rke_worker_nodes:
        node_roles[node_ip].add('worker')

    rke_manifest_nodes = []
    for (node_ip, roles) in node_roles.items():
        rke_manifest_nodes.append({
            'address': str(node_ip),
            'user': 'root',
            'role': list(roles)
        })

    rke_manifest_services = {}
    for (service, image) in RKE_IMAGES.items():
        rke_manifest_services[service] = {
            'image': image
        }

    rke_manifest = {
        'nodes': rke_manifest_nodes,
        'services': rke_manifest_services
    }

    print('Writing RKE cluster manifest...')

    with open(cluster_manifest_file, 'w') as manifest_file:
        manifest_file.write('# RKE Manifest\n')
        yaml.dump(rke_manifest, manifest_file,
            default_flow_style=False
        )

    print('Done.')

if __name__ == '__main__':
    main()
