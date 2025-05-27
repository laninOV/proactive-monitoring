from host_logic import Host, get_all_metrics, get_instance, get_all_deltas
from copy import deepcopy
from alert import alert, send_all_alert_mail
import time
import yaml
from datetime import datetime
import config

with open("way4_hosts.yml") as host_groups_yaml:
    try:
        host_groups = yaml.safe_load(host_groups_yaml)
    except:
        pass

class Count_host():
    def __init__(self, hostname):
        self.hostname = hostname
        self.fqdn = None
        self.alive = 0
        self.cpu = 0
        self.cpu_more_60 = 0
        self.cpu_dfy = 0 # dfy is different from yesterday
        self.ram = 0
        self.ram_more_60 = 0
        self.ram_dfy = 0
        self.iops = 0
        self.io_read = 0
        self.io_write = 0
        self.net_socket_tcp_alloc = 0
        self.net_socket_tcp_inuse = 0
        self.net_socket_tcp_mem = 0
        self.net_socket_tcp_orphan = 0
        self.net_socket_tcp_tw = 0

    def send_alert(self, value, text, time):
        if value == config.counter:
            alert(self.fqdn, time, text)

    def count_metric(self, metric, text, time):
        value = getattr(self, metric)
        setattr(self, metric, value + 1)
        self.send_alert(getattr(self, metric), text, time)

def current_timestamp():
    return int(time.time())

def day_ago_timestamp():
    return int(time.time()) - 86400

def check_attribute(count_object, attribute):
    try:
        x = getattr(count_object, attribute)
    except:
        setattr(count_object, attribute, 0)

def search_delta(hostname, host_list, metric, i):
    for host in host_list:
        if host.hostname == hostname:
            return abs(getattr(host, metric + '_delta')[i])

def compare_deltas(hosts, hosts_day_ago, hosts_two_ago, hosts_three_ago, metric, alert_value, time, text, counter):
    for host in hosts:
        try:
            values = getattr(host, metric + '_delta')
            for i in range(len(values)):
                delta_1 = abs(values[i])
                delta_2 = search_delta(host.hostname, hosts_day_ago, metric, i)
                delta_3 = search_delta(host.hostname, hosts_two_ago, metric, i)
                delta_7 = search_delta(host.hostname, hosts_three_ago, metric, i)
                # print(host.hostname, metric, delta_1, delta_2, delta_3, delta_7)
                if delta_7 > alert_value and delta_1 > alert_value and delta_2 > alert_value and delta_3 > alert_value:
                    counter[host.hostname].count_metric(metric + '_dfy' + str(i), text, time)
                else:
                    setattr(counter[host.hostname], metric + '_dfy' + str(i), 0)
        except:
            pass

def compare_data_cpu(hosts, hosts_day_ago, hosts_two_ago, hosts_three_ago, counter, time):
    compare_deltas(hosts, hosts_day_ago, hosts_two_ago, hosts_three_ago, 'cpu', 50, time, "значение cpu отличается от нормы", counter)
    for i in range(len(hosts)):
        if hosts[i].cpu:
            avg_value = hosts[i].cpu[0]
            counter[hosts[i].hostname].cpu = 0
            if avg_value > 60:
                counter[hosts[i].hostname].count_metric('cpu_more_60', "значение cpu выше 60 процентов.", time)

def compare_data_ram(hosts, hosts_day_ago, hosts_two_ago, hosts_three_ago, counter, time):
    compare_deltas(hosts, hosts_day_ago, hosts_two_ago, hosts_three_ago, 'ram', 20, time, "значение ram отличается от нормы", counter)
    for i in range(len(hosts)):
        if hosts[i].ram:
            avg_value = hosts[i].ram[0]
            counter[hosts[i].hostname].ram = 0
            if avg_value > 60:
                counter[hosts[i].hostname].count_metric('ram_more_60', "значение total_memory выше 60 процентов.", time)
        else:
            counter[hosts[i].hostname].count_metric('ram', "Нет данных для хоста, проверьте API", time)

