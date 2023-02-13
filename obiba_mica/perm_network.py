"""
Apply permissions on a network.
"""

import obiba_mica.core as core
import obiba_mica.perm as perm

def add_arguments(parser):
    """
    Add command specific options
    """
    perm.add_permission_arguments(parser)
    parser.add_argument('id', help='Network ID')

def do_command(args):
    """
    Execute permission command
    """
    # Build and send requests
    perm.validate_args(args)

    request = core.MicaClient.build(core.MicaClient.LoginInfo.parse(args)).new_request()

    if args.verbose:
        request.verbose()

    # send request
    if args.delete:
        request.delete()
    else:
        request.put()

    response = request.resource(perm.do_ws(args, ['draft','network', args.id, 'permissions'])).send()

    # format response
    if response.code != 204:
        print(response.content)
