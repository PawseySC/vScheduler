# distinguishes commands arguments
import sys
from vscheduler.general.help import Help

arg_num = len(sys.argv)

class PrintCondition():
    fprint = True if '-v' in sys.argv[1:] or '--verbose' in sys.argv[1:] else False

class Initiation:
    node = user = start = end = ''
    
    for arg in range (1, arg_num-1):
        if sys.argv[arg] == '-u':
            if arg+1 <= arg_num-1 and sys.argv[arg+1] != '-n' and sys.argv[arg+1] != '-d' and sys.argv[arg+1] != '-v':
                user = sys.argv[arg+1]
        elif sys.argv[arg] == '-n':
            if arg+1 <= arg_num-1 and sys.argv[arg+1] != '-u' and sys.argv[arg+1] != '-d' and sys.argv[arg+1] != '-v':
                node = sys.argv[arg+1]
        elif sys.argv[arg] == '-d':
            if arg+1 <= arg_num-1 and sys.argv[arg+1] != '-u' and sys.argv[arg+1] != '-n' and sys.argv[arg+1] != '-v':
                start = sys.argv[arg+1]
                if sys.argv[arg+2] and sys.argv[arg+2] != '-u' and sys.argv[arg+2] != '-n' and sys.argv[arg+2] != '-v':
                    end = sys.argv[arg+2]

    if sys.argv[1:].count('-u') > 1 or sys.argv[1:].count('-n') > 1 or sys.argv[1:].count('-d') > 1:
        print ("error in arguments, please see help")
        sys.exit()