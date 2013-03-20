# Generates download stats for all days in the given log files,
# except for the oldest and the newest day.
from bandersnatch import apache_reader, apache_stats
import sys, os, csv

def usage(msg=None):
    if msg:
        print msg
    print "Usage: processlogs <pypi-targetdir> logfile [logfile...]"
    raise SystemExit

def main():
    if len(sys.argv) < 3:
        usage()

    targetdir = sys.argv[1]

    if not os.path.exists(targetdir):
        usage(targetdir + ' does not exist')

    if not os.path.exists(os.path.join(targetdir, 'web')):
        usage('Not a pypi mirror (%s/web does not exist)' % targetdir)

    statsdir = os.path.join(targetdir, 'web/local-stats')

    if not os.path.isdir(statsdir):
        os.mkdir(statsdir)
        os.mkdir(os.path.join(statsdir, 'days'))

    days = set()
    records = []
    for fn in sys.argv[2:]:
        for record in apache_reader.ApacheLogReader(fn, files_url='/packages'):
            days.add((record['year'], record['month'], record['day']))
            records.append(record)

    days = sorted(days)[1:-1]

    class Stats(apache_stats.LocalStats):
        def _get_logs(self, logfile, files_url):
            return records
    stats = Stats()
    for year,month,day in days:
        stats.build_local_stats(year, month, day, None, os.path.join(statsdir, 'days'))