def compare_data_iops(hosts, hosts_day_ago, hosts_two_ago, hosts_three_ago, counter, time):
    for i in range(len(hosts)):
        if hosts[i].io_read and hosts[i].io_write:
            for y in range(len(hosts[i].io_read)):
                check_attribute(counter[hosts[i].hostname], 'io_read' + str(y))
                value = hosts[i].io_read[y]
                if value > 2000:
                    counter[hosts[i].hostname].count_metric('io_read' + str(y), "значение io_read выше 2000.", time)
                else:
                    setattr(counter[hosts[i].hostname], 'io_read' + str(y), 0)
            for y in range(len(hosts[i].io_write)):
                check_attribute(counter[hosts[i].hostname], 'io_write' + str(y))
                value = hosts[i].io_write[y]
                if value > 2000:
                    counter[hosts[i].hostname].count_metric('io_write' + str(y), "значение io_write выше 2000.", time)
                else:
                    setattr(counter[hosts[i].hostname], 'io_write' + str(y), 0)
        else:
            counter[hosts[i].hostname].count_metric('iops', "Нет данных для хоста, проверьте API", time)

def compare_data_socket_tcp(hosts, hosts_day_ago, hosts_two_ago, hosts_three_ago, counter, time):
    for metric in ['net_socket_tcp_alloc', 'net_socket_tcp_inuse', 'net_socket_tcp_mem', 'net_socket_tcp_orphan']:
        # compare_deltas(hosts, hosts_day_ago, hosts_two_ago, hosts_three_ago, metric, 50, time, "значение " + metric + " отличается от нормы", counter)
        for i in range(len(hosts)):
            check_attribute(counter[hosts[i].hostname], metric, 0)
            avg_value = getattr(hosts[i], metric)[0]
            if avg_value > 10000:
                counter[hosts[i].hostname].count_metric(metric + '_10k', "значение " + metric + " выше 10k.", time)
            else:
                setattr(counter[hosts[i].hostname], metric + '_10k', 0)
            if not getattr(hosts[i], metric):
                counter[hosts[i].hostname].count_metric(metric, "Нет данных для хоста, проверьте API", time)

def check_host_alive(hosts, counter, time):
    for host in hosts:
        if host.hostname in counter:
            if counter[host.hostname].alive == config.counter:
                alert(host.hostname, time, "Нет данных для хоста, проверьте API")
            counter[host.hostname].fqdn = host.fqdn
            if host.instance:
                counter[host.hostname].alive = 0
            else:
                counter[host.hostname].alive = counter[host.hostname].alive + 1
        else:
            counter[host.hostname] = Count_host(host.hostname)

def main_logic(counter, groups, step_minutes):
    step = step_minutes * 60
    time_now = current_timestamp()
    time_yesterday = day_ago_timestamp()
    for group in host_groups:
        if group['name'] in groups:
            hosts = groups[group['name']]
        else:
            hosts = []
            for host in group['hosts']:
                hosts.append(Host(host))
            try:
                hosts = get_instance(hosts)
            except:
                print('Не удалось прочитать инстансы', group['name'])
            groups[group['name']] = hosts

        check_host_alive(hosts, counter, time_now)

        hosts_day_ago = deepcopy(hosts)
        hosts_two_ago = deepcopy(hosts)
        hosts_three_ago = deepcopy(hosts)
        hosts_day_ago = get_all_deltas(hosts_day_ago, time_now, step, '1d')
        hosts_two_ago = get_all_deltas(hosts_two_ago, time_now, step, '2d')
        hosts_three_ago = get_all_deltas(hosts_three_ago, time_now, step, '3d')
        hosts = get_all_metrics(hosts, time_now, step)
        hosts = get_all_deltas(hosts, time_now, step, '7d')

        print(group['name'], str(datetime.fromtimestamp(time_now)))

        compare_data_cpu(hosts, hosts_day_ago, hosts_two_ago, hosts_three_ago, counter, time_now)
        compare_data_ram(hosts, hosts_day_ago, hosts_two_ago, hosts_three_ago, counter, time_now)
        compare_data_iops(hosts, hosts_day_ago, hosts_two_ago, hosts_three_ago, counter, time_now)
        compare_data_socket_tcp(hosts, hosts_day_ago, hosts_two_ago, hosts_three_ago, counter, time_now)
        send_all_alert_mail(group['name'])
