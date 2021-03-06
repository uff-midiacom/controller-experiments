from mininet.net import Mininet
# from mininet.cli import CLI
from mininet.log import setLogLevel
from time import sleep
from sys import argv as args


def ovsns(user, ctrl_ip='10.0.0.13'):

    "Create an empty network and add nodes to it."

    mn = Mininet(topo=None, build=False)

    h1 = mn.addHost('h1', ip='10.0.0.1', mac='00:00:00:00:00:01')
    s1 = mn.addHost('s1', ip='0.0.0.0')
    s2 = mn.addHost('s2', ip='0.0.0.0')
    h2 = mn.addHost('h2', ip='10.0.0.2', mac='00:00:00:00:00:02')

    c0 = mn.addHost('c0', ip=ctrl_ip, mac='00:00:00:00:00:13')

    mn.addLink(h1, s1)
    mn.addLink(s1, s2)
    mn.addLink(h2, s2)
    mn.addLink(c0, s2)

    mn.start()

    c0.cmd(
        '/home/' + user +
        '/.local/bin/ryu-manager ../simple_switch_13_timeout.py '
        '> logs/ryu.log 2>&1 &')

    sleep(1)

    s1.cmd(
        'bash sw_config_script.sh s1 100 2 ' +
        ctrl_ip + ' > logs/s1.log')
    s2.cmd(
        'bash sw_config_script.sh s2 101 3 ' +
        ctrl_ip + ' > logs/s2.log')

    sleep(1)

    s1.cmd('tcpdump -i s1-eth1 -w logs/s1-eth1.pcap &')
    s2.cmd('tcpdump -i s2-eth0 -w logs/s2-eth0.pcap &')
    h1.cmd('tcpdump -i h1-eth0 -w logs/h1.pcap &')
    h2.cmd('tcpdump -i h2-eth0 -w logs/h2.pcap &')

    sleep(1)

    h2.cmdPrint('ping -c 1 10.0.0.1')

    # h1.cmd(
    #     'tcpreplay -i h1-eth0 -K --mbps 2 packets.pcap '
    #     '> logs/tcpreplay_info.txt')
    # sleep(30)
    # s1.cmd('ovs-ofctl dump-flows s1 > logs/flows_s1.log 2>&1 &')
    # s2.cmd('ovs-ofctl dump-flows s1 > logs/flows_s1.log 2>&1 &')

    # CLI(mn)

    sleep(1)

    s1.cmd('killall -2 tcpdump')

    h1.cmd('rm -rf /tmp/mininet-s*')
    mn.stop()


if __name__ == '__main__':
    setLogLevel('info')
    if len(args) == 2:
        ovsns(args[1])
    else:
        print('Usage: sudo python inband_test.py $USER')
