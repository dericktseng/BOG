from constants import SC2EXT
import pathlib
from discord.message import Attachment


def is_replay(attachment: Attachment) -> bool:
    """ determines whether given attachment is an SC2Replay. """
    file_ext = pathlib.Path(attachment.filename).suffix
    return file_ext == SC2EXT and attachment.content_type == None


def boLine(timestamp: str, buildOrderLine: dict) -> str:
    """ return string in format '00:24 Zealot(2) Probe(3)' """
    buildOrderstr = ''
    for line in buildOrderLine:
        count = buildOrderLine[line]
        buildOrderstr += f'{line}({count})' if count != 1 else line
        buildOrderstr += ' '
    return timestamp + ' ' + buildOrderstr.strip()


def pad(string: str, length: int) -> str:
    """ pads string with spaces at end so that it will use length characters """
    diff = length - len(string)
    if diff > 0:
        return string + ' ' * diff
    else:
        return string


def arr_to_string(arr: list, cutoff=float('inf')) -> str:
    """ Converts arr to string table, with cutoff length of characters
    arr is given as an array of arrays of strings, all of arbitrary length.
    expects every string in its list to have the same length
    e.g. arr
    [
        ['line 1', 'line 2'],
        ['line 12', 'line 23', 'line 34']
    ]

    returns:
        line 1 | line 12
        line 2 | line 23
               | line 34
    """
    # removes empty columns from arr
    lst = [col for col in arr if col]

    # catches the error if lst is empty, otherwise max complains
    if not lst:
        return ''

    max_lines = max([len(col) for col in lst])
    paddings = [len(col[0]) for col in lst]

    totalLen = 0
    result = ''
    
    for i in range(max_lines):
        nextstr = ''

        for col in range(len(lst)):
            if col != 0:
                nextstr += ' | '

            if i >= len(lst[col]):
                nextstr += ' ' * paddings[col]
            else:
                nextstr += lst[col][i]

        totalLen += len(nextstr) + 1 # +1 accounts for newline character
        if totalLen < cutoff:
            result += nextstr + "\n"
        else:
            break
            
    return result.strip()


def generate_build_order_list(buildorder: dict) -> list:
    """ from spawningtool player's buildorder dict
    obtain list where each string represents a line in the build order
    """

    strlist = list()
    timestampbuilditem = [None, dict()] # [timestamp, {"probe": 3, "zealot": 2}]

    # ignore workers from the build order
    for builditem in filter(lambda e: not e['is_worker'], buildorder):
        # we need to initialize it
        buildname = builditem['name']
        buildtime = builditem['time']
        if not timestampbuilditem[0]:
            timestampbuilditem[0] = buildtime
        curritemtime = timestampbuilditem[0]

        if curritemtime != buildtime:
            # add string version of timestampbuilditem to strlist
            timestamp, buildline = timestampbuilditem
            strlist.append(boLine(timestamp, buildline))

            # clears timestampbuilditem for new timestamp
            timestampbuilditem[0] = buildtime
            timestampbuilditem[1] = dict()

        # adds current build item to the current time line
        buildline = timestampbuilditem[1]
        if buildname in buildline:
            buildline[buildname] += 1
        else:
            buildline[buildname] = 1

    # append final timestampbuilditem to strlist
    timestamp, buildline = timestampbuilditem
    if timestamp:
        strlist.append(boLine(timestamp, buildline))

    return strlist


def get_replay_strs(replaydata: dict, playername: str) -> str:
    """ Obtains the formatted build order string from replaydata.
    ReplayData is the data obtained from spawningtool parser as documented
    https://github.com/StoicLoofah/spawningtool/wiki/Diving-into-the-Data
    """
    mapname = replaydata['map']
    players = replaydata['players']
    game_type = replaydata['game_type']
    globaldata = game_type + ' ' + mapname

    # total string array to pass to arr_to_string()
    stringarray = list()

    # determines whether we want to just obtain the result for a single player
    playernames = [players[n]['name'].lower() for n in players]
    filterplayer = playername.lower() in playernames

    for p in players:
        player = players[p]
        name = player['name']
        result = player['result'] or ''
        race = player['pick_race']

        # ignore bot players and those that do not pass the filter
        if not player['is_human']:
            continue
        if filterplayer and name.lower() != playername.lower():
            continue

        buildorder = player['buildOrder']
        bostrlist = generate_build_order_list(buildorder)

        header = f'{name} ({race}): {result}'
        longestLineLen = max([len(line) for line in bostrlist])
        headerlen = len(header)
        maxlen = max(headerlen, longestLineLen)
        linebreak = '—' * maxlen
        header = pad(header, maxlen)

        bostrlist = [pad(line, maxlen) for line in bostrlist]
        bostrlist.insert(0, header)
        bostrlist.insert(1, linebreak)

        stringarray.append(bostrlist)

    totalstr = arr_to_string(stringarray)
    return f'{globaldata}\n{totalstr}'
