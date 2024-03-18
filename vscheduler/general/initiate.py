# distinguishes commands arguments
import sys
from vscheduler.general.help import Help

arg_num = len(sys.argv)

class PrintCondition():
    fprint = True if '-v' in sys.argv[1:] or '--verbose' in sys.argv[1:] else False

class Initiation:
    node = user = start = end = status = ''
    email = session = False
    
    for arg in range (1, arg_num-1):
        if sys.argv[arg] == '-u':
            if arg+1 <= arg_num-1 and sys.argv[arg+1] != '-n' and sys.argv[arg+1] != '-d' and sys.argv[arg+1] != '-v' and sys.argv[arg+1] != '--status':
                user = sys.argv[arg+1]
        elif sys.argv[arg] == '-n':
            if arg+1 <= arg_num-1 and sys.argv[arg+1] != '-u' and sys.argv[arg+1] != '-d' and sys.argv[arg+1] != '-v' and sys.argv[arg+1] != '--status':
                node = sys.argv[arg+1]
        elif sys.argv[arg] == '-d':
            if arg+1 <= arg_num-1 and sys.argv[arg+1] != '-u' and sys.argv[arg+1] != '-n' and sys.argv[arg+1] != '-v' and sys.argv[arg+1] != '--status':
                start = sys.argv[arg+1]
                if sys.argv[arg+2] and sys.argv[arg+2] != '-u' and sys.argv[arg+2] != '-n' and sys.argv[arg+2] != '-v' and sys.argv[arg+2] != '--status':
                    end = sys.argv[arg+2]
        elif sys.argv[arg] == '--status' and arg+1 <= arg_num-1:
            if sys.argv[arg+1] == 'up':
                status = 'up'                       # up means fresh node in production with no one logged in = idle
            elif sys.argv[arg+1] == 'down':
                status = 'down'
            elif sys.argv[arg+1] == 'maint':
                status = 'maint'
            elif sys.argv[arg+1] == 'allocated':    # any node with logged in user
                status = 'allocated'
            # elif sys.argv[arg+1] == 'idle':         # nodes from bookable partition which are not booked and with no logged in user OR nodes not allocated to any user in general pool (meaning no user is logged in)
            #     status = 'idle'
            elif sys.argv[arg+1] == 'reserved':     # booked (only for bookable partition)
                status = 'reserved'
        elif sys.argv[arg] == '--session':
            session = True
        

    if sys.argv[1:].count('-u') > 1 or sys.argv[1:].count('-n') > 1 or sys.argv[1:].count('-d') > 1 or sys.argv[1:].count('--add') > 1 or sys.argv[1:].count('--remove') > 1 or sys.argv[1:].count('--status') > 1:
        print ("error in arguments, please see help")
        sys.exit()