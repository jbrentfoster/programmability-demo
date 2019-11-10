from ydk.services import CRUDService
from ydk.providers import NetconfServiceProvider
from ydk.models.cisco_ios_xr import Cisco_IOS_XR_clns_isis_oper \
    as xr_clns_isis_oper
from ydk.models.openconfig import openconfig_bgp \
    as oc_bgp
from ydk.models.cisco_ios_xr import Cisco_IOS_XR_cdp_oper \
    as xr_cdp_oper
import re
import logging


def process_isis(address, port, username, password, protocol):
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
    return foo
