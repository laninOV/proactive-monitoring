#!/usr/bin/env python3
import yaml
import json
import api
from datetime import datetime

class Host():
    def __init__(self, hostname):
        self.hostname = hostname
        self.instance = None
        self.fqdn = None
        self.clean_metric()
        self.clean_delta()

    def clean_metric(self):
        self.cpu = None
        self.ram = None
        self.io_read = None
        self.io_write = None
        self.net_socket_tcp_alloc = None
        self.net_socket_tcp_inuse = None
        self.net_socket_tcp_mem = None
        self.net_socket_tcp_orphan = None
        self.net_socket_tcp_tw = None

    def clean_delta(self):
        self.cpu_delta = None
        self.ram_delta = None
        self.io_read_delta = None
        self.io_write_delta = None
        self.net_socket_tcp_alloc_delta = None
        self.net_socket_tcp_inuse_delta = None
        self.net_socket_tcp_mem_delta = None
        self.net_socket_tcp_orphan_delta = None
        self.net_socket_tcp_tw_delta = None

    def set_instance(self, instance):
        self.instance = instance

    def set_fqdn(self, fqdn):
        self.fqdn = fqdn

    def get_instance(self):
        return self.instance

    def get_avg_value(self, values):
        all_values = [float(value) for value in values]
        return sum(all_values) / len(all_values)

    def get_plural_value(self, values):
        metrics = []
        for item in values:
            metrics.append(self.get_avg_value(item))
        return metrics

    def set_metric(self, values, metric):
        if metric == "cpu_utilization":
            self.cpu = self.get_plural_value(values)
        elif metric == "ram_utilization":
            self.ram = self.get_plural_value(values)
        elif metric == "io_read":
            self.io_read = self.get_plural_value(values)
        elif metric == "io_write":
            self.io_write = self.get_plural_value(values)
        elif metric == "tcp_alloc":
            self.net_socket_tcp_alloc = self.get_plural_value(values)
        elif metric == "tcp_inuse":
            self.net_socket_tcp_inuse = self.get_plural_value(values)
        elif metric == "tcp_mem":
            self.net_socket_tcp_mem = self.get_plural_value(values)
        elif metric == "tcp_orphan":
            self.net_socket_tcp_orphan = self.get_plural_value(values)
        elif metric == "tcp_tw":
            self.net_socket_tcp_tw = self.get_plural_value(values)
        else:
            pass

    def set_delta(self, values, metric):
        if metric == "cpu_utilization":
            self.cpu_delta = self.get_plural_value(values)
        elif metric == "ram_utilization":
            self.ram_delta = self.get_plural_value(values)
        elif metric == "io_read":
            self.io_read_delta = self.get_plural_value(values)
        elif metric == "io_write":
            self.io_write_delta = self.get_plural_value(values)
        elif metric == "tcp_alloc":
            self.net_socket_tcp_alloc_delta = self.get_plural_value(values)
        elif metric == "tcp_inuse":
            self.net_socket_tcp_inuse_delta = self.get_plural_value(values)
        elif metric == "tcp_mem":
            self.net_socket_tcp_mem_delta = self.get_plural_value(values)
        elif metric == "tcp_orphan":
            self.net_socket_tcp_orphan_delta = self.get_plural_value(values)
        elif metric == "tcp_tw":
            self.net_socket_tcp_tw_delta = self.get_plural_value(values)
        else:
            pass

def parse_instance(json, hosts):
    for result in json['result']:
        for host in hosts:
            if result['metric']['nodename'].split('.')[0] == host.hostname:
                host.set_instance(result['metric']['instance'])
                host.set_fqdn(result['metric']['nodename'])
    return hosts

def get_instance(hosts):
    # Получение списка объектов типа Host.
    # Каждому присваивается атрибут instance
    l = []
    for host in hosts:
        l.append(host.hostname)
    l = api.get_metric(l, ['search_instance'])
    return parse_instance(l, hosts)

def clear_all_metrics(hosts):
    for host in hosts:
        host.clean_metric()
    return hosts

def clear_all_deltas(hosts):
    for host in hosts:
        host.clean_delta()
    return hosts

def get_all_endpoints(hosts):
    result = []
    for host in hosts:
        if host.instance:
            result.append(host.instance)
    return result

def get_avg_metric(hosts, data, metric_name):
    for host in hosts:
        metric_list = []
        for metric in data:
            if metric['metric']['instance'] == host.instance:
                metric_list.append(metric['values'])
        host.set_metric(metric_list, metric_name)
    return hosts

def get_delta(hosts, data, metric_name):
    for host in hosts:
        metric_list = []
        for metric in data:
            if metric['metric']['instance'] == host.instance:
                metric_list.append(metric['values'])
        host.set_delta(metric_list, metric_name)
    return hosts

def get_all_metrics(hosts, end_time, step):
    metrics = ["cpu_utilization", "ram_utilization", "io_read", "io_write", "tcp_alloc", "tcp_inuse", "tcp_mem", "tcp_orphan", "tcp_tw"]
    endpoints = get_all_endpoints(hosts)
    row_metrics = api.get_metric(endpoints, metrics, end_time, step)
    hosts = clear_all_metrics(hosts)
    for metric in metrics:
        try:
            hosts = get_avg_metric(hosts, row_metrics[metric]['result'], metric)
        except:
            print("Не получена метрика:", metric, str(datetime.fromtimestamp(end_time)))
            print(row_metrics)
    return hosts

def get_all_deltas(hosts, end_time, step, delta):
    metrics = ["cpu_utilization", "ram_utilization", "io_read", "io_write", "tcp_alloc", "tcp_inuse", "tcp_mem", "tcp_orphan", "tcp_tw"]
    endpoints = get_all_endpoints(hosts)
    row_metrics = api.get_metric(endpoints, metrics, end_time, step, delta=delta)
    hosts = clear_all_deltas(hosts)
    for metric in metrics:
        try:
            hosts = get_delta(hosts, row_metrics[metric]['result'], metric)
        except:
            print("Не получена метрика:", metric, str(datetime.fromtimestamp(end_time)))
            print(row_metrics)
    return hosts
