"""Python example script showing proper use of the Cisco Sample Code header.
Copyright (c) {{current_year}} Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

from ydk.services import CRUDService
from ydk.providers import NetconfServiceProvider
from ydk.services import CodecService
from ydk.providers import CodecServiceProvider
from ydk.models.cisco_ios_xr import Cisco_IOS_XR_clns_isis_oper \
    as xr_clns_isis_oper
from ydk.models.openconfig import openconfig_bgp \
    as oc_bgp
from ydk.models.cisco_ios_xr import Cisco_IOS_XR_cdp_oper \
    as xr_cdp_oper
from ydk.models.cisco_ios_xr import Cisco_IOS_XR_ifmgr_cfg \
    as xr_ifmgr_cfg
from ydk.models.cisco_ios_xr import Cisco_IOS_XR_l2_eth_infra_cfg \
    as xr_eth_infra_cfg
from ydk.models.cisco_ios_xr import Cisco_IOS_XR_l2_eth_infra_datatypes \
    as xr_eth_infra_dt
from ydk.models.cisco_ios_xr import Cisco_IOS_XR_l2vpn_cfg \
    as xr_l2vpn_cfg
from ydk.models.cisco_ios_xr import Cisco_IOS_XR_ipv4_bgp_cfg \
    as xr_ipv4_bgp_cfg
from ydk.models.cisco_ios_xr import Cisco_IOS_XR_ipv4_bgp_datatypes \
    as xr_ipv4_bgp_datatypes
from ydk.models.cisco_ios_xr import Cisco_IOS_XR_ipv4_io_cfg \
    as xr_ipv4_io_cfg
from ydk.models.openconfig import openconfig_bgp \
    as oc_bgp
from ydk.models.openconfig import openconfig_bgp_types as oc_bgp_types
from ydk.types import Empty
from ydk.types import ChildrenMap
from ydk.filters import YFilter
import logging

__author__ = "Brent Foster <brfoster@cisco.com>"
__copyright__ = "Copyright (c) 2020 Cisco and/or its affiliates."
__license__ = "Cisco Sample Code License, Version 1.1"

nc_providers = []

def create_netconf_provider(request):
    address = request['node-ip']
    port=830
    username = request['node-user']
    password = request['node-pass']
    protocol = "ssh"
    # create NETCONF provider
    nc_provider = NetconfServiceProvider(address=address, port=port, username=username, password=password, protocol=protocol)
    nc_provider_dict = {'node-ip':address, 'provider':nc_provider}
    return nc_provider_dict

def create_service(request, nc_provider):
    # create CRUD service
    crud = CRUDService()
    # create codec provider
    codec_provider = CodecServiceProvider(type="xml")
    # create codec service
    codec = CodecService()
    interface_name = request ['interface-name']
    # create ifmgr obj
    if_cfg = xr_ifmgr_cfg.InterfaceConfigurations.InterfaceConfiguration()
    if_cfg.active = "act"
    if_cfg.interface_name = interface_name
    if_cfg.interface_mode_non_physical = xr_ifmgr_cfg.InterfaceModeEnum.l2_transport

    # creat ethernet service Encapsulation obj
    if_cfg.ethernet_service.encapsulation = if_cfg.ethernet_service.Encapsulation()
    encap_type = xr_eth_infra_dt.Match.match_dot1q
    encap_value = xr_eth_infra_dt.Vlan = int(request['vlan-id'])
    if_cfg.ethernet_service.encapsulation.outer_tag_type = encap_type
    if_cfg.ethernet_service.encapsulation.outer_range1_low = encap_value

    if_cfg.ethernet_service.rewrite = xr_ifmgr_cfg.InterfaceConfigurations.InterfaceConfiguration.EthernetService.Rewrite()
    rewrite_type = xr_eth_infra_dt.Rewrite.pop1
    if_cfg.ethernet_service.rewrite.rewrite_type = rewrite_type

    # create localtraffic obj
    local_traffic_def_encap = if_cfg.ethernet_service.LocalTrafficDefaultEncapsulation()
    if_cfg.ethernet_service.local_traffic_default_encapsulation = local_traffic_def_encap
    if_cfg.ethernet_service.local_traffic_default_encapsulation = if_cfg.ethernet_service.encapsulation

    # create the interface configurations add the if_cfg to it
    if_cfgs = xr_ifmgr_cfg.InterfaceConfigurations()
    if_cfgs.interface_configuration.append(if_cfg)
    if request['delete-config'] == 'off':
        crud.create(nc_provider, if_cfgs)
    elif request['delete-config'] == 'on':
        crud.delete(nc_provider, if_cfg)

    # create the l2vpn object, database and pw classes
    # set enable as "Empty" type
    l2vpn_cfg = xr_l2vpn_cfg.L2vpn()
    l2vpn_cfg.enable = Empty()
    l2vpn_cfg.database = xr_l2vpn_cfg.L2vpn.Database()
    l2vpn_cfg.database.pseudowire_classes = l2vpn_cfg.Database.PseudowireClasses()

    test_class = xr_l2vpn_cfg.L2vpn.Database.PseudowireClasses.PseudowireClass()
    test_class.name = "ELINE-PW"
    test_class.enable = Empty()
    test_class.mpls_encapsulation = xr_l2vpn_cfg.L2vpn.Database.PseudowireClasses.PseudowireClass().MplsEncapsulation()
    test_class.mpls_encapsulation.enable = Empty()
    test_class.mpls_encapsulation.control_word = xr_l2vpn_cfg.ControlWord.enable
    flow_label = xr_l2vpn_cfg.FlowLabelLoadBalance()
    # flow_label = xr_l2vpn_cfg.L2vpn.Database.PseudowireClasses.PseudowireClass.MplsEncapsulation.LoadBalanceGroup.FlowLabelLoadBalance()
    test_class.mpls_encapsulation.load_balance_group = xr_l2vpn_cfg.L2vpn.Database.PseudowireClasses.PseudowireClass.MplsEncapsulation.LoadBalanceGroup()
    test_class.mpls_encapsulation.load_balance_group.flow_label_load_balance.flow_label = flow_label.both
    l2vpn_cfg.database.pseudowire_classes.pseudowire_class.append(test_class)

    l2vpn_cfg.database.xconnect_groups = xr_l2vpn_cfg.L2vpn.Database.XconnectGroups()
    test_group = xr_l2vpn_cfg.L2vpn.Database.XconnectGroups.XconnectGroup()
    test_group.name = "ELINE-SVCS"
    l2vpn_cfg.database.xconnect_groups.xconnect_group.append(test_group)

    test_group.p2p_xconnects = l2vpn_cfg.Database.XconnectGroups.XconnectGroup.P2pXconnects()
    test_xconnect = xr_l2vpn_cfg.L2vpn.Database.XconnectGroups.XconnectGroup.P2pXconnects.P2pXconnect()
    test_xconnect.name = request['vlan-id'] + "-" + request['pw-id']
    test_group.p2p_xconnects.p2p_xconnect.append(test_xconnect)

    test_xconnect.attachment_circuits = xr_l2vpn_cfg.L2vpn.Database.XconnectGroups.XconnectGroup.P2pXconnects.P2pXconnect.AttachmentCircuits()
    test_ac = xr_l2vpn_cfg.L2vpn.Database.XconnectGroups.XconnectGroup.P2pXconnects.P2pXconnect.AttachmentCircuits.AttachmentCircuit()
    test_ac.name = request['interface-name']
    test_ac.enable = Empty()
    test_xconnect.attachment_circuits.attachment_circuit.append(test_ac)

    test_xconnect.pseudowires = xr_l2vpn_cfg.L2vpn.Database.XconnectGroups.XconnectGroup.P2pXconnects.P2pXconnect.Pseudowires()
    test_pw = xr_l2vpn_cfg.L2vpn.Database.XconnectGroups.XconnectGroup.P2pXconnects.P2pXconnect.Pseudowires.Pseudowire()
    test_pw.pseudowire_id = int(request['pw-id'])
    test_neighbor = xr_l2vpn_cfg.L2vpn.Database.XconnectGroups.XconnectGroup.P2pXconnects.P2pXconnect.Pseudowires.Pseudowire.Neighbor()
    test_neighbor.neighbor = request['neighbor-ip']
    test_neighbor.class_ = "ELINE-PW"
    test_pw.neighbor.append(test_neighbor)
    test_xconnect.pseudowires.pseudowire.append(test_pw)

    the_xml = codec.encode(codec_provider, l2vpn_cfg)
    if request['delete-config'] == 'off':
        crud.create(nc_provider, l2vpn_cfg)
    elif request['delete-config'] == 'on':
        xc_group = l2vpn_cfg.database.xconnect_groups.xconnect_group.get("ELINE-SVCS")
        xc = xc_group.p2p_xconnects.p2p_xconnect[test_xconnect.name]
        xc.yfilter = YFilter.delete
        # xc.attachment_circuits.yfilter = YFilter.delete
        # xc.pseudowires.yfilter = YFilter.delete
        crud.update(nc_provider, xc_group)
    return

def create_l3_service(request, nc_provider):
    # create CRUD service
    crud = CRUDService()
    # create codec provider
    codec_provider = CodecServiceProvider(type="xml")
    # create codec service
    codec = CodecService()

    # interface configuration
    interface_name = request['interface-name']
    # create ifmgr obj
    if_cfg = xr_ifmgr_cfg.InterfaceConfigurations.InterfaceConfiguration()
    if_cfg.active = "act"
    if_cfg.interface_name = interface_name
    if_cfg.interface_mode_non_physical = xr_ifmgr_cfg.InterfaceModeEnum.default

    if_cfg.statistics = xr_ifmgr_cfg.InterfaceConfigurations.InterfaceConfiguration.Statistics()
    if_cfg.statistics.load_interval = 30

    if_cfg.ipv4_network = xr_ifmgr_cfg.InterfaceConfigurations.InterfaceConfiguration.Ipv4Network()
    if_cfg.ipv4_network.addresses = xr_ifmgr_cfg.InterfaceConfigurations.InterfaceConfiguration.Ipv4Network().Addresses()

    primary_address = xr_ifmgr_cfg.InterfaceConfigurations.InterfaceConfiguration.Ipv4Network().Addresses().Primary()
    primary_address.address = request['intf-ip']
    primary_address.netmask = "255.255.255.252"

    if_cfg.ipv4_network.addresses.primary = primary_address

    if_cfg.vlan_sub_configuration = xr_ifmgr_cfg.InterfaceConfigurations.InterfaceConfiguration().VlanSubConfiguration()
    if_cfg.vlan_sub_configuration.vlan_identifier = xr_ifmgr_cfg.InterfaceConfigurations.InterfaceConfiguration().VlanSubConfiguration().VlanIdentifier()
    if_cfg.vlan_sub_configuration.vlan_identifier.first_tag = int(request['vlan-id'])
    encap_type = xr_eth_infra_dt.Vlan.vlan_type_dot1q
    if_cfg.vlan_sub_configuration.vlan_identifier.vlan_type = encap_type

    the_xml = codec.encode(codec_provider, if_cfg)
    # logging.info(the_xml)
    # create the interface configurations add the if_cfg to it
    if_cfgs = xr_ifmgr_cfg.InterfaceConfigurations()
    if_cfgs.interface_configuration.append(if_cfg)

    if request['delete-config'] == 'off':
        crud.create(nc_provider, if_cfgs)
    elif request['delete-config'] == 'on':
        crud.delete(nc_provider, if_cfg)

    # global configuration
    bgp = xr_ipv4_bgp_cfg.Bgp()
    instance = bgp.Instance()
    instance.instance_name = "default"
    instance_as = instance.InstanceAs()
    instance_as.as_ = 0
    four_byte_as = instance_as.FourByteAs()
    four_byte_as.as_ = int(request['bgp-as'])
    four_byte_as.bgp_running = Empty()
    # global address family
    global_af = four_byte_as.default_vrf.global_.global_afs.GlobalAf()
    global_af.af_name = xr_ipv4_bgp_datatypes.BgpAddressFamily.ipv4_unicast
    global_af.enable = Empty()
    global_af.sourced_networks = four_byte_as.default_vrf.global_.global_afs.GlobalAf().SourcedNetworks()
    network = four_byte_as.default_vrf.global_.global_afs.GlobalAf().SourcedNetworks().SourcedNetwork()
    addr_parsed = request['intf-ip'].split('.')
    addr = addr_parsed[0] + "." + addr_parsed[1] + "." + addr_parsed[2] + ".0"
    network.network_addr = addr
    network.network_prefix = int(request['mask'])
    global_af.sourced_networks.sourced_network.append(network)

    four_byte_as.default_vrf.global_.global_afs.global_af.append(global_af)
    instance_as.four_byte_as.append(four_byte_as)
    instance.instance_as.append(instance_as)
    bgp.instance.append(instance)


    the_xml = codec.encode(codec_provider, bgp)
    logging.info(the_xml)

    if request['delete-config'] == 'off':
        crud.create(nc_provider, bgp)
    elif request['delete-config'] == 'on':
        bgp_instance = bgp.instance['default']
        sourced = bgp.instance['default'].instance_as['0'].four_byte_as[request['bgp-as']].default_vrf.global_.global_afs.global_af['ipv4-unicast'].sourced_networks
        sn = sourced.sourced_network[addr, int(request['mask'])]
        sn.yfilter = YFilter.delete
        crud.update(nc_provider, bgp)

    return


def get_cdp(address, port, username, password, protocol):
    # create NETCONF provider
    provider = NetconfServiceProvider(address=address, port=port, username=username, password=password, protocol=protocol)
    # create CRUD service
    crud = CRUDService()
    cdp = xr_cdp_oper.Cdp()
    cdp = crud.read(provider, cdp)
    cdp_neigh =''
    for node in cdp.nodes.node:
        for detail in node.neighbors.details.detail:
            cdp_neigh += detail.device_id + '\n'
    return cdp_neigh