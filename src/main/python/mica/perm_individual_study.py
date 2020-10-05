"""
Apply permissions on an individual study.
"""

import sys
import mica.core
import mica.perm

def add_arguments(parser):
    """
    Add command specific options
    """
    mica.perm.add_permission_arguments(parser)
    parser.add_argument('id', help='Individual Study ID')

def do_command(args):
    """
    Execute permission command
    """
    # Build and send requests
    try:
        mica.perm.validate_args(args)

        request = mica.core.MicaClient.build(mica.core.MicaClient.LoginInfo.parse(args)).new_request()

        if args.verbose:
            request.verbose()

        # send request
        if args.delete:
            request.delete()
        else:
            request.put()

        try:
            response = request.resource(mica.perm.do_ws(args, ['draft','individual-study', args.id, 'permissions'])).send()
        except Exception as e:
            print(Exception, e)

        # format response
        if response.code != 204:
            print(response.content)

    except Exception as e:
        print(e)
        sys.exit(2)

    except pycurl.error as error:
        errno, errstr = error
        print('An error occurred: ', errstr, file=sys.stderr)
        sys.exit(2)
