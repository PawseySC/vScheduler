# distinguishes commands arguments
import sys
from vscheduler.general.help import Help

arg_num = len(sys.argv)

class PrintCondition():
    fprint = True if '-v' in sys.argv[1:] or '--verbose' in sys.argv[1:] else False

class Initiation:
    node = user = start = end = status = ''
    email = False
    
    for arg in range (1, arg_num-1):
        if sys.argv[arg] == '-u':
            if arg+1 <= arg_num-1 and sys.argv[arg+1] != '-n' and sys.argv[arg+1] != '-d' and sys.argv[arg+1] != '-v' and sys.argv[arg+1] != '--add' and sys.argv[arg+1] != '--remove' and sys.argv[arg+1] != '--status' and sys.argv[arg+1] != '--email':
                user = sys.argv[arg+1]
        elif sys.argv[arg] == '-n':
            if arg+1 <= arg_num-1 and sys.argv[arg+1] != '-u' and sys.argv[arg+1] != '-d' and sys.argv[arg+1] != '-v' and sys.argv[arg+1] != '--add' and sys.argv[arg+1] != '--remove' and sys.argv[arg+1] != '--status' and sys.argv[arg+1] != '--email':
                node = sys.argv[arg+1]
        elif sys.argv[arg] == '-d':
            if arg+1 <= arg_num-1 and sys.argv[arg+1] != '-u' and sys.argv[arg+1] != '-n' and sys.argv[arg+1] != '-v' and sys.argv[arg+1] != '--add' and sys.argv[arg+1] != '--remove' and sys.argv[arg+1] != '--status' and sys.argv[arg+1] != '--email':
                start = sys.argv[arg+1]
                if sys.argv[arg+2] and sys.argv[arg+2] != '-u' and sys.argv[arg+2] != '-n' and sys.argv[arg+2] != '-v' and sys.argv[arg+2] != '--add' and sys.argv[arg+2] != '--remove' and sys.argv[arg+2] != '--status' and sys.argv[arg+1] != '--email':
                    end = sys.argv[arg+2]
        elif sys.argv[arg] == '--add':
            status = 'add'
        elif sys.argv[arg] == '--remove':
            status = 'remove'
        elif sys.argv[arg] == '--status':
            status = 'status'
        elif sys.argv[arg] == '--email':
            email = True

    if sys.argv[1:].count('-u') > 1 or sys.argv[1:].count('-n') > 1 or sys.argv[1:].count('-d') > 1 or sys.argv[1:].count('--add') > 1 or sys.argv[1:].count('--remove') > 1 or sys.argv[1:].count('--status') > 1:
        print ("error in arguments, please see help")
        sys.exit()