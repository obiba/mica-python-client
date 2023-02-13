"""
Apply access on a study dataset.
"""

import obiba_mica.core as core
import obiba_mica.access as access

def add_arguments(parser):
    """
    Add command specific options
    """
    access.add_permission_arguments(parser, True)
    parser.add_argument('id', help='Collected dataset ID')

def do_command(args):
    """
    Execute access command
    """
    # Build and send requests
    access.validate_args(args)

    request = core.MicaClient.build(core.MicaClient.LoginInfo.parse(args)).new_request()

    if args.verbose:
        request.verbose()

    # send request
    if args.delete:
        request.delete()
    else:
        request.put()

    try:
        response = request.resource(access.do_ws(args, ['draft','collected-dataset', args.id, 'accesses'])).send()
    except Exception as e:
        print(Exception, e)

    # format response
    if response.code != 204:
        print(response.content)
