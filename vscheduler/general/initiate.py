# distinguishes commands arguments
import sys
from vscheduler.general.help import Help

arg_num = len(sys.argv)

class PrintCondition():
    fprint = True if '-v' in sys.argv[1:] or '--verbose' in sys.argv[1:] else False

class Initiation:
    node = user = ''
    
    for arg in range (1, arg_num-1):
        if sys.argv[arg] == '-u':
            if arg+1 <= arg_num-1 and sys.argv[arg+1] != '-n':
                user = sys.argv[arg+1]
        elif sys.argv[arg] == '-n':
            if arg+1 <= arg_num-1 and sys.argv[arg+1] != '-u':
                node = sys.argv[arg+1]