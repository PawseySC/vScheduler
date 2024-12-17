# distinguishes commands arguments
import sys
from vscheduler.general.help import Help
from vscheduler.lib.config import Credentials as MyCredentials

arg_num = len(sys.argv)

class PrintCondition():
    fprint = True if '-v' in sys.argv[1:] else False

class Initiation:
    node = user = start = end = status = mode = partition = time = ''
    email = session = list = activate = deactivate = False
    
    for arg in range (1, arg_num-1):
        if sys.argv[arg] == '-u':
            if arg+1 <= arg_num-1 and sys.argv[arg+1] != '-n' and sys.argv[arg+1] != '-d' and sys.argv[arg+1] != '-v' and sys.argv[arg+1] != '-t':
                user = sys.argv[arg+1]
            else:
                print ("error in arguments, please see help")
                sys.exit()
        elif sys.argv[arg] == '-n':
            if arg+1 <= arg_num-1 and sys.argv[arg+1] != '-u' and sys.argv[arg+1] != '-d' and sys.argv[arg+1] != '-v' and sys.argv[arg+1] != '-t':
                node = sys.argv[arg+1]
            else:
                print ("error in arguments, please see help")
                sys.exit()
        elif sys.argv[arg] == '-t':
            if arg+1 <= arg_num-1 and sys.argv[arg+1] != '-n' and sys.argv[arg+1] != '-u' and sys.argv[arg+1] != '-d' and sys.argv[arg+1] != '-v':
                time = sys.argv[arg+1]
            else:
                print ("error in arguments, please see help")
                sys.exit()
        elif sys.argv[arg] == '-d':
            if arg+1 <= arg_num-1 and sys.argv[arg+1] != '-u' and sys.argv[arg+1] != '-n' and sys.argv[arg+1] != '-v' and sys.argv[arg+1] != '-t':
                start = sys.argv[arg+1]
                if arg+2 <= arg_num-1:
                    # if sys.argv[arg+2] and sys.argv[arg+2] != '-u' and sys.argv[arg+2] != '-n' and sys.argv[arg+2] != '-v' and sys.argv[arg+1] != '-t':
                    if sys.argv[arg+2] and sys.argv[arg+2] != '-u' and sys.argv[arg+2] != '-n' and sys.argv[arg+2] != '-v' and sys.argv[arg+2] != '-t':
                        end = sys.argv[arg+2]
                    else:
                        print ("error in arguments, please see help")
                        sys.exit()
            else:
                print ("error in arguments, please see help")
                sys.exit()
        elif sys.argv[arg+1] == 'up':
            status = 'up'                       # up means fresh node in production with no one logged in = idle
        elif sys.argv[arg+1] == 'down':
            status = 'down'
        elif sys.argv[arg+1] == 'maint':
            status = 'maint'
        elif sys.argv[arg+1] == 'dev':
            status = 'dev'                      # dev nodes communicate with dev-vscheduler
        elif sys.argv[arg+1] == 'allocated':    # any node with logged in user
            status = 'allocated'
        # elif sys.argv[arg+1] == 'idle':         # nodes from bookable partition which are not booked and with no logged in user OR nodes not allocated to any user in general pool (meaning no user is logged in)
        #     status = 'idle'
        elif sys.argv[arg+1] == 'reserved':     # booked (only for bookable partition)
            status = 'reserved'
        elif sys.argv[arg] == 'create':
            mode = 'create'
            partition = sys.argv[arg+1]
        elif sys.argv[arg] == 'delete':
            mode = 'delete'
            partition = sys.argv[arg+1]
        elif sys.argv[arg] == 'status':
            mode = 'status'
        elif sys.argv[arg] == 'list':
            mode = 'list'
        elif sys.argv[arg] == 'activate':
            mode = 'activate'
        elif sys.argv[arg] == 'deactivate':
            mode = 'deactivate'
        

    if sys.argv[1:].count('-u') > 1 or sys.argv[1:].count('-n') > 1 or sys.argv[1:].count('-d') > 1 or sys.argv[1:].count('--add') > 1 or sys.argv[1:].count('--remove') > 1 or sys.argv[1:].count('--status') > 1:
        print ("error in arguments, please see help")
        sys.exit()