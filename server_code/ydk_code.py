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
from ydk.types import Empty
import logging

nc_providers = []

def create_netconf_provider(request):
    address = request['node-ip']
    port=830
    username = request['node-user']
    password = request['node-pass']
    protocol = "ssh"
    interface_name = request ['interface-name']
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
    # the_xml = codec.encode(codec_provider, l2vpn_cfg)
    if request['delete-config'] == 'off':
        crud.create(nc_provider, l2vpn_cfg)
    elif request['delete-config'] == 'on':
        to_delete = l2vpn_cfg.database.xconnect_groups.xconnect_group.get("ELINE-SVCS")
        crud.delete(nc_provider, to_delete)
    return



def get_cdp(address, port, username, password, protocol):
    # create NETCONF provider
    provider = NetconfServiceProvider(address=address, port=port, username=username, password=password, protocol=protocol)

    # create CRUD service
    crud = CRUDService()
    bgp = oc_bgp.Bgp()  # create object
    cdp = xr_cdp_oper.Cdp()
    cdp = crud.read(provider, cdp)
    foo =''
    for node in cdp.nodes.node:
        for detail in node.neighbors.details.detail:
            foo += detail.device_id + '\n'
    return foo
    # read data from NETCONF device
    # bgp = crud.read(provider, bgp)
    # # create object
    # isis_obj = xr_clns_isis_oper.Isis()
    # # read data from NETCONF device
    # isis = crud.read(provider, isis_obj)
    #
    # """Process data in isis object."""
    # # format string for isis neighbor header
    # isis_header = ("IS-IS {instance} neighbors:\n"
    #                "System Id      Interface        SNPA           State "
    #                "Holdtime Type IETF-NSF")
    # # format string for isis neighbor row
    # isis_row = ("{sys_id:<14} {intf:<16} {snpa:<14} {state:<5} "
    #             "{hold:<8} {type_:<4} {ietf_nsf:^8}")
    # # format string for isis neighbor trailer
    # isis_trailer = "Total neighbor count: {count}"
    #
    # nbr_state = {0: "Up", 1: "Init", 2: "Fail"}
    # nbr_type = {0: "None", 1: "L1", 2: "L2", 3: "L1L2"}
    #
    # if isis.instances.instance:
    #     show_isis_nbr = str()
    # else:
    #     show_isis_nbr = "No IS-IS instances found"
    #
    # # iterate over all instances
    # for instance in isis.instances.instance:
    #     if show_isis_nbr:
    #         show_isis_nbr += "\n\n"
    #
    #     show_isis_nbr += isis_header.format(instance=instance.instance_name)
    #     nbr_count = 0
    #     host_name = instance.host_names.host_name
    #     host_names = dict([(h.system_id, h.host_name) for h in host_name])
    #     # iterate over all neighbors
    #     for neighbor in instance.neighbors.neighbor:
    #         nbr_count += 1
    #         sys_id = host_names[neighbor.system_id]
    #         intf = (neighbor.interface_name[:2] +
    #                 re.sub(r'\D+', "", neighbor.interface_name, 1))
    #         state = nbr_state[neighbor.neighbor_state.value]
    #         type_ = nbr_type[neighbor.neighbor_circuit_type.value]
    #         ietf_nsf = "Y" if neighbor.neighbor_ietf_nsf_capable_flag else "N"
    #         show_isis_nbr += ("\n" +
    #                           isis_row.format(sys_id=sys_id,
    #                                           intf=intf,
    #                                           snpa=neighbor.neighbor_snpa,
    #                                           state=state,
    #                                           hold=neighbor.neighbor_holdtime,
    #                                           type_=type_,
    #                                           ietf_nsf=ietf_nsf))
    #     if nbr_count:
    #         show_isis_nbr += "\n\n" + isis_trailer.format(count=nbr_count)
    #
    # # return formatted string
    # return show_isis_nbr
