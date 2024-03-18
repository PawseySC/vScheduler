import sys
from optparse import OptionParser, OptionError

class Help:
    
    prog = 'Desktop Session Management and Reporting Platform [Vscheduler'
    version = '2023.1'
    title = '''
                        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                        *                                           *
                        *        Pawsey Supercomputing Centre       *
                        *           Visualisation Scheduler         *
                        *                                           *
                        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    '''
    help_text = '''
Notes:
    Specifying <user> without <node> will check the current bookings for the specific user against all nodes.
    Specifying <node> without <user> will check the current bookings of the specific node against all users.
    Specifying <node> & <user> will check the current bookings of the specific node against specific user.
    Specifying no <node> & <user> will check the current bookings for all nodes against all users.
    Specifying <date> is only considered for report.
    Specifying no <date> considers whole database records.
    Specifying only one date considers current date for end.
    '''
    # usage = '%s [-h --help] [-v --verbose] [-l --license] [-u user] [-n node] [-d YYYY-MM-DD YYYY-MM-DD]\n %s' % (sys.argv[0], help_text)
    usage = '%prog [-h --help] [-v --verbose] [-l --license] [-u user] [-n node] [-d YYYY-MM-DD YYYY-MM-DD] [--status status] [--session]\n' + help_text
    parser = OptionParser(version=version, usage=usage)

    def license(title, prog, version):
        print (
                        """
                                   _              _       _           
                        __   _____| |__   ___  __| |_   _| | ___ _ __ 
                        \ \ / / __| '_ \ / _ \/ _` | | | | |/ _ \ '__|
                         \ V /\__ \ | | |  __/ (_| | |_| | |  __/ |   
                          \_/ |___/_| |_|\___|\__,_|\__,_|_|\___|_|  
                        """
        )
        print ('''%s \n\t*** %s v%s] ***

        Copyright (C) 2023:
                        Pawsey Supercomputing Centre (www.pawsey.org.au)

        This program is to manage web-based user desktop sessions established 
        through Apache Guacamole (www.guacamole.apache.org). Access could be on the 
        go or through reservations via booked scheduler (www.bookedscheduler.com). 
        Remote desktop link is populated at end user Guacamole dashboard.
        
        ''' %(title, prog, version))

    parser.add_option('-u', dest='<user>', help='check the script against particular user')
    parser.add_option('-n', dest='<node>', help='check the script against particular node')
    parser.add_option('-d', dest='<date>', help='date bracket used only for report')
    parser.add_option('--status', dest='<status>', help='set status for the node')
    parser.add_option('--session', help='retreives user(s) logged into the node(s)')
    parser.add_option('-v', '--verbose', action='store_true', help='verbose/debug mode')
    parser.add_option('-l', '--license', action='store_true', help='license')

    (options, args) = parser.parse_args()

    if options.license:
        license(title, prog, version)
        sys.exit(0)